from pypaperless import Paperless
from pypaperless.models.documents import Document


async def corrmap(paperless: Paperless) -> dict[int | None, str | None]:
    return dict([(c.id, c.name) async for c in paperless.correspondents])


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
