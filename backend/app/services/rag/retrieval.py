"""
RAG retrieval service for querying brand knowledge.
"""
from typing import List, Dict, Optional
import logging

from app import config

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving relevant brand information."""
    
    def __init__(self, vector_adapter, db):
        self.vector_adapter = vector_adapter
        self.db = db
        self.top_k = config.RAG_TOP_K
    
    def retrieve(self, brand_id: str, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Retrieve relevant chunks for a brand and query.
        Returns list of dicts with chunk text, metadata, and scores.
        """
        if top_k is None:
            top_k = self.top_k
        
        logger.info(f"Retrieving top {top_k} chunks for brand: {brand_id}, query: {query[:50]}...")
        
        results = self.vector_adapter.search(brand_id, query, top_k)
        
        logger.info(f"Retrieved {len(results)} chunks")
        
        return results
    
    def get_brand_context(self, brand_id: str, query: Optional[str] = None, top_k: Optional[int] = None) -> str:
        """
        Get brand context as a formatted string.
        If query is provided, retrieves relevant chunks.
        Otherwise, returns all brand metadata.
        """
        if query:
            results = self.retrieve(brand_id, query, top_k)
            
            if not results:
                return ""
            
            context_parts = []
            for i, result in enumerate(results, 1):
                text = result.get('text', '')
                score = result.get('score', 0)
                context_parts.append(f"[{i}] (relevance: {score:.2f})\n{text}")
            
            return "\n\n".join(context_parts)
        else:
            all_data = self.vector_adapter.get_all_texts(brand_id)
            
            if not all_data:
                return ""
            
            context_parts = []
            for item in all_data:
                text = item.get('text', '')
                context_parts.append(text)
            
            return "\n".join(context_parts)
    
    def get_brand_metadata_dict(self, brand_id: str) -> Dict[str, str]:
        """
        Get brand metadata as a key-value dictionary.
        Useful for structured brand attributes.
        """
        all_data = self.vector_adapter.get_all_texts(brand_id)
        
        metadata = {}
        for item in all_data:
            text = item.get('text', '')
            if ':' in text:
                parts = text.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower().replace(' ', '_')
                    value = parts[1].strip()
                    metadata[key] = value
        
        return metadata
