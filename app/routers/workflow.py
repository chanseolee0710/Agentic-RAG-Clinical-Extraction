# app/routers/workflow.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import schemas
from ..llm_client import summarize_note
from ..llm_client import summarize_note
from ..rag import rag
from ..agent import extract_structured_note
from ..fhir_mapper import structured_to_fhir

router = APIRouter(tags=["workflow"])


class FullWorkflowRequest(BaseModel):
    note: str
    question: str | None = None  # for RAG (optional)


@router.post("/full_workflow", response_model=schemas.FullWorkflowResponse)
def full_workflow(body: FullWorkflowRequest):
    """
    Orchestrates the full end-to-end workflow:
    1) Summarize note
    2) (Optional) RAG answer to a question
    3) Agent: structured extraction
    4) FHIR Bundle conversion
    """
    try:
        total_usage = schemas.TokenUsage()

        # 1) Summarize note
        summary, sum_usage = summarize_note(body.note)
        if sum_usage:
            total_usage.input_tokens += sum_usage.prompt_tokens
            total_usage.output_tokens += sum_usage.completion_tokens
            total_usage.total_tokens += sum_usage.total_tokens

        # 2) RAG question (optional)
        rag_answer = None
        if body.question:
            # rag.answer returns a dict with "answer", "used_documents", and "usage"
            result = rag.answer(body.question, note=body.note)
            rag_answer = result["answer"]
            rag_usage = result.get("usage")
            if rag_usage:
                total_usage.input_tokens += rag_usage.prompt_tokens
                total_usage.output_tokens += rag_usage.completion_tokens
                total_usage.total_tokens += rag_usage.total_tokens

        # 3) Structured extraction
        structured, struct_usage = extract_structured_note(body.note)
        if struct_usage:
            total_usage.input_tokens += struct_usage.prompt_tokens
            total_usage.output_tokens += struct_usage.completion_tokens
            total_usage.total_tokens += struct_usage.total_tokens

        # 4) FHIR conversion
        fhir_bundle = structured_to_fhir(structured)

        return schemas.FullWorkflowResponse(
            summary=summary,
            rag_answer=rag_answer,
            structured=structured,
            fhir=fhir_bundle,
            usage=total_usage,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
