from fastapi import FastAPI
from app.models import SearchRequest, SearchResponse
from app.search import semantic_search

app = FastAPI()

@app.post("/search")
def search(request: SearchRequest, metric: str = Query("l2", enum=["l2", "cosine"])):
    results = semantic_search(
        query=request.query,
        top_k=request.top_k,
        metric=metric
    )
    return SearchResponse(results=results)

