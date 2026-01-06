from __future__ import annotations
from pathlib import Path
from typing import List, Dict

ALLOWED_EXT = {".txt", ".md"}

def load_documents(folder: str = "docs") -> List[Dict]:
    """
    Loads text-like documents from ./docs (txt/md).
    Returns list of {name, text}.
    """
    base = Path(folder)
    if not base.exists():
        raise FileNotFoundError(f"Folder not found: {base.resolve()}")

    docs = []
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.suffix.lower() in ALLOWED_EXT:
            text = p.read_text(encoding="utf-8", errors="ignore")
            if text.strip():
                docs.append({"name": p.name, "text": text})
    return docs

def chunk_text(text: str, max_chars: int = 8000) -> List[str]:
    """
    Simple chunking by character count.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+max_chars])
        i += max_chars
    return chunks