import json
import re
from typing import Optional, Dict
from src.logger import logger

class JSONParser:
    """Parse LLM responses into valid JSON"""
    
    @staticmethod
    def extract_json(response_text: str) -> Optional[Dict]:
        """Extract JSON from LLM response"""
        
        try:
            # Try direct parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try removing markdown code blocks
        try:
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Try extracting JSON object with regex
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Try fixing common issues
        try:
            # Fix single quotes
            fixed = response_text.replace("'", '"')
            # Try parsing
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        
        logger.error(f"Could not parse JSON from response: {response_text[:100]}")
        return None
    
    @staticmethod
    def validate_json(data: Dict, required_fields: list) -> bool:
        """Validate JSON has required fields"""
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False
        return True