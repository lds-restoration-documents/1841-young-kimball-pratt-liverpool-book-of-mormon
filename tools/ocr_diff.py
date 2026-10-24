#!/usr/bin/env python3
"""Flag pages whose transcription disagrees with a local tesseract OCR of the scan.

For each PDF page the full page image is OCR'd with tesseract (cached in work/ocr/),
and compared word by word with the page file (comments, markdown and punctuation ignored). Disagreements are
runs of 4 or more characters that differ (compared as letters and digits with spaces removed), including real
words the OCR has and the transcription lacks (a dropped word). The OCR is noisy (bleed-through, worn type), so this only
ranks pages for the blind proofread; it never edits anything.

Writes work/ocr/summary.tsv (page, words, diffs, rate) and work/ocr/diffs/NNN.txt (the disagreeing words with a bit
of context). Usage: python3 tools/ocr_diff.py [--pages 9-642] [--force]
Needs pypdfium2, Pillow and tesseract (~/.venvs/lds-transcribe/bin/python).
"""
import argparse, difflib, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import prepare_images as P  # noqa: E402
import pypdfium2 as pdfium  # noqa: E402

PAGES_DIR = ROOT / 'book-of-mormon-1841-pages'
OUT = ROOT / 'work' / 'ocr'
WORDS = None


def words_set():
    global WORDS
    if WORDS is None:
        WORDS = set()
        for f in ('/usr/share/dict/web2', '/usr/share/dict/words'):
            try:
                WORDS |= {l.strip().lower() for l in open(f, errors='ignore')}
            except OSError:
                pass
    return WORDS


def tok(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def page_tokens(n):
    t = (PAGES_DIR / f'page-{n:03d}.md').read_text(encoding='utf-8')
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'\[illegible\]', ' ', t)
    return tok(t.replace('Footer:', ' ').replace('Header:', ' '))


def ocr_page(doc, n, force):
    f = OUT / f'p{n:03d}.txt'
    if f.exists() and not force:
        return f.read_text(encoding='utf-8')
    im = P.page_image(doc[n - 1])
    png = OUT / f'tmp{n}.png'
    im.save(png)
    out = subprocess.run(['tesseract', str(png), 'stdout', '--psm', '6'], capture_output=True, text=True).stdout
    png.unlink()
    out = re.sub(r'-\s*\n\s*', '', out)  # join line-end hyphens
    f.write_text(out, encoding='utf-8')
    return out


def compare(a, b):
    """a, b = token lists. Compared as one string of letters and digits with the spaces removed (the OCR often merges
    or splits words in tight lines). Returns (blocks, bad_chars): blocks are (trans_text, ocr_text) for each run of
    4 or more differing characters; shorter runs are ordinary OCR noise and are ignored."""
    x, y = ''.join(a), ''.join(b)
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    blocks, bad = [], 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal' or max(i2 - i1, j2 - j1) < 4:
            continue
        if op == 'insert':
            # extra OCR characters count only if they look like real words (a dropped word), not bleed-through garbage
            wset = words_set()
            frag = y[j1:j2]
            if not any(frag[k:k + 4] and any(frag[k:k + m] in wset for m in range(4, min(9, len(frag) - k + 1))) for k in range(len(frag))):
                continue
        ctx_x = x[max(0, i1 - 12):i1] + '[' + x[i1:i2] + ']' + x[i2:i2 + 12]
        ctx_y = y[max(0, j1 - 12):j1] + '[' + y[j1:j2] + ']' + y[j2:j2 + 12]
        blocks.append((ctx_x, ctx_y))
        bad += max(i2 - i1, j2 - j1)
    return blocks, bad


def parse_pages(spec):
    out = []
    for part in spec.split(','):
        if '-' in part:
            x, y = part.split('-')
            out.extend(range(int(x), int(y) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pages', default='5-8,9-642,643-649')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()
    (OUT / 'diffs').mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(ROOT / 'Book-of-Mormon-1841.pdf'))
    rows = []
    for n in parse_pages(args.pages):
        a = page_tokens(n)
        if len(a) < 20:
            continue
        b = tok(ocr_page(doc, n, args.force))
        blocks, bad = compare(a, b)
        rate = bad / max(1, sum(len(w) for w in a))
        rows.append((n, len(a), bad, rate))
        with open(OUT / 'diffs' / f'{n:03d}.txt', 'w') as f:
            for cx, cy in blocks:
                f.write(f"transcription {cx} | ocr {cy}\n")
        print(n, len(a), bad, f'{rate:.3f}', flush=True)
    with open(OUT / 'summary.tsv', 'a') as f:
        for r in rows:
            f.write('%d\t%d\t%d\t%.4f\n' % r)


if __name__ == '__main__':
    main()
