# shubham2345.github.io

Personal research site for [Shubham Gaur](https://shubham2345.github.io), Ph.D. student in
Computer Science at UC Santa Cruz.

Static HTML built and served by GitHub Pages.

| Path | What it is |
| --- | --- |
| `index.html` | About, news, research threads, selected publications, experience |
| `publications.html` | Full publication list with labels and per-paper highlights, posters, code |
| `cv.html` | CV rendered in-page with PDF.js |
| `blog.html` | Links to writing hosted on Notion and Medium |
| `misc.html` | Non-research page (placeholder) |
| `assets/css/site.css` | Shared stylesheet for every page |
| `assets/cv/Shubham_Gaur_CV.pdf` | The published CV |

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Updating the CV

The published PDF is generated from a source resume that is **not** committed (it
contains a phone number). Drop the new resume in the repo root and re-run the build
script, which strips the phone number and rebuilds the contact line:

```bash
python3 scripts/build_cv.py
```
