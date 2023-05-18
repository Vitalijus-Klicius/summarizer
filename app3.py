import streamlit as st
from docx2txt import process as docx_process
import io
import base64
import openai
import time
import docx

# Function to extract and preprocess text from document
# Function to download result as txt file
def get_text_download_link(text):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="output.txt">Download Results as .txt</a>'

    
def text_preprocessing(file, split_lenght: int):
    
    import tiktoken
    from docx import Document
    
    def split_text_into_chunks(doc: str, lenght: int):

        def decode_chunks(text):
            return enc.decode(text)

        def divide_chunks(l, n):
            # looping till length l
            for i in range(0, len(l), n):
                yield l[i:i + n]   

        enc = tiktoken.get_encoding("cl100k_base")

        data_tokenized = enc.encode(doc) 
        # How many elements each
        # list should have
        n = lenght

        x = list(divide_chunks(data_tokenized, n))

        output_list = list(map(decode_chunks, x))

        return output_list

    doc_doc = Document(io.BytesIO(file.read()))
    doc = ' '.join([p.text for p in doc_doc.paragraphs])

    result = split_text_into_chunks(doc, split_lenght)
    
    return result

def make_request(question_input: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{question_input}"},
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
        if api_key == '':
            st.write("Please provide your OpenAI API key.")

        else:
            openai.api_key = api_key
        
        if uploaded_file is not None:
            chunks = text_preprocessing(uploaded_file, chunk_size)
    
        else:
            st.write("Please provide some input (text and file).")
        
        sumarized = []
        for val in chunks:
            
            text = command + val
            
            st.write("Number of words in chunk: ~",len(val.split()))
            
            output = make_request(text)
            response_text = output["choices"][0]["message"]["content"]
            
            st.write("Number of words in summarized text: ~",len(response_text.split()))

            time.sleep(20)
            
            sumarized.append(output["choices"][0]["message"]["content"])
        
        results_txt = "\n\n".join(sumarized)
        st.markdown(get_text_download_link(results_txt), unsafe_allow_html=True)

if __name__ == "__main__":
    main()