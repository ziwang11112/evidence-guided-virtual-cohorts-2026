"""Download an identified public data supplement without displaying participant values."""
from pathlib import Path
import hashlib
import json
import sys

import pandas as pd
import pyreadstat
import requests

from catalogue import PRIVATE


def obtain(doi, ext):
    ident = doi.rsplit("/", 1)[-1]
    path = PRIVATE / (ident + "." + ext)
    if not path.exists():
        r = requests.get("https://journals.plos.org/plosone/article/file",
                         params={"id": doi, "type": "supplementary"}, timeout=50)
        r.raise_for_status()
        if not 0 < len(r.content) < 20_000_000:
            raise ValueError("Unexpected file size")
        path.write_bytes(r.content)
    if ext == "sav":
        _, meta = pyreadstat.read_sav(path, metadataonly=True)
        fields = dict(zip(meta.column_names, meta.column_labels))
    else:
        fields = {}
    return {"doi": doi, "size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "fields": {k:v for k,v in fields.items() if any(w in (str(k) + str(v)).lower()
                       for w in ("chol", "hdl", "lipid", "age", "ident", "idno", "ldl", "tg"))}}


if __name__ == "__main__":
    print(json.dumps(obtain(*sys.argv[1:]), ensure_ascii=True))
