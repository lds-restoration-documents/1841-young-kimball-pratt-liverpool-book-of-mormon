#!/usr/bin/env python3
"""Build printer-typos.md: a catalog of the likely printer's typos and misspellings in the 1841 text.

The list of forms is curated below (triaged from a dictionary scan of the compiled text plus the audit notes); this script
finds every occurrence of each form in book-of-mormon-1841.md, with its image and a snippet of context, so the page
numbers and contexts always come from the current text. Spellings that were normal or intentional for the period or the edition
(shew, sayeth, marvellous, ...) are deliberately NOT cataloged; see the NOT_INCLUDED notes at the end of the output.

Usage:  python3 tools/make_typo_catalog.py [--md FILE] [--out FILE]
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (printed, should be, note). `printed` is matched as a whole word, case-sensitive; a tuple (regex, label) matches a pattern.
# Curated from a dictionary scan of the compiled text (words not in /usr/share/dict, then checked by eye) plus a scan for
# doubled words and the "came pass" slip; forms that do not occur in the text simply produce no rows.
SECTIONS = [
    ('Letters dropped, added or wrong (single-word slips)', [
        (w, sh, n) for w, sh, n in [
            ('abont', 'about', 'worn u'), ('abou', 'about', 'with `tthe` after it'), ('accouut', 'account', 'worn n'),
            ('acording', 'according', ''), ('af', 'of', ''), ('afflctions', 'afflictions', ''), ('afier', 'after', ''),
            ('allgathereing', 'all gathering', 'run together, extra e'), ('amoug', 'among', 'worn n'), ('atonemeut', 'atonement', 'worn n'),
            ('attribnted', 'attributed', 'worn u'), ('auointed', 'anointed', 'worn n'), ('aud', 'and', 'the d for n slip; also worn type'),
            ('babtise', 'baptise', ''), ('bablings', 'babblings', ''), ('baptsim', 'baptism', ''), ('becouse', 'because', ''),
            ('beeame', 'became', 'worn c'), ('begau', 'began', 'worn n'), ('boudage', 'bondage', 'worn n'), ('bro\'t', 'brought', 'printed contraction'),
            ('brotber', 'brother', 'worn h'), ('brethen', 'brethren', ''), ('brethern', 'brethren', ''), ('camc', 'came', 'worn e'),
            ('cau', 'can', 'worn n'), ('chatisement', 'chastisement', ''), ('coecerning', 'concerning', ''), ('commadments', 'commandments', ''),
            ('comsuming', 'consuming', ''), ('contemtions', 'contentions', ''), ('contentron', 'contention', ''), ('coucerning', 'concerning', 'worn n'),
            ('deciple', 'disciple', ''), ('diciples', 'disciples', ''), ('dilligence', 'diligence', ''), ('dispise', 'despise', ''),
            ('divorsed', 'divorced', ''), ('ef', 'of', ''), ('espedially', 'especially', ''), ('exhor', 'exhort', 'no hyphen printed at the line end'),
            ('fonght', 'fought', 'worn u'), ('forgotton', 'forgotten', ''), ('gocd', 'good', 'worn o'), ('goverment', 'government', ''),
            ('govenor', 'governor', ''), ('grcat', 'great', 'worn e'), ('grevious', 'grievous', ''), ('harrass', 'harass', ''),
            ('haviug', 'having', 'worn n'), ('heaveu', 'heaven', 'worn n'), ('heen', 'been', 'worn b'),
            ('heheld', 'beheld', 'worn b'), ('hehold', 'behold', 'worn b'), ('heigth', 'height', ''), ('hemselves', 'themselves', ''),
            ('himse\'f', 'himself', 'worn l'), ('humbte', 'humble', 'worn l'), ('inasmnch', 'inasmuch', 'worn u'), ('iu', 'in', 'worn n'),
            ('kingnom', 'kingdom', ''), ('lamantation', 'lamentation', ''), ('magies', 'magics', ''), ('mainatin', 'maintain', ''),
            ('malace', 'malice', ''), ('manfest', 'manifest', ''), ('manifesed', 'manifested', ''), ('maniifestations', 'manifestations', ''),
            ('mauy', 'many', 'worn n'), ('mercifnl', 'merciful', 'worn u'), ('mimself', 'himself', 'worn h'), ('mnch', 'much', 'worn u'),
            ('mnltitude', 'multitude', 'worn u'), ('monntains', 'mountains', 'worn u'), ('murmer', 'murmur', ''), ('natious', 'nations', 'worn n'),
            ('neigbour', 'neighbour', ''), ('nimself', 'himself', 'worn h'), ('nnmber', 'number', 'worn u'), ('nnto', 'unto', 'worn u'),
            ('nro', 'nor', ''), ('ohtained', 'obtained', 'worn b'), ('omong', 'among', ''), ('oried', 'cried', 'worn c'), ('ot', 'of', ''),
            ('otherway', 'other way', 'run together'), ('peeple', 'people', ''), ('pertake', 'partake', ''), ('pevail', 'prevail', ''),
            ('posible', 'possible', ''), ('praparations', 'preparations', ''), ('prepations', 'preparations', ''), ('proffiteth', 'profiteth', ''),
            ('prolamation', 'proclamation', ''), ('reqentance', 'repentance', ''), ('resurrectien', 'resurrection', 'worn c'), ('seeret', 'secret', 'worn c'),
            ('snch', 'such', 'worn u'), ('snd', 'and', 'worn a'), ('sholl', 'shall', ''), ('shonld', 'should', 'worn u'), ('speakiug', 'speaking', 'worn n'),
            ('statagem', 'stratagem', ''), ('strenghen', 'strengthen', ''), ('struek', 'struck', 'worn c'), ('swollowed', 'swallowed', ''),
            ('tbe', 'the', 'worn h'), ('thall', 'shall', ''), ('therfore', 'therefore', ''), ('therof', 'thereof', ''), ('thot', 'that', ''),
            ('tnat', 'that', ''), ('tny', 'any', ''), ('trampeleth', 'trampleth', ''), ('tthe', 'the', 'doubled t'), ('unchangeble', 'unchangeable', ''),
            ('unpardonoble', 'unpardonable', ''), ('unpn', 'upon', ''), ('uot', 'not', 'worn n'), ('upan', 'upon', ''), ('upou', 'upon', 'worn n'),
            ('uow', 'now', 'worn n'), ('uuto', 'unto', 'worn n'), ('valey', 'valley', ''), ('whieh', 'which', 'worn c'), ('wickednsss', 'wickedness', ''),
            ('wildernes', 'wilderness', ''), ('wirlwind', 'whirlwind', ''), ('witb', 'with', 'worn h'), ('witbout', 'without', 'worn h'),
            ('wonld', 'would', 'worn u'), ('writen', 'written', ''), ('whrefore', 'wherefore', ''), ('yepent', 'repent', ''),
        ]]),
    ('Words run together or split', [
        ('areevil', 'are evil', 'no space printed'), ('cameto', 'came to', 'no space printed'), ('dwellin', 'dwell in', 'no space printed'),
        ('mustrepen', 'must repent', 'no space printed'), ('strengthof', 'strength of', 'no space printed'), ('theflesh', 'the flesh', 'no space printed'),
        ('therewere', 'there were', 'no space printed'), ('untohim', 'unto him', 'no space printed'),
        (('Poisonousserpentsdestroyed', 'Poisonousserpentsdestroyed'), 'Poisonous serpents destroyed', 'index entry, no spaces printed'),
    ]),
    ('Wrong, missing or doubled words (grammar slips kept as printed)', [
        (('came pass', 'came pass'), 'came to pass', 'the to dropped'),
        (('the the', 'the the'), 'the', 'doubled word'),
        (('have have', 'have have'), 'have', 'doubled word'),
        (('and and', 'and and'), 'and', 'doubled word'),
        (('a a', 'a a'), 'a', 'doubled word'),
        (('ye ye', 'ye ye'), 'ye', 'doubled word'),
        (('not not', 'not not'), 'not', 'doubled word'),
        (('may may', 'may may'), 'may', 'doubled word'),
        (('had began', 'had began'), 'had begun', 'wrong participle'),
        (('had came', 'had came'), 'had come', 'wrong participle'),
        (('has fell', 'has fell'), 'has fallen', 'wrong participle'),
        (('have went', 'have went'), 'have gone', 'wrong participle'),
        (('there was but few', 'there was but few'), 'there were but few', ''),
        (('should he', 'should he'), 'should be', 'worn b (or a real "he")'),
    ]),
    ('Variant spellings of names (next to a much more frequent spelling)', [
        (w, sh, n) for w, sh, n in [
            ('Nepbi', 'Nephi', 'worn h'), ('Spjrit', 'Spirit', ''), ('Jurusalem', 'Jerusalem', ''), ('Jesusalem', 'Jerusalem', ''),
            ('Jeruselem', 'Jerusalem', ''), ('Jerusalen', 'Jerusalem', 'worn m'), ('Isreal', 'Israel', ''), ('Zarahelmla', 'Zarahemla', ''),
            ('Zerahemla', 'Zarahemla', ''), ('Zarahemnah', 'Zerahemnah', 'the Lamanite leader; Zerahemnah is far commoner'),
            ('Zoiamites', 'Zoramites', ''), ('Lamanttes', 'Lamanites', ''), ('Laminites', 'Lamanites', ''), ('Teacum', 'Teancum', ''),
            ('Cortantumr', 'Coriantumr', ''), ('Coiiantumr', 'Coriantumr', 'worn r'), ('Amalcikiah', 'Amalickiah', ''), ('Amelekites', 'Amalekites', ''),
            ('Limher', 'Limhi', ''), ('Limhah', 'Limhi', ''), ('Pahorau', 'Pahoran', 'worn n'), ('Pahoron', 'Pahoran', ''), ('Amoron', 'Ammoron', ''),
            ('Morini', 'Moroni', ''), ('Maroni', 'Moroni', ''), ('Unqarponable', 'Unpardonable', 'index entry'),
        ]]),
]

# Misspellings that recur (the same slip printed several times): listed in their own section, with all pages.
RECURRING = [
    ('aud', ['aud'], 'and', 'worn d/n slip'),
    ('brethern/brethen', ['brethern', 'brethen'], 'brethren', 'wrong letter before the end'),
    ('harrass', ['harrass'], 'harass', 'single r/ss'),
    ('tbe', ['tbe'], 'the', 'worn h'),
    ('uuto', ['uuto'], 'unto', 'worn n'),
    ('the the', [('the the', 'the the')], 'the', 'doubled word'),
    ('had began', [('had began', 'had began')], 'had begun', 'wrong participle'),
    ('had came', [('had came', 'had came')], 'had come', 'wrong participle'),
]

NOT_INCLUDED = """## Not included: spellings that were normal or intentional

