# 🐍 Python Tutor: Agentic RAG Tutor
An autonomous AI Mentor that teaches Python by retrieving curriculum from a Vector Database and executing/testing student code in real-time.

##  Architecture
- **Brain:** Groq Llama-3.3-70B via API.
- **Memory (RAG):** ChromaDB with `all-MiniLM-L6-v2` embeddings for dynamic syllabus injection.
- **Hands (Agent):** Custom Tool Dispatcher using Python's `exec()` for autonomous code testing.
- **Backend:** FastAPI (Decoupled Microservice).
- **Frontend:** Streamlit Chat Interface.

## Key Features
- **Stateful Memory:** Remembers student context across messages.
- **Zero-Hallucination:** Strictly follows the provided syllabus in ChromaDB.
- **Live Code Execution:** AI physically tests student code and explains traceback errors.