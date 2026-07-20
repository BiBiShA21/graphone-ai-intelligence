
import arxiv
from datetime import datetime
from typing import List, Dict
from src.logger import logger

class ArxivAPIScraper:
    def __init__(self):
        self.name = "ArxivAPI"
    
    async def fetch_papers(self, query: str = "AI", max_results: int = 1000) -> List[Dict]:
        """Fetch papers from Arxiv using official API"""
        papers = []
        
        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            for i, result in enumerate(client.results(search)):
                paper = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "paper_url": result.entry_id,
                    "github_url": None,
                    "github_stars": 0,
                    "published_date": result.published.isoformat() + "Z",
                    "abstract": result.summary[:500],
                    "source_url": result.entry_id,
                    "source_name": "arXiv"
                }
                papers.append(paper)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"✓ Fetched {i + 1} papers from Arxiv")
            
            logger.info(f"✓ Total {len(papers)} papers from Arxiv")
            return papers
        
        except Exception as e:
            logger.error(f"Error fetching from Arxiv: {str(e)}")
            return []