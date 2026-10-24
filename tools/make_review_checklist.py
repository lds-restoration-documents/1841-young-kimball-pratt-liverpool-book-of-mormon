#!/usr/bin/env python3
"""Build a self-contained HTML checklist (work/review/checklist.html) for the owner's decisions: the
disagreements in proofread-disagreements.md and every `uncertain` comment in the page files, each with an
image crop at the spot. Needs pypdfium2 and Pillow (~/.venvs/lds-transcribe/bin/python) and the scan PDF.
The page stores decisions in the browser (localStorage) and can export them as text.

Each crop is located by an estimate (where the quoted text falls in the page's text, taken as a share of the
page's height), so the mark can be a few lines above or below the middle of the crop: use the whole-page
link (a PDF page at 1x, written beside the checklist) when in doubt. No images go in tracked files; the
output is under work/ (gitignored).

Usage:  ~/.venvs/lds-transcribe/bin/python tools/make_review_checklist.py [--pdf FILE] [--half 300]
"""
import argparse
import base64
import html
import io
import json
import re
import sys
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_images import PDF, page_image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / 'book-of-mormon-1841-pages'
OUT = ROOT / 'work' / 'review'


def body_text(p):
    """Page text as one string, without comments, header/footer lines or markdown marks."""
    t = (PAGES / f'page-{p:03d}.md').read_text(encoding='utf-8')
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'\n---\n.*', '', t, flags=re.S)
    lines = [l for l in t.split('\n') if l.strip() and not l.startswith(('**Header', 'Footer'))]
    return re.sub(r'\s+', ' ', ' '.join(lines)).replace('*', '').replace('#', '').strip()


def disagreements():
    items = []
    for line in (ROOT / 'proofread-disagreements.md').read_text(encoding='utf-8').split('## Disagreements', 1)[-1].split('\n'):
        m = re.match(r'- \*\*(\d+)\*\*: (.*)', line)
        if not m:
            continue
        p, text = int(m.group(1)), m.group(2)
        quoted = re.findall(r'"([^"]+)"', text)
        needle = '' if re.search(r'\bheader\b|first (word|line)', text.split(':')[0], re.I) else next(
            (q.strip(' .,;:!?-') for q in quoted if len(q.strip(' .,;:!?-')) > 2), '')
        items.append({'kind': 'disagreement', 'p': p, 'q': text, 'n': needle})
    return items


def uncertain():
    items = []
    for f in sorted(PAGES.glob('page-*.md')):
        p = int(f.stem[-3:])
        t = f.read_text(encoding='utf-8')
        for m in re.finditer(r'<!--\s*(uncertain.*?)\s*-->', t, flags=re.S):
            before = re.sub(r'<!--.*?-->', '', t[:m.start()], flags=re.S)
            before = re.sub(r'\s+', ' ', before).replace('*', '').strip()
            items.append({'kind': 'uncertain', 'p': p, 'q': re.sub(r'\s+', ' ', m.group(1)), 'n': before[-40:]})
    return items


