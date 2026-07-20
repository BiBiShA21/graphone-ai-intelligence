from typing import List, Dict, Tuple
from src.logger import logger
from src.entity_resolution.fuzzy_matcher import FuzzyMatcher
from src.entity_resolution.canonical_entities import get_canonical_name

class Deduplicator:
    """Remove duplicates and canonicalize entity names"""
    
    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher(threshold=0.90)
        self.mapping_log = []  # Track all transformations
    
    def deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """Deduplicate research papers"""
        logger.info("🔍 Deduplicating research papers...")
        
        seen_urls = set()
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            # Check by URL first (most reliable)
            paper_url = paper.get("paper_url", "").lower().strip()
            if paper_url and paper_url in seen_urls:
                logger.debug(f"   Duplicate (URL): {paper_url}")
                self.mapping_log.append({
                    "type": "duplicate_removed",
                    "entity_type": "paper",
                    "original": paper_url,
                    "reason": "exact_url_match"
                })
                continue
            
            # Check by title similarity
            title = paper.get("title", "").lower().strip()
            if title:
                is_duplicate = False
                for seen_title in seen_titles:
                    if self.fuzzy_matcher.similarity(title, seen_title) > 0.95:
                        logger.debug(f"   Duplicate (Title): {title}")
                        self.mapping_log.append({
                            "type": "duplicate_removed",
                            "entity_type": "paper",
                            "original": title,
                            "matched_with": seen_title,
                            "reason": "title_similarity"
                        })
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    if paper_url:
                        seen_urls.add(paper_url)
                    seen_titles.add(title)
                    unique_papers.append(paper)
        
        logger.info(f"   ✓ Removed {len(papers) - len(unique_papers)} duplicates")
        return unique_papers
    
    def deduplicate_news(self, news: List[Dict]) -> List[Dict]:
        """Deduplicate news articles"""
        logger.info("🔍 Deduplicating news articles...")
        
        seen_urls = set()
        seen_titles = set()
        unique_news = []
        
        for article in news:
            # Check by URL first
            article_url = article.get("url", "")
            if isinstance(article_url, str):
                article_url = article_url.lower().strip()
                
                if article_url and article_url in seen_urls:
                    logger.debug(f"   Duplicate (URL): {article_url}")
                    self.mapping_log.append({
                        "type": "duplicate_removed",
                        "entity_type": "news",
                        "original": article_url,
                        "reason": "exact_url_match"
                    })
                    continue
            
            # Check by title similarity
            title = article.get("title", "")
            if isinstance(title, str):
                title_lower = title.lower().strip()
                
                if title_lower:
                    is_duplicate = False
                    for seen_title in seen_titles:
                        if self.fuzzy_matcher.similarity(title_lower, seen_title) > 0.90:
                            logger.debug(f"   Duplicate (Title): {title_lower}")
                            self.mapping_log.append({
                                "type": "duplicate_removed",
                                "entity_type": "news",
                                "original": title_lower,
                                "matched_with": seen_title,
                                "reason": "title_similarity"
                            })
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        if isinstance(article_url, str) and article_url:
                            seen_urls.add(article_url)
                        seen_titles.add(title_lower)
                        unique_news.append(article)
            else:
                unique_news.append(article)
        
        logger.info(f"   ✓ Removed {len(news) - len(unique_news)} duplicate news")
        return unique_news
    
    def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Deduplicate job postings"""
        logger.info("🔍 Deduplicating job postings...")
        
        seen_urls = set()
        unique_jobs = []
        
        for job in jobs:
            job_url = job.get("url", "")
            
            # Type check - ensure it's a string
            if not isinstance(job_url, str):
                job_url = str(job_url) if job_url else ""
            
            job_url = job_url.lower().strip()
            
            if job_url and job_url in seen_urls:
                logger.debug(f"   Duplicate job: {job_url}")
                self.mapping_log.append({
                    "type": "duplicate_removed",
                    "entity_type": "job",
                    "original": job_url,
                    "reason": "exact_url_match"
                })
                continue
            
            if job_url:
                seen_urls.add(job_url)
            unique_jobs.append(job)
        
        logger.info(f"   ✓ Removed {len(jobs) - len(unique_jobs)} duplicate jobs")
        return unique_jobs
    
    def deduplicate_companies(self, companies: List[str]) -> List[str]:
        """Deduplicate company names"""
        logger.info("🔍 Deduplicating company names...")
        
        seen = set()
        unique = []
        
        for company in companies:
            canonical = get_canonical_name(company, "company")
            canonical_lower = canonical.lower().strip()
            
            if canonical_lower not in seen:
                seen.add(canonical_lower)
                unique.append(canonical)
                
                if canonical != company:
                    self.mapping_log.append({
                        "type": "canonicalized",
                        "entity_type": "company",
                        "original": company,
                        "canonical": canonical
                    })
        
        logger.info(f"   ✓ Deduplicated {len(companies)} → {len(unique)} unique companies")
        return unique
    
    def canonicalize_companies_in_data(self, data: List[Dict]) -> List[Dict]:
        """Canonicalize company names in dataset"""
        logger.info("🔄 Canonicalizing company names...")
        
        for item in data:
            if "company" in item:
                original = item["company"]
                canonical = get_canonical_name(original, "company")
                
                if canonical != original:
                    item["company_canonical"] = canonical
                    self.mapping_log.append({
                        "type": "canonicalized",
                        "entity_type": "company",
                        "original": original,
                        "canonical": canonical,
                        "context": item.get("title", "")[:50]
                    })
        
        logger.info(f"   ✓ Canonicalized company names")
        return data
    
    def get_mapping_log(self) -> List[Dict]:
        """Get all transformations"""
        return self.mapping_log