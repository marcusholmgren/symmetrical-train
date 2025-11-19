"""
Service for indexing documents for the search engine.
"""

import math
from typing import List
from app.models import NewsClassification, IndexToken, IndexEntry
from app.services.search.tokenizers import Tokenizer, WordTokenizer, PrefixTokenizer, NGramTokenizer


class IndexingService:
    """Service to handle the indexing of documents."""

    def __init__(self, tokenizers: List[Tokenizer] = None):
        if tokenizers is None:
            self.tokenizers = [
                WordTokenizer(),
                PrefixTokenizer(),
                NGramTokenizer(),
            ]
        else:
            self.tokenizers = tokenizers

    async def index_document(self, document: NewsClassification):
        """Index a single document."""
        await self.remove_document_from_index(document.id)

        entries_to_create = []
        field_weight = 10  # Weight for the 'review' field

        for tokenizer in self.tokenizers:
            tokens = tokenizer.tokenize(document.review)
            for token in tokens:
                token_obj, _ = await IndexToken.get_or_create(
                    name=token.value, weight=token.weight
                )
                final_weight = (
                    field_weight
                    * token.weight
                    * math.ceil(math.sqrt(len(token.value)))
                )
                entries_to_create.append(
                    IndexEntry(
                        token=token_obj,
                        document_id=document.id,
                        document_type="NewsClassification",
                        field_id="review",
                        weight=final_weight,
                    )
                )

        if entries_to_create:
            await IndexEntry.bulk_create(entries_to_create)

    async def remove_document_from_index(self, document_id: int):
        """Remove all index entries for a given document."""
        await IndexEntry.filter(document_id=document_id).delete()


    async def reindex_all(self):
        """Re-index all documents in the database."""
        await IndexToken.all().delete()
        await IndexEntry.all().delete()
        documents = await NewsClassification.all()
        for document in documents:
            await self.index_document(document)


class DefaultIndexingService(IndexingService):
    def __init__(self):
        super().__init__()
