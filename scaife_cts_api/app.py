import json
import logging

from capitains_nautilus.flask_ext import FlaskNautilus
from flask import Flask, jsonify
from flask_caching import Cache

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


@app.route("/repos")
def repos():
    with open("/var/lib/nautilus/repos.json", "r") as f:
        return jsonify(json.loads(f.read()))


@app.route("/healthz")
def healthz():
    return "ok"
