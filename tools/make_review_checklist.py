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
import subprocess
import sys
import difflib
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw

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
        quoted = [q.strip(' .,;:!?-') for q in re.findall(r'"([^"]+)"', text)]
        header_item = re.search(r'\bheader\b|first (word|line)', text.split(':')[0], re.I)
        items.append({'kind': 'disagreement', 'p': p, 'q': text, 'n': '', 'cands': [] if header_item else [q for q in quoted if len(q) >= 2]})
    return items


def raw(p):
    return (PAGES / f'page-{p:03d}.md').read_text(encoding='utf-8')


def words_before(text, pos, n=4):
    """The last n words of the page text before pos (comments and markdown marks removed)."""
    t = re.sub(r'<!--.*?-->', ' ', text[:pos], flags=re.S).replace('*', ' ').replace('#', ' ')
    return re.sub(r'\s+', ' ', t).strip().split(' ')[-n:]


def uncertain():
    items = []
    for f in sorted(PAGES.glob('page-*.md')):
        p = int(f.stem[-3:])
        t = f.read_text(encoding='utf-8')
        for m in re.finditer(r'<!--\s*(uncertain.*?)\s*-->', t, flags=re.S):
            items.append({'kind': 'uncertain', 'p': p, 'q': re.sub(r'\s+', ' ', m.group(1)),
                          'span': (m.start(), m.end()), 'key': words_before(t, m.start(), 4), 'tail': 2})
    return items


STOP = {'mark', 'after', 'before', 'dot', 'speck', 'line', 'end', 'last', 'first', 'para', 'of', 'the', 'between', '2nd',
        '1st', 'comma', 'period', 'at', 'in', 'a'}


def flex(phrase):
    """Regex for a phrase as it may appear in the raw page file: any whitespace, comments or italics marks between words."""
    toks = phrase.split()
    return r'(?<!\w)' + r'(?:\s|<!--.*?-->|\*)+'.join(re.escape(t) for t in toks) + r'(?!\w)'


def resolve(it):
    """For a disagreement: find, in the RAW page file, the longest quoted string that occurs (whole words),
    and record its span and the words to look for in the scan. Nothing is taken from anywhere but the file."""
    t = raw(it['p'])
    cands = list(it.get('cands', []))
    m = re.search(r'to "([^"]+)" \(was "([^"]+)"\)', it['q'])
    if m:
        new, old = m.group(1), m.group(2)
        cands += [c.replace(old, new) for c in cands if re.search(r'(?<!\w)' + re.escape(old) + r'(?!\w)', c)]
    cleaned = []
    for c in cands:
        ws = [w for w in c.split() if re.sub(r'\W', '', w).lower() not in STOP]
        if ws and ' '.join(ws) != c:
            cleaned.append(' '.join(ws))
    hit = None
    for cand in sorted(cands, key=len, reverse=True) + sorted(cleaned, key=len, reverse=True):
        if len(cand) < 4 and cand not in cands:
            continue
        mm = re.search(flex(cand), t, re.I | re.S)
        if mm:
            hit = mm
            break
    if hit is None and re.search(r'end of (the )?(last line|page)', it['q']):
        body = re.sub(r'\n---\n.*', '', re.sub(r'<!--.*?-->', '', t, flags=re.S), flags=re.S).split()
        hit = list(re.finditer(flex(' '.join(body[-4:])), t, re.S))[-1:] or [None]
        hit = hit[0]
    if hit:
        it['span'] = hit.span()
        it['key'] = words_before(t, hit.end(), 4)
        it['tail'] = min(4, max(1, len(hit.group(0).split())))
    else:
        it['span'] = None
        lines = t.split('\n')
        if re.search(r'header|folio|running head', it['q'], re.I):
            it['line'] = next((l for l in lines if l.startswith('**Header')), None)
        elif re.search(r'footer|signature', it['q'], re.I):
            it['line'] = next((l for l in lines if l.startswith('Footer')), None)


