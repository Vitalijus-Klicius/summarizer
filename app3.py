import streamlit as st
import io
import base64
import openai
import time
from docx import Document
import tiktoken

# Function to download the result as a txt file
def get_text_download_link(text):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="output.txt">Download Results as .txt</a>'

# Function to split text into chunks
def split_text_into_chunks(text, max_length):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text) 
    chunks = []
    current_chunk = []
    current_length = 0
    for token in tokens:
        if current_length + 1 <= max_length:
            current_chunk.append(token)
            current_length += 1
        else:
            chunks.append(current_chunk)
            current_chunk = [token]
            current_length = 1
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# Function to extract and preprocess text from document
def preprocess_text(file, max_length):
    document = Document(io.BytesIO(file.read()))
    text = ' '.join([p.text for p in document.paragraphs])
    return split_text_into_chunks(text, max_length)

# Function to make OpenAI API request
def make_request(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": text},
        ]
    )
    return response

# Streamlit App
def main():
    st.title("Text Processing with ChatGPT")

    api_key = st.text_input("Enter your OpenAI API key", type="password")
    chunk_size = st.slider("Select chunk size in tokens", 100, 3900, 1000)
    command = st.text_area("Enter some text","Summarize the following text, as it would be yours and you would be the author, please  avoid such text as 'in this text' or 'author discusses':  ")
    uploaded_file = st.file_uploader("Upload a file (.docx)")

    if st.button('Process'):
        if not api_key:
            st.write("Please provide your OpenAI API key.")
            return
        if not uploaded_file:
            st.write("Please provide a document to process.")
            return
        
        openai.api_key = api_key
        chunks = preprocess_text(uploaded_file, chunk_size)
        summarized = []
        
        for chunk in chunks:
            st.write("Number of words in chunk: ~", len(chunk))
            text = command + chunk
            response = make_request(text)
            summarized_chunk = response["choices"][0]["message"]["content"]
            st.write("Number of words in summarized text: ~", len(summarized_chunk))
            time.sleep(20)
            summarized.append(summarized_chunk)
        
        results_txt = "\n\n".join(summarized)
        st.markdown(get_text_download_link(results_txt), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
