# Clinical Extraction using Agentic RAG

Please reach out to Chanseo Lee with any feedback!
The point of this project is to open-source and de-mystify agentic AI to the broader medical research community. It provides an easy-to-use UI and minimal coding knowledge to execute a full clinical extraction workflow using an AI agent and a retrieval-augmented generation (RAG) system.

This project is a comprehensive AI-powered backend for medical documentation, connected to a user-friendly interface. It leverages OpenAI's GPT models to perform various tasks such as summarizing clinical notes, answering questions, extracting structured data, and mapping it to FHIR (Fast Healthcare Interoperability Resources) standards.

## Features

*   **RAG Knowledge Base**: Upload medical guidelines or documents to a knowledge base. Feel free to play around with this feature using some of the included documents, such as the American Association of Family Physicians (AAFP) guidelines provided in the "example_rag_guidelines" folder.
*   **Question Answering**: Ask questions about the uploaded documents using RAG.
*   **Clinical Note Summarization**: Automatically summarize complex clinical notes.
*   **Structured Data Extraction**: Extract patient info, conditions, medications, vitals, and labs from unstructured text.
*   **FHIR Mapping**: Convert extracted data into FHIR-compliant JSON bundles.
*   **Document Management**: View, list, and delete uploaded documents via the web interface.
*   **File Upload**: Upload text files directly for RAG documents and clinical notes.
*   **Token Usage Tracking**: Monitor input, output, and total token usage for each request.

## Prerequisites

*   **Docker** (Recommended for easy setup)
*   **Python 3.11+** (For local development)
*   **OpenAI API Key**: You need a valid API key from OpenAI (or a compatible provider).

## Configuration

The application is model-agnostic and can be configured to use different OpenAI models or compatible providers (like Groq, DeepSeek, etc.) via environment variables in your `.env` file.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | Your API key. | Required |
| `OPENAI_BASE_URL` | Base URL for the API (optional). Use this for other providers. | `None` (OpenAI default) |
| `LLM_MODEL` | The name of the chat model to use. | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | The name of the embedding model to use. | `text-embedding-3-small` |

**Example `.env` for Groq:**
```bash
OPENAI_API_KEY=your_groq_api_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=text-embedding-3-small
```

## Setup & Installation

### Option 1: Docker (Recommended)

1.  **Clone the repository** (if you haven't already).
2.  **Create a `.env` file** in the root directory and add your OpenAI API key:
    ```bash
    OPENAI_API_KEY=sk-your-api-key-here
    ```
3.  **Build and Run**:
    ```bash
    docker compose up --build
    ```
4.  **Access the App**: Open your browser and go to `http://localhost:8000`.

### Option 2: Local Development

1.  **Create a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set Environment Variable**:
    ```bash
    export OPENAI_API_KEY=sk-your-api-key-here
    ```
4.  **Run the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```
5.  **Access the App**: Open your browser and go to `http://localhost:8000`.

## Usage Guide

The application provides a simple web interface at `http://localhost:8000`.

1.  **RAG Knowledge Base**:
    *   **Upload**: Enter a title and paste content (or upload a text file) in the "RAG Knowledge Base" section. Click "Upload RAG Document".
    *   **Manage**: Use the "Manage Documents" section to list, view, or delete uploaded documents.

2.  **Run Full Workflow**:
    *   **Clinical Note**: Paste a medical note (or upload a text file) in the "Clinical Note" section.
    *   **Question (Optional)**: Ask a question related to the note or the RAG knowledge base.
    *   **Run**: Click "Run Full Workflow".
    *   **Results**: The application will display:
        *   **Summary**: A concise summary of the note.
        *   **RAG Answer**: An answer to your question based on the uploaded documents.
        *   **Structured Extraction**: JSON data extracted from the note.
        *   **FHIR Bundle**: The extracted data formatted as a FHIR bundle.

3.  **API Endpoints**:
    The API endpoints are available at `http://localhost:8000/docs`.
    *   `POST /full_workflow`: Runs the complete analysis pipeline.
    *   `GET /documents/`: List all documents.
    *   `POST /documents/`: Upload a new document.
    *   `GET /documents/{doc_id}`: Get details (including content) of a specific document.
    *   `DELETE /documents/{doc_id}`: Delete a document.
    *   `POST /summarize`: Summarize a text.
    *   `POST /agent`: Run the agentic workflow.

## Code Structure

Here is a breakdown of the project structure and what each file does:

*   **`app/`**: Main application directory.
    *   **`main.py`**: The entry point of the FastAPI application. It sets up the API routers and static file serving.
    *   **`config.py`**: Handles configuration settings (like loading environment variables).
    *   **`db.py`**: Database setup and connection logic (using SQLite and SQLAlchemy).
    *   **`models.py`**: SQLAlchemy database models (defines the `Document` table).
    *   **`schemas.py`**: Pydantic models for data validation and API request/response structures.
    *   **`rag.py`**: Implements the Retrieval-Augmented Generation logic (embedding and searching documents).
    *   **`llm_client.py`**: Client for interacting with OpenAI's API (for summarization).
    *   **`fhir_mapper.py`**: Logic for mapping structured data to FHIR resources.
    *   **`agent.py`**: Orchestrates the "agentic" workflow (planning and execution).
    *   **`routers/`**: Contains API route definitions.
        *   **`documents.py`**: Endpoints for managing RAG documents (create, list, view, delete).
        *   **`workflow.py`**: The main endpoint (`/full_workflow`) that ties everything together.
        *   **`llm.py`**: Endpoint for simple summarization.
        *   **`agent.py`**: Endpoint for the agentic workflow.
        *   **`fhir.py`**: Endpoint for FHIR conversion.
    *   **`static/`**: Contains static assets.
        *   **`index.html`**: The frontend user interface.

*   **`Dockerfile`**: Instructions for building the Docker image.
*   **`docker-compose.yml`**: Configuration for running the application with Docker.
*   **`requirements.txt`**: List of Python dependencies.
