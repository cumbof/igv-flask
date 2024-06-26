#!/usr/bin/env python3
"""Flask webserver for rendering igv.js"""

__author__ = "Fabio Cumbo (fabio.cumbo@gmail.com)"
__version__ = "1.4"
__date__ = "Apr 29, 2024"

import argparse as ap
import errno
import json
import os
import sys

from flask import Flask
from igv.routes import *

TOOL_ID = "igv-tool"

IGV_VERSION = "2.15.5"

# https://github.com/igvteam/igv.js/wiki/Tracks-2.0
IGV_TYPES = {
    "annotation": ["bed", "gff", "gff3", "gtf", "bedpe"],  # Non-quantitative genome annotations such as genes. This is the most generic track type
    "wig": ["wig", "bigWig", "bedGraph"],  # Quantitative genomic data, such as ChIP peaks and alignment coverage
    "alignment": ["bam", "cram"],  # Sequencing and alignments
    "variant": ["vcf"],  # Genomic variants
    "seg": ["seg"],  # Segmented copy number data
    "mut": ["maf", "mut"],  # Mutation data, primarily from cancer studies
    "interact": ["bedpe", "interact", "bigInteract"],  # Arcs representing associations or interactions between 2 genomic loci
    "gwas": ["gwas", "bed"],  # Genome wide association data (manhattan plots)
    "arc": ["bp", "bed"],  # RNA secondary structure
    "junction": ["bed"],  # RNA splice junctions
}


def read_params(argv):
    """Read and test input arguments.

    Returns
    -------
    The ArgumentParser object
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
        "--cytoband",
        type=os.path.abspath,
        help="Path to the input cytoband file"
    )
    p.add_argument(
        "--tracks-path",
        type=os.path.abspath,
        nargs="+",
        required=False,
        dest="tracks_path",
        help="Path to one or more input track files"
    )
    p.add_argument(
        "--tracks-type",
        type=str,
        nargs="+",
        choices=list(IGV_TYPES.keys()),
        dest="tracks_type",
        help="Type of input track files"
    )
    p.add_argument(
        "--tracks-format",
        type=str,
        nargs="+",
        dest="tracks_format",
        help="Format of input track files"
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
    return p.parse_args(argv)


def main():
    # Load command line parameters
    args = read_params(sys.argv[1:])

    # Check whether the input fasta file exist
    if args.input and not os.path.isfile(args.input):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.input)

    # Also check whether the input index file exist
    if args.index and not os.path.isfile(args.index):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.index)

    # Do the same for the cytoband file
    if args.cytoband and not os.path.isfile(args.cytoband):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.cytoband)

    # Do the same for tracks
    if args.tracks_path:
        if args.tracks_type:
            if len(args.tracks_path) != len(args.tracks_type):
                raise Exception("Unspecified track type")

        if args.tracks_format:
            if len(args.tracks_path) != len(args.tracks_format):
                raise Exception("Unspecified track format")

        for track_pos, track in enumerate(args.tracks_path):
            if not os.path.isfile(track):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), track)

            if args.tracks_type and args.tracks_format:
                if args.tracks_format[track_pos] not in IGV_TYPES[args.tracks_type[track_pos]]:
                    raise Exception(
                        "[{}]: Unsupported format \"{}\" for track type \"{}\"".format(
                            track,
                            args.tracks_format[track_pos],
                            args.tracks_type[track_pos]
                        )
                    )

    # Check whether the json igv session file exist
    if args.igv_session and not os.path.isfile(args.igv_session):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.igv_session)

    if args.gxit and args.dump_session and os.path.isfile(args.dump_session):
        print("Warning: the output IGV session file already exists!")

    if args.gxit and args.dump_session and args.run_it and args.input:
        # Save an empty IGV session file and exit
        # Used for testing purposes only
        with open(args.dump_session, "w+") as igv_session:
            session_dict = {
                "version": IGV_VERSION,
                "reference": {
                    "id": os.path.splitext(os.path.basename(args.input))[0],
                    "name": os.path.splitext(os.path.basename(args.input))[0],
                    "fastaURL": os.path.join("/static", os.path.basename(args.input))
                },
                "wholeGenomeView": True
            }

            if args.index:
                session_dict["indexURL"] = os.path.basename(args.index)

            else:
                session_dict["indexed"] = False
            
            if args.cytoband:
                session_dict["cytobandURL"] = os.path.basename(args.cytoband)
            
            if args.tracks_path:
                session_dict["tracks"] = list()

                for track_pos, track in enumerate(args.tracks_path):
                    track_dict = {
                        "name": os.path.basename(track),
                        "url": os.path.basename(track),
                    }

                    if args.tracks_type:
                        track_dict["type"] = args.tracks_type[track_pos]

                    if args.tracks_format:
                        track_dict["format"] = args.tracks_format[track_pos]

                    session_dict["tracks"].append(track_dict)

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

    if args.input:
        # Symlink the input file in the static folder
        # And add the input file name to the config
        static_input = os.path.join(working_dir, "static", os.path.basename(args.input))

        if not os.path.exists(static_input):
            os.symlink(args.input, static_input)

        app.config["input"] = os.path.basename(static_input)

        if args.index:
            # Do the same with the index file
            static_index = os.path.join(working_dir, "static", os.path.basename(args.index))

            if not os.path.exists(static_index):
                os.symlink(args.index, static_index)

            app.config["index"] = os.path.basename(static_index)

        if args.cytoband:
            # Do the same with the cytoband file
            static_cytoband = os.path.join(working_dir, "static", os.path.basename(args.cytoband))

            if not os.path.exists(static_cytoband):
                os.symlink(args.cytoband, static_cytoband)

            app.config["cytoband"] = os.path.basename(static_cytoband)

        if args.tracks_path:
            # And again for tracks
            app.config["tracks"] = list()

            for track_pos, track in enumerate(args.tracks_path):
                static_track = os.path.join(working_dir, "static", os.path.basename(track))

                if not os.path.exists(static_track):
                    os.symlink(track, static_track)

                track_dict = {
                    "name": os.path.basename(static_track),
                    "url": os.path.basename(static_track),
                }

                if args.tracks_type:
                    track_dict["type"] = args.tracks_type[track_pos]

                if args.tracks_format:
                    track_dict["format"] = args.tracks_format[track_pos]

                app.config["tracks"].append(track_dict)

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
