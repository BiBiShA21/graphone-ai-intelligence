import json
import os
from datetime import datetime
from typing import List, Dict
from src.logger import logger
from src.config import config

class StorageManager:
    def __init__(self):
        os.makedirs(config.DATA_RAW_DIR, exist_ok=True)
        os.makedirs(config.DATA_PROCESSED_DIR, exist_ok=True)
    
    def save_raw_data(self, data: List[Dict], filename: str):
        """Save raw scraped data"""
        filepath = os.path.join(config.DATA_RAW_DIR, f"{filename}.json")
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"✓ Saved {len(data)} records to {filepath}")
    
    def load_raw_data(self, filename: str) -> List[Dict]:
        """Load raw data"""
        filepath = os.path.join(config.DATA_RAW_DIR, f"{filename}.json")
        
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def save_processed_data(self, data: List[Dict], filename: str):
        """Save processed data"""
        filepath = os.path.join(config.DATA_PROCESSED_DIR, f"{filename}.json")
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"✓ Saved {len(data)} records to {filepath}")
    
    def save_as_csv(self, data: List[Dict], filename: str):
        """Export as CSV for Google Sheets"""
        import pandas as pd
        
        filepath = os.path.join(config.DATA_PROCESSED_DIR, f"{filename}.csv")
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Exported {len(data)} records to {filepath}")