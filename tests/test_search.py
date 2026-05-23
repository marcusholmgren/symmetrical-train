import asyncio
import pytest
import pytest_asyncio
from tortoise import Tortoise
from app.models import NewsClassification, IndexToken, IndexEntry
from app.services.search.tokenizers import WordTokenizer, PrefixTokenizer, NGramTokenizer
from app.services.search.indexing import IndexingService
from app.services.search.search import SearchService

# Test database configuration
TEST_TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": ":memory:"},
        }
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        },
    },
}


@pytest_asyncio.fixture(scope="function")
async def init_test_db():
    """Fixture to initialize and tear down test database."""
    await Tortoise.init(config=TEST_TORTOISE_ORM)
    await Tortoise.generate_schemas()
    # Enable WAL and busy timeout for the sqlite database
    connection = Tortoise.get_connection("default")
    await connection.execute_script("PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;")
    yield
    await Tortoise.close_connections()


def test_tokenizers():
    """Test individual tokenizer behavior and outputs."""
    word_tok = WordTokenizer(weight=20)
    tokens = word_tok.tokenize("The market shows growth!")
    # Normalize lowercases and ignores <= 1 char words
    values = {t.value for t in tokens}
    assert "market" in values
    assert "shows" in values
    assert "growth" in values
    assert "the" in values
    assert "" not in values
    for t in tokens:
        assert t.weight == 20

    prefix_tok = PrefixTokenizer(weight=5, min_prefix_len=4)
    tokens = prefix_tok.tokenize("grow")
    values = {t.value for t in tokens}
    # "grow" itself is >= 4, so it should be included
    assert "grow" in values

    ngram_tok = NGramTokenizer(weight=1, ngram_len=3)
    tokens = ngram_tok.tokenize("cat")
    values = {t.value for t in tokens}
    assert "cat" in values


@pytest.mark.asyncio
async def test_indexing_deduplication(init_test_db):
    """Test that indexing a document does not create duplicate IndexEntry rows."""
    doc = await NewsClassification.create(
        review="The market shows strong growth and business opportunities in the market.",
        label="BUSINESS"
    )
    
    indexing_service = IndexingService()
    await indexing_service.index_document(doc)
    
    # Verify all index entries for the document are unique by token
    entries = await IndexEntry.filter(document_id=doc.id)
    assert len(entries) > 0
    
    token_ids = [entry.token_id for entry in entries]
    assert len(token_ids) == len(set(token_ids)), "Found duplicate IndexEntry records for the same token!"


@pytest.mark.asyncio
async def test_indexing_concurrency(init_test_db):
    """Test that concurrent indexing handles new tokens gracefully without crashing."""
    doc1 = await NewsClassification.create(
        review="Totally unique phrase with brand new unseen tokens and vocabulary.",
        label="BUSINESS"
    )
    doc2 = await NewsClassification.create(
        review="Totally unique phrase with brand new unseen tokens and vocabulary.",
        label="SPORTS"
    )
    
    indexing_service = IndexingService()
    
    # Run concurrently
    await asyncio.gather(
        indexing_service.index_document(doc1),
        indexing_service.index_document(doc2)
    )
    
    # Check that both are indexed properly
    entries1 = await IndexEntry.filter(document_id=doc1.id)
    entries2 = await IndexEntry.filter(document_id=doc2.id)
    assert len(entries1) > 0
    assert len(entries2) > 0


@pytest.mark.asyncio
async def test_search_validation_and_scoring(init_test_db):
    """Test search service validation, boundaries, and result correctness."""
    doc1 = await NewsClassification.create(review="The quick brown fox jumps over the lazy dog.", label="FOX")
    doc2 = await NewsClassification.create(review="The lazy dog sleeps all day long.", label="DOG")
    
    indexing_service = IndexingService()
    await indexing_service.index_document(doc1)
    await indexing_service.index_document(doc2)
    
    search_service = SearchService()
    
    # 1. Test empty/None/whitespace validation
    assert await search_service.search("") == []
    assert await search_service.search("   ") == []
    assert await search_service.search(None) == []
    
    # 2. Test searching for a word present in both docs
    results = await search_service.search("dog")
    assert len(results) == 2
    
    # 3. Test searching for specific words
    results_fox = await search_service.search("fox")
    assert len(results_fox) == 1
    assert results_fox[0].id == doc1.id
    
    # 4. Test limits constraint
    results_limit = await search_service.search("dog", limit=1)
    assert len(results_limit) == 1
