"""
Acceptance tests for the AI Content Generation POC.
Tests the complete end-to-end functionality.
"""
import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.adapters.embeddings_local import LocalEmbeddingsAdapter
from app.adapters.vector_faiss import FAISSVectorAdapter
from app import config


@pytest.mark.asyncio
async def test_database_initialization():
    """Test 1: Database initializes correctly."""
    db = Database(Path("/tmp/test_app.db"))
    await db.init_db()
    
    session = await db.create_session("test-session-1", "Test Session")
    assert session['id'] == "test-session-1"
    assert session['name'] == "Test Session"
    
    sessions = await db.list_sessions()
    assert len(sessions) >= 1
    
    print("✓ Test 1 passed: Database initialization works")


@pytest.mark.asyncio
async def test_multi_session_chat():
    """Test 2: Multi-session chat works correctly."""
    db = Database(Path("/tmp/test_app.db"))
    await db.init_db()
    
    session1 = await db.create_session("session-1", "Session 1")
    session2 = await db.create_session("session-2", "Session 2")
    
    await db.add_message("session-1", "user", "Hello from session 1")
    await db.add_message("session-1", "assistant", "Response to session 1")
    
    await db.add_message("session-2", "user", "Hello from session 2")
    await db.add_message("session-2", "assistant", "Response to session 2")
    
    messages1 = await db.get_messages("session-1")
    messages2 = await db.get_messages("session-2")
    
    assert len(messages1) == 2
    assert len(messages2) == 2
    assert messages1[0]['content'] == "Hello from session 1"
    assert messages2[0]['content'] == "Hello from session 2"
    
    print("✓ Test 2 passed: Multi-session chat works correctly")


def test_embeddings_and_faiss():
    """Test 3: RAG pipeline with FAISS and embeddings works."""
    embeddings = LocalEmbeddingsAdapter(device="cpu")
    
    text = "This is a test document about brand guidelines"
    embedding = embeddings.embed_text(text)
    assert embedding.shape[0] == embeddings.get_dimension()
    
    vector_store = FAISSVectorAdapter(embeddings, Path("/tmp/test_vectors"))
    
    texts = [
        "Brand tone: warm and caring",
        "Visual style: natural and authentic",
        "Color palette: soft blues and whites"
    ]
    metadatas = [
        {"brand_id": "test_brand", "text": texts[0]},
        {"brand_id": "test_brand", "text": texts[1]},
        {"brand_id": "test_brand", "text": texts[2]}
    ]
    
    vector_store.add_texts("test_brand", texts, metadatas)
    
    results = vector_store.search("test_brand", "What is the brand tone?", top_k=2)
    assert len(results) > 0
    assert "warm" in results[0]['text'].lower() or "caring" in results[0]['text'].lower()
    
    print("✓ Test 3 passed: RAG with FAISS and embeddings works")


def test_safety_service():
    """Test 4: Safety checks work."""
    from app.services.safety import SafetyService
    
    safety = SafetyService(device="cpu")
    
    safe_text = "This is a nice and friendly message"
    is_safe, scores = safety.check_text_safety(safe_text)
    assert is_safe == True
    
    print("✓ Test 4 passed: Safety service works")


def test_template_service():
    """Test 5: Template service works."""
    from app.services.rag.templates import TemplateService
    
    template_service = TemplateService()
    
    templates = template_service.list_templates()
    assert len(templates) > 0
    
    template = template_service.get_template("product_showcase")
    assert template is not None
    assert template['type'] == 'image'
    
    filled = template_service.fill_template("product_showcase", {
        "product_name": "Test Product",
        "setting": "outdoor scene",
        "mood": "bright and cheerful"
    })
    assert "Test Product" in filled
    assert "outdoor scene" in filled
    
    print("✓ Test 5 passed: Template service works")


if __name__ == "__main__":
    print("Running acceptance tests...")
    print("=" * 60)
    
    asyncio.run(test_database_initialization())
    asyncio.run(test_multi_session_chat())
    
    test_embeddings_and_faiss()
    test_safety_service()
    test_template_service()
    
    print("=" * 60)
    print("All acceptance tests passed! ✓")
