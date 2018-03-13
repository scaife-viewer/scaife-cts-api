import json
import os
from collections import defaultdict

import click

from .data import load_repo, resolve_commit


@click.group()
def cli():
    pass


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
    for repo, ref in repos.items():
        sha = resolve_commit(repo, ref)
        load_repo(
            f"https://api.github.com/repos/{repo}/tarball/{sha}",
            os.path.join(root_dir, "data"),
        )
        metadata[repo]["sha"] = sha
        repo_path = os.path.join(root_dir, "data", f"{repo.replace('/', '-')}-{sha[:7]}")
        click.echo(f"Loaded {repo} at {ref} to {sha}")
    with open(os.path.join(root_dir, "repos.json"), "w") as f:
        f.write(json.dumps(dict(metadata)))
