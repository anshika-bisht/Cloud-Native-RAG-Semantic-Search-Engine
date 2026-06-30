import os
import sys
import time
import asyncio
import numpy as np
import uuid

# Ensure imports work from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.chunking.service import SemanticSlidingWindowChunker
from app.services.embeddings.service import EmbeddingService
from app.services.vectorstore.faiss import FAISSVectorStore

async def run_benchmarks():
    print("========================================")
    print(" RAG Engine Benchmark Suite")
    print("========================================\n")

    # 1. Chunking Benchmark
    print("[1] Chunk Generation Speed...")
    chunker = SemanticSlidingWindowChunker()
    # Generate 1 MB of dummy text
    dummy_text = "The quick brown fox jumps over the lazy dog. " * 25000 
    start = time.time()
    chunks = chunker.chunk(dummy_text)
    duration = time.time() - start
    print(f"    Processed {len(dummy_text)/1024/1024:.2f} MB of text in {duration:.2f}s")
    print(f"    Generated {len(chunks)} chunks.")
    print(f"    Throughput: {len(chunks) / duration:.2f} chunks/sec\n")

    # 2. Embedding Benchmark
    print("[2] Embedding Generation Speed (Batching)...")
    embedder = EmbeddingService()
    # Take 500 chunks to embed
    sample_chunks = chunks[:500] if len(chunks) > 500 else chunks
    start = time.time()
    vectors = await embedder.embed_batch(sample_chunks)
    duration = time.time() - start
    print(f"    Embedded {len(sample_chunks)} chunks in {duration:.2f}s")
    print(f"    Throughput: {len(sample_chunks) / duration:.2f} vectors/sec\n")

    # 3. Vector Retrieval Latency (FAISS Local)
    print("[3] Vector Retrieval Latency (FAISS Local)...")
    faiss_store = FAISSVectorStore(dimension=embedder.dimension)
    await faiss_store.create_collection()
    
    # Generate 10,000 random vectors for indexing
    num_vectors = 10000
    print(f"    Indexing {num_vectors} random vectors...")
    random_vectors = np.random.rand(num_vectors, embedder.dimension).astype('float32').tolist()
    ids = [str(uuid.uuid4()) for _ in range(num_vectors)]
    
    start = time.time()
    await faiss_store.add_embeddings(ids, random_vectors)
    print(f"    Indexing took: {time.time() - start:.2f}s")
    
    print("    Running 100 random queries...")
    start = time.time()
    for _ in range(100):
        query = np.random.rand(embedder.dimension).astype('float32').tolist()
        await faiss_store.search(query, top_k=5)
    duration = time.time() - start
    print(f"    Average Retrieval Latency: {(duration / 100) * 1000:.2f} ms/query\n")
    
    print("========================================")
    print(" Benchmarks Completed.")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
