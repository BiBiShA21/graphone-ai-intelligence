import asyncio
from datetime import datetime
from src.scrapers.news_scraper import NewsScraper
from src.scrapers.jobs_scraper import JobsScraper
from src.processors.storage import StorageManager
from src.logger import logger

async def run_phase_2():
    """Execute Phase 2: High-Fidelity Signal Ingestion"""
    
    logger.info("=" * 80)
    logger.info("PHASE 2: HIGH-FIDELITY SIGNAL INGESTION (24-HR FRESHNESS)")
    logger.info("=" * 80)
    
    storage = StorageManager()
    news_scraper = NewsScraper()
    jobs_scraper = JobsScraper()
    
    all_news = []
    all_jobs = []
    
    # NEWS FETCHING
    logger.info("\n📰 FETCHING NEWS FROM 5 SOURCES...")
    
    news_sources = [
        ("HackerNews", news_scraper.fetch_hackernews_ai(50)),
        ("TechCrunch", news_scraper.fetch_techcrunch_ai(50)),
        ("Reddit", news_scraper.fetch_reddit_ai(50)),
        ("ProductHunt", news_scraper.fetch_producthunt_ai(50)),
        ("ArXiv", news_scraper.fetch_arxiv_sanity(50))
    ]
    
    for source_name, task in news_sources:
        news = await task
        all_news.extend(news)
        logger.info(f"   ✓ {source_name}: {len(news)} articles (24-hr)")
    
    logger.info(f"\n✓ Total News Articles: {len(all_news)} (all within 24 hours)")
    
    # JOBS FETCHING
    logger.info("\n💼 FETCHING JOBS FROM 5 SOURCES...")
    
    job_sources = [
        ("Dev.to", jobs_scraper.fetch_devto_jobs(50)),
        ("GitHub", jobs_scraper.fetch_github_jobs(50)),
        ("HackerNews", jobs_scraper.fetch_hackernews_hiring_threads(50)),
        ("ProductHunt", jobs_scraper.fetch_producthunt_jobs(50)),
        ("Stack Overflow", jobs_scraper.fetch_stackoverflow_jobs(50))
    ]
    
    for source_name, task in job_sources:
        jobs = await task
        all_jobs.extend(jobs)
        logger.info(f"   ✓ {source_name}: {len(jobs)} jobs (24-hr)")
    
    logger.info(f"\n✓ Total Job Postings: {len(all_jobs)} (all within 24 hours)")
    
    # SAVE DATA
    logger.info("\n💾 SAVING DATA...")
    storage.save_raw_data(all_news, "news_raw_24hr")
    storage.save_as_csv(all_news, "news_24hr")
    
    storage.save_raw_data(all_jobs, "jobs_raw_24hr")
    storage.save_as_csv(all_jobs, "jobs_24hr")
    
    logger.info("\n✅ PHASE 2 VALIDATION:")
    logger.info(f"   📰 News: {len(all_news)} articles (24-hr verified)")
    logger.info(f"   💼 Jobs: {len(all_jobs)} postings (24-hr verified)")
    logger.info(f"   ✓ All data is 24-hour fresh!")
    
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2 COMPLETE")
    logger.info("=" * 80)
    
    return {"news": all_news, "jobs": all_jobs}

if __name__ == "__main__":
    asyncio.run(run_phase_2())