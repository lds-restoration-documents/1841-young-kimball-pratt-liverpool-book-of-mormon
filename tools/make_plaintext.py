#!/usr/bin/env python3
"""Convert book-of-mormon-1841.md into plain text with no Markdown.

Headings become plain lines; * and ** emphasis markers, HTML comments (the page
markers), horizontal rules and tags are removed; tables become tab-separated rows.

Usage:  python3 tools/make_plaintext.py [--md FILE] [--out FILE]
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def to_plaintext(t):
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    out = []
    for l in t.split('\n'):
        if re.match(r'^\s*---+\s*$', l):
            continue
        if l.startswith('|'):
            if re.match(r'^\|[\s:|-]+\|?\s*$', l):  # table separator row
                continue
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            cells = [re.sub(r'\s*<br\s*/?>\s*', ' ', c) for c in cells]
            l = '\t'.join(cells).rstrip('\t')
        else:
            l = re.sub(r'^#{1,6}[ \t]+', '', l)
        l = l.replace('**', '').replace('*', '')
        l = re.sub(r'</?[a-zA-Z][^>]*>', '', l)
        l = re.sub(r'(?<=\S)[ ]{2,}(?=\S)', ' ', l)
        out.append(l.rstrip())
    s = '\n'.join(out)
    return re.sub(r'\n{3,}', '\n\n', s).strip('\n') + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--md', default=str(ROOT / 'book-of-mormon-1841.md'))
    ap.add_argument('--out', default=str(ROOT / 'book-of-mormon-1841.txt'))
    args = ap.parse_args()
    s = to_plaintext(Path(args.md).read_text(encoding='utf-8'))
    Path(args.out).write_text(s, encoding='utf-8')
    print(f'{len(s.split())} words -> {args.out}')


if __name__ == '__main__':
    main()
