# 1841 Young, Kimball & Pratt Liverpool Book of Mormon
[Markdown](#what-is-markdown) & Plain Text extractions of the content of the 1841 edition of the Book of Mormon published by Brigham Young, Heber C. Kimball, and Parley P. Pratt in Liverpool, England ("First European, from the Second American Edition"; printed by J. Tompkins, "by order of the Translator"). Reprint of the 1837 edition with British spellings. Extracted using AI.

Future editions of The Book of Mormon printed by the Church of Jesus Christ of Latter-day Saints descended from this 1841 British edition, not the 1840 edition.

## Files
* [book-of-mormon-1841.md](book-of-mormon-1841.md): the whole text in a single [Markdown](#what-is-markdown) file (about 275,000 words): the title page, the testimonies of the Three and Eight Witnesses, the Book of Mormon and the index. A `<!-- page NNN -->` comment marks where each PDF page begins.
* [book-of-mormon-1841.txt](book-of-mormon-1841.txt): the same text as plain text, with no [Markdown](#what-is-markdown).
* [book-of-mormon-1841-sparse.txt](book-of-mormon-1841-sparse.txt): plain text of the Book of Mormon proper only: the title page (PDF page 5) that was translated from the plates ("An account written by the hand of Mormon…"), followed by the text from 1 Nephi through Moroni (PDF pages 9–642). It leaves out the 1841 imprint on the title page (translator, edition, printer, publishers, year), the title-page verso, the testimonies of the witnesses and the index.
* [book-of-mormon-1841-pages/](book-of-mormon-1841-pages/): one [Markdown](#what-is-markdown) file per page of the scan PDF (`page-001.md` to `page-656.md`), with running heads, headings and signature marks. File numbers are PDF page numbers (printed page number = PDF page minus 8 in the main text, minus 6 in the index). These are the source of truth; the files above are generated from them. Pages with no text (covers, endpapers, blank leaves) have a one-line description.
* [printer-typos.md](printer-typos.md): a catalog of the printer's slips and misspellings in the 1841 print (about 280 occurrences, each with its page and context), leaving out spellings that were normal or intentional for the period, such as "shew" (likely, not exhaustive).

## What is in the 1841 edition
* This is the **first European edition**, a reprint of the American second edition (1837) with **British spellings** ("favour", "honour", "neighbour", "armour", "centre"), printed by J. Tompkins at Liverpool for Brigham Young, Heber C. Kimball and Parley P. Pratt. The print has printer's errors of its own, all kept as printed.
* **No verse numbers**, no double columns, no footnotes and no cross-references; text in paragraphs on a single wide column. Chapters are numbered within each book in Roman numerals ("CHAPTER II."), often with a short rule printed above the heading, and some chapters open with an italic summary.
* Spelling, capitalization, punctuation and grammar are kept exactly as printed, **printer's errors included**; nothing has been corrected from other editions. Punctuation is **ordinary** (commas, semicolons, colons and periods), much fuller than the sparse punctuation of the 1830 first edition. Printed page numbers and running heads are kept too, including the odd ones (for example "BOOK OR MOSIAH.").
* Like the 1830, 1837 and 1840 editions, it has **no later book divisions** (no 3 Nephi or 4 Nephi by name): the books are the First and Second Book of Nephi, Jacob, Enos, Jarom, Omni, Words of Mormon, Mosiah, Alma, Helaman, two successive books each headed "The Book of Nephi" (PDF pages 494 and 561), "Book of Mormon" (566), Ether (588) and Moroni (627). Many books open in the middle of a page.
* There is **no Preface**: the text opens with the title page (page 5), its verso ("ENTERED AT STATIONERS' HALL."), the **Testimony of the Three Witnesses and the Testimony of the Eight Witnesses** (pages 7–8, at the front of the book, unlike the 1840 edition) and then 1 Nephi (page 9, which prints no page number; page 10 is printed page 2). The text ends on page 642 (printed page 634) with "…both quick and dead. Amen."
* A seven-page **topical index** (PDF pages 643–649, printed pages 637–643) follows the text, in two columns with dotted leaders. In the page files each index entry is its own line, with the dotted leader written as "…".
* Signature marks at the foot of pages ("A", "A 2", "B", …) are recorded as footers.

## Source
Transcribed from a 656-page PDF scan of the 1841 edition, as published by the [Joseph Smith Papers](https://www.josephsmithpapers.org/paper-summary/book-of-mormon-1841/). The page images were downloaded with the [Archive Viewer](https://archiveviewer.org) tool and printed as a PDF (the PDF is not included in this repository). Each PDF page holds one photographed leaf; the PDF has no text layer. Page 1 is the front cover (dark leather with blind-stamped scrollwork), pages 2–4 endpapers and a blank leaf, page 5 the title page, page 6 its verso, pages 7–8 the testimonies, page 9 the opening of 1 Nephi, pages 10–642 the text, pages 643–649 the index, pages 650–652 blank leaves, page 653 the inside back cover, 654 an endpaper, 655 a leaf with faint pencil handwriting and 656 the back cover. Page 653 has a pasted-in printed newspaper clipping that is not part of the 1841 book; it is described in a comment in the page file and not transcribed. Handwriting, stamps and the like are likewise described only.

## What is Markdown?
Markdown is a simple way of writing formatted text using plain characters, such as `#` for headings and `*asterisks*` for *italics*. A Markdown file is still readable as ordinary text, and can also be displayed with formatting.
* Learn more at [markdown.org](https://markdown.org/).
* Tools for displaying, editing, or converting Markdown files: [https://markdown.org/tools/](https://markdown.org/tools/)

## Artificial Intelligence
Extracted with Claude Code from Anthropic using the Sonnet 5.5 model. Each page is transcribed from one full-page image of the scan (there is no text layer or OCR), four pages at a time, by separate AI agents (about fifteen pilot pages were written first in the main session to fix the conventions); a script then checks the structure of every page file. A local OCR (tesseract) was compared with the transcription of every page; it found one page with a dropped last line (PDF page 326), which was fixed. A separate AI agent working blind then proofread a sample of 60 pages against the scan: 49 pages drawn at random plus 11 chosen because the OCR comparison or the process flagged them. It found no errors in the random pages and one punctuation mark in the others. As a check on the proofreading itself, six errors were deliberately planted in sampled pages and five were caught, so it catches most single-word slips but can miss an extra inserted word. Where a mark was too worn to tell a comma from a period, the gap after it and whether the next word starts with a capital letter were used to decide. The text is meant to show what the page shows, so printer's spellings and errors, punctuation, hyphenation and paragraphing are kept. A few things are deliberately **not** reproduced: the thin space the type may put before `;`, `:`, `?` and `!`, handwriting, stamps, the pasted-in newspaper clipping, and ink specks, stains and bleed-through that are not letters or punctuation.

**This is an AI transcription and has not been proofread by a person.**

**Status: all 656 pages of the scan are transcribed and structure-checked, and 60 of the 634 text pages have been proofread blind by a separate AI agent. The remaining text pages have not been proofread, and a human proofread has not been done.** The sample suggests that few errors remain, but expect some, especially colon versus semicolon and comma versus period on worn type, worn letters that the AI may have normalized, and inserted or dropped words. About 300 doubtful readings are marked in the page files. For anything that matters, check the scan.

These files record how it was checked:

* [uncertain-log.md](uncertain-log.md): every doubtful reading and layout note recorded in the transcription, by page.
* [transcription-notes.md](transcription-notes.md): the layout of the scan, the conventions used and the review status.

## Rebuilding the combined files
```
python3 tools/compile_markdown.py   # book-of-mormon-1841.md
python3 tools/make_plaintext.py     # book-of-mormon-1841.txt
python3 tools/make_sparse.py        # book-of-mormon-1841-sparse.txt
python3 tools/make_typo_catalog.py  # printer-typos.md
python3 tools/make_uncertain_log.py # uncertain-log.md
python3 tools/check_structure.py    # mechanical checks of the page files
python3 tools/ocr_diff.py           # OCR-vs-transcription comparison (work/ocr/, needs tesseract)
```
See [tools/README.md](tools/README.md) for the full pipeline.
