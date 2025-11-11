"""
FAISS vector store adapter for local vector search.
"""
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class FAISSVectorAdapter:
    """Adapter for FAISS vector store with brand-scoped indices."""
    
    def __init__(self, embeddings_adapter, persist_dir: Path):
        self.embeddings_adapter = embeddings_adapter
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.indices: Dict[str, faiss.Index] = {}
        self.metadata: Dict[str, List[Dict]] = {}
        
        self._load_indices()
    
    def _get_index_path(self, brand_id: str) -> Path:
        """Get path for brand index file."""
        return self.persist_dir / f"{brand_id}.index"
    
    def _get_metadata_path(self, brand_id: str) -> Path:
        """Get path for brand metadata file."""
        return self.persist_dir / f"{brand_id}.metadata"
    
    def _load_indices(self):
        """Load all existing indices from disk."""
        for index_file in self.persist_dir.glob("*.index"):
            brand_id = index_file.stem
            try:
                self.indices[brand_id] = faiss.read_index(str(index_file))
                metadata_file = self._get_metadata_path(brand_id)
                if metadata_file.exists():
                    with open(metadata_file, 'rb') as f:
                        self.metadata[brand_id] = pickle.load(f)
                else:
                    self.metadata[brand_id] = []
                logger.info(f"Loaded FAISS index for brand: {brand_id}")
            except Exception as e:
                logger.error(f"Error loading index for {brand_id}: {e}")
    
    def _save_index(self, brand_id: str):
        """Save brand index to disk."""
        if brand_id in self.indices:
            faiss.write_index(self.indices[brand_id], str(self._get_index_path(brand_id)))
            with open(self._get_metadata_path(brand_id), 'wb') as f:
                pickle.dump(self.metadata[brand_id], f)
            logger.info(f"Saved FAISS index for brand: {brand_id}")
    
    def add_texts(self, brand_id: str, texts: List[str], metadatas: List[Dict]) -> List[int]:
        """Add texts to brand-specific index."""
        if len(texts) != len(metadatas):
            raise ValueError("texts and metadatas must have same length")
        
        embeddings = self.embeddings_adapter.embed_texts(texts)
        
        if brand_id not in self.indices:
            dimension = self.embeddings_adapter.get_dimension()
            self.indices[brand_id] = faiss.IndexFlatL2(dimension)
            self.metadata[brand_id] = []
        
        start_idx = self.indices[brand_id].ntotal
        self.indices[brand_id].add(embeddings.astype('float32'))
        
        for i, meta in enumerate(metadatas):
            meta['vector_index'] = start_idx + i
            self.metadata[brand_id].append(meta)
        
        self._save_index(brand_id)
        
        return list(range(start_idx, start_idx + len(texts)))
    
    def search(self, brand_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar texts in brand-specific index."""
        if brand_id not in self.indices:
            return []
        
        query_embedding = self.embeddings_adapter.embed_text(query)
        
        distances, indices = self.indices[brand_id].search(
            query_embedding.reshape(1, -1).astype('float32'), 
            min(top_k, self.indices[brand_id].ntotal)
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata[brand_id]):
                result = self.metadata[brand_id][idx].copy()
                result['distance'] = float(distances[0][i])
                result['score'] = 1.0 / (1.0 + float(distances[0][i]))  # Convert distance to similarity score
                results.append(result)
        
        return results
    
    def get_all_texts(self, brand_id: str) -> List[Dict]:
        """Get all texts and metadata for a brand."""
        if brand_id not in self.metadata:
            return []
        return self.metadata[brand_id].copy()
    
    def delete_brand(self, brand_id: str) -> bool:
        """Delete all data for a brand."""
        if brand_id in self.indices:
            del self.indices[brand_id]
            del self.metadata[brand_id]
            
            index_path = self._get_index_path(brand_id)
            metadata_path = self._get_metadata_path(brand_id)
            
            if index_path.exists():
                index_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            
            logger.info(f"Deleted FAISS index for brand: {brand_id}")
            return True
        return False
    
    def list_brands(self) -> List[str]:
        """List all brands with indices."""
        return sorted(list(self.indices.keys()))
    
    def get_stats(self, brand_id: str) -> Dict:
        """Get statistics for a brand index."""
        if brand_id not in self.indices:
            return {"exists": False}
        
        return {
            "exists": True,
            "total_vectors": self.indices[brand_id].ntotal,
            "dimension": self.indices[brand_id].d,
            "metadata_count": len(self.metadata[brand_id])
        }
