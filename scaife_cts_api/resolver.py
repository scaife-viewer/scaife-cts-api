import os

from capitains_nautilus.cts.resolver import NautilusCTSResolver
from werkzeug.contrib.cache import FileSystemCache

from .data import ROOT_DIR_PATH


root_dir_path = os.environ.get("ROOT_DIR", ROOT_DIR_PATH)
data_path = os.path.join(root_dir_path, "data")
cache_path = os.path.join(root_dir_path, "cache")

if not os.path.exists(data_path):
    os.mkdir(data_path)
if not os.path.exists(cache_path):
    os.mkdir(cache_path)

cache = FileSystemCache(cache_path)

resolver = NautilusCTSResolver(
    [
        os.path.join(data_path, entry)
        for entry in os.listdir(data_path)
        if os.path.isdir(os.path.join(data_path, entry))
    ],
    cache=cache
)


def preload():
    resolver.getMetadata(objectId=None)
