import asyncio
import time
import uuid
import os
import sys

# Ensure the src module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.vector_store.faiss_repo import FAISSRepository
from src.infrastructure.vector_store.qdrant_repo import QdrantVectorStore
import numpy as np

async def benchmark():
    num_vectors = 10000
    dimension = 384
    
    print(f"Generating {num_vectors} random vectors for benchmarking...")
    vectors = np.random.rand(num_vectors, dimension).astype('float32').tolist()
    chunk_ids = [str(uuid.uuid4()) for _ in range(num_vectors)]
    
    # Payload testing
    payloads = [{"meta": f"data_{i}"} for i in range(num_vectors)]

    # --- Qdrant Benchmark ---
    print("\n--- QDRANT BENCHMARK ---")
    qdrant = QdrantVectorStore(dimension=dimension)
    try:
        await qdrant.create_collection()
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
        print("Skipping Qdrant benchmark. Is the container running?")
        qdrant = None
        
    if qdrant:
        start = time.time()
        # Batch insert in chunks to avoid HTTP timeouts on huge payloads
        batch_size = 1000
        for i in range(0, num_vectors, batch_size):
            await qdrant.add_embeddings(
                chunk_ids[i:i+batch_size], 
                vectors[i:i+batch_size], 
                payloads[i:i+batch_size]
            )
        qdrant_ingest_time = time.time() - start
        
        start = time.time()
        # 100 random searches
        for _ in range(100):
            await qdrant.search(vectors[np.random.randint(0, num_vectors)], top_k=5)
        qdrant_search_time = time.time() - start
        
        print(f"Qdrant Ingestion Time ({num_vectors}): {qdrant_ingest_time:.2f}s")
        print(f"Qdrant Search Time (100 queries): {qdrant_search_time:.2f}s")

    # --- FAISS Benchmark ---
    print("\n--- FAISS BENCHMARK ---")
    faiss_repo = FAISSRepository(dimension=dimension)
    await faiss_repo.create_collection()
    
    start = time.time()
    await faiss_repo.add_embeddings(chunk_ids, vectors, payloads)
    faiss_ingest_time = time.time() - start
    
    start = time.time()
    for _ in range(100):
        await faiss_repo.search(vectors[np.random.randint(0, num_vectors)], top_k=5)
    faiss_search_time = time.time() - start
    
    print(f"FAISS Ingestion Time ({num_vectors}): {faiss_ingest_time:.2f}s")
    print(f"FAISS Search Time (100 queries): {faiss_search_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(benchmark())
