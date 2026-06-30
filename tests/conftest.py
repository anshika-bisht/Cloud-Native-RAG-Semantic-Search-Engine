import pytest
from app.services.chunking.service import SemanticSlidingWindowChunker
from app.services.parser.service import DocumentParser

@pytest.fixture
def chunker():
    return SemanticSlidingWindowChunker()

@pytest.fixture
def parser():
    return DocumentParser()
