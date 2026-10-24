#!/usr/bin/env python3
"""Mechanical structure check of book-of-mormon-1841-pages/page-*.md.

Checks (each problem is printed as `page NNN: message`; exit status 1 if any ERROR):
  ERROR  first line is not `<!-- image NNN -->` matching the file name
  ERROR  `<!-- cont -->` on a page's first paragraph with no text before it (or on a non-first paragraph)
  ERROR  a space before `; : ? !` in the text (the transcription writes none)
  ERROR  stray `--word` fragments or a `---` rule that is not followed by a Footer line
  ERROR  an italic marker CommonMark would not honour (opening * followed by a space, closing * after a space, odd count)
  WARN   chapter numeral not previous + 1 (restarts at each book title; use --allow-gaps while only some pages exist)
  WARN   page ends with a hyphen but the next page has no `<!-- cont -->`
  WARN   printed page number in **Header:** differs from PDF page - 8 (INDEX pages 643-649: - 6) (printed folio errors are kept; confirm)
  INFO   counts of uncertain / illegible comments

Usage:  python3 tools/check_structure.py [--pages-dir DIR] [--allow-gaps] [--quiet]
"""
import argparse
import glob
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFSET = 8  # printed page = PDF page - 8 in the text pages (10-642); the INDEX (643-649) is offset 6, see index_offset()
INDEX_PAGES = range(643, 650)


def index_offset(n):
    return 6 if n in INDEX_PAGES else OFFSET

ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}


def roman(s):
    total = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        total += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return total


def strip_comments(t):
    return re.sub(r'<!--.*?-->', '', t, flags=re.S)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pages-dir', default=str(ROOT / 'book-of-mormon-1841-pages'))
    ap.add_argument('--allow-gaps', action='store_true', help='do not warn about chapter gaps across missing pages')
    ap.add_argument('--quiet', action='store_true', help='print only errors and the summary')
    args = ap.parse_args()

    files = sorted(glob.glob(str(Path(args.pages_dir) / 'page-*.md')))
    errors = warns = 0
    unc = ill = 0
    chapter = None
    prev_n = None
    prev_tail_hyphen = False
    skip_next = False

    def report(level, n, msg):
        nonlocal errors, warns
        if level == 'ERROR':
            errors += 1
        else:
            warns += 1
            if args.quiet:
                return
        print(f'{level:5} page {n:03d}: {msg}')

    for f in files:
        n = int(Path(f).stem.split('-')[1])
        raw = Path(f).read_text(encoding='utf-8')
        first = raw.split('\n', 1)[0].strip()
        if first != f'<!-- image {n:03d} -->':
            report('ERROR', n, f'first line is {first!r}, expected the page comment')
        unc += len(re.findall(r'<!--\s*uncertain', raw))
        ill += raw.count('[illegible]')

        gap_before = prev_n is not None and n != prev_n + 1
        if gap_before and args.allow_gaps:
            skip_next = True  # pages are missing: do not compare the next verse/chapter with the last one seen
        body = re.sub(r'<!--\s*cont\s*-->', '\x00', raw)
        body = strip_comments(body)
        body = re.sub(r'(?m)^\*\*Header:\*\*(.*)$', lambda m: '\x01' + m.group(1), body)
        paras = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]

        # footer / rule consistency
        for m in re.finditer(r'(?m)^---+\s*$', raw):
            after = raw[m.end():].lstrip()
            if not after.startswith('Footer:'):
                report('ERROR', n, 'a `---` rule is not followed by a Footer: line')
        # header printed number
        hm = re.search(r'(?m)^\*\*Header:\*\*\s*(.*)$', raw)
        if hm:
            nums = re.findall(r'\d+', hm.group(1))
            if nums and '[illegible]' not in hm.group(1) and int(nums[0]) != n - index_offset(n):
                report('WARN', n, f'header prints {hm.group(1).strip()!r}, the printed folio expected for PDF page {n} is {n - index_offset(n)}')

        text_paras = [p for p in paras if not p.startswith('\x01') and not p.startswith('Footer:') and not p.startswith('---')]
        for i, p in enumerate(text_paras):
            if '\x00' in p:
                if not p.startswith('\x00'):
                    report('ERROR', n, '`<!-- cont -->` is not at the start of a paragraph')
                elif i != 0:
                    report('ERROR', n, '`<!-- cont -->` on a paragraph that is not the first on the page')
                elif prev_n is None or gap_before:
                    if not args.allow_gaps:
                        report('ERROR', n, '`<!-- cont -->` but the previous page is missing')
        if prev_tail_hyphen and not gap_before and not (text_paras and text_paras[0].startswith('\x00')):
            report('WARN', n, 'previous page ends with a hyphen but this page does not start with `<!-- cont -->`')

        for p in text_paras:
            q = p.replace('\x00', '').strip()
            plain = re.sub(r'[*_]', '', q)
            if re.search(r' [;:?!]', plain):
                report('ERROR', n, f'space before ; : ? ! in: {plain[:60]!r}')
            if re.search(r'(^|\s)--\w', plain):
                report('ERROR', n, f'stray `--` fragment in: {plain[:60]!r}')
            # italic markers that CommonMark would not treat as emphasis: an opening * followed by whitespace, or a closing * after whitespace
            stars = [m.start() for m in re.finditer(r'(?<!\\)\*', q)]
            if len(stars) % 2:
                report('ERROR', n, f'odd number of italic markers in: {plain[:60]!r}')
            for s, pos in enumerate(stars):
                after = q[pos + 1:pos + 2]
                before = q[pos - 1:pos] if pos else ''
                if s % 2 == 0 and (after == '' or after.isspace()):
                    report('ERROR', n, f'opening * is followed by a space (renders as a literal asterisk) in: {q[max(0, pos - 20):pos + 25]!r}')
                if s % 2 == 1 and before.isspace():
                    report('ERROR', n, f'closing * is preceded by a space (renders as a literal asterisk) in: {q[max(0, pos - 20):pos + 25]!r}')
            if re.match(r'^#\s+(?!#)', q) and not re.match(r'^#+\s*CHAPTER', q):
                chapter = None  # a new book title restarts the chapter count
            hm2 = re.match(r'^#+\s*CHAPTER\s+([IVXLC]+|\d+)\b', q)
            if hm2:
                g = hm2.group(1)
                c = int(g) if g.isdigit() else roman(g)
                if chapter is not None and c != chapter + 1 and not skip_next:
                    report('WARN', n, f'chapter {g} ({c}) follows chapter {chapter}')
                chapter = c
                skip_next = False

        if text_paras:
            tail = text_paras[-1].replace('\x00', '').rstrip()
            prev_tail_hyphen = tail.endswith('-') and not tail.endswith(' -') and not tail.endswith('earth-')
        else:
            prev_tail_hyphen = False
        prev_n = n

    print(f'{len(files)} pages: {errors} errors, {warns} warnings; {unc} uncertain comments, {ill} [illegible] marks')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
