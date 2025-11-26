# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


# ---------- Documents ----------

class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentRead(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True


class DocumentReadContent(DocumentRead):
    content: str


# ---------- Summarization ----------

class SummarizeRequest(BaseModel):
    note: str


class SummarizeResponse(BaseModel):
    summary: str


# ---------- RAG Question Answering ----------

class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    used_documents: List[int]


# ---------- Structured Data Extraction (Part 4) ----------

class PatientInfo(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None  # "male", "female", "other", etc.


class Condition(BaseModel):
    name: str
    icd10_code: Optional[str] = None


class Medication(BaseModel):
    name: str
    dose: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    rxnorm_code: Optional[str] = None


class VitalSign(BaseModel):
    type: str          # e.g., "blood pressure"
    value: str         # e.g., "140/90"
    unit: Optional[str] = None  # e.g., "mmHg"


class LabResult(BaseModel):
    name: str          # e.g., "HbA1c"
    value: Optional[str] = None         # e.g., "7.2"
    unit: Optional[str] = None  # e.g., "%"


class PlanItem(BaseModel):
    description: str   # e.g., "Start lisinopril 10 mg daily"


class StructuredNote(BaseModel):
    patient: Optional[PatientInfo] = None
    conditions: List[Condition] = []
    medications: List[Medication] = []
    vitals: List[VitalSign] = []
    labs: List[LabResult] = []
    plan: List[PlanItem] = []


class ExtractStructuredRequest(BaseModel):
    note: str


class ExtractStructuredResponse(BaseModel):
    structured: StructuredNote


# ---------- FHIR Mapping (Part 5) ----------

class ToFhirRequest(BaseModel):
    structured: StructuredNote


class ToFhirResponse(BaseModel):
    # We keep this generic; it's a FHIR-like Bundle or collection of resources.
    fhir: Dict[str, Any]


# ---------- Token Usage ----------

class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


# ---------- Full Workflow ----------

class FullWorkflowResponse(BaseModel):
    summary: str
    rag_answer: str | None = None
    structured: StructuredNote
    fhir: Dict[str, Any]
    usage: TokenUsage