Spellings that were normal or intentional for the period or the edition are not printer's slips and are left out: `shew`/`shewed`/`shewn`/`sheweth`/`shewing`, `annointed`, `burthen(s)`/`burthensome`, `centre`, `sepulchre`, `vapour`, `armour`, `lustre`, `mouldering`, `moulten`, `favour`, `offence`, `skilful`, `wilfully`/`wilfulness`, `marvellous`, `quarrellings`, `counsellor(s)`, `cimeter(s)`/`cymeter`, `carcases`, `phrensied`, `wrapt`, `threatnings`, `dissentions`, `dependant`, `changable`, `fulfil`, `spake`, `whoso`, `stiffneckedness`, `abridgement`, `ancles`, and the archaic verb endings (`-eth`, `-est`). Roman-numeral chapter numbers (`ii`, `xix`) and place and personal names are also left out unless a variant sits next to a much more frequent spelling of the same name (see the names section).
"""


def load(md):
    raw = md.read_text(encoding='utf-8')
    parts = re.split(r'<!-- page (\d+) -->', raw)
    segs, cur = [], 0
    for i, t in enumerate(parts):
        if i % 2 == 1:
            cur = int(t)
            continue
        t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
        segs.append((cur, re.sub(r'\s+', ' ', t)))
    return segs


def find(segs, spec):
    """Yield (page, snippet) for each occurrence."""
    if isinstance(spec, tuple):
        pat, hit = spec
        rx = re.compile(r'(?<![A-Za-z])' + re.escape(pat) + r'(?![A-Za-z])')
        hl = hit
    else:
        rx = re.compile(r'(?<![A-Za-z])' + re.escape(spec) + r'(?![A-Za-z])')
        hl = spec
    for pg, t in segs:
        if pg < 5 or pg > 649:
            continue
        for m in rx.finditer(t):
            a = max(0, m.start() - 38)
            b = min(len(t), m.end() + 30)
            s = t[a:b]
            i = s.find(hl) if hl in s else 0
            s = s[:i] + '**' + s[i:i + len(hl)] + '**' + s[i + len(hl):]
            yield pg, ('…' if a else '') + s.strip() + ('…' if b < len(t) else '')


def printed(pg):
    return str(pg - 8) if 10 <= pg <= 642 else '—'  # printed folio = PDF page - 8 (page 10 is p. 2)


def row(spec, should, note, segs):
    out = []
    for pg, snip in find(segs, spec):
        label = spec[1] if isinstance(spec, tuple) else spec
        out.append((pg, '| `%s` | %s | %d | %s | %s%s |' % (label, should, pg, printed(pg), snip.replace('|', '\\|'),
                                                           (' (' + note + ')') if note else '')))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--md', default=str(ROOT / 'book-of-mormon-1841.md'))
    ap.add_argument('--out', default=str(ROOT / 'printer-typos.md'))
    args = ap.parse_args()
    segs = load(Path(args.md))
    out, total, missing = [], 0, []
    header = '| Printed | Should be | Image | Printed p. | In context |\n|---|---|---|---|---|'
    body = []
    for title, items in SECTIONS:
        rows = []
        for spec, should, note in items:
            r = row(spec, should, note, segs)
            if not r:
                missing.append(spec)
            rows += r
        rows.sort(key=lambda x: x[0])
        total += len(rows)
        body.append('\n## %s (%d)\n\n%s\n%s' % (title, len(rows), header, '\n'.join(r for _, r in rows)))
    rec = []
    for label, forms, should, why in RECURRING:
        hits = [h for f in forms for h in find(segs, f)]
        hits.sort()
        total += len(hits)
        pages = ', '.join(str(p) for p, _ in hits)
        rec.append('| `%s` | %s | %d | %s | %s |' % (label, should, len(hits), why, pages))
    intro = f"""# Printer's typos and misspellings in the 1841 Book of Mormon

