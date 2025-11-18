from tortoise import Tortoise


# Database configuration
TORTOISE_ORM = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initialize database connection"""
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db():
    """Close database connection"""
    await Tortoise.close_connections()
