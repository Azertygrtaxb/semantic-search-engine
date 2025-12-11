import json
import numpy as np
from pathlib import Path
from typing import List, Dict

import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from app.preprocessing import clean_text


DATA_PATH = Path("data/processed/documents.jsonl")
INDEX_DIR = Path("index")
INDEX_DIR.mkdir(exist_ok=True)

# Model used for embedding
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


###############################################
############### Data loading ##################
###############################################

def load_documents(path: Path) -> List[Dict]:
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs


###############################################
############### Index building ################
###############################################

def build_faiss_index(metric: str = "l2"):
    """
    Build a FAISS index using either:
      - L2 (IndexFlatL2)
      - Cosine similarity (IndexFlatIP with normalized vectors)
    """

    docs = load_documents(DATA_PATH)
    texts = [clean_text(doc["text"]) for doc in docs]

    print(f"Encoding {len(texts)} documents...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    embeddings = np.array(embeddings).astype(np.float32)

    # normalize vectors if cosine mode
    if metric == "cosine":
        faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]

    if metric == "l2":
        index = faiss.IndexFlatL2(dim)
        index_file = INDEX_DIR / "faiss_l2.bin"

    elif metric == "cosine":
        index = faiss.IndexFlatIP(dim)
        index_file = INDEX_DIR / "faiss_cosine.bin"

    else:
        raise ValueError("metric must be 'l2' or 'cosine'")

    index.add(embeddings)

    print(f"Saving index: {index_file}")
    faiss.write_index(index, str(index_file))

    # Metadata mapping
    meta = {
        str(i): {"doc_id": docs[i]["id"], "parent_id": docs[i]["parent_id"], "chunk_index": docs[i]["chunk_index"],"title": docs[i]["title"]}
        for i in range(len(docs))
    }

    with open(INDEX_DIR / f"meta_{metric}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("Index and metadata saved.")


###############################################
############## Semantic search ################
###############################################

def semantic_search(query: str, top_k: int = 5, metric: str = "l2"):
    """
    Unified semantic search backend.
    metric = "l2" or "cosine"
    """
    query = clean_text(query)
    q_emb = model.encode([query])
    q_emb = np.array(q_emb).astype(np.float32)

    # Normalize for cosine similarity
    if metric == "cosine":
        faiss.normalize_L2(q_emb)
        index_path = INDEX_DIR / "faiss_cosine.bin"
        meta_path = INDEX_DIR / "meta_cosine.json"

    elif metric == "l2":
        index_path = INDEX_DIR / "faiss_l2.bin"
        meta_path = INDEX_DIR / "meta_l2.json"

    else:
        raise ValueError("metric must be 'l2' or 'cosine'")

    index = faiss.read_index(str(index_path))

    distances, indices = index.search(q_emb, top_k)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    results = []
    for rank, idx in enumerate(indices[0]):
        info = meta[str(idx)]
        results.append(
            {
                "chunk_id": info["doc_id"],
		"parent_id": info.get("parent_id"),
                "title": info["title"],
		"chunk_index": info.get("chunk_index"),
                "score": float(distances[0][rank]),
            }
        )

    return results

