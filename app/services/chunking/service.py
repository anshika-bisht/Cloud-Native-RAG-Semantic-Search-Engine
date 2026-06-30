import re
import tiktoken
from typing import List
from app.core.config import settings

class SemanticSlidingWindowChunker:
    """
    Splits document text into overlapping chunks.
    Respects sentence boundaries to prevent semantic fragmentation.
    """
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE_TOKENS
        self.overlap_ratio = settings.CHUNK_OVERLAP_PERCENTAGE
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def chunk(self, text: str) -> List[str]:
        if not text.strip():
            return []

        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk_sentences = []
        current_token_count = 0

        for sentence in sentences:
            sentence_tokens = len(self.encoder.encode(sentence))
            
            if current_token_count + sentence_tokens > self.chunk_size and current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
                
                # Backtrack to create sliding window overlap
                overlap_tokens = 0
                overlap_sentences = []
                for s in reversed(current_chunk_sentences):
                    s_tokens = len(self.encoder.encode(s))
                    if overlap_tokens + s_tokens > (self.chunk_size * self.overlap_ratio):
                        break
                    overlap_sentences.insert(0, s)
                    overlap_tokens += s_tokens
                    
                current_chunk_sentences = overlap_sentences
                current_token_count = overlap_tokens
                
            current_chunk_sentences.append(sentence)
            current_token_count += sentence_tokens
            
        if current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))
            
        return chunks