def locate(p, needle):
    """Share (0-1) of the page text at which needle ends, and the file's text around it."""
    body = body_text(p)
    key = re.sub(r'\s+', ' ', needle)
    i = body.find(key) if key else -1
    if i < 0:
        return (0.0 if not key else 0.5), '', bool(key) is False
    frac = (i + len(key)) / max(1, len(body)) if len(key) > 30 else (i + len(key) / 2) / max(1, len(body))
    return frac, body[max(0, i - 50): i + len(key) + 50], True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pdf', default=str(PDF))
    ap.add_argument('--half', type=int, default=300, help='half-height of each crop in px (default 300)')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    items = disagreements() + uncertain()
    doc = pdfium.PdfDocument(args.pdf)
    cache = {}
    rows = []
    for k, it in enumerate(items):
        p = it['p']
        if p not in cache:
            cache.clear()
            im = page_image(doc[p - 1])
            cache[p] = im
            whole = OUT / f'p{p:03d}.jpg'
            cache[p].save(whole, quality=80)
        pg = cache[p]
        frac, ctx, found = locate(p, it['n'])
        cy = int(pg.height * (0.02 + 0.96 * frac)) if it['n'] else args.half
        top = max(0, min(pg.height - 2 * args.half, cy - args.half))
        c = pg.crop((0, top, pg.width, min(pg.height, top + 2 * args.half)))
        if c.width > 1300:
            c = c.resize((1300, int(c.height * 1300 / c.width)), Image.LANCZOS)
        buf = io.BytesIO()
        c.save(buf, 'JPEG', quality=75)
        data = base64.b64encode(buf.getvalue()).decode()
        ctx_html = (f'<p class="ctx">file reads: <code>&hellip;{html.escape(ctx)}&hellip;</code></p>' if ctx else
                    ('<p class="ctx">(quoted text not found in page file; crop is a guess)</p>' if it['n'] else ''))
        rows.append(f'''<section class="item" id="i{k}" data-k="{k}" data-kind="{it['kind']}">
<h2>#{k+1} &middot; PDF page {p} (printed {p-8}) <a href="p{p:03d}.jpg" target="_blank">whole page</a></h2>
<p class="q">{html.escape(it['q'])}</p>{ctx_html}
<img src="data:image/jpeg;base64,{data}" alt="crop of PDF page {p}">
<p class="btn"><label><input type="radio" name="d{k}" value="keep"> keep the file</label>
<label><input type="radio" name="d{k}" value="change"> change</label>
<label><input type="radio" name="d{k}" value="unsure"> can't tell</label>
<input type="text" name="n{k}" placeholder="what it should read / note" size="40"></p></section>''')
        print(f'{k+1}/{len(items)} page {p} {it["kind"]}', file=sys.stderr)

    nd = sum(1 for i in items if i['kind'] == 'disagreement')
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review checklist</title><style>
:root{--bg:#fff;--fg:#1c1c1c;--mu:#666;--bd:#ccc;--ac:#0b57d0}
@media (prefers-color-scheme: dark){:root{--bg:#161616;--fg:#e8e8e8;--mu:#999;--bd:#444;--ac:#8ab4f8}}
body{background:var(--bg);color:var(--fg);font:16px/1.45 system-ui,sans-serif;max-width:1100px;margin:0 auto;padding:0 16px 80px}
.item{border-top:1px solid var(--bd);padding:12px 0}img{max-width:100%;height:auto;border:1px solid var(--bd);background:#fff}
.q{font-weight:600;margin:.2em 0}.ctx{color:var(--mu);margin:.2em 0}code{background:rgba(127,127,127,.15);padding:0 3px}
label{margin-right:16px}a{color:var(--ac)}.top{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--bd)}
button{font:inherit;padding:4px 12px}textarea{width:100%;height:160px;margin-top:8px}
</style></head><body>
<div class="top"><b>Review checklist</b> &mdash; <span id="cnt"></span> decided
<button onclick="exp()">Export decisions</button></div>
<p>''' + f'{nd} proofreader disagreements, then {len(items) - nd} uncertain marks from the page files. ' + '''Pick what the original shows. The crop is centred on an <i>estimate</i> of where the mark is, a few lines either way; open the whole page if you do not see it. &ldquo;Keep&rdquo; leaves the page file as it is.</p>
<textarea id="out" placeholder="exported decisions appear here (copy them back into the chat)"></textarea>
''' + '\n'.join(rows) + '''
<script>
const items=''' + json.dumps([{'p': i['p'], 'n': i['n'], 'kind': i['kind'], 'q': i['q']} for i in items]) + ''';
const KEY="review-checklist-1841";let s={};try{s=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(s))}catch(e){}cnt()}
function cnt(){document.getElementById("cnt").textContent=Object.keys(s).filter(k=>s[k].d).length+" of "+items.length}
document.querySelectorAll(".item").forEach(sec=>{const k=sec.dataset.k;s[k]=s[k]||{};
 sec.querySelectorAll("input[type=radio]").forEach(r=>{if(s[k].d===r.value)r.checked=true;r.onchange=()=>{s[k].d=r.value;save()}});
 const t=sec.querySelector("input[type=text]");t.value=s[k].n||"";t.oninput=()=>{s[k].n=t.value;save()}});
cnt();
function exp(){const L=[];items.forEach((it,k)=>{const d=(s[k]||{}).d||"undecided";L.push("#"+(k+1)+" ("+it.kind+") PDF page "+it.p+" \\""+it.n+"\\": "+(d==="change"?"CHANGE":d==="keep"?"keep":d)+((s[k]||{}).n?" ["+s[k].n+"]":""))});
 document.getElementById("out").value=L.join("\\n")}
</script></body></html>'''
    dest = OUT / 'checklist.html'
    dest.write_text(page, encoding='utf-8')
    print(f'{nd} disagreements + {len(items) - nd} uncertain -> {dest}  ({dest.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
