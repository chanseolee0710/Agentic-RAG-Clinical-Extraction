# app/rag.py

"""
Simple Retrieval-Augmented Generation (RAG) implementation.

- Reads documents from the database
- Embeds them using OpenAI embeddings
- On a question:
  - Embeds the question
  - Finds most similar documents using cosine similarity
  - Sends context + question to the chat model
"""

from typing import List, Tuple

import numpy as np
from openai import OpenAI

from .config import settings
from .db import SessionLocal
from . import models


# Create an OpenAI client
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)


def _embed_texts(texts: List[str]) -> np.ndarray:
    """
    Get embeddings for a list of texts using OpenAI embeddings API.
    """
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set for embeddings.")

    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
    )

    vectors = [item.embedding for item in response.data]
    return np.array(vectors, dtype="float32")


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    """
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-8
    return float(np.dot(a, b) / denom)


class SimpleRAG:
    """
    Minimal in-memory RAG system.
    """

    def __init__(self) -> None:
        self.doc_ids: List[int] = []
        self.doc_texts: List[str] = []
        self.embeddings: np.ndarray | None = None

    def build_index_from_db(self) -> None:
        """
        Load all documents and build embeddings.
        """
        db = SessionLocal()
        docs = db.query(models.Document).all()
        db.close()

        self.doc_ids = [d.id for d in docs]
        self.doc_texts = [d.content for d in docs]

        if not self.doc_texts:
            self.embeddings = None
            return

        self.embeddings = _embed_texts(self.doc_texts)

    def _ensure_index_built(self) -> None:
        if self.embeddings is None:
            self.build_index_from_db()

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[int, str]]:
        """
        Return the top-k most similar documents to the query.
        """
        self._ensure_index_built()

        if self.embeddings is None or not self.doc_texts:
            return []

        query_vec = _embed_texts([query])[0]

        sims = [
            _cosine_sim(query_vec, doc_vec)
            for doc_vec in self.embeddings
        ]

        ranked = sorted(
            zip(self.doc_ids, self.doc_texts, sims),
            key=lambda x: x[2],
            reverse=True,
        )

        top = ranked[:k]
        return [(doc_id, text) for doc_id, text, _ in top]

    def answer(self, question: str, note: str | None = None) -> dict:
        """
        Uses retrieved docs to answer the question with grounding.
        """
        contexts = self.retrieve(question, k=3)

        if not contexts:
            context_text = "No background documents found."
        else:
            parts = [
                f"Document {doc_id}:\n{text}"
                for doc_id, text in contexts
            ]
            context_text = "\n\n".join(parts)

        system_prompt = (
            "You are a clinical assistant. "
            "Synthesize an answer by applying the principles in the Context Documents to the specific situation in the Clinical Note. "
            "Combine information from both sources to provide a comprehensive answer. "
            "If the answer is not contained in the context documents or the clinical note, say: "
            "\"I don't know based on the provided information.\""
        )

        user_prompt = f"Context Documents:\n{context_text}\n\n"
        if note:
            user_prompt += f"Current Clinical Note:\n{note}\n\n"
        
        user_prompt += f"Question: {question}\nAnswer:"

        print(f"DEBUG: RAG System Prompt: {system_prompt}")
        print(f"DEBUG: RAG User Prompt: {user_prompt}")

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        answer_text = response.choices[0].message.content.strip()
        used_ids = [doc_id for doc_id, _ in contexts]

        return {
            "answer": answer_text,
            "used_documents": used_ids,
            "usage": response.usage,
        }


# Global RAG instance
rag = SimpleRAG()