def excerpt_html(it):
    """The literal file text around the item, verbatim, with the item marked."""
    t = raw(it['p'])
    if it.get('span'):
        a, b = it['span']
        s0, e0 = max(0, a - 140), min(len(t), b + 140)
        while s0 > 0 and not t[s0].isspace():
            s0 -= 1
        while e0 < len(t) and not t[e0 - 1].isspace():
            e0 += 1
        pre, hit, post = t[s0:a], t[a:b], t[b:e0]
        kind = 'the doubtful comment' if it['kind'] == 'uncertain' else 'the text this item is about'
        return (f'<p class="cap">Exact text from <code>page-{it["p"]:03d}.md</code> ({kind} highlighted):</p>'
                f'<pre class="file">{"&hellip;" if s0 else ""}{html.escape(pre)}<mark>{html.escape(hit)}</mark>{html.escape(post)}{"&hellip;" if e0 < len(t) else ""}</pre>')
    if it.get('line'):
        return (f'<p class="cap">Exact line from <code>page-{it["p"]:03d}.md</code>:</p>'
                f'<pre class="file"><mark>{html.escape(it["line"])}</mark></pre>')
    return '<p class="cap">The quoted text was not found in the page file; see the whole page.</p>'


def ocr_words(img, tmp):
    """Word boxes from a local tesseract pass: [(norm_text, left, top, width, height)] in reading order."""
    img.save(tmp)
    out = subprocess.run(['tesseract', str(tmp), 'stdout', '--psm', '6', 'tsv'], capture_output=True, text=True).stdout
    words = []
    for line in out.split('\n')[1:]:
        c = line.split('\t')
        if len(c) < 12 or not c[11].strip():
            continue
        w = re.sub(r'[^a-z0-9]', '', c[11].lower())
        if w:
            words.append((w, int(c[6]), int(c[7]), int(c[8]), int(c[9])))
    return words


