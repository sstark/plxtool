import asyncio
from pypaperless import Paperless
import argparse


async def main(paperless):
    await paperless.initialize()
    async for doc in paperless.documents.search(f"asn:[1 TO 105]"):
        print(f"ASN{doc.archive_serial_number}: {doc.title}")
    await paperless.close()


def createArgumentParser():
    parser = argparse.ArgumentParser(prog="pltool", description="pltool description")
    parser.add_argument("-u", "--url", required=True, help="Paperless Server URL")
    parser.add_argument(
        "-a", "--auth", required=True, help="Paperless Authentication Token"
    )
    return parser


def cliRun():
    parser = createArgumentParser()
    args = parser.parse_args()
    paperless = Paperless(args.url, args.auth)
    asyncio.run(main(paperless))
