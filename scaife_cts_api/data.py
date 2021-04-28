import os
import re
import subprocess

import requests


ROOT_DIR_PATH = os.environ.get("ROOT_DIR", "/var/lib/nautilus")


def load_repo(tarball_url, dest):
    resp = requests.get(tarball_url, stream=True)
    resp.raise_for_status()
    r, w = os.pipe()
    os.makedirs(dest, exist_ok=True)
    proc = subprocess.Popen(["tar", "-zxf", "-", "-C", dest, "--strip-components", "1"], stdin=r)
    os.close(r)
    for chunk in resp.iter_content(chunk_size=4092):
        if chunk:
            os.write(w, chunk)
    os.close(w)
    proc.wait()

