"""
Local embeddings adapter using sentence-transformers.
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class LocalEmbeddingsAdapter:
    """Adapter for local sentence-transformers embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.dimension = None
        
    def load_model(self):
        """Lazy load the embeddings model."""
        if self.model is None:
            logger.info(f"Loading embeddings model: {self.model_name} on {self.device}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            test_embedding = self.model.encode(["test"])
            self.dimension = test_embedding.shape[1]
            logger.info(f"Embeddings model loaded. Dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text."""
        self.load_model()
        return self.model.encode([text])[0]
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embed multiple texts."""
        self.load_model()
        return self.model.encode(texts)
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        self.load_model()
        return self.dimension
