import concurrent.futures
import json
import os
from collections import defaultdict

import click

from . import resolver
from .data import load_repo, resolve_commit


@click.group()
def cli():
    pass


@cli.command()
def preload():
    resolver.preload()


@cli.command()
@click.option(
    "--root-dir",
    default="/var/lib/nautilus",
    help="root directory to store corpus, cache and metadata",
)
def loadcorpus(root_dir):
    metadata = defaultdict(dict)
    with open(os.path.join(os.curdir, "corpus.json")) as fp:
        repos = json.loads(fp.read())
    fs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for repo, ref in repos.items():
            dest = os.path.join(root_dir, "data")
            f = executor.submit(do_load_repo, repo, ref, dest)
            fs[f] = (repo, ref)
        for f in concurrent.futures.as_completed(fs):
            repo, ref = fs[f]
            sha = f.result()
            metadata[repo]["sha"] = sha
            # repo_path = os.path.join(root_dir, "data", f"{repo.replace('/', '-')}-{sha[:7]}")
            click.echo(f"Loaded {repo} at {ref} to {sha}")
    with open(os.path.join(root_dir, "repos.json"), "w") as f:
        f.write(json.dumps(dict(metadata)))


def do_load_repo(repo, ref, dest):
    sha = resolve_commit(repo, ref)
    tarball_url = f"https://api.github.com/repos/{repo}/tarball/{sha}"
    load_repo(tarball_url, dest)
    return sha


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
        "--bind=0.0.0.0",
        "--log-config=logging.ini",
        "scaife_cts_api.app:app",
    ]
    os.execvpe(args[0], args, os.environ.copy())
