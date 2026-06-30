import os
import hashlib
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from typing import List

from app.api.dependencies import get_document_repo, get_vector_store, get_parser, get_chunker, get_embedding_service
from app.models.orm import Document, Chunk
from app.schemas.domain import IngestResponse
from app.core.security import sanitize_filename, validate_file_size
from app.core.config import settings
from app.core.logger import logger

router = APIRouter(prefix="/upload", tags=["Ingestion"])

async def process_document_background(
    doc_id: str,
    file_path: str,
    doc_repo,
    vector_store,
    parser,
    chunker,
    embeddings
):
    try:
        # Parse PDF
        text = parser.parse(file_path)
        
        # Chunk Text
        text_chunks = chunker.chunk(text)
        
        # Save chunks to DB
        db_chunks = []
        for i, chunk_text in enumerate(text_chunks):
            db_chunks.append(Chunk(
                document_id=doc_id,
                chunk_index=i,
                text=chunk_text,
                token_count=len(chunker.encoder.encode(chunk_text))
            ))
        await doc_repo.add_chunks(db_chunks)
        
        # Generate Embeddings
        chunk_ids = [c.id for c in db_chunks]
        chunk_texts = [c.text for c in db_chunks]
        payloads = [
            {
                "document_id": doc_id,
                "chunk_index": i,
                "text": text
            }
            for i, text in enumerate(chunk_texts)
        ]
        
        vector_embeddings = await embeddings.embed_batch(chunk_texts)
        
        # Upload to Vector Store
        await vector_store.add_embeddings(chunk_ids, vector_embeddings, payloads)
        
        # Update Document status
        doc = await doc_repo.get_by_id(doc_id)
        if doc:
            doc.status = "indexed"
            await doc_repo.add(doc)
            
        logger.info(f"Successfully indexed document {doc_id} with {len(db_chunks)} chunks.")
    except Exception as e:
        logger.error(f"Failed to process document {doc_id}: {e}")
        doc = await doc_repo.get_by_id(doc_id)
        if doc:
            doc.status = "failed"
            await doc_repo.add(doc)
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("", response_model=List[IngestResponse])
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    doc_repo = Depends(get_document_repo),
    vector_store = Depends(get_vector_store),
    parser = Depends(get_parser),
    chunker = Depends(get_chunker),
    embeddings = Depends(get_embedding_service)
):
    os.makedirs("uploads", exist_ok=True)
    responses = []
    
    for file in files:
        safe_filename = sanitize_filename(file.filename)
        file_content = await file.read()
        validate_file_size(len(file_content), settings.MAX_FILE_SIZE_MB)
        
        content_hash = hashlib.sha256(file_content).hexdigest()
        
        # Deduplication Check
        existing_doc = await doc_repo.get_by_hash(content_hash)
        if existing_doc:
            logger.info(f"Document {safe_filename} already exists. Skipping.")
            responses.append(IngestResponse(
                document_id=existing_doc.id,
                filename=safe_filename,
                chunks_created=0,
                message="Document already exists (Duplicate detected)."
            ))
            continue
            
        # Create Document Record
        new_doc = Document(filename=safe_filename, content_hash=content_hash)
        await doc_repo.add(new_doc)
        
        # Save temp file
        temp_path = os.path.join("uploads", f"{new_doc.id}.pdf")
        with open(temp_path, "wb") as f:
            f.write(file_content)
            
        # Dispatch background task
        background_tasks.add_task(
            process_document_background,
            new_doc.id,
            temp_path,
            doc_repo,
            vector_store,
            parser,
            chunker,
            embeddings
        )
        
        responses.append(IngestResponse(
            document_id=new_doc.id,
            filename=safe_filename,
            chunks_created=-1,
            message="Processing initiated in background."
        ))
        
    return responses
