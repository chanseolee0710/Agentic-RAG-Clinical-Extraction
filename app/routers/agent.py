# app/routers/agent.py

from fastapi import APIRouter, HTTPException

from .. import schemas
from ..agent import extract_structured_note

# NOTE: no prefix here; prefix is added in main.py
router = APIRouter(tags=["agent"])


@router.post("/extract_structured", response_model=schemas.ExtractStructuredResponse)
def extract_structured_endpoint(body: schemas.ExtractStructuredRequest):
    """
    Takes a raw clinical note and returns structured data
    enriched with ICD-10 and RxNorm codes.
    """
    try:
        structured = extract_structured_note(body.note)
        return schemas.ExtractStructuredResponse(structured=structured)
    except Exception as e:
        # In production, you'd have more granular error handling and logging
        raise HTTPException(status_code=500, detail=str(e))
