import os
import re
import subprocess

import requests


ROOT_DIR_PATH = os.environ.get("ROOT_DIR", "/var/lib/nautilus")


def load_repo(tarball_url, dest):
    resp = requests.get(tarball_url, stream=True)
    resp.raise_for_status()
    r, w = os.pipe()
    proc = subprocess.Popen(["tar", "-zxf", "-", "-C", dest], stdin=r)
    os.close(r)
    for chunk in resp.iter_content(chunk_size=4092):
        if chunk:
            os.write(w, chunk)
    os.close(w)
    proc.wait()


def resolve_commit(repo, ref):
    if re.match(r"^[a-f0-9]{40}$", ref):
        return ref
    ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{ref}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    resp = requests.get(ref_url, headers=headers)
    if resp.status_code == 404:
        tag_url = f"https://api.github.com/repos/{repo}/git/tags/{ref}"
        resp = requests.get(tag_url, headers=headers)
        if resp.status_code == 404:
            raise Exception(f"{repo}: ref ({ref}) not found")
        else:
            resp.raise_for_status()
            ref_obj = resp.json()["object"]
    else:
        resp.raise_for_status()
        ref_obj = resp.json()["object"]
    return ref_obj["sha"]
