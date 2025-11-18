from tortoise import fields
from tortoise.models import Model


class NewsClassification(Model):
    """
    Model for storing news reviews and their classification labels.
    Based on the Hugging Face dataset argilla/synthetic-text-classification-news.
    """

    id = fields.IntField(primary_key=True)
    review = fields.TextField()
    label = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "news_classifications"

    def __str__(self):
        return f"NewsClassification(id={self.id}, label={self.label})"
