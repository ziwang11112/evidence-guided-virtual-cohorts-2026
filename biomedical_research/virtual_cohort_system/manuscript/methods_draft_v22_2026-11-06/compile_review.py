"""Compile the paper and independent ZIP; render a contact sheet for each 6 pages."""
import argparse
from pathlib import Path
import subprocess
import zipfile

import fitz
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent


def compile_twice(folder):
    for index in [1,2]:
        path = folder / f"build-pass-{index}.txt"
        with path.open("w", encoding="utf8") as stream:
            subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error", "paper.tex"],
                           cwd=folder, stdout=stream, stderr=subprocess.STDOUT, check=True)


def render():
    folder = HERE / "tmp/pdfs/render"
    folder.mkdir(parents=True, exist_ok=True)
    with fitz.open(HERE / "paper.pdf") as doc:
        for j,p in enumerate(doc,1):
            pix = p.get_pixmap(matrix=fitz.Matrix(1.25,1.25), alpha=False)
            pix.save(str(folder / f"page-{j:02d}.png"))
        n = len(doc)
    for first in range(1,n+1,6):
        canvas = Image.new("RGB", (1320, 1170), "#dadce1")
        draw = ImageDraw.Draw(canvas)
        for index in range(first,min(first+6,n+1)):
            x = ((index-first) % 3) * 440
            y = ((index-first) // 3) * 585
            with Image.open(folder / f"page-{index:02d}.png") as image:
                image.thumbnail((426,550))
                canvas.paste(image, (x+5,y+22))
            draw.text((x+6, y+4),str(index),fill="#111827")
        canvas.save(folder / f"sheet-{first:02d}.png")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--standalone",action="store_true")
    p.add_argument("--render",action="store_true")
    opts=p.parse_args()
    if opts.standalone:
        standalone=HERE/"tmp/pdfs/standalone"
        standalone.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(HERE/"overleaf_v22.zip") as archive:
            archive.extractall(standalone)
        compile_twice(standalone)
    else:
        compile_twice(HERE)
    if opts.render:
        render()


if __name__=="__main__":main()
