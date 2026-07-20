EXTRACTION_PROMPTS = {
    "research_paper": """
Extract structured data from this research paper information. Return ONLY valid JSON (no markdown, no backticks).

Return this exact JSON structure:
{
  "title": "paper title",
  "authors": ["author1", "author2"],
  "abstract": "brief summary",
  "key_findings": ["finding1", "finding2"],
  "methodology": "description of methodology",
  "dataset_used": "dataset name if mentioned",
  "github_url": "github url if mentioned",
  "arxiv_id": "arxiv ID if available",
  "publication_date": "YYYY-MM-DD",
  "citations": 0,
  "relevance_score": 0.85
}

Be strict: only include data that is explicitly mentioned. Use null for missing fields.
""",
    
    "news_article": """
Extract structured data from this news article. Return ONLY valid JSON (no markdown, no backticks).

Return this exact JSON structure:
{
  "title": "article title",
  "source": "news source name",
  "url": "article url",
  "published_date": "YYYY-MM-DD",
  "summary": "2-3 sentence summary",
  "main_topics": ["topic1", "topic2"],
  "companies_mentioned": ["company1", "company2"],
  "key_quotes": ["quote1"],
  "sentiment": "positive/neutral/negative",
  "impact_level": "high/medium/low"
}

Be strict: only include data that is explicitly mentioned.
""",
    
    "job_posting": """
Extract structured data from this job posting. Return ONLY valid JSON (no markdown, no backticks).

Return this exact JSON structure:
{
  "title": "job title",
  "company": "company name",
  "url": "job url",
  "posted_date": "YYYY-MM-DD",
  "description": "full description",
  "required_skills": ["skill1", "skill2"],
  "salary_range": "$X - $Y or null",
  "location": "location or Remote",
  "employment_type": "Full-time/Contract/Startup",
  "seniority_level": "Junior/Mid/Senior",
  "company_stage": "Seed/Series A/Established",
  "remote_friendly": true/false
}

Be strict: only include data that is explicitly mentioned.
""",
    
    "startup": """
Extract structured data about this startup. Return ONLY valid JSON (no markdown, no backticks).

Return this exact JSON structure:
{
  "name": "startup name",
  "description": "what they do",
  "founded_year": 2024,
  "founders": ["founder1", "founder2"],
  "location": "city, country",
  "funding_stage": "Seed/Series A/Series B",
  "total_funding": "amount in USD or null",
  "website": "url",
  "github_url": "url if available",
  "ai_focus": true/false,
  "primary_product": "product name",
  "market": "target market"
}

Be strict: only include data that is explicitly mentioned.
"""
}

def get_extraction_prompt(entity_type: str) -> str:
    """Get extraction prompt for entity type"""
    return EXTRACTION_PROMPTS.get(entity_type, EXTRACTION_PROMPTS["startup"])