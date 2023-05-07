import json
import os

from flask import current_app, render_template, Response, request
from . import blueprint


@blueprint.route("/")
def root_route():
    if "input" in current_app.config and "index" in current_app.config:
        return web("custom")

    return web("demo")


@blueprint.errorhandler(404)
def page_not_found():
    err = {
        "message": "This route does not exist",
        "type": "Error",
        "status": 404
    }
    js = json.dumps(err, indent=4, sort_keys=True)
    resp = Response(js, status=404, mimetype="application/json")
    return resp


@blueprint.route("/igv/<string:page>", methods = ["GET", "POST"])
def web(page):
    if page.strip() == "demo" or page.strip() == "index" or page.strip() == "home":
        return render_template("demo.html")

    elif page.strip() == "custom":
        # An IGV session is already into config in case of --igv-session
        return render_template("custom.html", fasta=current_app.config["input"], index=current_app.config["index"])

    elif page.strip() == "session":
        igv_session = request.get_json()

        if "igv_session" in current_app.config:
            with open(current_app.config["igv_session"], "w+") as igv:
                igv.write(json.dumps(igv_session))
            
            data = {
                "message": "IGV session dumped to {}".format(current_app.config["igv_session"]),
                "type": "Info",
                "status": 200
            }
            js = json.dumps(data, indent=4, sort_keys=True)
            resp = Response(js, status=200, mimetype="application/json")
            return resp

    else:
        return page_not_found()


