#!/usr/bin/env python3
"""Build the sparse plain-text file (Book of Mormon text only) from book-of-mormon-1841.md.

Keeps book titles, chapter headings and paragraphs from the page ranges that hold the
Book of Mormon proper, plus the title page (PDF page 5: "An account written by the hand of Mormon upon
plates taken from the plates of Nephi ... Moroni"), which was translated from the plates; the imprint paragraphs
on it (translator, edition, printer, publishers, year) are dropped. Also dropped: the title-page verso, the
testimonies, the INDEX, and any paragraph that is only an end marker such as FINIS.

The compiled Markdown carries <!-- page NNN --> markers, which this script uses
to decide what is in range. PAGE_RANGES is specific to the scan (PDF page
numbers, not printed folios): see transcription-notes.md §1.

Usage:  python3 tools/make_sparse.py [--md FILE] [--out FILE] [--verbose]
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Inclusive PDF-page ranges kept: the title page (5, which also carries the abridgment translated from the plates) and the
# text from page 9 (1 Nephi) through page 642 (end of Moroni). Outside it: covers and endpapers (1-4), the title-page verso
# (6), the testimonies (7-8), and the INDEX and blank leaves (643-656). Printed folio = PDF page - 8.
# PROVISIONAL: confirm 642 as the last text page and the title-page paragraphs below against the page files.
PAGE_RANGES = [(5, 5), (9, 642)]

# On the title page, the paragraphs of the 1841 imprint are dropped (they start with these words).
TITLE_PAGE = 5
IMPRINT_PREFIXES = ('TRANSLATED BY', 'JOSEPH SMITH', 'First European', 'PRINTED BY', 'Liverpool', 'FOR BRIGHAM', 'By order', '1841')

END_MARKERS = re.compile(r'\*?(THE END[.,]?|FINIS[.,]?)\*?', re.I)


def in_range(pg):
    return pg is not None and any(a <= pg <= b for a, b in PAGE_RANGES)


def annotate(md_text):
    """Split into paragraphs, each tagged with the image it starts on."""
    page = None
    items = []
    for p in md_text.split('\n\n'):
        ms = re.findall(r'<!-- page (\d+) -->', p)
        clean = re.sub(r'\s*<!-- page \d+ -->\s*', ' ', p).strip()
        if ms and p.startswith('<!-- page'):
            page = int(ms[0])
        if clean:
            items.append((page, clean))
        if ms and not p.startswith('<!-- page'):
            page = int(ms[-1])
    return items


def plain(l):
    l = l.replace('**', '').replace('*', '')
    l = re.sub(r'^#{1,6}[ \t]+', '', l)
    l = re.sub(r'</?[a-zA-Z][^>]*>', '', l)
    return re.sub(r'(?<=\S) {2,}(?=\S)', ' ', l).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--md', default=str(ROOT / 'book-of-mormon-1841.md'))
    ap.add_argument('--out', default=str(ROOT / 'book-of-mormon-1841-sparse.txt'))
    ap.add_argument('--verbose', action='store_true', help='list the paragraphs that were dropped')
    args = ap.parse_args()

    if not PAGE_RANGES:
        raise SystemExit('PAGE_RANGES is empty: set the Book of Mormon page ranges at the top of this script first.')

    items = annotate(Path(args.md).read_text(encoding='utf-8'))
    kept, dropped = [], []
    for pg, p in items:
        if (in_range(pg) and not END_MARKERS.fullmatch(p.strip())
                and not (pg == TITLE_PAGE and p.lstrip('*').startswith(IMPRINT_PREFIXES))):
            kept.append(p)
        else:
            dropped.append((pg, p))
    text = '\n\n'.join(q for q in (plain(p) for p in kept) if q) + '\n'
    text = re.sub(r'\n{3,}', '\n\n', text)
    Path(args.out).write_text(text, encoding='utf-8')
    print(f'kept {len(kept)} paragraphs, dropped {len(dropped)}, {len(text.split())} words -> {args.out}')
    if args.verbose:
        for pg, p in dropped:
            print(pg, p[:70])


if __name__ == '__main__':
    main()
