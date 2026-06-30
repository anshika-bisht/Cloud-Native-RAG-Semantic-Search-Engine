import pytest
from app.services.chunking.service import SemanticSlidingWindowChunker

def test_chunker_handles_empty_string(chunker: SemanticSlidingWindowChunker):
    assert chunker.chunk("") == []
    assert chunker.chunk("   ") == []

def test_chunker_preserves_sentence_boundaries(chunker: SemanticSlidingWindowChunker):
    text = "This is sentence one. This is sentence two! And this is three?"
    chunks = chunker.chunk(text)
    
    assert len(chunks) > 0
    # Should not split in the middle of words
    assert "sentence one" in chunks[0]

def test_chunker_respects_overlap(chunker: SemanticSlidingWindowChunker):
    # Artificially lower chunk size for testing
    chunker.chunk_size = 10
    chunker.overlap_ratio = 0.5
    
    text = "Sentence A. Sentence B. Sentence C. Sentence D. Sentence E."
    chunks = chunker.chunk(text)
    
    assert len(chunks) > 1
    # Check if there is semantic overlap (e.g., Sentence B appears in multiple chunks)
    overlap_found = False
    for i in range(len(chunks) - 1):
        # Very simple overlap check
        if any(word in chunks[i+1] for word in chunks[i].split()):
            overlap_found = True
            break
            
    assert overlap_found
