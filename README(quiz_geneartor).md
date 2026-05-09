#  QuizMaster AI: Agentic RAG Assessment Generator

An autonomous, full-stack AI platform that transforms any educational PDF into interactive, hallucination-free Multiple Choice Questions (MCQs) using an Agentic Retrieval-Augmented Generation (RAG) architecture.

##  System Architecture

This project is built using a decoupled **Microservices** architecture, separating the heavy data-processing backend from the lightweight user interface.

- **The Brain (LLM):** Groq API (Llama-3) utilizing strict JSON function-calling (Agentic Tools) to format MCQs and prevent conversational filler.
- **The Memory (Vector DB):** ChromaDB with `all-MiniLM-L6-v2` embeddings for semantic search.
- **The Backend (API):** FastAPI with Pydantic for strict data validation and endpoint routing.
- **The Frontend (UI):** Streamlit for file uploading, state management (`st.session_state`), and dynamic quiz rendering.
- **Document Processing:** `PyPDF2` combined with custom mathematical chunking and overlap logic to preserve context window integrity.

##  Key Features

1. **Context-Grounded Generation:** The AI is mathematically restricted from relying on pre-trained knowledge. It uses ChromaDB to fetch specific paragraphs from the uploaded PDF and bases the quiz *only* on that localized data.
2. **Context Roulette:** The backend fetches multiple semantic matches and randomly selects one to ensure the user receives a unique question every time they click "Generate."
3. **Automated Option Shuffling:** The UI dynamically shuffles the MCQ options so the correct answer is not biased toward a default position.
4. **Agentic Tool Calling:** Instead of standard text generation, the LLM is forced to pass its output through a strict JSON Schema, ensuring predictable software integration.

##  Tech Stack
- **Python 3**
- **FastAPI & Uvicorn**
- **Streamlit**
- **ChromaDB & SentenceTransformers**
- **Groq Cloud API**
- **PyPDF2**