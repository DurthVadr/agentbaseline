"""The papers this repository publishes as PDFs, and where each one's files live.

One table, read by bin/build-pdf (what to render, and where), and by
bin/check-pdf-current and bin/check-pdf-reproducible (what to hold the committed
artifacts to). The checks used to name static/whitepaper.pdf and its manifest in
their own constants; a second paper with a second copy of those constants in each
script is how a check ends up guarding one artifact while the other drifts.

`required` says what an absent artifact means, and both papers are required. The
reference architecture's PDF was optional while it did not exist yet: the site
links it only through fileExists-guarded templates, so a checkout without it
rendered no dead link. Now that it is published, that guard is the failure: delete
the PDF and its manifest and every gate still passed while all five links to it
quietly left the site. A missing PDF is a defect for either paper, and a PDF that
is present is held to its source.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

PAPERS = {
    "whitepaper": {
        "src": ROOT / "whitepaper" / "whitepaper.md",
        "out": ROOT / "static" / "whitepaper.pdf",
        "provenance": ROOT / "whitepaper" / "pdf.provenance.json",
        "work": ROOT / "whitepaper" / ".build",
        "required": True,
    },
    "software-factory": {
        "src": ROOT / "software-factory" / "software-factory.md",
        "out": ROOT / "static" / "software-factory.pdf",
        "provenance": ROOT / "software-factory" / "pdf.provenance.json",
        "work": ROOT / "software-factory" / ".build",
        "required": True,
    },
}

DEFAULT = "whitepaper"
