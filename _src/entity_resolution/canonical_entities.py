# Seed list of known canonical AI entities
CANONICAL_ENTITIES = {
    # Companies
    "openai": ["OpenAI", "Open AI", "OpenAI Inc", "openai.com"],
    "deepmind": ["DeepMind", "Deep Mind", "Google DeepMind"],
    "anthropic": ["Anthropic", "anthropic.com"],
    "meta": ["Meta", "Facebook AI", "Meta AI"],
    "google": ["Google", "Google AI", "Alphabet"],
    "microsoft": ["Microsoft", "Microsoft Research", "MSFT"],
    "nvidia": ["NVIDIA", "Nvidia", "NVDA"],
    "tesla": ["Tesla", "Tesla AI"],
    "huggingface": ["Hugging Face", "HuggingFace", "huggingface.co"],
    "stability_ai": ["Stability AI", "StabilityAI"],
    "midjourney": ["Midjourney", "Mid-journey"],
    "elevenlabs": ["ElevenLabs", "Eleven Labs"],
    "databricks": ["Databricks", "databricks.com"],
    "scale_ai": ["Scale AI", "ScaleAI"],
    "together_ai": ["Together AI", "TogetherAI"],
    "groq": ["Groq", "groq.com"],
    "cohere": ["Cohere", "cohere.ai"],
    "aleph_alpha": ["Aleph Alpha", "AlephAlpha"],
    "perplexity": ["Perplexity", "Perplexity AI"],
    "pinecone": ["Pinecone", "pinecone.io"],
    "weaviate": ["Weaviate", "weaviate.io"],
    "milvus": ["Milvus", "milvus.io"],
    "langchain": ["LangChain", "langchain.com"],
    "llamaindex": ["LlamaIndex", "Llama Index"],
    
    # Research Papers / Projects
    "transformer": ["Transformer", "Transformers", "attention is all you need"],
    "bert": ["BERT", "Bidirectional Encoder Representations"],
    "gpt": ["GPT", "Generative Pre-trained Transformer"],
    "diffusion_models": ["Diffusion Models", "Diffusion Model", "DDPM"],
    "stable_diffusion": ["Stable Diffusion", "StableDiffusion"],
    "clip": ["CLIP", "Contrastive Language-Image"],
    "vit": ["ViT", "Vision Transformer", "visual transformer"],
    "resnet": ["ResNet", "Residual Networks"],
}

def get_canonical_name(entity_name: str, entity_type: str = "company") -> str:
    """Get canonical name for an entity"""
    
    if not entity_name:
        return None
    
    entity_lower = entity_name.lower().strip()
    
    # Check exact matches in canonical list
    for canonical, variations in CANONICAL_ENTITIES.items():
        if entity_lower == canonical.lower():
            return canonical
        
        for variation in variations:
            if entity_lower == variation.lower():
                return canonical
    
    # Return original if no match found
    return entity_name