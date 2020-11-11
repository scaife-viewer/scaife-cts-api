import json
import logging
import os

from capitains_nautilus.flask_ext import FlaskNautilus
from flask import Flask, jsonify
from flask_caching import Cache
from raven.contrib.flask import Sentry

from .data import ROOT_DIR_PATH
from .resolver import resolver


app = Flask("Nautilus")
http_cache = Cache(config={"CACHE_TYPE": "simple"})
nautilus = FlaskNautilus(
    app=app,
    prefix="/api",
    name="nautilus",
    resolver=resolver,
    flask_caching=http_cache,
    logger=logging.getLogger("nautilus"),
)
http_cache.init_app(app)
Sentry(app)


@app.route("/repos")
def repos():
    repos_json = os.path.join(ROOT_DIR_PATH, "repos.json")
    with open(repos_json, "r") as f:
        return jsonify(json.loads(f.read()))

@app.route("/corpus-metadata")
def corpus_metadata():
    repos_json = os.path.join(ROOT_DIR_PATH, ".scaife-viewer.json")
    with open(repos_json, "r") as f:
        return jsonify(json.loads(f.read()))


@app.route("/healthz")
def healthz():
    return "ok"
