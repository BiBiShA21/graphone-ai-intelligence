import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from src.logger import logger
from src.utils.date_parser import DateNormalizer
import html2text

class NewsScraper:
    """Scrape AI news from multiple sources"""
    
    def __init__(self):
        self.name = "NewsScraper"
        self.date_normalizer = DateNormalizer()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def fetch_hackernews_ai(self, max_results: int = 50) -> List[Dict]:
        """Fetch AI-related stories from HackerNews"""
        articles = []
        
        try:
            # HackerNews API endpoint for AI stories
            url = "https://hacker-news.firebaseio.com/v0/newstories.json"
            response = requests.get(url, timeout=10)
            story_ids = response.json()[:300]  # Get top 300 stories
            
            for story_id in story_ids[:max_results]:
                try:
                    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    story_response = requests.get(story_url, timeout=5)
                    story = story_response.json()
                    
                    # Filter for AI/ML related content
                    title = story.get('title', '')
                    if any(keyword in title.lower() for keyword in ['ai', 'machine learning', 'neural', 'gpt', 'llm', 'deep learning']):
                        article = {
                            "title": title,
                            "url": story.get('url', story.get('id', '')),
                            "source": "HackerNews",
                            "published_date": datetime.fromtimestamp(story.get('time', 0)).isoformat() + "Z",
                            "content": story.get('title', ''),
                            "author": story.get('by', 'Unknown'),
                            "collected_at": datetime.utcnow().isoformat() + "Z"
                        }
                        
                        if self.date_normalizer.is_within_24_hours(article['published_date']):
                            articles.append(article)
                
                except:
                    continue
            
            logger.info(f"✓ Fetched {len(articles)} AI articles from HackerNews")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching HackerNews: {str(e)}")
            return []
    
    async def fetch_techcrunch_ai(self, max_results: int = 50) -> List[Dict]:
        """Fetch AI news from TechCrunch"""
        articles = []
        
        try:
            url = "https://feeds.techcrunch.com/TechCrunch/"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_results]:
                try:
                    published = entry.get('published', datetime.utcnow().isoformat())
                    
                    article = {
                        "title": entry.get('title', ''),
                        "url": entry.get('link', ''),
                        "source": "TechCrunch",
                        "published_date": self.date_normalizer.to_iso8601(published),
                        "content": entry.get('summary', '')[:500],
                        "author": entry.get('author', 'TechCrunch'),
                        "collected_at": datetime.utcnow().isoformat() + "Z"
                    }
                    
                    if self.date_normalizer.is_within_24_hours(article['published_date']):
                        articles.append(article)
                
                except:
                    continue
            
            logger.info(f"✓ Fetched {len(articles)} AI articles from TechCrunch")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching TechCrunch: {str(e)}")
            return []
    
    async def fetch_reddit_ai(self, max_results: int = 50) -> List[Dict]:
        """Fetch AI discussions from Reddit"""
        articles = []
        
        try:
            subreddits = ['MachineLearning', 'artificial', 'Futurology']
            
            for subreddit in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
                    response = requests.get(url, headers=self.headers, timeout=10)
                    data = response.json()
                    
                    for post in data.get('data', {}).get('children', [])[:max_results]:
                        try:
                            post_data = post.get('data', {})
                            
                            article = {
                                "title": post_data.get('title', ''),
                                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                                "source": f"Reddit/{subreddit}",
                                "published_date": datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat() + "Z",
                                "content": post_data.get('selftext', '')[:500],
                                "author": post_data.get('author', 'Unknown'),
                                "collected_at": datetime.utcnow().isoformat() + "Z"
                            }
                            
                            if self.date_normalizer.is_within_24_hours(article['published_date']):
                                articles.append(article)
                        
                        except:
                            continue
                
                except:
                    continue
            
            logger.info(f"✓ Fetched {len(articles)} AI posts from Reddit")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching Reddit: {str(e)}")
            return []
    
    async def fetch_producthunt_ai(self, max_results: int = 50) -> List[Dict]:
        """Fetch AI products from Product Hunt"""
        articles = []
        
        try:
            url = "https://api.producthunt.com/v2/posts?order=newest"
            
            # Product Hunt API requires auth, use RSS as fallback
            url = "https://www.producthunt.com/feed.xml"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_results]:
                try:
                    if 'ai' in entry.get('title', '').lower() or 'machine' in entry.get('title', '').lower():
                        published = entry.get('published', datetime.utcnow().isoformat())
                        
                        article = {
                            "title": entry.get('title', ''),
                            "url": entry.get('link', ''),
                            "source": "ProductHunt",
                            "published_date": self.date_normalizer.to_iso8601(published),
                            "content": entry.get('summary', '')[:500],
                            "author": "ProductHunt",
                            "collected_at": datetime.utcnow().isoformat() + "Z"
                        }
                        
                        if self.date_normalizer.is_within_24_hours(article['published_date']):
                            articles.append(article)
                
                except:
                    continue
            
            logger.info(f"✓ Fetched {len(articles)} AI products from ProductHunt")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching ProductHunt: {str(e)}")
            return []
    
    async def fetch_arxiv_sanity(self, max_results: int = 50) -> List[Dict]:
        """Fetch latest AI papers from ArXiv (via RSS)"""
        articles = []
        
        try:
            url = "http://feeds.arxiv.org/rss/cs.AI"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_results]:
                try:
                    published = entry.get('published', datetime.utcnow().isoformat())
                    
                    article = {
                        "title": entry.get('title', ''),
                        "url": entry.get('link', ''),
                        "source": "ArXivAI",
                        "published_date": self.date_normalizer.to_iso8601(published),
                        "content": entry.get('summary', '')[:500],
                        "author": entry.get('author', 'ArXiv'),
                        "collected_at": datetime.utcnow().isoformat() + "Z"
                    }
                    
                    if self.date_normalizer.is_within_24_hours(article['published_date']):
                        articles.append(article)
                
                except:
                    continue
            
            logger.info(f"✓ Fetched {len(articles)} papers from ArXiv")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching ArXiv: {str(e)}")
            return []