import requests
from datetime import datetime
from typing import List, Dict
from src.logger import logger

class HuggingFaceScraper:
    def __init__(self):
        self.name = "HuggingFace"
    
    async def fetch_models(self, max_results: int = 1000) -> List[Dict]:
        """Fetch AI models from HuggingFace"""
        models = []
        
        try:
            # Use the correct HuggingFace models endpoint
            url = "https://huggingface.co/api/models"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Fetch with pagination
            for page in range(0, max_results // 20 + 1):
                try:
                    params = {
                        "p": page,
                        "sort": "likes",
                        "direction": -1,
                        "limit": 20
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if not data:
                        break
                    
                    for model in data:
                        model_data = {
                            "title": model.get("id", "Unknown"),
                            "description": model.get("description", "")[:200] if model.get("description") else "No description",
                            "model_url": f"https://huggingface.co/{model.get('id')}",
                            "downloads": model.get("downloads", 0),
                            "likes": model.get("likes", 0),
                            "published_date": model.get("lastModified", datetime.utcnow().isoformat()) + "Z",
                            "source_url": f"https://huggingface.co/{model.get('id')}",
                            "source_name": "HuggingFace"
                        }
                        models.append(model_data)
                        
                        if len(models) >= max_results:
                            break
                    
                    if len(models) >= max_results:
                        break
                
                except Exception as e:
                    logger.warning(f"Error fetching page {page}: {str(e)}")
                    continue
            
            logger.info(f"✓ Fetched {len(models)} models from HuggingFace")
            return models[:max_results]
        
        except Exception as e:
            logger.error(f"Error fetching from HuggingFace: {str(e)}")
            return []
    
    async def fetch_datasets(self, max_results: int = 500) -> List[Dict]:
        """Fetch AI datasets from HuggingFace"""
        datasets = []
        
        try:
            url = "https://huggingface.co/api/datasets"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            for page in range(0, max_results // 20 + 1):
                try:
                    params = {
                        "p": page,
                        "sort": "likes",
                        "direction": -1,
                        "limit": 20
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if not data:
                        break
                    
                    for dataset in data:
                        dataset_data = {
                            "title": dataset.get("id", "Unknown"),
                            "description": dataset.get("description", "")[:200] if dataset.get("description") else "No description",
                            "dataset_url": f"https://huggingface.co/datasets/{dataset.get('id')}",
                            "downloads": dataset.get("downloads", 0),
                            "likes": dataset.get("likes", 0),
                            "published_date": dataset.get("lastModified", datetime.utcnow().isoformat()) + "Z",
                            "source_url": f"https://huggingface.co/datasets/{dataset.get('id')}",
                            "source_name": "HuggingFace"
                        }
                        datasets.append(dataset_data)
                        
                        if len(datasets) >= max_results:
                            break
                    
                    if len(datasets) >= max_results:
                        break
                
                except Exception as e:
                    logger.warning(f"Error fetching datasets page {page}: {str(e)}")
                    continue
            
            logger.info(f"✓ Fetched {len(datasets)} datasets from HuggingFace")
            return datasets[:max_results]
        
        except Exception as e:
            logger.error(f"Error fetching datasets from HuggingFace: {str(e)}")
            return []