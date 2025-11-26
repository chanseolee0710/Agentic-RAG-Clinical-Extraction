# app/routers/documents.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.DocumentRead])
def list_documents(db: Session = Depends(get_db)):
    """
    Return a list of all documents (id, title).
    """
    return db.query(models.Document).all()


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """
    Delete a document by ID.
    """
    db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(db_doc)
    db.commit()
    return None


@router.post(
    "/", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED
)
def create_document(doc: schemas.DocumentCreate, db: Session = Depends(get_db)):
    """
    Create a new document with title and content.

    Request body: { "title": "...", "content": "..." }
    Response: { "id": 1, "title": "..." }
    """
    db_doc = models.Document(title=doc.title, content=doc.content)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


@router.get("/{doc_id}", response_model=schemas.DocumentReadContent)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single document by ID.

    If not found, returns 404.
    """
    db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc
