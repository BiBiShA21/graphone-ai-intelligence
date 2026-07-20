import asyncio
from datetime import datetime
from src.logger import logger
from src.processors.storage import StorageManager
from src.entity_resolution.deduplicator import Deduplicator
import json

async def run_phase_4():
    """Execute Phase 4: Entity Resolution & Deduplication"""
    
    logger.info("=" * 80)
    logger.info("PHASE 4: ENTITY RESOLUTION & DEDUPLICATION")
    logger.info("=" * 80)
    
    storage = StorageManager()
    deduplicator = Deduplicator()
    
    # Load Phase 3 data
    logger.info("\n📥 LOADING PHASE 3 DATA...")
    papers = storage.load_raw_data("phase3_papers")
    news = storage.load_raw_data("phase3_news")
    jobs = storage.load_raw_data("phase3_jobs")
    
    logger.info(f"   Loaded {len(papers)} papers")
    logger.info(f"   Loaded {len(news)} news articles")
    logger.info(f"   Loaded {len(jobs)} job postings")
    
    # Deduplication
    logger.info("\n🔍 STEP 1: DEDUPLICATION...")
    
    unique_papers = deduplicator.deduplicate_papers(papers)
    unique_news = deduplicator.deduplicate_news(news)  # Same logic
    unique_jobs = deduplicator.deduplicate_jobs(jobs)
    
    # Canonicalization
    logger.info("\n🔄 STEP 2: CANONICALIZATION...")
    
    unique_papers = deduplicator.canonicalize_companies_in_data(unique_papers)
    unique_news = deduplicator.canonicalize_companies_in_data(unique_news)
    unique_jobs = deduplicator.canonicalize_companies_in_data(unique_jobs)
    
    # Get mapping log
    mapping_log = deduplicator.get_mapping_log()
    
    # Save resolved data
    logger.info("\n💾 SAVING RESOLVED DATA...")
    
    storage.save_raw_data(unique_papers, "resolved_papers")
    storage.save_as_csv(unique_papers, "resolved_papers")
    
    storage.save_raw_data(unique_news, "resolved_news")
    storage.save_as_csv(unique_news, "resolved_news")
    
    storage.save_raw_data(unique_jobs, "resolved_jobs")
    storage.save_as_csv(unique_jobs, "resolved_jobs")
    
    # Save mapping log
    logger.info("\n📋 SAVING ENTITY MAPPING LOG...")
    storage.save_raw_data(mapping_log, "entity_mapping_log")
    
    # Create CSV of mappings
    if mapping_log:
        import pandas as pd
        df = pd.DataFrame(mapping_log)
        df.to_csv("data/processed/entity_mapping_log.csv", index=False)
        logger.info(f"   ✓ Saved {len(mapping_log)} mapping records")
    
    # Results
    logger.info("\n✅ PHASE 4 RESULTS:")
    logger.info(f"   📄 Unique Papers: {len(papers)} → {len(unique_papers)}")
    logger.info(f"   📰 Unique News: {len(news)} → {len(unique_news)}")
    logger.info(f"   💼 Unique Jobs: {len(jobs)} → {len(unique_jobs)}")
    logger.info(f"   📋 Entity Mappings: {len(mapping_log)}")
    
    # Summary stats
    duplicates_removed = (len(papers) - len(unique_papers)) + \
                        (len(news) - len(unique_news)) + \
                        (len(jobs) - len(unique_jobs))
    
    canonicalizations = len([m for m in mapping_log if m.get("type") == "canonicalized"])
    
    logger.info(f"\n📊 DEDUPLICATION STATS:")
    logger.info(f"   Duplicates Removed: {duplicates_removed}")
    logger.info(f"   Entities Canonicalized: {canonicalizations}")
    logger.info(f"   Data Quality Score: {(1 - duplicates_removed / (len(papers) + len(news) + len(jobs))) * 100:.1f}%")
    
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 4 COMPLETE - ENTITY RESOLUTION & DEDUPLICATION")
    logger.info("=" * 80)
    
    return {
        "papers": unique_papers,
        "news": unique_news,
        "jobs": unique_jobs,
        "mapping_log": mapping_log
    }

if __name__ == "__main__":
    asyncio.run(run_phase_4())