A catalog of the places where the 1841 print itself has a slip of the type, a misspelling, or a doubled word, as the transcription records
it. {total} occurrences, grouped by the kind of slip, each with its image, printed page (PDF page - 8 in the text) and context.

**What is and is not here.** The transcription keeps every printed error exactly as printed (nothing was corrected from later editions), so
all of these are in the page files as printed. This list leaves out spellings that were normal or intentional for the period or the edition
(`shew`, `sayeth`, `marvellous`, `wilfully` and the like; see the end of the file). It was built from a dictionary scan of the whole text,
triaged by eye from the list of words not in a dictionary (individual rows were not all re-checked against the scan), so it is **likely, not exhaustive**: a slip that happens to produce another real word (`he` for `be`) is only caught where it was noticed, and a few
entries are judgment calls (marked in the notes). Some rows are worn-type readings (`whieh`, `tbe`): the scan shows a letter that looks like the printed one, which the
transcription kept as printed. Names are listed only where a variant sits next to a much more frequent spelling of the same name; whether such a variant is a typo or a deliberate spelling is not always certain.

**Where to see the original.** Numbers are PDF page numbers of the scan Book-of-Mormon-1841.pdf (656 pages, numbered 001-656 in order; printed page = PDF page - 8 in the main text, the index is - 6). No images are included in this repository.

Generated by `tools/make_typo_catalog.py` from the live text, so page numbers and contexts stay current if the pages are edited.
"""
    recsec = '\n## Misspellings that recur\n\nThe same slip printed more than once (compositor habits rather than one-off slips).\n\n| Printed | Should be | Times | Slip | images |\n|---|---|---|---|---|\n' + '\n'.join(rec)
    Path(args.out).write_text(intro + '\n'.join(body) + '\n' + recsec + '\n\n' + NOT_INCLUDED, encoding='utf-8')
    print(f'{total} occurrences -> {args.out}')
    if missing:
        print('NOT FOUND in the text:', missing)


if __name__ == '__main__':
    main()
