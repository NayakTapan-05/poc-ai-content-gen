import chromadb
from chromadb.config import Settings
import pandas as pd
from typing import List, Dict, Optional
import os

class VectorDBService:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="brand_metadata",
            metadata={"description": "Brand DNA metadata for RAG pipeline"}
        )
    
    def ingest_brand_metadata(self, csv_path: str, brand_name: str):
        """
        Ingest brand metadata from CSV file into ChromaDB.
        Expected CSV format: brand_key, brand_value
        """
        df = pd.read_csv(csv_path)
        
        if len(df.columns) != 2:
            raise ValueError("CSV must have exactly 2 columns: brand_key, brand_value")
        
        df.columns = ['brand_key', 'brand_value']
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in df.iterrows():
            brand_key = str(row['brand_key']).strip()
            brand_value = str(row['brand_value']).strip()
            
            doc_text = f"{brand_key}: {brand_value}"
            documents.append(doc_text)
            
            metadatas.append({
                "brand_name": brand_name,
                "brand_key": brand_key,
                "brand_value": brand_value
            })
            
            ids.append(f"{brand_name}_{idx}")
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(documents)
    
    def ingest_brand_metadata_excel(self, excel_path: str, brand_name: str):
        """
        Ingest brand metadata from Excel file into ChromaDB.
        Expected Excel format: brand_key, brand_value
        """
        df = pd.read_excel(excel_path)
        
        if len(df.columns) != 2:
            raise ValueError("Excel must have exactly 2 columns: brand_key, brand_value")
        
        df.columns = ['brand_key', 'brand_value']
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in df.iterrows():
            brand_key = str(row['brand_key']).strip()
            brand_value = str(row['brand_value']).strip()
            
            doc_text = f"{brand_key}: {brand_value}"
            documents.append(doc_text)
            
            metadatas.append({
                "brand_name": brand_name,
                "brand_key": brand_key,
                "brand_value": brand_value
            })
            
            ids.append(f"{brand_name}_{idx}")
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(documents)
    
    def retrieve_brand_metadata(self, brand_name: str, n_results: int = 50) -> Dict[str, str]:
        """
        Retrieve all metadata for a specific brand.
        Returns a dictionary of brand_key: brand_value pairs.
        """
        results = self.collection.get(
            where={"brand_name": brand_name}
        )
        
        if not results or not results['metadatas']:
            return {}
        
        brand_data = {}
        for metadata in results['metadatas']:
            brand_key = metadata.get('brand_key', '')
            brand_value = metadata.get('brand_value', '')
            if brand_key and brand_value:
                brand_data[brand_key] = brand_value
        
        return brand_data
    
    def search_brand_metadata(self, query: str, brand_name: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """
        Search brand metadata using semantic search.
        """
        where_filter = {"brand_name": brand_name} if brand_name else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        if not results or not results['metadatas']:
            return []
        
        search_results = []
        for i, metadata in enumerate(results['metadatas'][0]):
            search_results.append({
                "brand_name": metadata.get('brand_name', ''),
                "brand_key": metadata.get('brand_key', ''),
                "brand_value": metadata.get('brand_value', ''),
                "distance": results['distances'][0][i] if results.get('distances') else None
            })
        
        return search_results
    
    def list_brands(self) -> List[str]:
        """
        List all brands in the vector database.
        """
        results = self.collection.get()
        
        if not results or not results['metadatas']:
            return []
        
        brands = set()
        for metadata in results['metadatas']:
            brand_name = metadata.get('brand_name', '')
            if brand_name:
                brands.add(brand_name)
        
        return sorted(list(brands))
    
    def delete_brand(self, brand_name: str):
        """
        Delete all metadata for a specific brand.
        """
        results = self.collection.get(
            where={"brand_name": brand_name}
        )
        
        if results and results['ids']:
            self.collection.delete(ids=results['ids'])
            return len(results['ids'])
        
        return 0

vector_db = VectorDBService()
