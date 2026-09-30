import re
from pathlib import Path


def read_docs(root="data/docs"):
    for p in sorted(Path(root).rglob("*")):
        if p.suffix in {".txt", ".md"} and p.name != "SOURCES.md":
            yield p, p.read_text(encoding="utf-8", errors="ignore")


def clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\x0c", "\n")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)      # markdown front matter
    text = re.sub(r"\{\{.*?\}\}", "", text)                          # jekyll template tags
    text = re.sub(r"^\{:.*\}\s*$", "", text, flags=re.M)
    text = re.sub(r"^.*\[Page \d+\]\s*$", "", text, flags=re.M)      # RFC page footers
    text = re.sub(r"^RFC \d+ .*\d{4}\s*$", "", text, flags=re.M)     # RFC page headers
    return re.sub(r"\n{3,}", "\n\n", text)


def chunk_text(text: str, size: int = 1000, overlap: int = 150) -> list[str]:
    chunks, cur = [], ""
    for p in [p.strip() for p in clean(text).split("\n\n") if p.strip()]:
        while len(p) > size:                       # very long paragraph: hard split
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.append(p[:size])
            p = p[size - overlap:]
        if len(cur) + len(p) + 2 <= size:
            cur = f"{cur}\n\n{p}" if cur else p
        else:
            if cur:
                chunks.append(cur)
            cur = (cur[-overlap:] + "\n\n" + p) if cur else p
    if cur:
        chunks.append(cur)
    return chunks