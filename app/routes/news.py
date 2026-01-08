from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Annotated

from app.models import NewsClassification
from app.services.search.indexing import IndexingService, DefaultIndexingService
from app.services.search.search import SearchService, DefaultSearchService
from app.schemas import (
    NewsClassificationCreate,
    NewsClassificationUpdate,
    NewsClassificationResponse,
)

router = APIRouter(prefix="/news", tags=["news-classification"])
NewsSearchService = Annotated[SearchService, Depends(DefaultSearchService)]
NewsIndexingService = Annotated[IndexingService, Depends(DefaultIndexingService)]


@router.get("/", response_model=List[NewsClassificationResponse])
async def list_news_classifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    label: Optional[str] = None,
):
    """
    List all news classifications with optional filtering and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **label**: Optional filter by label
    """
    query = NewsClassification.all()

    if label:
        query = query.filter(label__iexact=label)

    return await query.offset(skip).limit(limit)


@router.get("/{news_id}", response_model=NewsClassificationResponse)
async def get_news_classification(news_id: int):
    """Get a specific news classification by ID."""
    news = await NewsClassification.get_or_none(id=news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News classification not found")
    return news


@router.post("/", response_model=NewsClassificationResponse, status_code=201)
async def create_news_classification(
    data: NewsClassificationCreate,
    indexing_service: NewsIndexingService,
):
    """Create a new news classification."""
    news = await NewsClassification.create(review=data.review, label=data.label)
    await indexing_service.index_document(news)
    return news


@router.put("/{news_id}", response_model=NewsClassificationResponse)
async def update_news_classification(
    news_id: int,
    data: NewsClassificationUpdate,
    indexing_service: NewsIndexingService,
):
    """Update an existing news classification."""
    news = await NewsClassification.get_or_none(id=news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News classification not found")

    update_data = data.model_dump(exclude_unset=True)
    await news.update_from_dict(update_data).save()
    await indexing_service.index_document(news)
    return news


@router.delete("/{news_id}", status_code=204)
async def delete_news_classification(
    news_id: int,
    indexing_service: NewsIndexingService,
):
    """Delete a news classification."""
    news = await NewsClassification.get_or_none(id=news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News classification not found")

    await indexing_service.remove_document_from_index(news.id)
    await news.delete()
    return None


@router.get("/search/", response_model=List[NewsClassificationResponse])
async def search_news(
    q: Annotated[str, Query(..., min_length=3)],
    search_service: NewsSearchService,
):
    """Search for news articles."""
    results = await search_service.search(q)
    return [NewsClassificationResponse.model_validate(item) for item in results]


@router.get("/stats/summary")
async def get_statistics():
    """Get statistics about news classifications."""
    total = await NewsClassification.all().count()

    # Get unique labels and their counts
    labels = await NewsClassification.all().values_list("label", flat=True)
    label_counts = {}
    for label in labels:
        label_counts[label] = label_counts.get(label, 0) + 1

    return {
        "total_records": total,
        "label_distribution": label_counts,
    }
