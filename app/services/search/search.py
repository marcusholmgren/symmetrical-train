"""
Service for searching documents.
"""

from typing import List
from tortoise.expressions import Q
from tortoise.functions import Sum, Count, Avg, Coalesce
from app.models import IndexEntry, IndexToken, NewsClassification
from app.services.search.tokenizers import (
    Tokenizer,
    WordTokenizer,
    PrefixTokenizer,
    NGramTokenizer,
)


class SearchService:
    def __init__(self, tokenizers: List[Tokenizer] = None):
        if tokenizers is None:
            self.tokenizers = [
                WordTokenizer(),
                PrefixTokenizer(),
                NGramTokenizer(),
            ]
        else:
            self.tokenizers = tokenizers

    async def search(self, query: str, limit: int = 10) -> List[NewsClassification]:
        query_tokens = self._tokenize_query(query)
        if not query_tokens:
            return []

        token_values = sorted(
            list(set(token.value for token in query_tokens)),
            key=len,
            reverse=True,
        )
        if len(token_values) > 300:
            token_values = token_values[:300]

        base_query = (
            IndexEntry.filter(token__name__in=token_values)
            .group_by("document_id")
            .annotate(
                base_score=Sum("weight"),
                token_diversity=Count("token_id", distinct=True),
                avg_weight=Avg("weight"),
            )
        )

        doc_token_counts = (
            await IndexEntry.all()
            .group_by("document_id")
            .annotate(token_count=Count("id"))
            .values("document_id", "token_count")
        )
        doc_token_map = {item["document_id"]: item["token_count"] for item in doc_token_counts}

        results = await base_query.values(
            "document_id", "base_score", "token_diversity", "avg_weight"
        )

        scored_results = []
        for r in results:
            doc_token_count = doc_token_map.get(r["document_id"], 1)
            score = (
                r["base_score"]
                * (1 + (0 if r["token_diversity"] is None else r["token_diversity"]))
                * (1 + (0 if r["avg_weight"] is None else r["avg_weight"]))
                / (1 + doc_token_count)
            )
            scored_results.append({"document_id": r["document_id"], "score": score})

        sorted_results = sorted(scored_results, key=lambda x: x["score"], reverse=True)
        doc_ids = [result["document_id"] for result in sorted_results[:limit]]

        if not doc_ids:
            return []

        documents = await NewsClassification.filter(id__in=doc_ids)
        doc_map = {doc.id: doc for doc in documents}
        return [doc_map[doc_id] for doc_id in doc_ids if doc_id in doc_map]

    def _tokenize_query(self, query: str) -> List:
        tokens = []
        for tokenizer in self.tokenizers:
            tokens.extend(tokenizer.tokenize(query))
        return tokens

class DefaultSearchService(SearchService):
    def __init__(self):
        super().__init__()