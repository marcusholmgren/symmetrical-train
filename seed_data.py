"""
Seed script to populate the database with data from Hugging Face dataset.
Dataset: argilla/synthetic-text-classification-news
"""

import asyncio
from datasets import load_dataset
from app.models import NewsClassification
from app.database import init_db, close_db


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

    print("Loading dataset from Hugging Face...")
    try:
        # Load the dataset
        dataset = load_dataset("argilla/synthetic-text-classification-news", split="train")
        print(f"Loaded {len(dataset)} records from Hugging Face dataset.")

        # Insert data into database
        print("Inserting data into database...")
        batch_size = 100
        records_to_create = []

        for idx, item in enumerate(dataset):
            # The dataset has 'text' and 'label' columns
            # We'll map 'text' to 'review' in our model
            record_data = {
                "review": item.get("text", ""),
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

        total_count = await NewsClassification.all().count()
        print(f"Successfully seeded database with {total_count} records!")

    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Make sure you have internet access to download the dataset.")
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(seed_database())
