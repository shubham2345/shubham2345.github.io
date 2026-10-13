# shubham2345.github.io

Personal research site for [Shubham Gaur](https://shubham2345.github.io), Ph.D. student in
Computer Science at UC Santa Cruz.

Static HTML built and served by GitHub Pages.

| Path | What it is |
| --- | --- |
| `index.html` | About, news, research threads, selected publications, experience |
| `publications.html` | Full publication list with labels and per-paper highlights, posters, code |
| `blog.html` | Links to writing hosted on Notion and Medium |
| `misc.html` | Non-research page (placeholder) |
| `main 2.tex` | CV source |
| `assets/css/site.css` | Shared stylesheet for every page (light + dark themes) |
| `assets/js/theme.js` | Light/dark toggle |
| `assets/cv/Shubham_Gaur_CV.pdf` | The published CV, built from `main 2.tex` |
| `assets/img/figures/` | Publication teaser figures, extracted from the papers |
| `assets/img/figures/blobs.svg` | Hand-drawn; see `scripts/build_teasers.py` for why |

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Updating the CV

`main 2.tex` is the source of truth. Edit it, then:

```bash
python3 scripts/build_cv.py
```

That compiles it with whatever TeX engine is on PATH (tectonic, latexmk, pdflatex
or xelatex) and writes `assets/cv/Shubham_Gaur_CV.pdf`. The CV link in the nav
opens that file directly. With no TeX installed, compile the
file on Overleaf and drop the PDF at that path instead.

The phone number is commented out in the header because this file is published;
uncomment it for private copies.

## Updating publication teasers

```bash
python3 scripts/build_teasers.py
```

Downloads each paper, crops the figure named in the script's `PAPERS` table, and
writes web-sized PNGs to `assets/img/figures/`. Papers behind a bot wall
(OpenReview) or a paywall (Springer) cannot be fetched; those cards render
text-only until an image is added by hand.
