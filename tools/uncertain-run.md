# Second pass on doubtful places (read tools/transcription-spec.md and the "Tie-breaker" and "Editing policy" parts of tools/proofread-spec.md first)

Your prompt gives a batch id (`uNNN`) and PDF pages. Every page file has one or more `<!-- uncertain: … -->` comments (or an `[illegible]`). Your job is ONLY those spots: settle each from the scan, at a zoom where needed. Do not re-proofread the rest of the page (that was done) and do not touch other text.

Procedure per page:
1. `~/.venvs/lds-transcribe/bin/python tools/prepare_images.py --pages A,B,... --out work/unc_uNNN` and view each whole page with the Read tool once so you can locate the spot. List the spots with `grep -n "uncertain\|illegible" book-of-mormon-1841-pages/page-NNN.md`.
2. For each spot make a zoom of just that area (`--pages N --zoom 3 --box L,T,R,B --out work/unc_uNNNz`, box as fractions of the page; a small box such as a few words wide, zoom 3 or 4) and look at it. Read the mark/letters from the scan first, then compare with the file and the comment.
3. Decide, one of:
   - **Confirmed**: the file's reading is what the scan shows, clearly. Delete the `<!-- uncertain … -->` comment (keep the text, and its spacing: remove the comment and nothing else).
   - **Corrected**: the scan clearly shows something else. Fix the text (smallest edit) and delete the comment. Never correct a printed error toward the expected form; keep printed errors (`aud`, `iu`, `thay`...). If the print has an error and the file already shows it, that is "confirmed".
   - **Tie-breaker**: for a comma-versus-period mark use the gap/next-word-case rule in tools/proofread-spec.md; apply it, and delete the comment if the rule settles it.
   - **Still doubtful**: leave the text; rewrite the comment only to make it more precise (what you see at 3-4x), or leave it as is. Do not delete it.
   For `[illegible]`: if you can now read it, replace it; otherwise leave it.
   Worn-letter rule (applies to e/c, n/u, i/l, h/b and similar pairs): write the unexpected letter only when it is plainly that letter at 4-5x, with the shape the print uses for it elsewhere on the page (for example a closed bowl, or a crossbar, that wear could not make). If the difference could be wear (a missing crossbar, a broken stem), keep the expected letter and leave the comment in place, made more precise: that is "still doubtful", not "confirmed".
   A worn letter that still reads as the expected letter is the expected letter. Never use memory of the Book of Mormon or other editions.
4. Log to `work/unc-log-uNNN.md`: per page `## Page NNN`, then one line per spot: `- <where, 3-5 words>: <confirmed|corrected|tie-breaker|still doubtful> — <what the scan shows>`; for edits give `was "x" -> now "y"`.
5. Delete your images and zooms when done (same commands with `--clean`). Touch only your pages and your log. No git. If an image Read fails, skip that page and report it. On an API/usage limit, stop and say the last page completed.

Final reply (max 6 lines): pages done, counts of confirmed / corrected / tie-breaker / still doubtful, and each correction with its page.
