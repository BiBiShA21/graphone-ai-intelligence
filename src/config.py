import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    # Rate limiting
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", 1.5))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Targets
    MIN_PAPERS = 1000
    MIN_STARTUPS = 1000
    MIN_PRODUCTS = 1000
    
    # Paths
    DATA_RAW_DIR = "data/raw"
    DATA_PROCESSED_DIR = "data/processed"
    LOGS_DIR = "logs"

config = Config()