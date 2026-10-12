#!/usr/bin/env python3
"""Extract publication teaser figures from the papers themselves.

    python3 scripts/build_teasers.py

Downloads each paper, finds the named figure, crops the artwork above its
caption and writes a web-sized PNG to assets/img/teasers/. Re-run it when a
paper is updated or a new one is added; it is deliberately idempotent.

Papers behind a bot wall (OpenReview) or a paywall (Springer) cannot be
fetched, so those entries carry no teaser and their cards render text-only.
"""
import io
import sys
import urllib.request
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "teasers"
TARGET_WIDTH = 1400         # rendered px; cards show these ~670px wide, so this
                            # stays sharp on 2x displays
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"

# slug -> (url, caption to anchor on, or an explicit (page, rect) fallback)
PAPERS = {
    "relate":      ("https://arxiv.org/pdf/2610.09569", "Figure 1:", None),
    "benchshield": ("https://arxiv.org/pdf/2609.11028", "Figure 1:", None),
    "maat":        ("https://arxiv.org/pdf/2605.30514", "Figure 1:", None),
    "sdo":         ("https://arxiv.org/pdf/2606.06708", "Figure 1.", None),
    # Figure 1 is a single generated image; Figure 2 shows the actual task setup
    "semeval":     ("https://aclanthology.org/2025.semeval-1.274.pdf", "Figure 2:", None),
    # no text captions in this one, so point straight at the first real figure
    "blobs":       ("https://arxiv.org/pdf/2501.04002", None, (1, (38, 328, 258, 436))),
}


def fetch(url: str) -> fitz.Document:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    doc = fitz.open(stream=io.BytesIO(data), filetype="pdf")
    if doc.page_count == 0:
        raise ValueError(f"no pages in {url}")
    return doc


def artwork_above(page: fitz.Page, caption: fitz.Rect) -> fitz.Rect | None:
    """Union of everything drawn or placed above a caption, in its column."""
    boxes = [fitz.Rect(d["rect"]) for d in page.get_drawings()]
    for img in page.get_images(full=True):
        try:
            boxes.append(fitz.Rect(page.get_image_bbox(img)))
        except ValueError:
            continue
    keep = [b for b in boxes
            if b.y1 <= caption.y0 + 2 and b.y0 > 40
            and b.x1 > caption.x0 - 20 and b.x0 < caption.x1 + 20
            and b.width > 8 and b.height > 8 and b.is_valid]
    if not keep:
        return None
    rect = keep[0]
    for b in keep[1:]:
        rect |= b
    return rect


def locate(doc: fitz.Document, caption: str | None, explicit) -> tuple[int, fitz.Rect]:
    if explicit is not None:
        pno, rect = explicit
        return pno, fitz.Rect(*rect)
    for pno in range(min(8, doc.page_count)):
        page = doc[pno]
        hits = page.search_for(caption)
        if not hits:
            continue
        rect = artwork_above(page, hits[0])
        if rect is not None:
            return pno, rect
    raise LookupError(f"could not locate {caption!r}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    failures = []
    for slug, (url, caption, explicit) in PAPERS.items():
        try:
            doc = fetch(url)
            pno, rect = locate(doc, caption, explicit)
            # pad slightly so strokes at the edge are not clipped
            rect = (rect + (-3, -3, 3, 3)) & doc[pno].rect
            dpi = max(72, min(400, round(72 * TARGET_WIDTH / rect.width)))
            pix = doc[pno].get_pixmap(clip=rect, dpi=dpi)
            # these are flat-colour diagrams, so a 256-colour palette is visually
            # identical at a third of the file size
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
            img = img.quantize(colors=256, method=Image.MEDIANCUT)
            path = OUT / f"{slug}.png"
            img.save(path, "PNG", optimize=True)
            print(f"{slug:12s} p{pno + 1} {img.width}x{img.height} "
                  f"-> {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KiB)")
        except Exception as exc:                       # noqa: BLE001 - report and continue
            failures.append(slug)
            print(f"{slug:12s} FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
