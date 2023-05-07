#!/usr/bin/env python3
"""
Flask webserver for rendering igv.js
"""

__author__ = "Fabio Cumbo (fabio.cumbo@gmail.com)"
__version__ = "1.1"
__date__ = "May 4, 2023"

import argparse as ap
import errno
import json
import os
import shutil
import sys

from flask import Flask
from igv.routes import *

TOOL_ID = "igv-tool"

IGV_VERSION = "2.15.5"


def read_params():
    """
    Read and test input arguments

    :return:    The ArgumentParser object
    """

    p = ap.ArgumentParser(
        prog=TOOL_ID,
        description="Flask app with IGV",
        formatter_class=ap.ArgumentDefaultsHelpFormatter
    )
    p.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Webserver host address"
    )
    p.add_argument(
        "--port",
        type=int,
        default="5000",
        help="Webserver port number"
    )
    p.add_argument(
        "--input",
        type=os.path.abspath,
        help="Path to the input fasta file"
    )
    p.add_argument(
        "--index",
        type=os.path.abspath,
        help="Path to the input fasta index file"
    )
    p.add_argument(
        "--igv-session",
        type=os.path.abspath,
        dest="igv_session",
        help="Path to the json igv session file"
    )
    p.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Run Flask in debug mode"
    )
    p.add_argument(
        "--gxit",
        "--galaxy-interactive-tool",
        action="store_true",
        default=False,
        dest="gxit",
        help="The webserver has been started from Galaxy"
    )
    p.add_argument(
        "--dump-session",
        type=os.path.abspath,
        dest="dump_session",
        help="Dump the IGV session to a json file. This works in conjunction with --gxit"
    )
    p.add_argument(
        "--run-it",
        action="store_true",
        default=False,
        dest="run_it",
        help="Generate a session file and exit. Used in conjunction with --gxit and --dump-session only"
    )
    p.add_argument(
        "-v",
        "--version",
        action="version",
        version='"{}" version {} ({})'.format(TOOL_ID, __version__, __date__),
        help='Print the "{}" version and exit'.format(TOOL_ID)
    )
    return p.parse_args()


def main():
    # Load command line parameters
    args = read_params()

    # Check whether the input fasta file exist
    if args.input and not os.path.isfile(args.input):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.input)
    
    # Check whether the input index file exist
    if args.index and not os.path.isfile(args.index):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.index)

    # Check whether the json igv session file exist
    if args.igv_session and not os.path.isfile(args.igv_session):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.igv_session)

    if args.gxit and args.dump_session and os.path.isfile(args.dump_session):
        raise Exception("The output IGV session file already exists: {}".format(args.dump_session))

    if args.gxit and args.dump_session and args.run_it:
        # Save an empty IGV session file and exit
        # Used for testing purposes only
        with open(args.dump_session, "w+") as igv_session:
            session_dict = {
                "version": IGV_VERSION,
                "showSampleNames": False,
                "reference": {},
                "locus": "all",
                "roi": [],
                "tracks": []
            }

            json.dump(session_dict, igv_session)

            sys.exit(0)

    # Define the working directory
    working_dir = os.path.dirname(os.path.realpath(__file__))

    # Starting flask
    print(" * Configuring Flask")

    # Initializing app
    app = Flask(TOOL_ID, static_folder=os.path.join(working_dir, "static"), template_folder=os.path.join(working_dir, "templates"))

    # Register Blueprint
    # It is defined in routes/__init__.py
    app.register_blueprint(blueprint)

    # Register app name and version
    app.config["name"] = TOOL_ID
    app.config["tool_version"] = __version__
    app.config["igv_version"] = IGV_VERSION

    if args.input and args.index:
        # Copy the input file to the static folder
        # And add the input file name to the config
        shutil.copy(args.input, os.path.join(working_dir, "static", os.path.basename(args.input)))
        app.config["input"] = os.path.basename(args.input)

        # Do the same with the index file
        shutil.copy(args.index, os.path.join(working_dir, "static", os.path.basename(args.index)))
        app.config["index"] = os.path.basename(args.index)

        # Session file is used in conjunction with an input fasta only
        if args.igv_session:
            # Add the path to the json igv session file
            # Use json.load to check whether the input --igv-session is a valid json file
            app.config["igv_session"] = json.dumps(json.load(open(args.igv_session)))

    # The webserver has been started from Galaxy
    app.config["gxit"] = args.gxit

    if args.gxit and args.dump_session:
        # Dump the IGV session to a json file
        app.config["dump_session"] = args.dump_session

    # Start Flask
    app.secret_key = os.urandom(16)
    app.run(debug=args.debug, host=args.host, port=args.port, threaded=True)


if __name__ == "__main__":
    main()
