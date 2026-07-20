# GraphOne Intelligence Pipeline - Architecture Document

## Executive Summary

This document outlines the technical architecture for the GraphOne AI Intelligence Graph data ingestion pipeline. The system is designed to ingest, normalize, and enrich multi-dimensional datasets from diverse sources worldwide while maintaining data freshness and fidelity.

**Key Metrics:**
- Scalable to 500,000+ records
- 24-hour data freshness guarantee
- Multi-tier LLM fallback for extraction
- Production-grade error handling & logging

---

## 1. System Architecture

### High-Level Data Flow
SOURCE INGESTION → DATA EXTRACTION → NORMALIZATION → ENTITY RESOLUTION → STORAGE
↓                  ↓                 ↓                  ↓               ↓
APIs/RSS      LLM Fallback Chain   JSON Schema    Fuzzy Matching      PostgreSQL
Scrapers      (Gemini/Groq/DS)     Validation     Canonical Mapping   Vector DB
Rate Limit Handling    Type Coercion   Deduplication
### Component Architecture
┌─────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                      │
│  (Phase Controllers: Phase1, Phase2, Phase3, Phase4)        │
└──────────────────────┬──────────────────────────────────────┘
│
┌──────────────┼──────────────┐
↓              ↓              ↓
┌─────────┐  ┌──────────┐  ┌─────────────┐
│ Scrapers│  │LLM Engine│  │ Entity Res. │
│         │  │          │  │             │
│-Arxiv   │  │-Gemini   │  │-Fuzzy Match │
│-GitHub  │  │-Groq     │  │-Canonical   │
│-HF API  │  │-DeepSeek │  │-Dedup       │
└────┬────┘  └────┬─────┘  └────┬────────┘
│            │             │
└────────────┼─────────────┘
↓
┌────────────────────────┐
│  Storage Layer         │
│                        │
│ - JSON (Raw)           │
│ - CSV (Processed)      │
│ - PostgreSQL           │
│ - Vector Embeddings    │
└────────────────────────┘
---

## 2. Data Schema

### Research Paper Entity
```json
{
  "schemaVersion": "1.0",
  "recordType": "RESEARCH_PAPER",
  "content": {
    "title": "string",
    "authors": ["string"],
    "abstract": "string",
    "paper_url": "https://arxiv.org/...",
    "github_url": "https://github.com/...",
    "github_stars": 1234,
    "published_date": "2024-07-19T00:00:00Z"
  },
  "collectedAt": "2024-07-19T14:22:00Z"
}
```

### News Article Entity
```json
{
  "title": "string",
  "url": "string",
  "source": "HackerNews|TechCrunch|Reddit",
  "published_date": "2024-07-19T00:00:00Z",
  "content": "string (first 500 chars)",
  "freshness": "24-hour verified"
}
```

### Job Posting Entity
```json
{
  "title": "string",
  "company": "string",
  "url": "string",
  "published_date": "2024-07-19T00:00:00Z",
  "description": "string (first 500 chars)",
  "is_remote": true,
  "location": "string",
  "freshness": "24-hour verified"
}
```

---

## 3. Handling 413s & 429s

### 413 Payload Too Large

**Problem:** LLM context windows have limits (Gemini: 30K tokens, Groq: 8K)

**Solution - Intelligent Chunking:**
```python
class IntelligentChunker:
    max_tokens = 4000  # Stay under API limits
    
    def chunk_text(text):
        # Split by paragraphs (semantic boundaries)
        # If still too large, split by sentences
        # Preserve metadata in each chunk
```

### 429 Rate Limits

**Problem:** API rate limits trigger when concurrent requests exceed thresholds

**Solution - Exponential Backoff:**
```python
async def extract_with_fallback(prompt, content):
    models = [gemini_flash, groq_llama, deepseek]
    backoff = 1  # Start at 1 second
    
    for model in models:
        try:
            return await model.extract(prompt, content)
        except RateLimitError:
            await asyncio.sleep(backoff)  # Wait
            backoff = min(backoff * 2, 60)  # Cap at 60s
            continue  # Try next model
```

**Rate Limit Awareness:**
- GitHub API: 5000 req/hr (authenticated)
- Groq API: 30 req/min (free tier)
- Gemini Flash: 60 req/min (free tier)
- ArXiv: ~3 req/sec (soft limit, respect User-Agent)

---

## 4. Freshness Tracking

### 24-Hour Freshness Guarantee

**Implementation:**
```python
def is_within_24_hours(date_string):
    parsed_date = parse_date(date_string)  # Handle "2 hours ago"
    now = datetime.utcnow()
    
    return (now - parsed_date).total_seconds() < 86400
```

