# app/routers/fhir.py

from fastapi import APIRouter, HTTPException

from .. import schemas
from ..fhir_mapper import structured_to_fhir

router = APIRouter(tags=["fhir"])


@router.post("/to_fhir", response_model=schemas.ToFhirResponse)
def to_fhir_endpoint(body: schemas.ToFhirRequest):
    """
    Takes the structured data (from Part 4) and returns a simplified FHIR-like JSON Bundle.
    """
    try:
        bundle = structured_to_fhir(body.structured)
        return schemas.ToFhirResponse(fhir=bundle)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
