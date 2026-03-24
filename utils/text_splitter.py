# utils/text_splitter.py

from typing import List


def split_text_into_chunks(
    text: str,
    chunk_size: int = 800,
    overlap: int = 200,
) -> List[str]:
    """
    Split text into overlapping chunks by character count.
    Tries to split at sentence/paragraph boundaries where possible.
    """
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to break at a natural boundary (newline or period) if not at end
        if end < text_len:
            for boundary in ["\n\n", "\n", ". ", " "]:
                pos = text.rfind(boundary, start, end)
                if pos != -1 and pos > start:
                    end = pos + len(boundary)
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap if end - overlap > start else end

    return chunks
