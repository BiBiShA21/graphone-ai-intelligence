from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
from typing import List, Dict
from src.scrapers.base_scraper import BaseScraper
from src.logger import logger
import re

class PapersWithCodeScraper(BaseScraper):
    def __init__(self):
        super().__init__("PapersWithCode")
        self.base_url = "https://paperswithcode.com"
    
    async def get_paper_links(self, query: str = "ai", start: int = 0) -> List[str]:
        """Get paper links from Papers with Code"""
        url = f"https://paperswithcode.com/papers?q={query}&page={start//20 + 1}"
        html = await self.fetch(url)
        
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        # Find paper links (adjust selector based on actual HTML)
        for item in soup.find_all('a', class_='paper-link'):
            href = item.get('href', '')
            if '/paper/' in href:
                links.append(f"https://paperswithcode.com{href}")
        
        logger.info(f"Found {len(links)} papers from PapersWithCode")
        return links
    
    async def parse_paper(self, url: str) -> Dict:
        """Parse individual paper from Papers with Code"""
        html = await self.fetch(url)
        
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            # Extract title
            title = soup.find('h1')
            title_text = title.text.strip() if title else "Unknown"
            
            # Extract authors
            authors = []
            authors_section = soup.find('div', class_='authors')
            if authors_section:
                for author in authors_section.find_all('a'):
                    authors.append(author.text.strip())
            
            # Extract GitHub link
            github_url = None
            github_link = soup.find('a', {'title': 'View on GitHub'})
            if github_link:
                github_url = github_link.get('href', '')
            
            # Extract published date
            date_span = soup.find('span', class_='paper-published-date')
            published_date = date_span.text if date_span else datetime.utcnow().isoformat() + "Z"
            
            return {
                "title": title_text,
                "authors": authors,
                "paper_url": url,
                "github_url": github_url,
                "github_stars": 0,  # Will be fetched separately
                "published_date": published_date,
                "source_url": url
            }
        
        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return None