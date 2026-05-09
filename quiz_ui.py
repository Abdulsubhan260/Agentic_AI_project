import streamlit as st
import requests
import PyPDF2
import json
import random
st.title("QuizMaster AI ")

uploaded_file = st.file_uploader("Upload your PDF study material", type="pdf")


if uploaded_file is not None:
    
    
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    st.info(f"Extracted {len(text)} characters from the PDF.")

    
    
    api_payload = {
        "file_text": text,
        "file_name": uploaded_file.name  
    }


    
    response = requests.post("http://localhost:8000/upload", json=api_payload)
    if response.status_code == 200:
        st.success("Backend: " + response.json().get("message"))
    else:
        st.error("Failed to process document on backend.")


    quiz_topic=st.text_input("Enter topic...")
    if st.button("Generate Quiz_questions"):
        if quiz_topic:
            quiz_payload={
                "topic":quiz_topic,
                "file_name":uploaded_file.name
            }
            response=requests.post("http://localhost:8000/generate_quiz",json=quiz_payload)
            raw_string = response.json()["quiz"]
            quiz_dict = json.loads(raw_string)
            st.write(f"### {quiz_dict['question']}")
            options = quiz_dict['options']
            random.shuffle(options)
            
            
            st.radio("Select an option", options, index=None)

            with st.expander("Reveal Answer"):

                st.write(f"**Correct Answer:** {quiz_dict['correct_answer']}")
                
                st.write(f"**Explanation:** {quiz_dict['explanation']}")

            
