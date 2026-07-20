from difflib import SequenceMatcher
from typing import Tuple, List, Dict
from src.logger import logger

class FuzzyMatcher:
    """Fuzzy string matching for deduplication"""
    
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
    
    def similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings (0-1)"""
        if not str1 or not str2:
            return 0.0
        
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        return SequenceMatcher(None, str1, str2).ratio()
    
    def are_duplicates(self, str1: str, str2: str) -> bool:
        """Check if two strings are duplicates"""
        return self.similarity(str1, str2) >= self.threshold
    
    def find_duplicates_in_list(self, items: List[str]) -> List[Tuple[int, int, float]]:
        """Find duplicate pairs in a list"""
        duplicates = []
        
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                sim = self.similarity(items[i], items[j])
                if sim >= self.threshold:
                    duplicates.append((i, j, sim))
        
        return duplicates