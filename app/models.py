from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    doc_id: str
    title: str
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
