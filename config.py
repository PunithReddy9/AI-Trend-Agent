# config.py
"""
Configuration file for AI News Aggregation Pipeline
"""

import os
from typing import Dict, List

class Config:
    """Application configuration"""
    
    # Ollama Configuration
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "llama3.1:8b"
    OLLAMA_TEMPERATURE = 0.3
    
    # ChromaDB Configuration
    VECTOR_DB_PATH = "./vectordb"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    COLLECTION_NAME = "ai_news_articles"
    
    # Data Sources Configuration
    NEWS_SOURCES = {
        'kdnuggets': {
            'url': 'https://www.kdnuggets.com/',
            'enabled': True
        },
        'ai_news': {
            'url': 'https://artificialintelligence-news.com/',
            'enabled': True
        },
        'the_new_stack': {
            'url': 'https://thenewstack.io/ai/',
            'enabled': True
        }
    }
    
    # Processing Configuration
    MIN_QUALITY_SCORE = 4.0
    MAX_ARTICLES_TO_PROCESS = 50
    TOP_ARTICLES_COUNT = 15
    SIMILARITY_THRESHOLD = 0.7
    
    # Output Configuration
    DATA_DIR = "data"
    OUTPUT_DIR = "outputs"
    LOGS_DIR = "logs"
    
    # Directories to create
    REQUIRED_DIRECTORIES = [DATA_DIR, OUTPUT_DIR, LOGS_DIR, "vectordb"]
    
    @classmethod
    def get_enabled_sources(cls) -> Dict[str, Dict]:
        """Get only enabled news sources"""
        return {
            name: config for name, config in cls.NEWS_SOURCES.items() 
            if config.get('enabled', True)
        }
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check if at least one source is enabled
        enabled_sources = cls.get_enabled_sources()
        if not enabled_sources:
            issues.append("No news sources are enabled")
        
        # Check Ollama model
        if not cls.OLLAMA_MODEL:
            issues.append("Ollama model not specified")
        
        return issues
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("🔧 Current Configuration:")
        print(f"   • Ollama Model: {cls.OLLAMA_MODEL}")
        print(f"   • Vector DB Path: {cls.VECTOR_DB_PATH}")
        print(f"   • Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"   • Enabled Sources: {list(cls.get_enabled_sources().keys())}")
        print(f"   • Quality Threshold: {cls.MIN_QUALITY_SCORE}")
        print(f"   • Max Articles: {cls.MAX_ARTICLES_TO_PROCESS}")

# Quality scoring criteria
QUALITY_CRITERIA = {
    'technical_accuracy': 0.25,
    'relevance_to_ai': 0.30,
    'content_freshness': 0.20,
    'source_credibility': 0.15,
    'practical_value': 0.10
}

# Trend detection keywords
AI_KEYWORDS = [
    'GPT', 'LLM', 'Large Language Model', 'ChatGPT', 'OpenAI',
    'machine learning', 'deep learning', 'neural network',
    'transformer', 'AI model', 'artificial intelligence',
    'computer vision', 'natural language processing', 'NLP',
    'reinforcement learning', 'generative AI', 'AGI',
    'AI ethics', 'AI safety', 'MLOps', 'AutoML'
]