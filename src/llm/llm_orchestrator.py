import asyncio
import time
from typing import Optional, Dict, List
from src.logger import logger
import google.generativeai as genai
from groq import Groq
import openai

class LLMOrchestrator:
    """Multi-tier LLM fallback chain with rate limit handling"""
    
    def __init__(self):
        # Initialize APIs
        self.gemini_key = "AIzaSyDJxxx"  # Will override with env
        self.groq_key = "gsk_xxx"  # Will override with env
        self.deepseek_key = "sk_xxx"  # Will override with env
        
        self.rate_limit_backoff = 1  # Start with 1 second
        self.max_backoff = 60  # Max 60 seconds
        
    def set_api_keys(self, gemini_key: str, groq_key: str, deepseek_key: str):
        """Set API keys"""
        self.gemini_key = gemini_key
        self.groq_key = groq_key
        self.deepseek_key = deepseek_key
        
        if gemini_key:
            genai.configure(api_key=gemini_key)
        
    async def extract_with_gemini(self, prompt: str, content: str) -> Optional[Dict]:
        """Try extraction with Gemini Flash"""
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            full_prompt = f"{prompt}\n\nContent to extract:\n{content}"
            
            response = await asyncio.to_thread(
                model.generate_content,
                full_prompt
            )
            
            logger.info("✓ Gemini Flash extraction successful")
            return {"model": "gemini", "response": response.text}
        
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                logger.warning(f"⚠ Gemini rate limit hit. Fallback to Groq.")
                await asyncio.sleep(self.rate_limit_backoff)
                self.rate_limit_backoff = min(self.rate_limit_backoff * 2, self.max_backoff)
            else:
                logger.warning(f"⚠ Gemini error: {str(e)}")
            
            return None
    
    async def extract_with_groq(self, prompt: str, content: str) -> Optional[Dict]:
        """Try extraction with Groq Llama 3"""
        try:
            client = Groq(api_key=self.groq_key)
            
            full_prompt = f"{prompt}\n\nContent to extract:\n{content}"
            
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3-70b-8192",
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            logger.info("✓ Groq Llama 3 extraction successful")
            return {"model": "groq", "response": response.choices[0].message.content}
        
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                logger.warning(f"⚠ Groq rate limit hit. Fallback to DeepSeek.")
                await asyncio.sleep(self.rate_limit_backoff)
                self.rate_limit_backoff = min(self.rate_limit_backoff * 2, self.max_backoff)
            else:
                logger.warning(f"⚠ Groq error: {str(e)}")
            
            return None
    
    async def extract_with_deepseek(self, prompt: str, content: str) -> Optional[Dict]:
        """Try extraction with DeepSeek (final fallback)"""
        try:
            client = openai.AsyncOpenAI(
                api_key=self.deepseek_key,
                base_url="https://api.deepseek.com"
            )
            
            full_prompt = f"{prompt}\n\nContent to extract:\n{content}"
            
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            logger.info("✓ DeepSeek extraction successful")
            return {"model": "deepseek", "response": response.choices[0].message.content}
        
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                logger.warning(f"⚠ DeepSeek rate limit hit. All fallbacks exhausted.")
                await asyncio.sleep(self.rate_limit_backoff)
            else:
                logger.warning(f"⚠ DeepSeek error: {str(e)}")
            
            return None
    
    async def extract_with_fallback(self, prompt: str, content: str) -> Optional[Dict]:
        """Try LLMs in fallback chain"""
        
        logger.info("🔄 Starting LLM fallback chain...")
        
        # Try Gemini
        result = await self.extract_with_gemini(prompt, content)
        if result:
            return result
        
        # Try Groq
        result = await self.extract_with_groq(prompt, content)
        if result:
            return result
        
        # Try DeepSeek
        result = await self.extract_with_deepseek(prompt, content)
        if result:
            return result
        
        logger.error("❌ All LLM fallbacks exhausted!")
        return None