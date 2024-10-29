import asyncio
from pypaperless import Paperless
import argparse


async def main(paperless):
    await paperless.initialize()
    # I gave up on querying the API for 'query=asn:[1 TO 10]', as I got totally
    # random results.
    # See also https://github.com/paperless-ngx/paperless-ngx/discussions/3139
    # Retrieve all documents and filter ourselves:
    docs = sorted(
        filter(
            lambda x: x.archive_serial_number >= 1 and x.archive_serial_number <= 10,
            [doc async for doc in paperless.documents if doc.archive_serial_number],
        ),
        key=lambda x: x.archive_serial_number,
    )
    for doc in docs:
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
