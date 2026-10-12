#!/usr/bin/env python3
"""Compile the LaTeX CV and publish it to assets/cv/.

    python3 scripts/build_cv.py

Source of truth is `main 2.tex` in the repo root. This builds it with whichever
TeX engine is on PATH and copies the result to assets/cv/Shubham_Gaur_CV.pdf,
which is what cv.html renders and what the Download buttons serve.

If no engine is installed, compile `main 2.tex` elsewhere (Overleaf works) and
drop the PDF at that path by hand. A self-contained option that needs no TeX
installation:

    https://github.com/tectonic-typesetting/tectonic/releases
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "main 2.tex"
OUT = ROOT / "assets" / "cv" / "Shubham_Gaur_CV.pdf"

# (binary, argv builder); first one found on PATH wins
ENGINES = [
    ("tectonic", lambda tex, outdir: ["tectonic", "-X", "compile", str(tex), "--outdir", str(outdir)]),
    ("latexmk", lambda tex, outdir: ["latexmk", "-pdf", "-interaction=nonstopmode",
                                     f"-outdir={outdir}", str(tex)]),
    ("pdflatex", lambda tex, outdir: ["pdflatex", "-interaction=nonstopmode",
                                      f"-output-directory={outdir}", str(tex)]),
    ("xelatex", lambda tex, outdir: ["xelatex", "-interaction=nonstopmode",
                                     f"-output-directory={outdir}", str(tex)]),
]


def main() -> int:
    if not SRC.exists():
        sys.exit(f"missing source: {SRC}")

    engine = next(((name, build) for name, build in ENGINES if shutil.which(name)), None)
    if engine is None:
        sys.exit("no TeX engine found (looked for: "
                 + ", ".join(name for name, _ in ENGINES)
                 + ").\nSee the docstring in this file for how to build without one.")
    name, build = engine

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # copy to a space-free name: some engines mishandle spaces in paths
        tex = tmp / "cv.tex"
        tex.write_bytes(SRC.read_bytes())

        # pdflatex/xelatex need two passes to settle references; latexmk and
        # tectonic handle that themselves
        passes = 2 if name in ("pdflatex", "xelatex") else 1
        for _ in range(passes):
            result = subprocess.run(build(tex, tmp), cwd=tmp,
                                    capture_output=True, text=True)
            if result.returncode != 0:
                sys.stderr.write(result.stdout[-4000:] + result.stderr[-4000:])
                sys.exit(f"{name} failed with exit code {result.returncode}")

        pdf = tmp / "cv.pdf"
        if not pdf.exists():
            sys.exit(f"{name} reported success but produced no PDF")

        OUT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pdf, OUT)

    print(f"built with {name}: {OUT.relative_to(ROOT)} "
          f"({OUT.stat().st_size // 1024} KiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
