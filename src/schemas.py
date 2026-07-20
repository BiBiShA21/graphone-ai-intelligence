from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ResearchPaperSchema(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "RESEARCH_PAPER"
    content: dict = Field(...)
    collectedAt: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "schemaVersion": "1.0",
                "recordType": "RESEARCH_PAPER",
                "content": {
                    "title": "Attention Is All You Need",
                    "authors": ["Ashish Vaswani", "Noam Shazeer"],
                    "paper_url": "https://arxiv.org/abs/1706.03762",
                    "github_url": "https://github.com/user/repo",
                    "github_stars": 1234,
                    "published_date": "2017-06-12T00:00:00Z"
                },
                "collectedAt": "2024-07-19T14:22:00Z"
            }
        }

class StartupSchema(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "STARTUP"
    source: dict
    content: dict
    collectedAt: datetime

class ProductSchema(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "PRODUCT"
    source: dict
    content: dict
    collectedAt: datetime