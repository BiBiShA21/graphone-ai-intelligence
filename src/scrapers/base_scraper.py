import aiohttp
import asyncio
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from src.logger import logger
from src.config import config
import time

class BaseScraper:
    def __init__(self, name: str):
        self.name = name
        self.session = None
        self.rate_limiter = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch URL with rate limiting and retry logic"""
        async with self.rate_limiter:
            try:
                await asyncio.sleep(config.RATE_LIMIT_DELAY)
                async with self.session.get(url) as response:
                    if response.status == 200:
                        logger.info(f"✓ Fetched: {url}")
                        return await response.text()
                    else:
                        logger.warning(f"✗ Status {response.status}: {url}")
                        return None
            except asyncio.TimeoutError:
                logger.error(f"✗ Timeout: {url}")
                raise
            except Exception as e:
                logger.error(f"✗ Error fetching {url}: {str(e)}")
                raise
    
    async def fetch_multiple(self, urls: List[str]) -> List[Dict]:
        """Fetch multiple URLs concurrently"""
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results