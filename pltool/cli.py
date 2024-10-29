import asyncio
from pypaperless import Paperless
import argparse


async def docs_by_asnrange(paperless, start, end):
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
        key=lambda x: x.archive_serial_number,
    )


async def main(paperless):
    await paperless.initialize()
    for doc in await docs_by_asnrange(paperless, 1, 10):
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
