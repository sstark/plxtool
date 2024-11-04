import asyncio
from pypaperless import Paperless
from pypaperless.models.documents import Document
import argparse
import io
from pathlib import Path
from subprocess import CalledProcessError, run
from plxtool.rename import interactive_rename


async def docs_by_asnrange(
    paperless: Paperless, start: int, end: int
) -> list[Document]:
    # I gave up on querying the API for 'query=asn:[1 TO 10]', as I got totally
    # random results.
    # See also https://github.com/paperless-ngx/paperless-ngx/discussions/3139
    # Retrieve all documents and filter ourselves:
    return sorted(
        [
            doc
            async for doc in paperless.documents
            if doc.archive_serial_number
            and doc.archive_serial_number >= start
            and doc.archive_serial_number <= end
        ],
        key=lambda x: -x.archive_serial_number,
    )


async def corrmap(paperless: Paperless) -> dict[int | None, str | None]:
    return dict([(c.id, c.name) async for c in paperless.correspondents])


async def index(paperless: Paperless, start: int, end: int):
    await paperless.initialize()
    cor = await corrmap(paperless)
    if end == 0:
        end = await paperless.documents.get_next_asn() - 1
    html = io.StringIO()
    html.write("<html><head><title>Paperless Index</title>\n")
    html.write(
        "<style>body{font-size:12px;}td{padding-top:4px;}.asn{font-weight:bold;text-align:right;}</style>\n"
    )
    html.write("</head><body><table>\n")
    for doc in await docs_by_asnrange(paperless, start, end):
        html.write("<tr>\n")
        html.write(f'<td class="asn">{doc.archive_serial_number}</td>')
        html.write(f"<td>{cor[doc.correspondent]}</td>\n")
        html.write(f"<td>{doc.title}</td>\n")
        html.write(f"<td>{doc.created_date}</td>\n")
        html.write("</tr>\n")
    html.write("</table></body></html>\n")
    html.flush()
    print(html.getvalue())
    await paperless.close()


def overlay_mount(src: Path, target: Path) -> bool:
    if not src.exists():
        print(f"{src} does not exist")
        return False
    if not target.exists():
        print(f"Mountpoint {target} does not exist")
        return False
    originals = next(src.rglob("originals"), None)
    if originals is None:
        print('"originals" folder not found')
        return False
    archive = next(src.rglob("archive"), None)
    if archive is None:
        print('"archive" folder not found')
        return False
    if originals.parent != archive.parent:
        print(f"{archive} and {originals} are not in same directory")
        return False
    cmd = [
        "sudo",
        "mount",
        "-t",
        "overlay",
        "overlay",
        f"-olowerdir={originals}:{archive}",
        target,
    ]
    try:
        run(cmd, check=True)
        print(f"Mount successful. You can access your documents under {target}")
        return True
    except CalledProcessError as e:
        print(f"Mounting returned an error: {e}")
        return False


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

    parser_rename = subparsers.add_parser("rename", help="Interactively rename documents")
    parser_rename.add_argument("-f", "--field", required=True, help="Field to rename")
    return parser


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
