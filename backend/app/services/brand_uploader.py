"""
Brand Data Upload and Ingestion Service
Supports CSV, XLSX, PDF, and TXT files
"""

import os
import io
from pathlib import Path
from typing import List, Dict, Any, Optional, BinaryIO
import pandas as pd
import pymupdf  # PyMuPDF
from .faiss_rag import FAISSRAGService

class BrandUploader:
    """Service for uploading and ingesting brand data"""
    
    def __init__(self):
        self.rag_service = FAISSRAGService()
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.ingest_dir = self.data_dir / "ingest"
        self.ingest_dir.mkdir(parents=True, exist_ok=True)
    
    def process_csv_xlsx(
        self,
        file_content: bytes,
        filename: str,
        brand_col: str = "brand",
        text_col: str = "text"
    ) -> Dict[str, Any]:
        """
        Process CSV or XLSX file with brand metadata
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            brand_col: Column name for brand identifier
            text_col: Column name for text/details
        
        Returns:
            Dict with ingestion stats
        """
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file type: {filename}")
            
            df.columns = df.columns.str.lower().str.strip()
            brand_col = brand_col.lower().strip()
            text_col = text_col.lower().strip()
            
            if brand_col not in df.columns:
                possible_cols = [col for col in df.columns if 'brand' in col]
                if possible_cols:
                    brand_col = possible_cols[0]
                else:
                    raise ValueError(f"Brand column '{brand_col}' not found. Available columns: {list(df.columns)}")
            
            if text_col not in df.columns:
                possible_cols = [col for col in df.columns if any(word in col for word in ['text', 'detail', 'description', 'content'])]
                if possible_cols:
                    text_col = possible_cols[0]
                else:
                    raise ValueError(f"Text column '{text_col}' not found. Available columns: {list(df.columns)}")
            
            brands_processed = []
            total_records = 0
            
            for brand_name, group in df.groupby(brand_col):
                brand_name = str(brand_name).strip()
                if not brand_name or brand_name.lower() == 'nan':
                    continue
                
                texts = group[text_col].dropna().astype(str).tolist()
                
                if not texts:
                    continue
                
                metadata = []
                for _, row in group.iterrows():
                    meta = {
                        "brand": brand_name,
                        "source": filename
                    }
                    for col in df.columns:
                        if col not in [brand_col, text_col]:
                            meta[col] = str(row[col])
                    metadata.append(meta)
                
                chunked_texts = []
                chunked_metadata = []
                for text, meta in zip(texts, metadata):
                    chunks = self.rag_service.chunk_text(text, chunk_size=500, overlap=50)
                    chunked_texts.extend(chunks)
                    chunked_metadata.extend([meta] * len(chunks))
                
                stats = self.rag_service.create_or_update_index(
                    brand_id=brand_name,
                    texts=chunked_texts,
                    metadata=chunked_metadata
                )
                
                brands_processed.append(brand_name)
                total_records += len(texts)
                
                brand_dir = self.ingest_dir / brand_name
                brand_dir.mkdir(parents=True, exist_ok=True)
                
                with open(brand_dir / filename, "wb") as f:
                    f.write(file_content)
            
            return {
                "status": "success",
                "brands_count": len(brands_processed),
                "brands": brands_processed,
                "records_ingested": total_records,
                "filename": filename
            }
        
        except Exception as e:
            raise Exception(f"Failed to process CSV/XLSX: {str(e)}")
    
    def process_pdf(
        self,
        file_content: bytes,
        filename: str,
        brand_name: str
    ) -> Dict[str, Any]:
        """
        Process PDF file for a specific brand
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            brand_name: Brand identifier
        
        Returns:
            Dict with ingestion stats
        """
        try:
            doc = pymupdf.open(stream=file_content, filetype="pdf")
            
            texts = []
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    texts.append(text.strip())
            
            doc.close()
            
            if not texts:
                raise ValueError("No text content found in PDF")
            
            chunked_texts = []
            for text in texts:
                chunks = self.rag_service.chunk_text(text, chunk_size=500, overlap=50)
                chunked_texts.extend(chunks)
            
            metadata = [{"brand": brand_name, "source": filename, "type": "pdf"}] * len(chunked_texts)
            
            stats = self.rag_service.create_or_update_index(
                brand_id=brand_name,
                texts=chunked_texts,
                metadata=metadata
            )
            
            brand_dir = self.ingest_dir / brand_name
            brand_dir.mkdir(parents=True, exist_ok=True)
            
            with open(brand_dir / filename, "wb") as f:
                f.write(file_content)
            
            return {
                "status": "success",
                "brand_name": brand_name,
                "records_ingested": len(chunked_texts),
                "pages": len(texts),
                "filename": filename
            }
        
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def process_txt(
        self,
        file_content: bytes,
        filename: str,
        brand_name: str
    ) -> Dict[str, Any]:
        """
        Process TXT file for a specific brand
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            brand_name: Brand identifier
        
        Returns:
            Dict with ingestion stats
        """
        try:
            text = file_content.decode('utf-8')
            
            if not text.strip():
                raise ValueError("Empty text file")
            
            chunked_texts = self.rag_service.chunk_text(text, chunk_size=500, overlap=50)
            
            metadata = [{"brand": brand_name, "source": filename, "type": "txt"}] * len(chunked_texts)
            
            stats = self.rag_service.create_or_update_index(
                brand_id=brand_name,
                texts=chunked_texts,
                metadata=metadata
            )
            
            brand_dir = self.ingest_dir / brand_name
            brand_dir.mkdir(parents=True, exist_ok=True)
            
            with open(brand_dir / filename, "wb") as f:
                f.write(file_content)
            
            return {
                "status": "success",
                "brand_name": brand_name,
                "records_ingested": len(chunked_texts),
                "filename": filename
            }
        
        except Exception as e:
            raise Exception(f"Failed to process TXT: {str(e)}")
