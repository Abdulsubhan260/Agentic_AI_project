import os
import io
import chromadb
from sentence_transformers import SentenceTransformer
import sys

import json
from fastapi import FastAPI

from pydantic import BaseModel
from dotenv import load_dotenv

from groq import Groq


load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI()



embed_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client()
syllabus_collection = chroma_client.get_or_create_collection("python_syllabus")


lessons =[
    "Lesson 1: Variables. Python uses variables to store data. Example: x = 5. Do not teach anything else until they master this.",
    "Lesson 2: Loops. Python uses 'for' and 'while' loops to repeat actions. Example: for i in range(5): print(i).",
    "Lesson 3: Functions. Python uses 'def' to create reusable blocks of code. Example: def greet(): print('Hello')."
]
syllabus_collection.add(
    documents=lessons,
    embeddings=embed_model.encode(lessons).tolist(),
    ids=["l1", "l2", "l3"]
)
print("Syllabus loaded into ChromaDB!")

class TutorChatRequest(BaseModel):
    conversation_history: list


def run_student_code(code: str):
    bucket = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = bucket
    try:
        exec(code)
        output = bucket.getvalue() or "Code ran successfully but didn't print anything."
    except Exception as e:
        output = f"crash  Error: {type(e).__name__}: {str(e)}"
    finally:
        sys.stdout = old_stdout
    return output


tutor_tools =[{
    "type": "function",
    "function": {
        "name": "run_student_code",
        "description": "Execute the student's Python code to check for errors.",
        "parameters": {
            "type": "object",
            "properties": {"code": {"type": "string", "description": "The exact Python code."}},
            "required": ["code"]
        }
    }
}]


@app.post("/chat")
def chat_with_my_AI(req: TutorChatRequest):
    history = req.conversation_history
    
    
    
    last_user_message = history[-1]["content"] 
    
    
    question_vector = embed_model.encode(last_user_message).tolist()
    results = syllabus_collection.query(query_embeddings=[question_vector], n_results=1)
    
    found_lesson = results["documents"][0][0]
    
    
    history[0]["content"] = f"You are a strict Python teacher.never give full code. Test their code using the run_student_code tool. today s  RELEVANT LESSON: {found_lesson}"


    
    response1 = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history,
        tools=tutor_tools,
        tool_choice="auto"
    )
    
    ai_message = response1.choices[0].message
    
    


    if ai_message.tool_calls:
        
        tool_call = ai_message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments) 
        student_code = arguments["code"]
        
        
        execution_result = run_student_code(student_code) 
        
        
        history.append({
            "role": "assistant",
            "content": None,
            "tool_calls":[{"id": tool_call.id, "type": "function", "function": {"name": tool_call.function.name, "arguments": tool_call.function.arguments}}]
        })
        
        
        history.append({
            "role": "tool", 
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": execution_result
        })
        
        



        response2 = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=history
        )
        final_reply = response2.choices[0].message.content
        return {"reply": final_reply}
        
    else:
        
        return {"reply": ai_message.content}

