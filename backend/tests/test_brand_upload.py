"""
Tests for brand knowledge upload and management.
"""
import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.adapters.embeddings_local import LocalEmbeddingsAdapter
from app.adapters.vector_faiss import FAISSVectorAdapter
from app.services.rag.ingestion import IngestionService


@pytest.mark.asyncio
async def test_brand_creation():
    """Test 1: Brand creation and retrieval."""
    db = Database(Path("/tmp/test_brand_app.db"))
    await db.init_db()
    
    brand = await db.create_brand("test_brand", "Test Brand")
    assert brand['id'] == "test_brand"
    assert brand['name'] == "Test Brand"
    
    retrieved = await db.get_brand("test_brand")
    assert retrieved is not None
    assert retrieved['name'] == "Test Brand"
    
    print("✓ Test 1 passed: Brand creation and retrieval works")


@pytest.mark.asyncio
async def test_brand_list_with_stats():
    """Test 2: Brand listing with statistics."""
    db = Database(Path("/tmp/test_brand_app.db"))
    await db.init_db()
    
    await db.create_brand("dove", "Dove")
    await db.create_brand("axe", "Axe")
    
    brands = await db.list_brands_with_stats()
    assert len(brands) >= 2
    
    brand_ids = [b['id'] for b in brands]
    assert "dove" in brand_ids
    assert "axe" in brand_ids
    
    print("✓ Test 2 passed: Brand listing with stats works")


@pytest.mark.asyncio
async def test_text_ingestion():
    """Test 3: Text ingestion for a brand."""
    db = Database(Path("/tmp/test_brand_app.db"))
    await db.init_db()
    
    embeddings = LocalEmbeddingsAdapter("sentence-transformers/all-MiniLM-L6-v2")
    vector_adapter = FAISSVectorAdapter(embeddings, Path("/tmp/test_vectors"))
    ingestion_service = IngestionService(vector_adapter, db)
    
    await db.create_brand("techcorp", "TechCorp")
    
    text = """
    TechCorp Brand Guidelines
    
    Brand Voice: Innovative and forward-thinking
    Visual Style: Modern with blue accents
    Target Audience: Business professionals
    """
    
    result = await ingestion_service.ingest_text(
        text=text,
        brand_id="techcorp",
        filename="guidelines.txt"
    )
    
    assert result['brand_id'] == "techcorp"
    assert result['chunks'] > 0
    assert result['vectors'] > 0
    
    print(f"✓ Test 3 passed: Text ingestion works ({result['chunks']} chunks, {result['vectors']} vectors)")


@pytest.mark.asyncio
async def test_csv_brand_upload():
    """Test 4: CSV upload with multiple brands."""
    db = Database(Path("/tmp/test_brand_app.db"))
    await db.init_db()
    
    embeddings = LocalEmbeddingsAdapter("sentence-transformers/all-MiniLM-L6-v2")
    vector_adapter = FAISSVectorAdapter(embeddings, Path("/tmp/test_vectors"))
    ingestion_service = IngestionService(vector_adapter, db)
    
    brands_data = {
        "Dove": "Dove is committed to real beauty and self-confidence.",
        "Axe": "Axe is bold and confident, targeting young men.",
        "Lipton": "Lipton brings natural refreshment and wellness."
    }
    
    for brand_name, text in brands_data.items():
        brand_id = brand_name.lower()
        await db.create_brand(brand_id, brand_name)
        
        result = await ingestion_service.ingest_text(
            text=text,
            brand_id=brand_id,
            filename=f"{brand_name}.csv"
        )
        
        assert result['brand_id'] == brand_id
        assert result['chunks'] > 0
    
    brands = await db.list_brands_with_stats()
    brand_names = [b['name'] for b in brands]
    
    assert "Dove" in brand_names
    assert "Axe" in brand_names
    assert "Lipton" in brand_names
    
    print("✓ Test 4 passed: CSV upload with multiple brands works")


@pytest.mark.asyncio
async def test_brand_scoped_retrieval():
    """Test 5: Brand-scoped retrieval."""
    db = Database(Path("/tmp/test_brand_app.db"))
    await db.init_db()
    
    embeddings = LocalEmbeddingsAdapter("sentence-transformers/all-MiniLM-L6-v2")
    vector_adapter = FAISSVectorAdapter(embeddings, Path("/tmp/test_vectors"))
    ingestion_service = IngestionService(vector_adapter, db)
    
    await db.create_brand("dove", "Dove")
    await ingestion_service.ingest_text(
        text="Dove focuses on real beauty and natural photography with soft whites and blues.",
        brand_id="dove",
        filename="dove_guidelines.txt"
    )
    
    await db.create_brand("axe", "Axe")
    await ingestion_service.ingest_text(
        text="Axe is bold and edgy with dark colors and high contrast.",
        brand_id="axe",
        filename="axe_guidelines.txt"
    )
    
    dove_results = vector_adapter.search(query="beauty and natural", brand_id="dove", top_k=3)
    assert len(dove_results) > 0
    assert any("Dove" in r['text'] or "beauty" in r['text'] for r in dove_results)
    
    axe_results = vector_adapter.search(query="bold and edgy", brand_id="axe", top_k=3)
    assert len(axe_results) > 0
    assert any("Axe" in r['text'] or "bold" in r['text'] for r in axe_results)
    
    print("✓ Test 5 passed: Brand-scoped retrieval works")


if __name__ == "__main__":
    asyncio.run(test_brand_creation())
    asyncio.run(test_brand_list_with_stats())
    asyncio.run(test_text_ingestion())
    asyncio.run(test_csv_brand_upload())
    asyncio.run(test_brand_scoped_retrieval())
    print("\n✅ All brand upload tests passed!")
