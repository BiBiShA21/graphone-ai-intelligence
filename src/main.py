import asyncio
from datetime import datetime
from src.scrapers.arxiv_api_scraper import ArxivAPIScraper
from src.scrapers.github_api_scraper import GitHubAPIScraper
from src.scrapers.huggingface_scraper import HuggingFaceScraper
from src.processors.storage import StorageManager
from src.logger import logger
from src.config import config

async def run_phase_1():
    """Execute Phase 1: API-Based Massive Data Acquisition"""
    
    logger.info("=" * 80)
    logger.info("PHASE 1: MASSIVE API-BASED DATA ACQUISITION")
    logger.info("=" * 80)
    
    storage = StorageManager()
    all_data = {
        "research_papers": [],
        "ai_repositories": [],
        "ai_models": [],
        "ai_datasets": []
    }
    
    # Step 1: Fetch arXiv Papers
    logger.info("\n📄 STEP 1: Fetching Research Papers from arXiv...")
    arxiv_scraper = ArxivAPIScraper()
    papers = await arxiv_scraper.fetch_papers(max_results=1000)
    all_data["research_papers"] = papers
    
    # Step 2: Fetch GitHub AI Repositories
    logger.info("\n💻 STEP 2: Fetching AI Repositories from GitHub...")
    github_scraper = GitHubAPIScraper()
    repos = await github_scraper.fetch_ai_repos(max_results=1000)
    all_data["ai_repositories"] = repos
    
    # Step 3: Fetch HuggingFace Models
    logger.info("\n🤗 STEP 3: Fetching AI Models from HuggingFace...")
    hf_scraper = HuggingFaceScraper()
    models = await hf_scraper.fetch_models(max_results=1000)
    all_data["ai_models"] = models
    
    # Step 4: Fetch HuggingFace Datasets
    logger.info("\n📊 STEP 4: Fetching AI Datasets from HuggingFace...")
    datasets = await hf_scraper.fetch_datasets(max_results=500)
    all_data["ai_datasets"] = datasets
    
    # Step 5: Save all data
    logger.info("\n💾 STEP 5: Saving data...")
    storage.save_raw_data(papers, "research_papers_raw")
    storage.save_as_csv(papers, "research_papers")
    
    storage.save_raw_data(repos, "ai_repositories_raw")
    storage.save_as_csv(repos, "ai_repositories")
    
    storage.save_raw_data(models, "ai_models_raw")
    storage.save_as_csv(models, "ai_models")
    
    storage.save_raw_data(datasets, "ai_datasets_raw")
    storage.save_as_csv(datasets, "ai_datasets")
    
    # Step 6: Validation
    logger.info("\n✅ STEP 6: Validation...")
    logger.info(f"📄 Research Papers: {len(papers)}/{config.MIN_PAPERS}")
    logger.info(f"💻 AI Repositories: {len(repos)}/{config.MIN_STARTUPS}")
    logger.info(f"🤗 AI Models: {len(models)}/{config.MIN_PRODUCTS}")
    logger.info(f"📊 AI Datasets: {len(datasets)}")
    
    total_records = len(papers) + len(repos) + len(models) + len(datasets)
    logger.success(f"\n✓ TOTAL RECORDS ACQUIRED: {total_records}")
    
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1 COMPLETE")
    logger.info("=" * 80)
    
    return all_data

if __name__ == "__main__":
    asyncio.run(run_phase_1())