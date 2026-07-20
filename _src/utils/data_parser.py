from datetime import datetime, timedelta
import re
from dateutil import parser as dateutil_parser
from src.logger import logger

class DateNormalizer:
    """Handle various date formats including relative dates like '2 hours ago'"""
    
    @staticmethod
    def is_within_24_hours(date_string: str) -> bool:
        """Check if date is within last 24 hours"""
        try:
            date = DateNormalizer.parse_date(date_string)
            if not date:
                return False
            
            now = datetime.utcnow()
            diff = now - date.replace(tzinfo=None)
            
            is_fresh = diff.total_seconds() < 86400  # 24 hours in seconds
            return is_fresh
        except:
            return False
    
    @staticmethod
    def parse_date(date_string: str) -> datetime:
        """Parse various date formats including relative dates"""
        
        if not date_string:
            return None
        
        try:
            # Handle relative dates like "2 hours ago", "1 day ago", etc.
            relative_match = re.search(
                r'(\d+)\s+(second|minute|hour|day|week|month)s?\s+ago',
                date_string.lower()
            )
            
            if relative_match:
                amount = int(relative_match.group(1))
                unit = relative_match.group(2).lower()
                
                now = datetime.utcnow()
                
                if unit == 'second':
                    return now - timedelta(seconds=amount)
                elif unit == 'minute':
                    return now - timedelta(minutes=amount)
                elif unit == 'hour':
                    return now - timedelta(hours=amount)
                elif unit == 'day':
                    return now - timedelta(days=amount)
                elif unit == 'week':
                    return now - timedelta(weeks=amount)
                elif unit == 'month':
                    return now - timedelta(days=30*amount)
            
            # Try standard date parsers
            parsed = dateutil_parser.parse(date_string, fuzzy=True)
            return parsed
        
        except Exception as e:
            logger.warning(f"Could not parse date: {date_string} - {str(e)}")
            return None
    
    @staticmethod
    def to_iso8601(date_obj: datetime) -> str:
        """Convert to ISO 8601 format"""
        if isinstance(date_obj, str):
            date_obj = DateNormalizer.parse_date(date_obj)
        
        if not date_obj:
            return datetime.utcnow().isoformat() + "Z"
        
        if date_obj.tzinfo:
            return date_obj.isoformat() + "Z"
        else:
            return date_obj.isoformat() + "Z"