import logging
from typing import Any, Type
import requests
import xml.etree.ElementTree as ET

from langchain_core.tools import BaseTool
from pydantic import BaseModel
from AI_Agent_MCP_Server.tookit.tools.research_paper_analyser.schema import (
    ArxivSearchInput,
    ArxivSearchResult,
)


class ArxivSearchTool(BaseTool):
    name: str = "arxiv_search"
    description: str = "Searches arXiv for research papers by query string."
    args_schema: Type[BaseModel] = ArxivSearchInput  # ✅ REQUIRED FOR MCP

    def _run(self, query: str, max_results: int = 5) -> Any:
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            results = []

            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns).text.strip()
                summary = entry.find("atom:summary", ns).text.strip()
                link = entry.find("atom:id", ns).text.strip()
                authors = [
                    author.find("atom:name", ns).text
                    for author in entry.findall("atom:author", ns)
                ]

                results.append(
                    ArxivSearchResult(
                        title=title,
                        authors=authors,
                        summary=summary,
                        link=link,
                    )
                )

            return results

        except Exception as ex:
            logging.error(f"Error: {ex}")
            return {"message": "Error at Research Paper Analyser tool"}
