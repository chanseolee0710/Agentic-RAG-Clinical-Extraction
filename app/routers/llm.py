# app/routers/llm.py
from fastapi import APIRouter, HTTPException

from .. import schemas
from ..llm_client import summarize_note
from ..rag import rag


router = APIRouter()


@router.post("/summarize_note", response_model=schemas.SummarizeResponse)
def summarize_endpoint(body: schemas.SummarizeRequest):
    try:
        summary, _ = summarize_note(body.note)
        return schemas.SummarizeResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer_question", response_model=schemas.AnswerResponse)
def answer_question_endpoint(body: schemas.QuestionRequest):
    try:
        result = rag.answer(body.question)
        return schemas.AnswerResponse(
            answer=result["answer"],
            used_documents=result["used_documents"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
