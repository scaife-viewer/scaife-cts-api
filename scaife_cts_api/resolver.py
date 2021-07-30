import json
import os
from collections import defaultdict
from glob import glob
from pathlib import Path

from MyCapytain.errors import UndispatchedTextError
from capitains_nautilus.cts.resolver import (
    NautilusCTSResolver as BaseNautilusCTSResolver,
)
from MyCapytain.resources.collections.cts import (
    XmlCtsTextgroupMetadata as TextGroup,
    XmlCtsWorkMetadata as Work,
    XmlCtsCitation as Citation,
)
from werkzeug.contrib.cache import FileSystemCache

from .data import ROOT_DIR_PATH


root_dir_path = Path(os.environ.get("ROOT_DIR", ROOT_DIR_PATH))
data_path = Path(root_dir_path, "data")
cache_path = Path(root_dir_path, "cache")

if not data_path.exists():
    data_path.mkdir(parents=True, exist_ok=True)
if not cache_path.exists():
    cache_path.mkdir(parents=True, exist_ok=True)

CACHE_THRESHOLD = 0  # A 0 value is treated by the cache backend as
                     # "no threshold", which will prevent the
                     # "Nautilus_repository_Inventory_Resources" and
                     # "Nautilus_repository_GetMetadata_None" cache keys
                     # from being pruned.
cache = FileSystemCache(cache_path, threshold=CACHE_THRESHOLD)


class NautilusCTSResolver(BaseNautilusCTSResolver):

    def extract_sv_metadata(self, folder):
        metadata_path = Path(folder, ".scaife-viewer.json")
        try:
            return json.load(open(metadata_path))
        except FileNotFoundError:
            print(f"{metadata_path} was not found")
            return {}

    def parse(self, resource=None):
        # NOTE: Extracted from 2dae321722c06fe8873c5f06b3f8fdbd45f643c2
        """Parse a list of directories ans
        :param resource: List of folders
        :param ret: Return a specific item ("inventory" or "texts")
        """
        if resource is None:
            resource = self.__resources__
        removing = []
        # start sv-metadata customization
        repo_urn_lookup = defaultdict()
        # end sv-metadata customization
        for folder in resource:
            # start sv-metadata customization
            repo_metadata = self.extract_sv_metadata(folder)
            repo_metadata["texts"] = []
            # end sv-metadata customization

            textgroups = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=folder))
            for __cts__ in textgroups:
                try:
                    with open(__cts__) as __xml__:
                        textgroup = TextGroup.parse(
                            resource=__xml__
                        )
                        tg_urn = str(textgroup.urn)
                    if tg_urn in self.dispatcher.collection:
                        self.dispatcher.collection[tg_urn].update(textgroup)
                    else:
                        self.dispatcher.dispatch(textgroup, path=__cts__)

                    for __subcts__ in glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(__cts__))):
                        with open(__subcts__) as __xml__:
                            work = Work.parse(
                                resource=__xml__,
                                parent=self.dispatcher.collection[tg_urn]
                            )
                            work_urn = str(work.urn)
                            if work_urn in self.dispatcher.collection[tg_urn].works:
                                self.dispatcher.collection[work_urn].update(work)

                        for __textkey__ in work.texts:
                            __text__ = self.dispatcher.collection[__textkey__]
                            __text__.path = "{directory}/{textgroup}.{work}.{version}.xml".format(
                                directory=os.path.dirname(__subcts__),
                                textgroup=__text__.urn.textgroup,
                                work=__text__.urn.work,
                                version=__text__.urn.version
                            )
                            if os.path.isfile(__text__.path):
                                try:
                                    t = self.read(__textkey__, __text__.path)
                                    cites = list()
                                    for cite in [c for c in t.citation][::-1]:
                                        if len(cites) >= 1:
                                            cites.append(Citation(
                                                xpath=cite.xpath.replace("'", '"'),
                                                scope=cite.scope.replace("'", '"'),
                                                name=cite.name,
                                                child=cites[-1]
                                            ))
                                        else:
                                            cites.append(Citation(
                                                xpath=cite.xpath.replace("'", '"'),
                                                scope=cite.scope.replace("'", '"'),
                                                name=cite.name
                                            ))
                                    del t
                                    __text__.citation = cites[-1]
                                    self.logger.info("%s has been parsed ", __text__.path)
                                    if __text__.citation.isEmpty() is True:
                                        removing.append(__textkey__)
                                        self.logger.error("%s has no passages", __text__.path)
                                except Exception as E:
                                    removing.append(__textkey__)
                                    self.logger.error(
                                        "%s does not accept parsing at some level (most probably citation) ",
                                        __text__.path
                                    )
                                else:
                                    # start sv-metadata customization
                                    repo_metadata["texts"].append(
                                        str(__text__.urn)
                                    )
                                    # end sv-metadata customization
                            else:
                                removing.append(__textkey__)
                                self.logger.error("%s is not present", __text__.path)
                except UndispatchedTextError as E:
                    self.logger.error("Error dispatching %s ", __cts__)
                    if self.RAISE_ON_UNDISPATCHED is True:
                        raise E
                except Exception as E:
                    self.logger.error("Error parsing %s ", __cts__)

            # start sv-metadata customization
            if repo_metadata.get("repo"):
                repo_urn_lookup[repo_metadata["repo"]] = repo_metadata
            # end sv-metadata customization

        for removable in removing:
            del self.dispatcher.collection[removable]

        removing = []

        if self.REMOVE_EMPTY is True:
            # Find resource with no readable descendants
            for item in self.dispatcher.collection.descendants:
                if item.readable != True and len(item.readableDescendants) == 0:
                    removing.append(item.id)

            # Remove them only if they have not been removed before
            for removable in removing:
                if removable in self.dispatcher.collection:
                    del self.dispatcher.collection[removable]

            # @@@ write out our own "inventory"
        corpus_metadata_path = Path(root_dir_path, ".scaife-viewer.json")
        json.dump(list(repo_urn_lookup.values()), open(corpus_metadata_path, "w"), indent=2)

        self.inventory = self.dispatcher.collection
        return self.inventory


resolver = NautilusCTSResolver(
    [
        Path(data_path, entry)
        for entry in data_path.iterdir()
        if Path(data_path, entry).is_dir()
    ],
    cache=cache
)


def preload():
    resolver.getMetadata(objectId=None)
