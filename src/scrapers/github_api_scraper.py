from github import Github
from datetime import datetime, timedelta
from typing import List, Dict
from src.logger import logger
from src.config import config

class GitHubAPIScraper:
    def __init__(self):
        self.name = "GitHubAPI"
        if config.GITHUB_TOKEN:
            self.github = Github(config.GITHUB_TOKEN)
        else:
            self.github = Github()
    
    async def fetch_ai_repos(self, max_results: int = 1000) -> List[Dict]:
        """Fetch top AI repositories from GitHub"""
        repos = []
        
        try:
            # Search for AI/ML repositories with proper syntax
            queries = [
                "machine learning stars:>1000 language:python",
                "deep learning stars:>1000 language:python",
                "neural network stars:>500 language:python",
                "tensorflow stars:>100 language:python",
                "pytorch stars:>100 language:python"
            ]
            
            for query in queries:
                try:
                    search_results = self.github.search_repositories(
                        query=query,
                        sort="stars",
                        order="desc"
                    )
                    
                    for repo in search_results[:200]:  # Get top 200 per query
                        repo_data = {
                            "title": repo.name,
                            "description": repo.description or "No description",
                            "repo_url": repo.html_url,
                            "github_url": repo.html_url,
                            "github_stars": repo.stargazers_count,
                            "language": repo.language,
                            "published_date": repo.created_at.isoformat() + "Z",
                            "source_url": repo.html_url,
                            "source_name": "GitHub",
                            "owner": repo.owner.login
                        }
                        
                        # Check if not already added (avoid duplicates)
                        if not any(r['github_url'] == repo_data['github_url'] for r in repos):
                            repos.append(repo_data)
                        
                        if len(repos) >= max_results:
                            break
                    
                    if len(repos) >= max_results:
                        break
                
                except Exception as e:
                    logger.warning(f"Error with query '{query}': {str(e)}")
                    continue
            
            logger.info(f"✓ Total {len(repos)} AI repos from GitHub")
            return repos[:max_results]
        
        except Exception as e:
            logger.error(f"Error fetching from GitHub: {str(e)}")
            return []