from pydantic import BaseModel
from typing import List


class ArxivSearchInput(BaseModel):
    query: str
    max_results: int = 5


class ArxivSearchResult(BaseModel):
    title: str
    authors: List[str]
    summary: str
    link: str
