import json
import os

from flask import current_app, render_template, Response, request
from . import blueprint


@blueprint.route("/")
def root_route():
    if "input" in current_app.config:
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


@blueprint.route("/igv/<string:page>", methods=["GET", "POST"])
def web(page):
    if page.strip() == "demo" or page.strip() == "index" or page.strip() == "home":
        return render_template("demo.html")

    elif page.strip() == "custom":
        return render_template(
            "custom.html",
            name=os.path.splitext(current_app.config["input"])[0],
            fasta=current_app.config["input"],
            index=current_app.config["index"] if "index" in current_app.config else False,
            cytoband=current_app.config["cytoband"] if "cytoband" in current_app.config else False,
            tracks=current_app.config["tracks"] if "tracks" in current_app.config else False
        )

    elif page.strip() == "session":
        igv_session = request.get_json()

        print(igv_session)

        if "dump_session" in current_app.config:
            with open(current_app.config["dump_session"], "w+") as igv:
                igv.write(json.dumps(igv_session))
            
            data = {
                "message": "IGV session dumped to {}".format(current_app.config["dump_session"]),
                "type": "Info",
                "status": 200
            }
            js = json.dumps(data, indent=4, sort_keys=True)
            resp = Response(js, status=200, mimetype="application/json")
            return resp

    else:
        return page_not_found()
