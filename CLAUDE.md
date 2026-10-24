# CLAUDE.md

Guidance for Claude Code in this repository.

## What this repo is

A text corpus, not software: AI-assisted transcription of the 1841 first European edition of the Book of Mormon (Liverpool: printed by J. Tompkins for Brigham Young, Heber C. Kimball and Parley P. Pratt; "First European, from the Second American Edition", a reprint of 1837 with British spellings), from `Book-of-Mormon-1841.pdf` (gitignored, ~730 MB, from josephsmithpapers.org via archiveviewer.org). The PDF has **656 pages**, each a US Letter page holding one ~1170x2000 px image of a single leaf, with **no text layer**. Method and tools are adapted from `../1840-robinson-smith-nauvoo-book-of-mormon` (newest; read its `transcription-notes.md` gotchas), `../1837-pratt-goodson-kirtland-book-of-mormon` and `../1830-grandin-palmyra-book-of-mormon`.

**Status:** set up; tools adapted; layout surveyed (see `transcription-notes.md` §1). **All 656 PDF pages are transcribed** (pilot by the main session, the rest by Sonnet 5.5 subagents in 4-page batches), `check_structure.py` clean (0 errors, 0 warnings, ~301 `uncertain` comments, 1 `[illegible]`). OCR diff done (one dropped line fixed on PDF 326; see `transcription-notes.md` §3). Blind proofread of a 60-page sample done (0 edits in 49 random pages; see §3, including the planted-error calibration). The generated outputs are built (see `transcription-notes.md` §3). Not yet done: the rest of the blind proofread (`tools/proofread-spec.md`), the owner review checklist, and the generated outputs (`compile_markdown.py`, `make_plaintext.py`, `make_sparse.py`, `make_typo_catalog.py`, `make_uncertain_log.py`; the scratch compile builds: ~275k words). `README.md` is owner-edited.

## Files
`book-of-mormon-1841-pages/page-NNN.md` (NNN = PDF page, 3 digits) are the source of truth; everything else is derived. Printed folio = PDF page − 8 in the main text (PDF 10 = p. 2; PDF 9 opens 1 Nephi without a folio); the INDEX (PDF 643–649) is − 6. Rebuild (standard library only):
```
python3 tools/compile_markdown.py   # book-of-mormon-1841.md
python3 tools/make_plaintext.py     # book-of-mormon-1841.txt
python3 tools/make_sparse.py        # book-of-mormon-1841-sparse.txt
python3 tools/check_structure.py [--allow-gaps]
```
`tools/prepare_images.py` (needs `~/.venvs/lds-transcribe/bin/python`) extracts each PDF page's image uncropped to `work/img/pNNNN.jpg` (gitignored); `--zoom Z --box L,T,R,B` makes an enlarged region for a doubtful spot. `tools/make_review_checklist.py` builds `work/review/checklist.html`. Rules for transcribers are in `tools/transcription-spec.md`; blind proofreading in `tools/proofread-spec.md`.

## Rules
- Write what the scan shows, never what you think it should say (no corrections from 1830/1837/1840/KJV/memory; 1841 is a 1837 reprint, so silent normalization is the main risk). Doubtful: `<!-- uncertain: … -->`; unreadable: `[illegible]`.
- Never transcribe without viewing the images. If the image tool fails, stop and report the page.
- Batches of 4 pages per subagent (token economy); skip pages whose file exists; `--clean` each batch's images afterwards; check `df -h .` before each group (disk is tight; subagent transcripts that embed images are large).
- Review is lean: local `tesseract` diff to flag pages, blind proofread of flagged pages plus a random sample, then the remaining pages. Do not claim a page was audited/proofread when it was not; record model and review per range in `transcription-notes.md`.
- No images in tracked files. **Never `git commit` or `git push`**; the owner does. `README.md` is owner-edited: change it with small edits.
