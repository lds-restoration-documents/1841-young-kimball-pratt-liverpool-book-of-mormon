# tools

The scripts and instructions used to produce the files in this repository. The page files in
`../book-of-mormon-1841-pages/` are the source of truth; the combined text files are generated from them.
(Adapted from the sibling `1840-robinson-smith-nauvoo-book-of-mormon`, `1837-pratt-goodson-kirtland-book-of-mormon` and `1830-grandin-palmyra-book-of-mormon` tooling.)

## Pipeline

1. **Prepare the images** (the scan is `../Book-of-Mormon-1841.pdf`, not in git; needs pypdfium2 and Pillow, e.g. `~/.venvs/lds-transcribe/bin/python`):
   `python3 tools/prepare_images.py --pages 12-15 [--zoom 2 --box L,T,R,B] [--out work]`
   extracts each page's embedded image (whole page, native resolution, uncropped) to `work/img/pNNNN.jpg`. `--zoom`/`--box` upscale a region for a doubtful spot. Delete a batch's images afterwards with `--clean`. The PDF has no text layer or OCR.
2. **Transcribe**: AI agents (Claude) view the page image and write one `page-NNN.md` per PDF page following
   [transcription-spec.md](transcription-spec.md), four pages per agent. Blind proofreading follows [proofread-spec.md](proofread-spec.md)
   (adapted from 1840, not yet run). This step is done by agents, not by a script.
3. **Check**: `python3 tools/check_structure.py [--allow-gaps]` (page comment, `cont` markers, spacing before `; : ? !`, italics, chapter sequence per book, printed folio = PDF page − 8; INDEX pages 643–649 − 6).
4. **Rebuild the combined files** (standard library only; run in this order; each writes to the repo root, `--out` redirects):
   ```
   python3 tools/compile_markdown.py     # -> book-of-mormon-1841.md
   python3 tools/make_plaintext.py       # -> book-of-mormon-1841.txt
   python3 tools/make_sparse.py          # -> book-of-mormon-1841-sparse.txt
   python3 tools/make_typo_catalog.py    # -> printer-typos.md
   python3 tools/make_uncertain_log.py   # -> uncertain-log.md
   ```

## Notes on the scripts

- `compile_markdown.py` strips comments, running heads and footers, and rejoins paragraphs that run across a page break using the `<!-- cont -->` marker; a line-end hyphen at a page end is closed up. It aborts if a `<!-- cont -->` has no paragraph to continue.
- `make_sparse.py` keeps only the page ranges in `PAGE_RANGES` (page 5, the title page, whose abridgment text was translated from the plates, minus its imprint paragraphs, and pages 9–642, 1 Nephi through Moroni); the testimonies (7–8) and the INDEX (643–649) are left out. Provisional until the pages are transcribed.
- `make_typo_catalog.py` builds `../printer-typos.md` from a curated list in the script (from a dictionary scan of the compiled text); forms that do not occur simply produce no rows.
- `make_uncertain_log.py` builds `../uncertain-log.md` from the comments in the page files.
- `make_review_checklist.py` (needs `~/.venvs/lds-transcribe/bin/python` and the PDF) builds `work/review/checklist.html` (gitignored, about 15 MB, images embedded) from the disagreements in `../proofread-disagreements.md` and every `uncertain` comment in the page files. Each item has a crop of the scan placed by estimate (a few lines either way) and keep/change/can't-tell buttons; decisions are kept in the browser and exported as text. Unlike 1837 there is no `review_items.json`: the items are read from the two sources, so it stays current.
