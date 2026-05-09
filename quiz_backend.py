import chromadb
from groq import Groq
import os
import random 
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("quiz_db")

def chunk_text(text, chunk_size, chunk_overlap):
    chunks =[]
    start = 0
    len_of_text = len(text)
    while start < len_of_text:
        end = start + chunk_size
        chunk_slice = text[start:end]
        chunks.append(chunk_slice)

        start = start + (chunk_size - chunk_overlap)
    return chunks

def ingest_document(raw_text: str, doc_name: str):

    my_chunks = chunk_text(text=raw_text, chunk_size=500, chunk_overlap=50)
    document_embeddings = model.encode(my_chunks).tolist()
    dynamic_ids = [f"{doc_name}_{i}" for i in range(len(my_chunks))]


    dynamic_metadatas = [{"source": doc_name}] * len(my_chunks)
    collection.add(
        documents=my_chunks,
        embeddings=document_embeddings,
        ids=dynamic_ids,
        metadatas=dynamic_metadatas
    )


# sample_text = "Photosynthesis is the process used by plants to convert light energy into chemical energy. Cellular respiration is the process of breaking down sugar into ATP."
# ingest_document(sample_text, "Biology_chapter_1")
print("Ingestion complete! Check ChromaDB.")

def get_context(topic: str, doc_name: str):
    topic_vector = model.encode(topic).tolist()
    

    
    total_docs = collection.count()
    fetch_count = min(5, total_docs) if total_docs > 0 else 1

    results = collection.query(
        query_embeddings=[topic_vector],
        n_results=fetch_count,
        where={"source": doc_name}
    )

    print(f"DEBUG: Searching for {topic} in {doc_name}")

    if results['documents'] and len(results['documents'][0]) > 0:
        


        random_chunk = random.choice(results['documents'][0])
        return random_chunk
    else:
        return "no relevant study material found in the database for this topic."

quiz_tool =[
    {
      "type": "function",
      "function": {
          "name": "submit_mcqs",
          "description": "Act as world class examiner,read context provided and use this tool to generate exactly one question.",
          "parameters": {
              "type": "object",
              "properties": {
                  "question": {"type": "string", "description": "the text of exam question"},
                  "options": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "A list of 4 possible answers"
                  },
                  "correct_answer": {"type": "string", "description": "The correct answer from option list"},
                  "explanation": {"type": "string", "description": "Explanation of why the ans is correct"}
              },
              "required":["question", "options", "correct_answer", "explanation"]
          }
      }
    }
]

class IngestRequest(BaseModel):
    file_text: str
    
    file_name: str
    
app = FastAPI()

@app.post("/upload")
def upload_pdf_Api(req: IngestRequest):
    
    ingest_document(req.file_text, req.file_name)

    return {"status": "Success", "message": "Document ingested"}

class QuizRequest(BaseModel):
    topic: str
    file_name: str

@app.post("/generate_quiz")

def generate_quiz_Api(req: QuizRequest):

    retrieved_context = get_context(req.topic, req.file_name)
    
    first_response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        max_tokens=500,

        temperature=0.9, 


        tools=quiz_tool,
        tool_choice={"type": "function", "function": {"name": "submit_mcqs"}},
        messages=[
            {
                "role": "system",
                "content": "Act as world class examiner, read context provided to you and use 'submit_mcqs' tool to generate exactly one question. Never mention the word 'context' or 'database' to student."
            },
            {
                "role": "user",
                "content": f"Context: {retrieved_context}\n\nGenerate ONE highly unique, random question from this context. Focus on minor details or different concepts. Do not ask the most obvious question."
            }
        ]
    )
    



    mcq_json = first_response.choices[0].message.tool_calls[0].function.arguments

    return {"quiz": mcq_json}