import asyncio
import json
from datetime import datetime
from src.logger import logger
from src.processors.storage import StorageManager

async def run_phase_3():
    """Phase 3: Simplified Extraction (Mock for demo)"""
    
    logger.info("=" * 80)
    logger.info("PHASE 3: DATA EXTRACTION & NORMALIZATION")
    logger.info("=" * 80)
    
    storage = StorageManager()
    
    # Load Phase 1 & 2 data
    logger.info("\n📥 LOADING DATA FROM PHASES 1-2...")
    papers = storage.load_raw_data("research_papers_raw")
    news = storage.load_raw_data("news_raw_24hr")
    jobs = storage.load_raw_data("jobs_raw_24hr")
    
    logger.info(f"   ✓ {len(papers)} papers loaded")
    logger.info(f"   ✓ {len(news)} news articles loaded")
    logger.info(f"   ✓ {len(jobs)} job postings loaded")
    
    # Normalize & structure data
    logger.info("\n🔄 NORMALIZING & STRUCTURING DATA...")
    
    normalized_papers = []
    for paper in papers[:100]:  # Sample 100
        normalized = {
            "title": paper.get("title", ""),
            "authors": paper.get("authors", []),
            "abstract": paper.get("abstract", ""),
            "paper_url": paper.get("paper_url", ""),
            "github_url": paper.get("github_url"),
            "github_stars": paper.get("github_stars", 0),
            "published_date": paper.get("published_date", ""),
            "source": "arXiv",
            "_normalized_at": datetime.utcnow().isoformat() + "Z"
        }
        normalized_papers.append(normalized)
    
    logger.info(f"   ✓ Normalized {len(normalized_papers)} papers")
    
    normalized_news = []
    for article in news[:50]:  # Sample 50
        normalized = {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "source": article.get("source", ""),
            "published_date": article.get("published_date", ""),
            "content": article.get("content", "")[:500],
            "author": article.get("author", ""),
            "freshness": "24-hour verified",
            "_normalized_at": datetime.utcnow().isoformat() + "Z"
        }
        normalized_news.append(normalized)
    
    logger.info(f"   ✓ Normalized {len(normalized_news)} news articles")
    
    normalized_jobs = []
    for job in jobs[:50]:  # Sample 50
        normalized = {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "url": job.get("url", ""),
            "source": job.get("source", ""),
            "published_date": job.get("published_date", ""),
            "description": job.get("description", "")[:500],
            "is_remote": job.get("is_remote", True),
            "location": job.get("location", "Remote"),
            "freshness": "24-hour verified",
            "_normalized_at": datetime.utcnow().isoformat() + "Z"
        }
        normalized_jobs.append(normalized)
    
    logger.info(f"   ✓ Normalized {len(normalized_jobs)} job postings")
    
    # Save normalized data
    logger.info("\n💾 SAVING NORMALIZED DATA...")
    storage.save_raw_data(normalized_papers, "phase3_papers")
    storage.save_as_csv(normalized_papers, "phase3_papers")
    
    storage.save_raw_data(normalized_news, "phase3_news")
    storage.save_as_csv(normalized_news, "phase3_news")
    
    storage.save_raw_data(normalized_jobs, "phase3_jobs")
    storage.save_as_csv(normalized_jobs, "phase3_jobs")
    
    logger.info("\n✅ PHASE 3 RESULTS:")
    logger.info(f"   📄 Extracted Papers: {len(normalized_papers)}")
    logger.info(f"   📰 Extracted News: {len(normalized_news)}")
    logger.info(f"   💼 Extracted Jobs: {len(normalized_jobs)}")
    logger.info(f"   ✓ All data normalized to canonical format")
    
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 3 COMPLETE - DATA EXTRACTION & NORMALIZATION")
    logger.info("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_phase_3())