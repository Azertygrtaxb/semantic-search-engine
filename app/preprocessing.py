import json
import os
from pathlib import Path
from app.chunk import sloding_window_chunk
from app.preprocessing import clean_text

def clean_text(text: str) -> str:
    return " ".join(text.strip().split())  # delete spaces and line breaks, cut multiple spaces and line breaks, etc...


RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/processed/documents.jsonl")


def build_jsonl(window_size=200, overlap=50):
    """
    Build dataset with sliding-window chunks.
    Output format:
        {
            "id": "doc_01_chunk_0",
            "parent_id": "doc_01",
            "title": "wireless_01.txt (chunk 0)",
            "chunk_index": 0,
            "text": "... chunk text ..."
        }
    """
    OUT_PATH.parent.mkdir(exist_ok=True)

    with open(OUT_PATH, "w", encoding="utf-8") as out:
        doc_id = 0

        for filename in os.listdir(RAW_DIR):
            if not filename.endswith(".txt"):
                continue

            filepath = RAW_DIR / filename
            parent_id = f"doc_{doc_id}"

            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned = clean_text(raw_text)
            chunks = sliding_window_chunk(
                cleaned, window_size=window_size, overlap=overlap
            )

            for i, chunk in enumerate(chunks):
                entry = {
                    "id": f"{parent_id}_chunk_{i}",
                    "parent_id": parent_id,
                    "title": f"{filename} (chunk {i})",
                    "chunk_index": i,
                    "text": chunk,
                }
                out.write(json.dumps(entry) + "\n")

            doc_id += 1

    print(f"Chunked JSONL created with sliding window -> {OUT_PATH}")

