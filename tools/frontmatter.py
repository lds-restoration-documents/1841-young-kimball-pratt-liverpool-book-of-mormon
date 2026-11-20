"""Helper for scripts that read book-of-mormon-1841.md: remove its YAML frontmatter."""


def strip_frontmatter(t):
    """Remove the YAML frontmatter block that compile_markdown.py puts at the top of book-of-mormon-1841.md."""
    if t.startswith('---\n'):
        end = t.find('\n---\n', 4)
        if end != -1:
            return t[end + 5:].lstrip('\n')
    return t


REPO = 'https://github.com/lds-restoration-documents/1841-young-kimball-pratt-liverpool-book-of-mormon'


def txt_header(sparse=False):
    """The single header line (plus a blank line) that starts each .txt output."""
    return (f"# The Book of Mormon (Liverpool, 1841) ({'sparse, ' if sparse else ''}"
            f"AI draft, no full human proofread) - {REPO}\n\n")
