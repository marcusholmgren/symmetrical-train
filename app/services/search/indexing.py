"""
Service for indexing documents for the search engine.
"""

import math
from typing import List
from app.models import NewsClassification, IndexToken, IndexEntry
from app.services.search.tokenizers import (
    Tokenizer,
    WordTokenizer,
    PrefixTokenizer,
    NGramTokenizer,
)


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
        field_weight = 10
        all_tokens = []
        for tokenizer in self.tokenizers:
            all_tokens.extend(tokenizer.tokenize(document.review))

        token_values = list(set(t.value for t in all_tokens))
        existing_tokens = await IndexToken.filter(name__in=token_values)
        existing_token_map = {t.name: t for t in existing_tokens}

        new_token_values = [t for t in token_values if t not in existing_token_map]
        if new_token_values:
            await IndexToken.bulk_create([IndexToken(name=v) for v in new_token_values])
            new_tokens = await IndexToken.filter(name__in=new_token_values)
            for t in new_tokens:
                existing_token_map[t.name] = t

        for token in all_tokens:
            token_obj = existing_token_map.get(token.value)
            if token_obj is None:
                continue
            final_weight = (
                field_weight * token.weight * math.ceil(math.sqrt(len(token.value)))
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

        document.token_count = len(entries_to_create)
        await document.save(update_fields=["token_count"])

    async def remove_document_from_index(self, document_id: int):
        """Remove all index entries for a given document."""
        await IndexEntry.filter(document_id=document_id).delete()

    async def reindex_all(self):
        """Re-index all documents in the database."""
        await IndexToken.all().delete()
        await IndexEntry.all().delete()
        async for document in NewsClassification.all():
            await self.index_document(document)


class DefaultIndexingService(IndexingService):
    def __init__(self):
        super().__init__()
