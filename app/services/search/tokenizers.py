"""
Tokenizers for the search engine.
"""

import re
from abc import ABC, abstractmethod
from typing import List
from unidecode import unidecode
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Token:
    """Represents a token with its value and weight."""

    value: str
    weight: int


class Tokenizer(ABC):
    """Abstract base class for tokenizers."""

    def __init__(self, weight: int):
        self.weight = weight

    @abstractmethod
    def tokenize(self, text: str) -> List[Token]:
        """Tokenize the given text."""
        pass

    def get_weight(self) -> int:
        """Return the tokenizer's weight."""
        return self.weight

    def _normalize(self, text: str) -> str:
        """Normalize text by lowercasing, removing special characters, and handling whitespace."""
        text = unidecode(text)
        text = text.lower()
        text = re.sub(r"[^a-z0-9]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_words(self, text: str) -> List[str]:
        """Extract words from normalized text."""
        normalized_text = self._normalize(text)
        return [word for word in normalized_text.split(" ") if len(word) >= 2]


class WordTokenizer(Tokenizer):
    """Splits text into individual words."""

    def __init__(self, weight: int = 20):
        super().__init__(weight)

    def tokenize(self, text: str) -> List[Token]:
        """Tokenize text into words."""
        words = self._extract_words(text)
        return [Token(word, self.weight) for word in set(words)]


class PrefixTokenizer(Tokenizer):
    """Generates word prefixes."""

    def __init__(self, weight: int = 5, min_prefix_len: int = 4):
        super().__init__(weight)
        self.min_prefix_len = min_prefix_len

    def tokenize(self, text: str) -> List[Token]:
        """Tokenize text into prefixes."""
        words = self._extract_words(text)
        tokens = set()
        for word in words:
            if len(word) >= self.min_prefix_len:
                for i in range(self.min_prefix_len, len(word) + 1):
                    tokens.add(word[:i])
        return [Token(token, self.weight) for token in tokens]


class NGramTokenizer(Tokenizer):
    """Creates character n-grams."""

    def __init__(self, weight: int = 1, ngram_len: int = 3):
        super().__init__(weight)
        self.ngram_len = ngram_len

    def tokenize(self, text: str) -> List[Token]:
        """Tokenize text into n-grams."""
        words = self._extract_words(text)
        tokens = set()
        for word in words:
            if len(word) >= self.ngram_len:
                for i in range(len(word) - self.ngram_len + 1):
                    tokens.add(word[i : i + self.ngram_len])
        return [Token(token, self.weight) for token in tokens]
