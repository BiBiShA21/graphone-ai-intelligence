from typing import List, Dict
from src.logger import logger

class IntelligentChunker:
    """Split content into chunks while preserving semantic meaning"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        # Rough estimate: 1 token ≈ 4 characters
        self.max_chars = max_tokens * 4
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text) // 4
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into semantic chunks"""
        
        if len(text) <= self.max_chars:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first (preserve semantic meaning)
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            # If single paragraph is too large, split by sentences
            if len(para) > self.max_chars:
                para = self._chunk_by_sentences(para)
            else:
                para = [para]
            
            for sentence_chunk in para:
                if len(current_chunk) + len(sentence_chunk) <= self.max_chars:
                    current_chunk += sentence_chunk + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence_chunk + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"📦 Chunked content into {len(chunks)} pieces (max {self.max_chars} chars each)")
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Split by sentences when paragraph is too large"""
        import re
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) <= self.max_chars:
                current += sentence + " "
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence + " "
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def chunk_dict(self, data: Dict) -> List[Dict]:
        """Chunk dictionary content"""
        chunks = []
        
        # Extract main text fields
        main_content = ""
        for key in ["content", "description", "body", "summary"]:
            if key in data and data[key]:
                main_content += f"[{key.upper()}]\n{data[key]}\n\n"
        
        if not main_content:
            return [data]
        
        # Chunk the content
        content_chunks = self.chunk_text(main_content)
        
        # Create chunk objects with metadata
        for i, chunk in enumerate(content_chunks):
            chunk_data = data.copy()
            chunk_data["_content_chunk"] = chunk
            chunk_data["_chunk_index"] = i
            chunk_data["_total_chunks"] = len(content_chunks)
            chunks.append(chunk_data)
        
        return chunks