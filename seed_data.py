"""
Seed script to populate the database with data from Hugging Face dataset.
Dataset: argilla/synthetic-text-classification-news

If the Hugging Face dataset is not accessible, it will use sample data.
"""

import asyncio
from app.models import NewsClassification
from app.database import init_db, close_db
from app.services.search.indexing import IndexingService


# Sample data for fallback when Hugging Face is not accessible
SAMPLE_DATA = [
    {
        "review": "The Federal Reserve announced a rate hike today, affecting markets worldwide.",
        "label": "BUSINESS",
    },
    {
        "review": "The new budget proposal includes significant infrastructure spending.",
        "label": "POLITICS",
    },
    {
        "review": "Scientists discover breakthrough in renewable energy technology.",
        "label": "SCIENCE",
    },
    {
        "review": "Local team wins championship in thrilling overtime victory.",
        "label": "SPORTS",
    },
    {
        "review": "New exhibition opens at the national museum showcasing modern art.",
        "label": "ENTERTAINMENT",
    },
    {
        "review": "Stock markets rally on positive earnings reports from tech sector.",
        "label": "BUSINESS",
    },
    {
        "review": "Senate debates new healthcare legislation in heated session.",
        "label": "POLITICS",
    },
    {
        "review": "Climate change report warns of accelerating global temperatures.",
        "label": "SCIENCE",
    },
    {
        "review": "Olympic athlete breaks world record in swimming competition.",
        "label": "SPORTS",
    },
    {
        "review": "Blockbuster film dominates box office on opening weekend.",
        "label": "ENTERTAINMENT",
    },
    {
        "review": "Major tech company announces quarterly profits exceeding expectations.",
        "label": "BUSINESS",
    },
    {
        "review": "Presidential candidate outlines economic policy platform.",
        "label": "POLITICS",
    },
    {
        "review": "New study reveals insights into human brain function.",
        "label": "SCIENCE",
    },
    {
        "review": "Tennis star advances to finals with dominant performance.",
        "label": "SPORTS",
    },
    {
        "review": "Music festival announces star-studded lineup for summer.",
        "label": "ENTERTAINMENT",
    },
]


async def seed_database():
    """Load data from Hugging Face and seed the database."""
    print("Initializing database connection...")
    await init_db()

    # Check if database already has data
    existing_count = await NewsClassification.all().count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} records.")
        response = input("Do you want to clear and reseed? (y/N): ")
        if response.lower() != "y":
            print("Skipping seed operation.")
            await close_db()
            return
        else:
            print("Clearing existing data...")
            await NewsClassification.all().delete()

    print("Loading dataset...")
    dataset = None

    try:
        # Try to load from Hugging Face
        from datasets import load_dataset
        if True:
            print("Attempting to load from Hugging Face...")
            dataset = load_dataset(
            "argilla/synthetic-text-classification-news", split="train"
            )
            print(f"Loaded {len(dataset)} records from Hugging Face dataset.")
        else:
            dataset = SAMPLE_DATA

        # Insert data into database
        print("Inserting data into database...")
        batch_size = 100
        records_to_create = []

        for idx, item in enumerate(dataset):
            # The dataset has 'text' and 'label' columns
            # We'll map 'text' to 'review' in our model
            record_data = {
                "review": item.get("text", item.get("review", "")),
                "label": item.get("label", ""),
            }
            records_to_create.append(record_data)

            # Insert in batches
            if len(records_to_create) >= batch_size:
                await NewsClassification.bulk_create(
                    [NewsClassification(**data) for data in records_to_create]
                )
                print(f"Inserted {idx + 1} records...")
                records_to_create = []

        # Insert remaining records
        if records_to_create:
            await NewsClassification.bulk_create(
                [NewsClassification(**data) for data in records_to_create]
            )

    except Exception as e:
        print(f"Could not load from Hugging Face: {e}")
        print("Using sample data instead...")

        # Use sample data
        for idx, data in enumerate(SAMPLE_DATA):
            await NewsClassification.create(**data)
            print(f"Inserted {idx + 1}/{len(SAMPLE_DATA)} records...")

    total_count = await NewsClassification.all().count()
    print(f"\n✓ Successfully seeded database with {total_count} records!")

    # Show label distribution
    labels = await NewsClassification.all().values_list("label", flat=True)
    label_counts = {}
    for label in labels:
        label_counts[label] = label_counts.get(label, 0) + 1

    print("\nLabel distribution:")
    for label, count in sorted(label_counts.items()):
        print(f"  {label}: {count}")

    print("\nStarting search index...")
    indexing_service = IndexingService()
    await indexing_service.reindex_all()
    print("✓ Search index completed!")

    await close_db()


if __name__ == "__main__":
    asyncio.run(seed_database())
