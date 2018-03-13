import os

from capitains_nautilus.cts.resolver import NautilusCTSResolver
from werkzeug.contrib.cache import FileSystemCache


root_path = "/var/lib/nautilus"
data_path = os.path.join(root_path, "data")
cache_path = os.path.join(root_path, "cache")

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
