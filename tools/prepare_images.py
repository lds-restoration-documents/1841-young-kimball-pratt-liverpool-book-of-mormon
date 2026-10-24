#!/usr/bin/env python3
"""Extract the page images used for transcription from the scan PDF.

The PDF (Book-of-Mormon-1841.pdf) has one embedded single-page JPEG per PDF page (about 1170x2000 px,
already under the 1568 px long edge the image tool would downscale), no text layer. The pages are not
cropped, so the whole leaf (and any running head or signature mark at the edge) stays visible.

For each PDF page N this writes <out>/img/pNNNN.jpg at native resolution.
With --zoom Z (and optionally --box L,T,R,B as fractions of the page, e.g. 0,0.4,1,0.6) the page or box
is upscaled by Z and written as pNNNN_zZ[_box].jpg; upscaling adds no information, it only helps the eye
on a doubtful spot. Delete zooms afterwards with --clean.

Usage:
  python3 tools/prepare_images.py --pages 21-24
  python3 tools/prepare_images.py --pages 21 --zoom 2 --box 0,0.4,1,0.6 --out work/zoom
  python3 tools/prepare_images.py --pages 21-24 --clean
Requires pypdfium2 and Pillow (~/.venvs/lds-transcribe/bin/python).
"""
import argparse
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'Book-of-Mormon-1841.pdf'


def parse_pages(spec, total):
    if not spec:
        return list(range(1, total + 1))
    out = []
    for part in spec.split(','):
        if '-' in part:
            a, b = part.split('-')
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def page_image(page):
    for o in page.get_objects():
        if o.type == 3:
            return o.get_bitmap().to_pil().convert('L')
    raise RuntimeError('no image on page')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pdf', default=str(PDF))
    ap.add_argument('--out', default=str(ROOT / 'work'))
    ap.add_argument('--pages', help='PDF page numbers, e.g. 1-16,302 (default: all)')
    ap.add_argument('--zoom', type=float, default=1)
    ap.add_argument('--box', help='L,T,R,B as fractions of the page (default: whole page)')
    ap.add_argument('--clean', action='store_true', help='delete generated images for --pages and exit')
    args = ap.parse_args()
    out = Path(args.out) / 'img'
    doc = pdfium.PdfDocument(args.pdf)
    pages = parse_pages(args.pages, len(doc))
    if args.clean:
        n = 0
        for p in pages:
            for f in out.glob(f'p{p:04d}*.jpg'):
                f.unlink()
                n += 1
        print(f'removed {n} files from {out}')
        return
    out.mkdir(parents=True, exist_ok=True)
    box = [float(v) for v in args.box.split(',')] if args.box else None
    suffix = ''
    if args.zoom != 1 or box:
        suffix = f'_z{args.zoom:g}' + ('_box' + args.box.replace(',', '-') if box else '')
    for n in pages:
        im = page_image(doc[n - 1])
        if box:
            w, h = im.size
            im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
        if args.zoom != 1:
            im = im.resize((int(im.width * args.zoom), int(im.height * args.zoom)), Image.LANCZOS)
        im.save(out / f'p{n:04d}{suffix}.jpg', quality=88)
        print(n, im.size)


if __name__ == '__main__':
    main()
