"""Definition-only HAALSI codebook extraction; never emit summary columns.

Read only the approved hash-bound PDF. No participant file or network access.
Optional private PNGs are masked before saving; the source PDF is unchanged.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

import fitz
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "private_documents/HAALSI Baseline Codebook.pdf"
EXPECTED = "49d79434d4836485f2e3291ff884535b42b356821a183985d20f6d7bcbfcaa07"
HEADERS = {"Variable": 48.6, "Type": 190.5, "Obs": 220.2, "Mean": 248.4,
           "Min": 304.9, "Max": 361.2, "Label": 412.0, "Source": 602.3}
WINDOWS = {"variable": (44, 185), "type": (188, 214), "label": (410, 598), "source": (600, 775)}
MATCH = re.compile(r"\bage\b|\bsex\b|gender|bmi|body.?mass|height|weight|glucose|hba1|glycat|fast|diabet|insulin|blood.?spot|"
                   r"blood.?sample|primary.?key|strat|cluster|village|medication|blood.?test|specimen|last.?ate|last.?eat|hours.?since", re.I)


def open_checked():
    if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED:
        raise ValueError("PDF identity changed")
    document = fitz.open(PDF)
    for page in document:
        if tuple(page.rect) != (0.0, 0.0, 792.0, 612.0):
            raise ValueError("Unreviewed page geometry")
        header = {w[4]: w[0] for w in page.get_text("words") if w[1] < 71 and w[4] in HEADERS}
        if set(header) != set(HEADERS) or any(abs(header[k] - x) > .15 for k, x in HEADERS.items()):
            raise ValueError("Unreviewed table layout; stop before extraction")
    return document


def definition_rows(document):
    records = []
    for page_index, page in enumerate(document):
        # Filter by geometry before retaining or emitting any cell text. The
        # forbidden Obs/Mean/Min/Max interval never enters a definition row.
        safe = {name: [w for w in page.get_text("words")
                       if w[1] >= 70 and w[0] >= left and w[2] <= right]
                for name, (left, right) in WINDOWS.items()}
        starts = {}
        for word in safe["variable"]:
            starts.setdefault(round(word[1], 1), []).append(word)
        ordered = sorted(starts)
        for index, y in enumerate(ordered):
            until = ordered[index + 1] - .2 if index + 1 < len(ordered) else 570
            row = {"page": page_index + 1, "row_y": y}
            for name, words in safe.items():
                kept = sorted((w for w in words if y - .2 <= w[1] < until), key=lambda w: (round(w[1], 1), w[0]))
                row[name] = " ".join(w[4] for w in kept)
            if MATCH.search(row["variable"] + " " + row["label"]) or re.match(r"^(?:c_|fl_c_)?bs", row["variable"]):
                records.append(row)
    return records


def masked_page(document, page_number):
    page = document[page_number - 1]
    zoom = 1.75
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    # Only definition windows are copied into an otherwise blank image. No
    # summary pixels reach the written PNG or the model's image viewer.
    masked = Image.new("RGB", image.size, "white")
    for left, right in WINDOWS.values():
        box = (int(left * zoom), 0, int(right * zoom), image.height)
        masked.paste(image.crop(box), box[:2])
    draw = ImageDraw.Draw(masked)
    # Also cover a forbidden word's entire bounding box if a long summary cell
    # protrudes past its nominal column boundary. No partial numbers survive.
    for word in page.get_text("words"):
        if 215 <= word[0] < 410:
            draw.rectangle((int(word[0] * zoom) - 2, int(word[1] * zoom) - 2,
                            int(word[2] * zoom) + 2, int(word[3] * zoom) + 2), fill="white")
    draw.rectangle((int(215 * zoom), int(45 * zoom), int(409 * zoom), int(570 * zoom)), fill="#dddddd")
    draw.text((int(230 * zoom), int(30 * zoom)), "SUMMARY COLUMNS MASKED", fill="black")
    destination = ROOT / "private_documents/schema_masks"
    destination.mkdir(exist_ok=True)
    path = destination / f"codebook_definition_only_page_{page_number:03d}.png"
    masked.save(path)
    return str(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mask-pages", type=int, nargs="*", default=[])
    args = parser.parse_args()
    document = open_checked()
    if args.mask_pages:
        print(json.dumps({"masked_images": [masked_page(document, p) for p in args.mask_pages]}, indent=2))
    else:
        print(json.dumps({"kind": "definition_cells_only_no_observed_summaries", "pages": len(document),
                          "source_sha256": EXPECTED, "records": definition_rows(document)}, indent=2))
