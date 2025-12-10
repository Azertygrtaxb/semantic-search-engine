# Semantic Search Engine for High-Throughput Technical Document Retrieval

This repository contains a complete semantic search pipeline designed for technical documents such as patents, engineering notes, scientific literature, and standards.  
It demonstrates the core components of a scalable vector-based retrieval system combining:

- deterministic preprocessing  
- dense embeddings using SentenceTransformers  
- FAISS vector indexing  
- semantic similarity search  
- an API interface via FastAPI  

The objective is to provide a compact but fully functional architecture representative of real-world R&D information retrieval systems, especially those used in patent intelligence, prior-art exploration, or large-scale document triage.

---

## 1. System Architecture

The system follows a controlled and reproducible pipeline:

```
                   +---------------------+
                   |    Raw .txt files   |
                   +----------+----------+
                              |
                              v
                 +-----------------------------+
                 |   Preprocessing Layer       |
                 |   build_jsonl()             |
                 +-----------------------------+
                              |
                normalized JSONL dataset
                              |
                              v
                 +-----------------------------+
                 |  Embedding Model            |
                 |  all-MiniLM-L6-v2           |
                 +-----------------------------+
                              |
                     dense vector space
                              |
                              v
                 +-----------------------------+
                 |  FAISS Index (IndexFlatL2)  |
                 +-----------------------------+
                              |
                    nearest-neighbor search
                              |
                              v
                 +-----------------------------+
                 |   semantic_search() API     |
                 +-----------------------------+
```

The architecture is modular, deterministic, and designed for reproducibility and extensibility.

---

## 2. Repository Structure

```
semantic-search-engine/
│
├── app/
│   ├── main.py               # FastAPI application
│   ├── preprocessing.py      # Raw → JSONL normalization
│   ├── search.py             # Embeddings, FAISS index, semantic search
│   ├── models.py             # Pydantic request/response schemas
│   └── config.py             # Future configuration module
│
├── data/
│   ├── raw/                  # Input .txt files
│   └── processed/            # Generated dataset (documents.jsonl)
│
├── index/
│   ├── faiss_index.bin       # Serialized FAISS index
│   └── meta.json             # Vector ID → metadata mapping
│
├── tests/                    # Basic unit tests
│
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

---

## 3. Installation

### 3.1 Create environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Dataset Construction

### 4.1 Raw documents

Place `.txt` files inside:

```
data/raw/
```

### 4.2 Generate normalized dataset

```bash
python3 -c "from app.preprocessing import build_jsonl; build_jsonl()"
```

Output:

```
data/processed/documents.jsonl
```

Each line contains:

```json
{"id": "doc_1", "title": "wireless 01", "text": "...", "tags": []}
```

---

## 5. Embeddings and FAISS Index

### 5.1 Build the vector index

```bash
python3 -c "from app.search import build_faiss_index; build_faiss_index()"
```

This step:

1. Loads the JSONL dataset  
2. Generates embeddings via SentenceTransformers  
3. Builds a FAISS `IndexFlatL2`  
4. Saves:

```
index/faiss_index.bin
index/meta.json
```

### 5.2 Embedding characteristics

- Model: `sentence-transformers/all-MiniLM-L6-v2`  
- Vector dimension: 384  
- Representation: dense float32  
- Design: optimized for semantic similarity  

---

## 6. Running the Semantic Search API

### 6.1 Start API

```bash
uvicorn app.main:app --reload
```

### 6.2 Navigate to the documentation

```
http://127.0.0.1:8000/docs
```

### 6.3 Query example

Request:

```json
{
  "query": "beamforming optimization in 5G antenna arrays",
  "top_k": 3
}
```

Response:

```json
{
  "results": [
    {
      "doc_id": "doc_10",
      "title": "wireless_03",
      "score": 0.731
    }
  ]
}
```

---

## 7. Design Decisions

### 7.1 Embedding Model
`all-MiniLM-L6-v2` was selected because it offers:

- favorable semantic performance  
- low inference latency  
- small memory footprint  
- pretrained encoding suitable for sentence-level retrieval  

Alternatives (SciBERT, PatentBERT, ColBERT) provide more domain depth but at significantly higher computational cost.

### 7.2 Index Structure
`IndexFlatL2` provides:

- exact nearest-neighbor search  
- deterministic ranking  
- simple serialization  
- strong baseline performance for corpora under several hundred thousand vectors  

For very large-scale retrieval, IVF or HNSW would become necessary.

### 7.3 Metadata Decoupling
FAISS only stores vectors and internal IDs.  
This system explicitly separates metadata into a JSON mapping:

```
vector_id → { doc_id, title }
```

This enables non-destructive metadata updates and simplifies index regeneration.

### 7.4 Determinism
All operations (preprocessing, encoding, indexing) are deterministic given a fixed dataset.  
No randomness is introduced, ensuring reproducible outputs.

---

## 8. Limitations

- Long documents are not chunked; each file is treated as a single unit.  
- `IndexFlatL2` does not scale efficiently to millions of vectors.  
- No hybrid BM25 + dense retrieval fusion is implemented.  
- No ranking normalization (e.g., softmax over similarity scores).  
- No evaluation metrics (recall, NDCG) are computed.  

---

## 9. Future Work

Planned or recommended improvements:

- Implement cosine similarity using normalized embeddings.  
- Add HNSW or IVF-PQ for large-scale approximate indexing.  
- Add document chunking and passage-level retrieval.  
- Integrate sparse-dense hybrid search (BM25 + embeddings).  
- Add performance benchmarks (query latency, throughput, memory usage).  
- Add Streamlit or React UI for interactive exploration.  
- Add pipeline orchestration (Makefile or Invoke).  

---

## 10. Example CLI Query

Run a search directly:

```bash
python3 -c "from app.search import semantic_search; print(semantic_search('optical signal attenuation models', 3))"
```

---

## 11. Testing

### 11.1 Run all tests

```bash
pytest
```

### 11.2 Example test file

```
tests/test_search.py
```

Contains minimal structural tests for the search function.

---

## 12. Docker Support

### 12.1 Build the image

```bash
docker build -t semantic-search-engine .
```

### 12.2 Run the container

```bash
docker run -p 8000:8000 semantic-search-engine
```

The API will be exposed at:

```
http://127.0.0.1:8000
```

---

## 13. License

MIT License.
