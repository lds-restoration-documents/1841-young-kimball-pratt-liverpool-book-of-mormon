# Transcription spec — 1841 Young, Kimball & Pratt (Liverpool) Book of Mormon

Instructions for transcribing agents. Source: `Book-of-Mormon-1841.pdf` (656 pages, one photographed leaf per PDF page, no text layer). Files are keyed to the **PDF page number** (3 digits). Printed folio = PDF page − 8 in the main text (PDF 9 opens 1 Nephi and prints no folio; PDF 10 = p. 2; PDF 21 = p. 13). The INDEX (PDF 643–649) is offset 6. Front matter: 1–4 covers/endpapers, 5 title page, 6 verso, 7–8 testimonies; 650–656 blank leaves and back cover.

Input for PDF page N (NNNN = 4-digit) in `work/`: `img/pNNNN.jpg`, the whole page at native resolution (about 1170x2000 px, uncropped: the running head and signature mark are at the edges). View it with Read before writing the page. If an image fails, stop and report the page as failed; never transcribe unseen.
For a doubtful spot only: `~/.venvs/lds-transcribe/bin/python tools/prepare_images.py --pages N --zoom 2 --box 0,0.4,1,0.6 --out work/zoom` (box = L,T,R,B as fractions of the page; then delete it).
Output: `book-of-mormon-1841-pages/page-NNN.md`. Skip pages whose file exists. Write each file right after viewing its page.

## Rules
- **Write what is printed, never what you think it should say.** Printer's errors, odd spellings, names, grammar, doubled or missing words, damaged type and wrong running heads are kept. Do not correct from the 1830, 1837 or 1840 editions, the KJV, the manuscripts or memory. This 1841 text is a reprint of 1837 ("First European, from the Second American Edition") with British spellings and its own printer's errors, so reading from memory is the main risk. Read letter by letter.
- Doubtful reading: best guess plus `<!-- uncertain: … -->` right after it. Unreadable: `[illegible]`.
- Line-end hyphenation is joined into the whole word; words hyphenated in the original stay hyphenated (grep other page files if ambiguous).
- No verse numbers, no marginal notes, one wide column, ordinary punctuation. Record punctuation, capitals after colons, `&c.` etc. exactly. Write NO space before `; : ? !` (the type has a thin space; not transcribed).
- Comma vs period when the mark is uncertain: more space and a capitalized next word = period; less space and a lowercase next word = comma. Colon vs semicolon: a semicolon's lower dot has a tail, a colon's two dots are round and equal; judge at zoom 2 when in doubt.
- Italic = `*italic*` (no space inside the asterisks). Small caps = capitals; ordinary capitalized words keep their case (`And now`).
- Ink specks, foxing, bleed-through (mirror-image text from the reverse leaf), dirt lines and page-edge shading are not text. Ignore without a comment. Use `uncertain` only for a real mark in doubt.

## Format
```
<!-- image NNN -->  (NNN = PDF page number)
**Header:** 8 | FIRST BOOK OF NEPHI.   <- running head, parts separated by " | ", as printed (omit if none)

# THE FIRST BOOK OF NEPHI:               <- book title; any printed subtitle as plain/italic text
## CHAPTER II.                           <- chapter heading, numerals as printed
<!-- decorative ornament printed above the chapter heading -->   (on its own line above `## CHAPTER`, only where an ornament is printed)

AND it came to pass ...                  <- one paragraph per printed paragraph

---

Footer: 2*                               <- signature mark / catchword not in the Header (omit if none)
```
- Even pages have the folio on the left of the head, odd on the right. Pages that open a book have no running head.
- A printed paragraph starts with an indented first line. If the page's first line is flush-left (continuing the previous page's paragraph) start it with `<!-- cont --> ` even if the previous page ended with a full stop. If the page ends mid-paragraph, write the fragment; a page-end hyphen stays (`vis-`) and the next page starts `<!-- cont --> ions …`.
- Chapter summaries (if printed under a heading) are italic paragraphs as printed. A new book opening mid-page: ornament comment, `# TITLE`, `## CHAPTER`, summary; the running head stays that of the book the page began in (note it in a comment).
- Text cut off by the edge of the scan: write the visible fragment, never complete it, and note which edge in a comment at the top.
- Front and back matter (title page, verso, testimonies, INDEX): transcribe in full as stacked lines in printed order and case, with a layout comment. Handwriting, stamps (e.g. HISTORIAN'S OFFICE), labels and bookplates: describe in an HTML comment only, not as text. A page with nothing to read: the page comment and a one-line description comment.
- No commentary, summaries or modern corrections.

## Agent run notes
- A batch is 4 pages. Run `python3 tools/prepare_images.py --pages A-B` first, `--clean` when done. Final reply: pages written, pages failed, anything unusual (brief).
