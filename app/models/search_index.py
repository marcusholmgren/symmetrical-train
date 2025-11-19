"""
Tortoise ORM models for the search index.
"""

from tortoise.models import Model
from tortoise import fields


class IndexToken(Model):
    """Stores unique tokens with their tokenizer weights."""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = "index_tokens"

    def __str__(self):
        return self.name


class IndexEntry(Model):
    """Links tokens to documents with field-specific weights."""

    id = fields.IntField(pk=True)
    token = fields.ForeignKeyField("models.IndexToken", related_name="entries")
    document_id = fields.IntField(index=True)
    document_type = fields.CharField(max_length=50)
    field_id = fields.CharField(max_length=50)
    weight = fields.IntField()

    class Meta:
        table = "index_entries"
        indexes = [("document_type", "document_id")]

    def __str__(self):
        return f"Token {self.token_id} in doc {self.document_id}"
