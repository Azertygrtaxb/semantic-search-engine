from fastapi import FastAPI
from app.models import SearchRequest, SearchResponse
from app.search import semantic_search

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    results = semantic_search(req.query, req.top_k)
    return SearchResponse(results=results)

