#!/usr/bin/env python3
"""Download PDFs listed in a CSV file.

Defaults:
- CSV: data/books/books.csv
- Output dir: data/books/pdfs

Usage:
  python download_pdfs.py
  python download_pdfs.py --csv path/to.csv --outdir out/dir
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import urllib.parse
from typing import Optional

import requests


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s]+", "_", s)
    return s[:200]


def get_filename_from_url(url: str) -> str:
    p = urllib.parse.urlparse(url)
    name = os.path.basename(p.path)
    if name and "." in name:
        return name
    # fallback
    host = p.netloc.replace(":", "_")
    return f"{slugify(host)}.pdf"


def download_file(url: str, dest_path: str, session: requests.Session) -> bool:
    try:
        with session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as fh:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        fh.write(chunk)
        return True
    except Exception as exc:  # pragma: no cover - network errors
        print(f"Error downloading {url}: {exc}")
        return False


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Download PDFs from a CSV file.")
    parser.add_argument("--csv", default=os.path.join("data", "books", "books.csv"), help="Path to CSV file")
    parser.add_argument("--outdir", default=os.path.join("data", "books", "pdfs"), help="Output directory")
    parser.add_argument("--url-column", default="pdf_url", help="CSV column with PDF URL")
    parser.add_argument("--title-column", default="title", help="CSV column with book title")
    args = parser.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)

    try:
        f = open(args.csv, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"CSV file not found: {args.csv}")
        return 2

    with f:
        reader = csv.DictReader(f)
        session = requests.Session()
        for idx, row in enumerate(reader, start=1):
            url = (row.get(args.url_column) or "").strip()
            title = (row.get(args.title_column) or f"book_{idx}").strip()
            if not url:
                print(f"Row {idx}: no URL found, skipping")
                continue

            remote_name = get_filename_from_url(url)
            safe_title = slugify(title)
            filename = f"{idx:03d}_{safe_title}_{remote_name}"
            dest = os.path.join(args.outdir, filename)

            if os.path.exists(dest):
                print(f"{idx:03d}: exists, skipping -> {dest}")
                continue

            print(f"{idx:03d}: Downloading '{title}'")
            ok = download_file(url, dest, session)
            if not ok:
                print(f"{idx:03d}: Failed: {url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