**Across Distributed Crawlers:**
- Last-run timestamp stored in Redis
- New records compared against previous batch
- Skip duplicates from prior runs
- Track by URL hash to avoid re-processing

---

## 5. Storage Strategy

### Primary Database: PostgreSQL

**Why PostgreSQL:**
- ACID compliance for data integrity
- Full-text search on content
- JSON column type for nested data
- Scalable with connection pooling
- Cost-effective at scale

**Schema:**
```sql
CREATE TABLE records (
  id BIGSERIAL PRIMARY KEY,
  record_type VARCHAR(50),  -- RESEARCH_PAPER, NEWS, JOB
  source_url TEXT,
  source_name VARCHAR(100),
  content JSONB,
  collected_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  INDEX (record_type, collected_at),
  INDEX (source_url)  -- Deduplication
);
```

### Vector/Graph Storage: Weaviate

**Why Weaviate:**
- Vector embeddings for semantic search
- Graph relationships (paper → author → repo)
- Real-time indexing
- Scales horizontally

**Usage:**
Paper embeddings → Find similar papers
Company → Products → GitHub repos
Author → Publications → Cited by
### File Storage: S3

**Backup Strategy:**
- Raw JSON in S3 (immutable archive)
- CSV exports for reporting
- Versioning enabled
- Encryption at rest

---

## 6. Deployment Architecture

### Local Development
graphone-ai-intelligence/
├── src/
│   ├── scrapers/      # Data acquisition
│   ├── llm/          # LLM orchestration
│   ├── entity_resolution/  # Dedup & canonicalization
│   └── processors/   # Storage & logging
├── data/
│   ├── raw/          # Original data
│   └── processed/    # CSV exports
└── phase1-4.py       # Orchestrators
### Production Deployment (AWS)
┌─────────────────┐
                │   API Gateway   │
                └────────┬────────┘
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
     ┌────────┐   ┌────────┐   ┌────────┐
     │  ECS   │   │  ECS   │   │  ECS   │
     │Worker 1│   │Worker 2│   │Worker N│
     └────┬───┘   └────┬───┘   └────┬───┘
          │            │            │
          └────────────┼────────────┘
                       ↓
                ┌─────────────────┐
                │  RDS PostgreSQL │
                │                 │
                │ - Records       │
                │ - Mappings      │
                │ - Audit Log     │
                └─────────────────┘
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
     ┌────────┐  ┌────────┐  ┌────────┐
     │ Redis  │  │ S3     │  │Weaviate│
     │ Queue  │  │ Backup │  │ Vector │
     └────────┘  └────────┘  └────────┘
     ---

## 7. Scalability Analysis

### Current Capacity (Single Instance)
- **Records/hour:** ~500
- **Concurrent requests:** 5
- **Storage:** Unlimited (local disk)
- **Cost:** $0 (local)

### Production Capacity (10 Workers)
- **Records/hour:** ~5,000
- **Concurrent requests:** 50
- **Storage:** PostgreSQL + S3
- **Cost:** ~$100-200/day

### Enterprise Scale (50 Workers)
- **Records/hour:** ~25,000
- **Concurrent requests:** 250
- **Storage:** Distributed PostgreSQL
- **Cost:** ~$500-1000/day

### Path to 500K Records
- **At 5K records/hour:** 100 hours (~4 days continuous)
- **With 50 workers:** ~5 hours total
- **Recommended:** Schedule jobs weekly for freshness

---

## 8. Monitoring & Observability

### Logging
- Structured JSON logs via Loguru
- Levels: INFO, WARNING, ERROR, SUCCESS
- Rotating file logs (500MB per file)

### Metrics to Track
- Records ingested/hour
- API response times
- Rate limit hits
- Error rates by source
- Duplicate detection rate
- Data freshness (% records < 24hrs)

### Alerting
- Slack notifications on errors
- Email for freshness violations
- PagerDuty for critical failures

---

## Conclusion

This architecture provides:
- ✅ Resilient data ingestion (multi-tier fallbacks)
- ✅ Production-grade reliability (error handling, logging)
- ✅ Horizontal scalability (distributed workers)
- ✅ Data quality (deduplication, canonicalization)
- ✅ Freshness guarantees (24-hour verification)
- ✅ Cost efficiency (serverless where possible)

**Next Steps:**
1. Deploy to AWS ECS
2. Set up PostgreSQL + Weaviate
3. Configure monitoring (CloudWatch, Datadog)
4. Run continuous collection jobs
5. Build API layer for GraphQL queries