"""
FAISS-based RAG Pipeline with Hugging Face Embeddings
Brand-scoped vector storage and retrieval
"""

import os
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from huggingface_hub import InferenceClient
import pickle
import json
from datetime import datetime

class FAISSRAGService:
    """FAISS-based RAG service with HF embeddings"""
    
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        if not self.hf_token:
            raise ValueError("HF_TOKEN environment variable not set")
        
        self.client = InferenceClient(token=self.hf_token)
        self.embedding_model = "intfloat/e5-small-v2"
        
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.vectors_dir = self.data_dir / "vectors"
        self.ingest_dir = self.data_dir / "ingest"
        self.vectors_dir.mkdir(parents=True, exist_ok=True)
        self.ingest_dir.mkdir(parents=True, exist_ok=True)
        
        self.indices_cache: Dict[str, Dict[str, Any]] = {}
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text using HF Inference API
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector as numpy array
        """
        try:
            response = self.client.feature_extraction(
                text=text,
                model=self.embedding_model
            )
            
            if isinstance(response, list):
                embedding = np.array(response, dtype=np.float32)
            else:
                embedding = np.array(response, dtype=np.float32)
            
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
        
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")
    
    def create_or_update_index(
        self,
        brand_id: str,
        texts: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create or update FAISS index for a brand
        
        Args:
            brand_id: Brand identifier
            texts: List of text chunks to index
            metadata: Optional metadata for each text chunk
        
        Returns:
            Stats about the indexing operation
        """
        try:
            embeddings = []
            for text in texts:
                emb = self.get_embedding(text)
                embeddings.append(emb)
            
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            index_path = self.vectors_dir / f"{brand_id}.index"
            metadata_path = self.vectors_dir / f"{brand_id}_metadata.pkl"
            
            if index_path.exists():
                index = faiss.read_index(str(index_path))
                
                with open(metadata_path, "rb") as f:
                    existing_metadata = pickle.load(f)
                
                index.add(embeddings_array)
                
                if metadata:
                    existing_metadata["texts"].extend(texts)
                    existing_metadata["metadata"].extend(metadata)
                else:
                    existing_metadata["texts"].extend(texts)
                    existing_metadata["metadata"].extend([{}] * len(texts))
                
                existing_metadata["last_updated"] = datetime.now().isoformat()
                existing_metadata["vector_count"] = index.ntotal
                
                with open(metadata_path, "wb") as f:
                    pickle.dump(existing_metadata, f)
                
                stats = {
                    "brand_id": brand_id,
                    "vectors_added": len(texts),
                    "total_vectors": index.ntotal,
                    "last_updated": existing_metadata["last_updated"]
                }
            
            else:
                dimension = embeddings_array.shape[1]
                index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
                index.add(embeddings_array)
                
                index_metadata = {
                    "brand_id": brand_id,
                    "texts": texts,
                    "metadata": metadata if metadata else [{}] * len(texts),
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "vector_count": index.ntotal,
                    "dimension": dimension
                }
                
                with open(metadata_path, "wb") as f:
                    pickle.dump(index_metadata, f)
                
                stats = {
                    "brand_id": brand_id,
                    "vectors_added": len(texts),
                    "total_vectors": index.ntotal,
                    "created_at": index_metadata["created_at"]
                }
            
            faiss.write_index(index, str(index_path))
            
            self.indices_cache[brand_id] = {
                "index": index,
                "metadata": index_metadata if not index_path.exists() else existing_metadata
            }
            
            return stats
        
        except Exception as e:
            raise Exception(f"Failed to create/update index: {str(e)}")
    
    def search(
        self,
        brand_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant texts in brand index
        
        Args:
            brand_id: Brand identifier
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of results with text, score, and metadata
        """
        try:
            if brand_id not in self.indices_cache:
                index_path = self.vectors_dir / f"{brand_id}.index"
                metadata_path = self.vectors_dir / f"{brand_id}_metadata.pkl"
                
                if not index_path.exists():
                    return []
                
                index = faiss.read_index(str(index_path))
                
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)
                
                self.indices_cache[brand_id] = {
                    "index": index,
                    "metadata": metadata
                }
            
            query_embedding = self.get_embedding(query)
            query_embedding = query_embedding.reshape(1, -1)
            
            index = self.indices_cache[brand_id]["index"]
            metadata = self.indices_cache[brand_id]["metadata"]
            
            scores, indices = index.search(query_embedding, min(top_k, index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(metadata["texts"]):
                    results.append({
                        "text": metadata["texts"][idx],
                        "score": float(score),
                        "metadata": metadata["metadata"][idx] if idx < len(metadata["metadata"]) else {}
                    })
            
            return results
        
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    def get_brand_stats(self, brand_id: str) -> Dict[str, Any]:
        """
        Get statistics for a brand's index
        
        Args:
            brand_id: Brand identifier
        
        Returns:
            Stats dictionary
        """
        try:
            metadata_path = self.vectors_dir / f"{brand_id}_metadata.pkl"
            
            if not metadata_path.exists():
                return {
                    "brand_id": brand_id,
                    "exists": False
                }
            
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            
            return {
                "brand_id": brand_id,
                "exists": True,
                "vector_count": metadata.get("vector_count", 0),
                "document_count": len(metadata.get("texts", [])),
                "created_at": metadata.get("created_at"),
                "last_updated": metadata.get("last_updated"),
                "dimension": metadata.get("dimension")
            }
        
        except Exception as e:
            raise Exception(f"Failed to get stats: {str(e)}")
    
    def list_brands(self) -> List[str]:
        """
        List all brands with indices
        
        Returns:
            List of brand IDs
        """
        try:
            brands = []
            for index_file in self.vectors_dir.glob("*.index"):
                brand_id = index_file.stem
                brands.append(brand_id)
            
            return sorted(brands)
        
        except Exception as e:
            raise Exception(f"Failed to list brands: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start += chunk_size - overlap
        
        return chunks
