from github import Github
from src.logger import logger
from src.config import config
from typing import Optional

class GitHubProcessor:
    def __init__(self):
        if config.GITHUB_TOKEN:
            self.github = Github(config.GITHUB_TOKEN)
        else:
            logger.warning("No GitHub token provided - rate limits will be low")
            self.github = Github()
    
    def get_repo_stars(self, github_url: str) -> Optional[int]:
        """Extract GitHub stars count from repo"""
        try:
            if not github_url or 'github.com' not in github_url:
                return None
            
            # Parse owner/repo from URL
            parts = github_url.strip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            repo_obj = self.github.get_repo(f"{owner}/{repo}")
            stars = repo_obj.stargazers_count
            
            logger.info(f"✓ {owner}/{repo}: {stars} stars")
            return stars
        
        except Exception as e:
            logger.error(f"Error fetching stars for {github_url}: {str(e)}")
            return None
    
    def enrich_papers_with_github_stars(self, papers: list) -> list:
        """Add GitHub stars to paper data"""
        for paper in papers:
            if paper.get('github_url'):
                stars = self.get_repo_stars(paper['github_url'])
                paper['github_stars'] = stars or 0
        
        return papers