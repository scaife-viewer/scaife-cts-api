import concurrent.futures
import json
import os
from collections import defaultdict

import click

from . import resolver
from .data import ROOT_DIR_PATH, load_repo


@click.group()
def cli():
    pass


@cli.command()
def preload():
    resolver.preload()


@cli.command()
@click.option(
    "--root-dir",
    default=ROOT_DIR_PATH,
    help="root directory to store corpus, cache and metadata",
)
def loadcorpus(root_dir):
    metadata = defaultdict(dict)
    with open(os.path.join(os.curdir, "corpus.json")) as fp:
        repos = json.loads(fp.read())
    fs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for repo, data in repos.items():
            dest = os.path.join(root_dir, "data")
            f = executor.submit(do_load_repo, repo, data, dest)
            fs[f] = (repo, data["ref"])
        for f in concurrent.futures.as_completed(fs):
            repo, ref = fs[f]
            data = f.result()
            metadata[repo].update(data)
            click.echo(f"Loaded {repo} at {ref} to {data['sha']}")
    with open(os.path.join(root_dir, "repos.json"), "w") as f:
        f.write(json.dumps(dict(metadata)))


def write_repo_metadata(metadata_path, data):
    json.dump(data, open(metadata_path, "w"), indent=2)


def do_load_repo(repo, data, dest):
    ref = data["ref"]
    sha = data["sha"]
    tarball_url = data["tarball_url"]
    tarball_path = f"{repo.replace('/', '-')}-{ref}-{sha[:7]}"
    absolute_tarball_path = os.path.join(dest, tarball_path)
    load_repo(tarball_url, absolute_tarball_path)
    repo_metadata = {
        "repo": repo,
        "sha": sha,
        "ref": ref,
        "tarball_url": tarball_url,
    }
    metadata_path = os.path.join(absolute_tarball_path, ".scaife-viewer.json")
    write_repo_metadata(metadata_path, repo_metadata)
    return repo_metadata


@cli.command()
@click.option(
    "--preload",
    default=False,
    is_flag=True,
    help="preload data before running web server"
)
def serve(preload):
    if preload:
        resolver.preload()
    args = [
        "gunicorn",
        "--log-config=logging.ini",
        "scaife_cts_api.app:app",
    ]
    os.execvp(args[0], args)
