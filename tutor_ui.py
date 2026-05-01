import streamlit as st
import requests

st.title("🐍 MY AI: Python Tutor")
st.caption("Write some Python code and I will test it for you!")


if "messages" not in st.session_state:
    st.session_state.messages =[
        {"role": "system", "content": "You are a strict Python teacher. Never give full code. Ask the student to write the code. If they write code, you MUST use your run_student_code tool to test it."}
    ]


for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]: 
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


prompt = st.chat_input("write your Python code or question here...")

if prompt:
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    
    api_data = {
        "conversation_history": st.session_state.messages 
    }

    try:
        
        response = requests.post("http://localhost:8000/chat", json=api_data) 
        
        
        ai_reply = response.json()["reply"]
        
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        with st.chat_message("assistant"):
            st.write(ai_reply)
            
    except Exception as e:
        st.error(f"Backend connection failed: {e}")