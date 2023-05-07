import json
import os

from flask import current_app, redirect, request, Response
from . import blueprint


@blueprint.route("/routes")
def routes():
    data = {
        "name": current_app.config["name"],
        "version": current_app.config["version"],
        "routes": {
            "api": [
                "/api/documentation",
                "/api/shutdown",
                "/api/version"
            ],
            "igv": [
                "/igv/demo",
                "/igv/custom",
                "/igv/session"
            ]
        }
    }
    js = json.dumps(data, indent=4, sort_keys=True)
    resp = Response(js, status=200, mimetype="application/json")
    return resp


@blueprint.route("/api/documentation")
def documentation():
    return redirect("https://github.com/igvteam/igv.js", code=302)


@blueprint.route("/api/shutdown")
def shutdown():
    try:
        request.environ.get("werkzeug.server.shutdown")()
    
    except Exception:
        raise RuntimeError("Not running with the Werkzeug Server")

    return "Shutting down..."


@blueprint.route("/api/version")
def api_version():
    data = {
        "tool_version": current_app.config["tool_version"],
        "igv_version": current_app.config["igv_version"]
    }
    js = json.dumps(data, indent=4, sort_keys=True)
    resp = Response(js, status=200, mimetype="application/json")
    return resp