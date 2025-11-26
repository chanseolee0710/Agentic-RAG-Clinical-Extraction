# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import documents, llm, agent, fhir, workflow
from .config import settings


app = FastAPI(
    title="AI Medical Backend",
    version="0.3.0",
)




@app.on_event("startup")
def on_startup():
    """
    Initialize the DB on startup.
    """
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------
# Routers
# ----------------------

# Document CRUD (Part 1)
app.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"],
)

# LLM endpoints: summarize, RAG QA (Parts 2 & 3)
app.include_router(
    llm.router,
    tags=["llm"],
)

# Agent for structured data extraction (Part 4)
app.include_router(
    agent.router,
    prefix="/agent",
    tags=["agent"],
)

# FHIR mapping (Part 5)
app.include_router(
    fhir.router,
    tags=["fhir"],
)

# Full workflow
app.include_router(
    workflow.router,
    tags=["workflow"],
)

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")