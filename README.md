# Semantic Search Engine for High-Throughput Technical Document Analysis

This repository contains a complete end-to-end semantic search pipeline tailored for large collections of technical documents, such as patent abstracts, scientific texts, standards, and engineering reports.  
The system combines:

- deterministic preprocessing,  
- dense vector representations (embeddings),  
- a FAISS similarity index for high-dimensional retrieval,  
- and a FastAPI service interface enabling real-time querying.

The architectural objective is to demonstrate the core components of a scalable AI-assisted retrieval system that could be integrated into patent acquisition workflows, prior-art relevance assessment, claim similarity exploration, or large-scale document triage.

---

## 1. System Overview

The system follows a controlled, modular pipeline:

1. **Raw document ingestion**  
2. **Deterministic text preprocessing**
3. **Dataset normalization into JSONL**
4. **Embedding generation through SentenceTransformers**
5. **Vector index construction using FAISS (IndexFlatL2)**
6. **Metadata serialization**
7. **Semantic query execution**
8. **API exposure for downstream integration**

The design prioritizes reproducibility, transparency, and extensibility.  
No training occurs; the system relies on state-of-the-art sentence-level embedding models optimized for semantic similarity tasks.

---

## 2. Architecture

```
semantic-search-engine/
│
├── app/
│   ├── main.py               # FastAPI application layer
│   ├── preprocessing.py      # Deterministic data ingestion and JSONL generation
│   ├── search.py             # Embedding model, FAISS index, vector similarity search
│   ├── models.py             # Typed Pydantic request/response definitions
│   └── config.py             # Future configuration management
│
├── data/
│   ├── raw/                  # Input documents (.txt)
│   └── processed/            # Normalized dataset (documents.jsonl)
│
├── index/
│   ├── faiss_index.bin       # Serialized FAISS structure
│   └── meta.json             # Mapping vector index → document metadata
│
└── README.md
```


### 2.1 System Architecture Overview

```
                   +---------------------+
                   |   Raw .txt files    |
                   +----------+----------+
                              |
                              v
                 +-----------------------------+
                 |  Preprocessing Layer        |
                 |  build_jsonl()              |
                 +-----------------------------+
                              |
               normalized JSONL dataset
                              |
                              v
                 +-----------------------------+
                 | Sentence Embedding Model    |
                 | all-MiniLM-L6-v2           |
                 +-----------------------------+
                              |
                     dense vector space
                              |
                              v
                 +-----------------------------+
                 | FAISS Index (IndexFlatL2)   |
                 +-----------------------------+
                              |
                     nearest-neighbor search
                              |
                              v
                 +-----------------------------+
                 | semantic_search() function  |
                 +-----------------------------+
                              |
                              v
                   +---------------------+
                   |   FastAPI /search   |
                   +---------------------+
```


---

## 3. Design Rationale

### 3.1 Choice of Embedding Model  
The model used is:

```
sentence-transformers/all-MiniLM-L6-v2
```

Rationale:

- Balanced trade-off between semantic performance and inference speed  
- Latency suitable for interactive search scenarios  
- Embedding dimension (384) reduces memory footprint  
- Model optimized for sentence-level similarity, fitting short-to-medium technical passages

Other candidates (BERT, RoBERTa, SPLADE, ColBERT) were not selected due to heavier inference cost or additional indexing infrastructure requirements.

### 3.2 Choice of FAISS Backend  
The system uses:

```
faiss.IndexFlatL2
```

Rationale:

- Deterministic, exact nearest-neighbor search
- Ideal for datasets up to several hundred thousand vectors
- Trivial to serialize and reload
- No quantization or approximate search errors

Possible extensions include IVF, HNSW, or PQ for million-scale corpora.

### 3.3 Metadata Management  
FAISS does not store document metadata.  
The design explicitly externalizes:

```
vector_id → {id, title}
```

This guarantees:

- full separation between vector index and document metadata  
- transparent reindexing and introspection  
- non-destructive updates of document descriptors  

---

## 4. Installation

### 4.1 Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]" sentence-transformers faiss-cpu pydantic python-dotenv pytest
```

---

## 5. Dataset Construction

### 5.1 Raw Documents  
All raw text files must be stored in:

```
data/raw/
```

Documents may include:

- patent abstracts  
- sections of RFCs  
- scientific or engineering paragraphs  
- descriptive technical narratives  

### 5.2 Build the JSONL Dataset

```bash
python3 -c "from app.preprocessing import build_jsonl; build_jsonl()"
```

Output is written to:

```
data/processed/documents.jsonl
```

Each entry includes:

```json
{"id": "doc_1", "title": "optical 01", "text": "...", "tags": []}
```

---

## 6. Embedding Generation and FAISS Index

### 6.1 Build the FAISS index

```bash
python3 -c "from app.search import build_faiss_index; build_faiss_index()"
```

Actions performed:

1. Load normalized JSONL dataset  
2. Encode all documents into dense vectors  
3. Construct FAISS index in memory  
4. Serialize index to disk  
5. Store metadata mapping in `meta.json`

Generated files:

```
index/faiss_index.bin
index/meta.json
```

### 6.2 Embedding Characteristics

- Dimensionality: 384  
- Vector type: float32  
- Model: MiniLM (Transformer encoder)  
- Search metric: L2 distance in embedding space  

---

## 7. Semantic Search API

### 7.1 Run the server

```bash
uvicorn app.main:app --reload
```

### 7.2 Interactive Documentation

```
http://127.0.0.1:8000/docs
```

### 7.3 Query Example

Endpoint:

```
POST /search
```

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
      "title": "wireless 03",
      "score": 0.731
    },
    {
      "doc_id": "doc_4",
      "title": "optical 01",
      "score": 0.894
    }
  ]
}
```

---

## 8. Retrieval Mechanics (Internal)

### 8.1 Query Execution Path

1. Preprocess the input query  
2. Compute embedding using the same encoder  
3. Submit vector to FAISS for nearest-neighbor lookup  
4. Retrieve indices and distances  
5. Map indices to document identifiers through metadata  
6. Return ranked results

### 8.2 Metric Considerations  
L2 distance is used, but cosine similarity could be adopted through vector normalization prior to indexing.  
Alternative settings include:

- IndexFlatIP  
- HNSW for high-recall approximate search  
- IVF for multi-million scale regression  

### 8.3 Determinism  
Given that embeddings and FAISS operations are deterministic, repeated indexing will always generate the same results for a fixed dataset.

---

## 9. CLI Query Example

Direct semantic query via command line:

```bash
python3 -c "from app.search import semantic_search; print(semantic_search('optical signal attenuation models', 3))"
```

---

## 10. Evaluation and Testing

### 10.1 Unit Tests

Tests can be extended to validate:

- dataset integrity  
- embedding dimension consistency  
- FAISS index loading  
- deterministic search results  
- API endpoint stability  

Run test suite:

```bash
pytest
```

---

## 11. Extension Opportunities

Several enhancements are architecturally compatible:

### 11.1 Model and Embedding Improvements

- Long document handling via chunking and hierarchical embeddings  
- Model distillation for accelerated inference  
- Domain-specific models (SciBERT, PatentBERT, LegalBERT)

### 11.2 Indexing Improvements

- IVF Flat for scalable approximate search  
- HNSW for graph-based retrieval  
- Product Quantization (PQ) for memory reduction  

### 11.3 API and System Extensions

- scoring normalization  
- contextual snippets returned with results  
- ranking fusion (BM25 + dense retrieval)  
- distributed index hosting  
- stream processing for continuous ingestion  

---

## 12. License

MIT License.
