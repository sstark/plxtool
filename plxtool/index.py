from weasyprint import HTML, CSS
from typing import TextIO
from pathlib import Path
from pypaperless import Paperless
import io
from plxtool.helpers import corrmap, docs_by_asnrange


async def index(paperless: Paperless, start: int, end: int):
    await paperless.initialize()
    cor = await corrmap(paperless)
    if end == 0:
        end = await paperless.documents.get_next_asn() - 1
    html = io.StringIO()
    html.write("<html><head><title>Paperless Index</title>\n")
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
    html.seek(0)
    outfile = Path(f"Index-ASN{start}-ASN{end}.pdf")
    make_pdf(html, outfile)
    print(f"{outfile} written.")
    await paperless.close()


def make_pdf(html_obj: TextIO, out: Path):
    html = HTML(file_obj=html_obj)
    css = CSS(
        string="""
        body {
            font-size: 12px;
        }
        td {
            padding-top: 4px;
        }
        .asn {
            font-weight: bold;
            text-align:right;
        }
    """
    )
    html.write_pdf(out, stylesheets=[css])
