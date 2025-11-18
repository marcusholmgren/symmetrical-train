# symmetrical-train

A FastAPI application for news text classification management, using Tortoise ORM with SQLite database and seeded with data from the Hugging Face dataset `argilla/synthetic-text-classification-news`.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **uv**: Fast Python package manager for dependency management
- **Tortoise ORM**: Easy-to-use async ORM for Python
- **SQLite**: Lightweight database for data persistence
- **Hugging Face Integration**: Seed data from `argilla/synthetic-text-classification-news` dataset

## Requirements

- Python 3.12+
- uv (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/marcusholmgren/symmetrical-train.git
cd symmetrical-train
```

2. Install dependencies using uv:
```bash
uv sync
```

## Database Setup

Initialize and seed the database with data from Hugging Face:

```bash
uv run python seed_data.py
```

This will download the `argilla/synthetic-text-classification-news` dataset and populate the SQLite database with news reviews and their classification labels.

## Running the Application

Start the FastAPI server:

```bash
uv run python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## API Endpoints

### News Classification Endpoints

- `GET /news/` - List all news classifications (supports pagination and filtering)
- `GET /news/{id}` - Get a specific news classification by ID
- `POST /news/` - Create a new news classification
- `PUT /news/{id}` - Update an existing news classification
- `DELETE /news/{id}` - Delete a news classification
- `GET /news/stats/summary` - Get statistics about the dataset

### General Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Example Usage

### List news classifications with pagination:
```bash
curl "http://localhost:8000/news/?skip=0&limit=10"
```

### Filter by label:
```bash
curl "http://localhost:8000/news/?label=POLITICS"
```

### Get statistics:
```bash
curl "http://localhost:8000/news/stats/summary"
```

### Create a new classification:
```bash
curl -X POST "http://localhost:8000/news/" \
  -H "Content-Type: application/json" \
  -d '{"review": "Breaking news about the economy", "label": "BUSINESS"}'
```

## Project Structure

```
symmetrical-train/
├── app/
│   ├── __init__.py
│   ├── database.py          # Database configuration
│   ├── schemas.py           # Pydantic schemas
│   ├── models/
│   │   ├── __init__.py
│   │   └── news_classification.py  # Tortoise ORM model
│   └── routes/
│       ├── __init__.py
│       └── news.py          # API routes
├── main.py                  # FastAPI application
├── seed_data.py            # Script to seed database
├── pyproject.toml          # Project dependencies (managed by uv)
└── README.md               # This file
```

## Development

The application uses:
- **FastAPI** for the web framework
- **Tortoise ORM** for database operations
- **Pydantic** for data validation
- **Uvicorn** as the ASGI server
- **Hugging Face Datasets** for loading seed data

## License

See LICENSE file for details.