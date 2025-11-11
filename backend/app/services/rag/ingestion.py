"""
RAG ingestion service for processing and storing documents.
"""
import uuid
from pathlib import Path
from typing import List, Dict, Optional
import logging
import pandas as pd
import fitz  # PyMuPDF
from docx import Document as DocxDocument

from app import config

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting documents into the RAG pipeline."""
    
    def __init__(self, vector_adapter, db):
        self.vector_adapter = vector_adapter
        self.db = db
        self.chunk_size = config.RAG_CHUNK_SIZE
        self.chunk_overlap = config.RAG_CHUNK_OVERLAP
    
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return ""
    
    def _extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            return ""
    
    def _extract_text_from_csv(self, file_path: Path) -> str:
        """Extract text from CSV file (brand metadata format)."""
        try:
            df = pd.read_csv(file_path)
            text = ""
            for _, row in df.iterrows():
                if len(row) >= 2:
                    key = str(row.iloc[0]).strip()
                    value = str(row.iloc[1]).strip()
                    text += f"{key}: {value}\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from CSV: {e}")
            return ""
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from file based on extension."""
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self._extract_text_from_docx(file_path)
        elif ext == '.txt':
            return self._extract_text_from_txt(file_path)
        elif ext == '.csv':
            return self._extract_text_from_csv(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return ""
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            
            if end < text_len:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
        
        return [c for c in chunks if c]  # Filter empty chunks
    
    async def ingest_file(self, file_path: Path, brand_id: str, filename: str) -> Dict:
        """
        Ingest a single file into the RAG pipeline.
        Returns dict with document_id, chunks_count, etc.
        """
        logger.info(f"Ingesting file: {filename} for brand: {brand_id}")
        
        text = self.extract_text(file_path)
        if not text:
            raise ValueError(f"No text extracted from file: {filename}")
        
        chunks = self.chunk_text(text)
        if not chunks:
            raise ValueError(f"No chunks created from file: {filename}")
        
        logger.info(f"Created {len(chunks)} chunks from {filename}")
        
        doc_id = str(uuid.uuid4())
        await self.db.save_document(
            doc_id=doc_id,
            brand_id=brand_id,
            filename=filename,
            file_type=file_path.suffix,
            metadata={"text_length": len(text), "chunks_count": len(chunks)}
        )
        
        chunk_texts = []
        chunk_metadatas = []
        chunk_ids = []
        
        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk_text)
            chunk_metadatas.append({
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "brand_id": brand_id,
                "chunk_index": i,
                "text": chunk_text
            })
            
            await self.db.save_chunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                brand_id=brand_id,
                content=chunk_text,
                chunk_index=i
            )
        
        vector_indices = self.vector_adapter.add_texts(
            brand_id=brand_id,
            texts=chunk_texts,
            metadatas=chunk_metadatas
        )
        
        for chunk_id, vector_idx in zip(chunk_ids, vector_indices):
            vector_id = f"{chunk_id}_vec"
            await self.db.save_vector(
                vector_id=vector_id,
                chunk_id=chunk_id,
                brand_id=brand_id,
                vector_index=vector_idx
            )
        
        logger.info(f"Successfully ingested {filename}: {len(chunks)} chunks, {len(vector_indices)} vectors")
        
        return {
            "document_id": doc_id,
            "brand_id": brand_id,
            "filename": filename,
            "chunks_count": len(chunks),
            "vectors_count": len(vector_indices)
        }
    
    async def ingest_files(self, file_paths: List[Path], brand_id: str) -> Dict:
        """
        Ingest multiple files for a brand.
        Returns summary dict.
        """
        results = []
        total_chunks = 0
        total_vectors = 0
        
        for file_path in file_paths:
            try:
                result = await self.ingest_file(file_path, brand_id, file_path.name)
                results.append(result)
                total_chunks += result['chunks_count']
                total_vectors += result['vectors_count']
            except Exception as e:
                logger.error(f"Error ingesting {file_path.name}: {e}")
                results.append({
                    "filename": file_path.name,
                    "error": str(e)
                })
        
        return {
            "brand_id": brand_id,
            "files_processed": len(results),
            "total_chunks": total_chunks,
            "total_vectors": total_vectors,
            "results": results
        }
