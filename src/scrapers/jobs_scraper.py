import requests
from datetime import datetime
from typing import List, Dict
from src.logger import logger
from src.utils.date_parser import DateNormalizer

class JobsScraper:
    """Scrape AI jobs from multiple working boards"""
    
    def __init__(self):
        self.name = "JobsScraper"
        self.date_normalizer = DateNormalizer()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def fetch_devto_jobs(self, max_results: int = 50) -> List[Dict]:
        """Fetch AI/ML jobs from Dev.to"""
        jobs = []
        
        try:
            url = "https://dev.to/api/listings"
            params = {
                "category": "jobs",
                "tag": "ai"
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for listing in data[:max_results]:
                try:
                    job_data = {
                        "title": listing.get('title', ''),
                        "company": listing.get('organization', {}).get('name', 'Unknown') if isinstance(listing.get('organization'), dict) else 'Dev.to',
                        "url": f"https://dev.to{listing.get('path', '')}",
                        "source": "Dev.to",
                        "published_date": self.date_normalizer.to_iso8601(listing.get('created_at', '')),
                        "description": listing.get('processed_html', '')[:500],
                        "is_remote": True,
                        "location": listing.get('location', 'Remote'),
                        "collected_at": datetime.utcnow().isoformat() + "Z"
                    }
                    
                    if self.date_normalizer.is_within_24_hours(job_data['published_date']):
                        jobs.append(job_data)
                
                except Exception as e:
                    logger.warning(f"Error parsing Dev.to job: {str(e)}")
                    continue
            
            logger.info(f"✓ Fetched {len(jobs)} AI jobs from Dev.to")
            return jobs
        
        except Exception as e:
            logger.error(f"Error fetching Dev.to jobs: {str(e)}")
            return []
    
    async def fetch_stackoverflow_jobs(self, max_results: int = 50) -> List[Dict]:
        """Fetch jobs from Stack Overflow"""
        jobs = []
        
        try:
            url = "https://stackoverflow.com/jobs"
            
            # Use GitHub search as proxy (Stack Overflow Jobs deprecated)
            # Alternative: search Google for recent Stack Overflow style jobs
            logger.info("⚠ Stack Overflow Jobs archived. Using alternative source...")
            
            return await self.fetch_github_jobs(max_results)
        
        except Exception as e:
            logger.error(f"Error fetching Stack Overflow: {str(e)}")
            return []
    
    async def fetch_github_jobs(self, max_results: int = 50) -> List[Dict]:
        """Fetch AI jobs from GitHub Issues (jobs posted as issues)"""
        jobs = []
        
        try:
            # Search GitHub for 'hiring' or 'job' issues in AI repos
            url = "https://api.github.com/search/issues"
            
            queries = [
                "label:hiring type:issue",
                "label:jobs type:issue",
                "title:hiring AI OR ML"
            ]
            
            for query in queries:
                try:
                    params = {
                        "q": query,
                        "sort": "created",
                        "order": "desc",
                        "per_page": 30
                    }
                    
                    response = requests.get(url, params=params, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    for issue in data.get('items', [])[:max_results]:
                        try:
                            job_data = {
                                "title": issue.get('title', ''),
                                "company": issue.get('repository_url', '').split('/')[-1],
                                "url": issue.get('html_url', ''),
                                "source": "GitHub",
                                "published_date": self.date_normalizer.to_iso8601(issue.get('created_at', '')),
                                "description": issue.get('body', '')[:500],
                                "is_remote": True,
                                "location": "Various",
                                "collected_at": datetime.utcnow().isoformat() + "Z"
                            }
                            
                            if self.date_normalizer.is_within_24_hours(job_data['published_date']):
                                jobs.append(job_data)
                        
                        except Exception as e:
                            logger.warning(f"Error parsing GitHub job: {str(e)}")
                            continue
                
                except Exception as e:
                    logger.warning(f"Error with GitHub query '{query}': {str(e)}")
                    continue
            
            logger.info(f"✓ Fetched {len(jobs)} AI jobs from GitHub")
            return jobs
        
        except Exception as e:
            logger.error(f"Error fetching GitHub jobs: {str(e)}")
            return []
    
    async def fetch_ycombinator_jobs(self, max_results: int = 50) -> List[Dict]:
        """Fetch jobs from YCombinator's Startup Job Board"""
        jobs = []
        
        try:
            # YC doesn't have public API, but we can parse their startup directory
            url = "https://www.ycombinator.com/companies"
            
            logger.info("⚠ YC Jobs requires scraping. Using HackerNews alternate...")
            return await self.fetch_hackernews_hiring_threads(max_results)
        
        except Exception as e:
            logger.error(f"Error fetching YC jobs: {str(e)}")
            return []
    
    async def fetch_hackernews_hiring_threads(self, max_results: int = 50) -> List[Dict]:
        """Fetch from HackerNews 'Who is Hiring' monthly threads"""
        jobs = []
        
        try:
            url = "https://hacker-news.firebaseio.com/v0/stories.json"
            response = requests.get(url, timeout=10)
            story_ids = response.json()[:500]
            
            found_hiring_threads = 0
            
            for story_id in story_ids:
                try:
                    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    story_response = requests.get(story_url, timeout=5)
                    story = story_response.json()
                    
                    title = story.get('title', '').lower()
                    
                    # Look for "Who is Hiring" threads
                    if 'who is hiring' in title or 'ask hn: who is hiring' in title:
                        job_data = {
                            "title": story.get('title', ''),
                            "company": "HackerNews Hiring Thread",
                            "url": f"https://news.ycombinator.com/item?id={story_id}",
                            "source": "HackerNews",
                            "published_date": datetime.fromtimestamp(story.get('time', 0)).isoformat() + "Z",
                            "description": "Open hiring thread with AI/ML opportunities",
                            "is_remote": True,
                            "location": "Various",
                            "collected_at": datetime.utcnow().isoformat() + "Z"
                        }
                        
                        if self.date_normalizer.is_within_24_hours(job_data['published_date']):
                            jobs.append(job_data)
                            found_hiring_threads += 1
                    
                    if found_hiring_threads >= max_results:
                        break
                
                except Exception as e:
                    logger.warning(f"Error parsing HN story: {str(e)}")
                    continue
            
            logger.info(f"✓ Fetched {len(jobs)} from HackerNews Hiring Threads")
            return jobs
        
        except Exception as e:
            logger.error(f"Error fetching HackerNews hiring threads: {str(e)}")
            return []
    
    async def fetch_producthunt_jobs(self, max_results: int = 50) -> List[Dict]:
        """Fetch jobs/gigs from Product Hunt"""
        jobs = []
        
        try:
            # Product Hunt has a Makers section
            url = "https://www.producthunt.com/feed.xml"
            
            import feedparser
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_results]:
                try:
                    if any(keyword in entry.get('title', '').lower() for keyword in ['job', 'hiring', 'looking for', 'seeking']):
                        job_data = {
                            "title": entry.get('title', ''),
                            "company": "ProductHunt",
                            "url": entry.get('link', ''),
                            "source": "ProductHunt",
                            "published_date": self.date_normalizer.to_iso8601(entry.get('published', '')),
                            "description": entry.get('summary', '')[:500],
                            "is_remote": True,
                            "location": "Various",
                            "collected_at": datetime.utcnow().isoformat() + "Z"
                        }
                        
                        if self.date_normalizer.is_within_24_hours(job_data['published_date']):
                            jobs.append(job_data)
                
                except Exception as e:
                    logger.warning(f"Error parsing ProductHunt entry: {str(e)}")
                    continue
            
            logger.info(f"✓ Fetched {len(jobs)} from ProductHunt")
            return jobs
        
        except Exception as e:
            logger.error(f"Error fetching ProductHunt jobs: {str(e)}")
            return []