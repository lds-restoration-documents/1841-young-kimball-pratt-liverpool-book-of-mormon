# Proofread run instructions (read after tools/proofread-spec.md)

You are an independent BLIND PROOFREADER. Read `tools/proofread-spec.md` completely and follow it exactly, and read `tools/transcription-spec.md`. Your batch id (`pNNN`) and your PDF pages are in your prompt.

Differences from the spec text for this run:
- Make your images with `~/.venvs/lds-transcribe/bin/python tools/prepare_images.py --pages A,B,C,D --out work/proof_pNNN`, view each `work/proof_pNNN/img/pNNNN.jpg` with the Read tool, and delete them at the end with the same command plus `--clean` (zoom spots: `--pages N --zoom 3 --box L,T,R,B --out work/proof_pNNNz`, delete afterwards).
- Write your log to `work/proof-log-pNNN.md`.
- Blindness: do NOT read `transcription-notes.md`, any other `work/proof-log-*.md`, `uncertain-log.md`, `printer-typos.md`, `work/canaries*.json`, or anything in `work/ocr/`. The conventions you need are in the spec files and below. Do not read page files other than your own four (do not use other pages as examples).

Conventions in the page files (written by the transcription pass): first line `<!-- image NNN -->`; `**Header:** a | b` is the running head with the printed folio (kept as printed, errors included); `# TITLE` / `## CHAPTER N.`; italic `*…*`; small caps as capitals; `<!-- cont -->` on a flush-left first line; `---` then `Footer: X` for a signature mark; a short rule printed above a chapter heading is `<!-- short centred rule printed above the chapter heading -->`, one printed below the last paragraph is `<!-- short centred rule printed below the last paragraph -->`, a diamond-swell ornament above a book title is `<!-- decorative ornament (a short centred rule with a diamond-shaped swell) printed above the book title … -->`; `<!-- uncertain: … -->` marks a doubtful reading. Line-end hyphens are joined; page-end hyphens stay on the page. Printed errors, old spellings (shew, sware…) and odd punctuation are KEPT: never normalize.
INDEX pages (643–649): two columns each headed `PAGE`, left column first; each entry is its own paragraph; the dotted leader is written as a single `…`; entries printed without a leader are written bare; compare every entry word by word and every page number digit by digit; index numbers may be printed wrongly: keep them as printed.
Front matter (5–8): title page, verso, testimonies: stacked lines in printed order and case.

Check especially: words dropped or ADDED anywhere (compare line by line, word by word, not just line ends and page ends; an extra word such as `also` or `the` is easy to miss), single-letter misreads, punctuation (colon vs semicolon, comma vs period), paragraph breaks, the cont marker, and the head/folio/footer. For each page read the scan line by line and the page file in parallel; do not skim.

Edit only when certain, smallest possible edit, naming the scan evidence in the log. Final reply (max 8 lines): pages proofread, pages failed, edits grouped by kind with page numbers, number of disagreements.