def find_box(words, key, tail):
    """Locate the file words `key` (the last up to 4 words before the spot) in the OCR words. Returns
    (box of the last `tail` words, the OCR text of the whole match) only when every check passes:
    each word reads (almost) the same, and the match is clearly better than any other place on the page.
    Otherwise None, so nothing is highlighted rather than something wrong."""
    nw = [re.sub(r'[^a-z0-9]', '', w.lower()) for w in key]
    nw = [w for w in nw if w]
    if len(nw) < 2 or not words:
        return None
    n = len(nw)
    scores = []
    for i in range(len(words) - n + 1):
        per = [difflib.SequenceMatcher(None, nw[j], words[i + j][0]).ratio() for j in range(n)]
        scores.append((sum(per) / n, min(per), i))
    if not scores:
        return None
    scores.sort(reverse=True)
    best, worst, bi = scores[0]
    second = scores[1][0] if len(scores) > 1 else 0.0
    # words of the same match overlapping the best one do not count as a competing place
    rivals = [sc for sc, _, i in scores[1:] if abs(i - bi) >= n]
    second = rivals[0] if rivals else 0.0
    if best < 0.85 or worst < 0.6 or best - second < 0.1:
        return None
    ws = words[bi:bi + n]
    sel = ws[-tail:]
    box = (min(w[1] for w in sel), min(w[2] for w in sel), max(w[1] + w[3] for w in sel), max(w[2] + w[4] for w in sel))
    return box, ' '.join(w[0] for w in ws)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pdf', default=str(PDF))
    ap.add_argument('--half', type=int, default=300, help='half-height of each crop in px (default 300)')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    items = disagreements() + uncertain()
    doc = pdfium.PdfDocument(args.pdf)
    cache = {}
    ocr = {}
    rows = []
    for k, it in enumerate(items):
        p = it['p']
        if it['kind'] == 'disagreement':
            resolve(it)
        if p not in cache:
            cache.clear()
            im = page_image(doc[p - 1])
            cache[p] = im
            whole = OUT / f'p{p:03d}.jpg'
            cache[p].save(whole, quality=80)
        pg = cache[p]
        if p not in ocr:
            ocr.clear()
            ocr[p] = ocr_words(pg, OUT / 'tmp-ocr.png')
        found = find_box(ocr[p], it.get('key', []), it.get('tail', 2)) if it.get('span') else None
        if found:
            (l, t, r, b), ocr_text = found
            lh = max(20, b - t)
            top = int(max(0, min(pg.height - 7 * lh, t - 2.5 * lh)))
            c = pg.crop((0, top, pg.width, int(min(pg.height, top + 7 * lh)))).convert('RGB')
            ImageDraw.Draw(c).rectangle((l - 6, t - top - 6, r + 6, b - top + 6), outline=(220, 0, 0), width=3)
            c = c.resize((int(c.width * 1.5), int(c.height * 1.5)), Image.LANCZOS)
            z = pg.crop((max(0, l - 60), max(0, t - 30), min(pg.width, r + 90), min(pg.height, b + 30))).convert('RGB')
            z = z.resize((z.width * 3, z.height * 3), Image.LANCZOS)
            bz = io.BytesIO(); z.save(bz, 'JPEG', quality=85)
            zdata = base64.b64encode(bz.getvalue()).decode()
            imgs = (f'<p class="cap">Image: the red box is placed by matching the file words <code>{html.escape(" ".join(it["key"]))}</code> '
                    f'to the scan (OCR read them as <code>{html.escape(ocr_text)}</code>); the item is at or just after the box. Enlarged:</p>'
                    f'<img class="zoom" src="data:image/jpeg;base64,{zdata}" alt="enlarged spot"><p class="cap">The line and its neighbours:</p>')
        else:
            c = pg.convert('RGB')
            imgs = ('<p class="cap">Image: the spot could not be located reliably, so nothing is outlined. '
                    'This is the whole page; find the words quoted above.</p>')
        if c.width > 1500:
            c = c.resize((1500, int(c.height * 1500 / c.width)), Image.LANCZOS)
        buf = io.BytesIO()
        c.save(buf, 'JPEG', quality=78)
        data = base64.b64encode(buf.getvalue()).decode()
        imgs += f'<img src="data:image/jpeg;base64,{data}" alt="PDF page {p}">'
        ctx_html = excerpt_html(it)
        rows.append(f'''<section class="item" id="i{k}" data-k="{k}" data-kind="{it['kind']}">
<h2>#{k+1} &middot; PDF page {p} (printed {p-8}) <a href="p{p:03d}.jpg" target="_blank">whole page</a></h2>
<p class="q">{html.escape(it['q'])}</p>{ctx_html}
{imgs}
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
button{font:inherit;padding:4px 12px}.cap{color:var(--mu);margin:.4em 0 .2em;font-size:14px}mark{background:#ffe08a;color:#000;padding:0 3px}img.zoom{border:2px solid #d00}pre.file{white-space:pre-wrap;word-break:break-word;background:rgba(127,127,127,.12);padding:8px;margin:.2em 0;font:14px/1.4 ui-monospace,monospace}textarea{width:100%;height:160px;margin-top:8px}
</style></head><body>
<div class="top"><b>Review checklist</b> &mdash; <span id="cnt"></span> decided
<button onclick="exp()">Export decisions</button></div>
<p>''' + f'{nd} proofreader disagreements, then {len(items) - nd} uncertain marks from the page files. ' + '''Pick what the original shows. The text above each image is quoted verbatim from the page file. A red box is drawn on the scan only when the file's words were found there reliably; otherwise the whole page is shown with nothing outlined. &ldquo;Keep&rdquo; leaves the page file as it is.</p>
<textarea id="out" placeholder="exported decisions appear here (copy them back into the chat)"></textarea>
''' + '\n'.join(rows) + '''
<script>
const items=''' + json.dumps([{'p': i['p'], 'n': ' '.join(i.get('key', [])), 'kind': i['kind'], 'q': i['q']} for i in items]) + ''';
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
