import asyncio
from pypaperless import Paperless
import argparse
from pathlib import Path
from plxtool.rename import interactive_rename
from plxtool.index import index
from plxtool.mount import overlay_mount
import os
from collections.abc import MutableMapping


def createArgumentParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="plxtool", description="plxtool description")
    parser.add_argument("-u", "--url", help="Paperless Server URL")
    parser.add_argument("-a", "--auth", help="Paperless Authentication Token")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    parser_index = subparsers.add_parser("index", help="Create ASN index PDF")
    parser_index.add_argument("-s", "--start", type=int, help="Start at this ASN")
    parser_index.add_argument("-e", "--end", type=int, help="End at this ASN")

    parser_mount = subparsers.add_parser(
        "mount", help="Overlay mount originals and archive document directory"
    )
    parser_mount.add_argument(
        "-s",
        "--src",
        required=True,
        help="Paperless folder (will search for originals/archive)",
    )
    parser_mount.add_argument("-t", "--target", required=True, help="Mount point")

    parser_rename = subparsers.add_parser(
        "rename", help="Interactively rename documents"
    )
    parser_rename.add_argument("-f", "--field", required=True, help="Field to rename")
    return parser


def get_auth(args: argparse.Namespace, env: MutableMapping = os.environ) -> tuple[str, str]:
    url = ""
    auth = ""
    if args.url:
        url = args.url
    else:
        try:
            url = env["PLXTOOL_PAPERLESS_URL"]
        except KeyError:
            print("Paperless URL missing")
    if args.auth:
        auth = args.auth
    else:
        try:
            auth = env["PLXTOOL_PAPERLESS_AUTH"]
        except KeyError:
            print("Paperless API token missing")
    return (url, auth)


def cliRun():
    parser = createArgumentParser()
    args = parser.parse_args()

    if args.command == "index":
        paperless = Paperless(args.url, args.auth)
        start = args.start if args.start else 1
        end = args.end if args.end else 0
        asyncio.run(index(paperless, start, end))
    elif args.command == "mount":
        overlay_mount(Path(args.src), Path(args.target))
    elif args.command == "rename":
        interactive_rename(args.field)
