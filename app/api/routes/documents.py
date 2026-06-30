from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.dependencies import get_document_repo, get_vector_store
from app.schemas.domain import DocumentResponse
from app.repositories.document import DocumentRepository
from app.services.vectorstore.base import VectorStore

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0, limit: int = 100, 
    repo: DocumentRepository = Depends(get_document_repo)
):
    docs = await repo.get_all(skip, limit)
    return [
        DocumentResponse(id=d.id, filename=d.filename, status=d.status, created_at=d.created_at)
        for d in docs
    ]

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str, 
    repo: DocumentRepository = Depends(get_document_repo)
):
    doc = await repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(id=doc.id, filename=doc.filename, status=doc.status, created_at=doc.created_at)

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    repo: DocumentRepository = Depends(get_document_repo),
    vector_store: VectorStore = Depends(get_vector_store)
):
    doc = await repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from DB (cascades to chunks)
    await repo.delete(doc)
    
    # Delete from Vector Store
    await vector_store.delete_by_document(doc_id)
    
    return {"status": "success", "message": f"Document {doc_id} deleted."}
