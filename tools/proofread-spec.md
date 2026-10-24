# Proofread spec — second, independent pass over the transcription

Every page has already been transcribed by one agent (there is no separate audit stage). This is a **second, independent
reading** meant to catch what the first missed. It works from its own page images and is deliberately blind to the
transcriber's notes, so that it does not inherit their judgments. The rules for the text itself are those in
`tools/transcription-spec.md` (read it completely first): write what the scan shows, nothing more and nothing less.

## Independence rules

- Do **not** read `work/proof-log-*.md` of other batches, `uncertain-log.md`, `printer-typos.md` or `transcription-notes.md` §3.
  (You may read §2 and `tools/transcription-spec.md`.) The point is to form your own reading of the page before seeing
  anyone else's.
- Make your own images (below); do not reuse images left by other agents.
- Existing `<!-- uncertain: ... -->` and layout comments in the page file are fine to read; they are part of the file.

## Optional hint: OCR disagreements

`work/ocr/diffs/NNN.txt` (from `tools/ocr_diff.py`) lists runs of 4 or more characters where a local OCR of page NNN differs from the page file. It is very noisy (bleed-through, worn type), so most lines are OCR errors, not transcription errors. Read it only after you have formed your own reading of the page; use it to re-look at the spots it names, and never to change the file without seeing the scan evidence yourself.

## Procedure per batch (the pages given to you)

1. Make your own page images in a private folder (the scan is `Book-of-Mormon-1841.pdf`, pages numbered by PDF page; there is no text layer):
   `~/.venvs/lds-transcribe/bin/python tools/prepare_images.py --pages A-B --out work/proof`
   This writes `work/proof/img/pNNNN.jpg` (the whole page at native resolution). Batches are 4 pages per agent, to keep each agent's context small.
   For a spot that is genuinely in doubt (not every colon or semicolon: only marks you cannot call at native size) make a zoom of that spot: `--pages N --zoom 3 --box L,T,R,B --out work/proof3` (box as fractions of the page), and delete it afterwards. An upscale adds no information, it only makes small marks easier to see.
2. For each page, in order: view the page image with the Read tool, and read the page file
   `book-of-mormon-1841-pages/page-NNN.md`. Compare **line by line, word by word, mark by mark**. Never read a page from
   memory of the text (you know the Book of Mormon; the scan is authoritative, the 1841 print has errors of its own, and differs from the 1830, 1837, 1840 and modern editions).
3. Check, on every page:
   - every word and its spelling (printer's errors kept: `aud`, `chall`, `thay`, `nnmber`, `accordidg`... if the scan prints
     it, the file must too; a worn letter that still reads as the expected letter is the expected letter);
   - **inserted or dropped words** (e.g. a dropped `of`, an added `which`), doubled words, transposed words, lines skipped;
   - proper names, letter by letter;
   - punctuation marks and their order, the capital after a colon, `.—` dashes, apostrophes, parentheses, italics;
   - hyphenation (line-end hyphens joined, compounds hyphenated mid-line kept) and page-end hyphens;
   - `<!-- cont -->` on the first line: flush-left first line = continuation (marker present); indented first line (or
     a heading at the top) = new paragraph (no marker); also that each page's last paragraph really continues;
   - paragraph breaks inside the page (an indented line starts a paragraph);
   - the running head and printed folio (kept as printed, errors included), footers and signature marks, headings, chapter
     summaries (italic), ornament comments only where an ornament or rule is actually printed, book titles and subtitles;
   - no space before `; : ? !`; no verse numbers; no modern punctuation. (The 1841 text has ordinary punctuation, unlike the sparse 1830 text: record exactly what is printed.)
4. **Editing policy (important).** Edit the page file only when you are *certain* the file is wrong and the scan right
   (a different letter, a missing/extra word, a wrong name, a wrong marker, a heading error). Make the smallest edit.
   For a borderline mark (comma vs period vs speck, a worn letter that could be two things, a blot) where you read it
   differently from the file, **do not edit**: record it under "Disagreements" in the log. **Exception: an uncertain
   comma-versus-period mark is settled by the tie-breaker rule below, and its result is written (edit the file if the
   rule gives a different mark) and logged as a `tie-breaker` line, not left as a disagreement.** Do not add `uncertain`
   comments of your own and do not remove existing ones, except to delete one you can settle with certainty at 4x
   (then say so). **Never correct a misspelling, a wrong word, a missing or doubled word, odd grammar, a wrong name form or any other
error that is printed in the original** to the standard or expected form: the file must keep exactly what the 1841 print
shows (`aud`, `thay`, `spotloss`, `came pass`, `the the`...). The only spelling edit allowed is the reverse one: restoring
a printed error that the transcription had silently normalized, and only when you can see it plainly on the scan.
Do not 'improve' anything from your knowledge of the Book of Mormon or of English. Every edit you log must name the scan
evidence (e.g. 'scan prints d-e-a-d-n-e-s, file had deadness'). An edit that moves the file closer to modern spelling,
punctuation or grammar, rather than closer to the scan, is a mistake.
5. Log to `work/proof-log-A-B.md` (create it): per page `## Page NNN` then `- no changes` or one line per change
   (`where: was "old" -> now "new" (reason)`), and under it, if any, `- disagreement: <where>: file has "x", I read "y"
   (why)`. Skip pages already logged so an interrupted run can resume.

## Tie-breaker for a comma versus a period (user-set rule)

When a mark after a word is genuinely uncertain between a period and a comma (worn type, a dot with a faint tail), decide by
the **gap after the mark and the case of the next word**:

- **more space after the mark, followed by a capitalized word = period**;
- **less (tighter) space after the mark, followed by a lowercase word = comma**.

Compare the gap with the ordinary word spaces on the same line. This is an educated guess for uncertain marks only: a mark that
is plainly a period or plainly a comma at zoom is written as it is, whatever follows (the 1841 print may have real periods before
lowercase words, e.g. "fire. and", and real commas before capitals). If the two signals disagree (wide gap before a lowercase
word, or a tight gap before a capital), fall back on the shape of the mark; if that is still unclear, keep the existing
reading and, where there was an `<!-- uncertain -->` comment, leave it in place. Applying this rule does not require a
comment; only a mark that still cannot be settled keeps one. Log each use in the proofread log as
`- tie-breaker: <where>: "x" -> "y" (gap/case)`.

## Dash spacing (do not edit)

After a sentence-final mark an em dash that ends a printed line is followed by the next line's first word; the book is
written `.— And` (a space after the dash). Do **not** add or remove that space: whether the print has a space at a line
wrap cannot be seen, and one convention is applied to the whole book afterwards. A dash inside a word run
(`Jerusalem—that`) has no spaces.

## Hard stops

- If an image Read fails for a page, do not guess the page: skip it and list it as failed.
- If you hit an API usage/rate limit or a content-filter block, stop and say exactly which page you were on and the last
  page you completed.
- Touch only your own page files and your own log; do not edit any other file; do not run git commands.

## Final reply (brief)

Images proofread, pages failed, total edits grouped by kind (spelling/printer's error, inserted or dropped word, name,
punctuation, cont marker, structure/heading, other), then the list of disagreements.

## Disk space

Create page images only for your own batch, and when you finish (or stop), delete them: `~/.venvs/lds-transcribe/bin/python tools/prepare_images.py --pages A-B --clean --out work/proof` (and the same for any zoom folder). Make zoom images only for a doubtful spot and delete them right after.
