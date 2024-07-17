from flask import Flask, request
import os
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

app = Flask(__name__)


def upload_demo_pdfs(assistant):
    '''
    This function takes our existing demo pdfs and uploads them to the given assistant

    returns a message indicating the response after uploading the files 

    Takes in an assistant object, and returns the response from the upload
    '''

    # Define the pretend path for PDFs
    pdf_paths = [
        "/path/to/demo1.pdf",
        "/path/to/demo2.pdf",
        "/path/to/demo3.pdf"
    ]

    # Upload each PDF to the assistant

    # list for checking which documents failed to upload
    errors = []

    for pdf_path in pdf_paths:
        response = assistant.upload_file(file_path=pdf_path, timeout=None)
        print(f"Uploaded {pdf_path}: {response}")
        if response.status_code != 200:
            errors.append(pdf_path)
    
    if errors:
        error_message = "The following files failed to upload: " + ", ".join(errors)
        print(error_message)
        return error_message
    
    return "Files uploaded!"


def check_assistant_docs_ready(assistant):
    '''
    This function checks the documents in the given assistant

    returns a message indicating the response after checking the documents 
    '''

    files = assistant.list_files()
    if not files:
        return False

    while True:
        all_ready = True
        all_failed = True

        for file in files:
            if file['status'] == "processing":
                all_ready = False
            elif file['status'] == "ready":
                all_failed = False

        if all_ready or not all_failed:
            return True
        elif all_failed:
            return False
        else:
            return False
    

        # Wait for a short period before checking again
        # Refresh the file statuses
    


@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/bootstrap")
def bootstrap_assistant():
    ''' After initializing application, assists creation of or access to Pinecone Assistant

    If PINECONE_API_KEY exists and PINECONE_ASSISTANT_NAME is valid and exists, 
    the assistant will be accessed and returned. 

    If PINECONE_API_KEY exists and PINECONE_ASSISTANT_NAME is valid and does not exist, 
    the assistant will first be created, and provided with a set of fixed local documents.

    This involves reading the local documents into memory, looping through them if needed and 
    uploading them to the created assistant. The Assistant API handles PDF ingestion! 

    Returns the created assistant

    '''
    # check the required key and names first, and error out if missing

    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ASSISTANT_NAME = os.getenv('PINECONE_ASSISTANT_NAME')

    if not PINECONE_API_KEY or not PINECONE_ASSISTANT_NAME:
  
        return f"<p>Error: PINECONE_API_KEY {PINECONE_API_KEY} and PINECONE_ASSISTANT_NAME {PINECONE_ASSISTANT_NAME} are required.</p>"


    from pinecone import Pinecone

    # Initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # List assistants to check if the assistant with the given name exists
    assistants = pc.assistant.list_assistants()
    assistant_exists = any(assistant.name == PINECONE_ASSISTANT_NAME for assistant in assistants)

    if assistant_exists:
        # Load the assistant for querying
        assistant = pc.assistant.describe_assistant(PINECONE_ASSISTANT_NAME)
        
        # Check if the assistant has documents
        files = assistant.list_files()
        if len(files) > 0:
            # add code here for accessing the assistant somehow 
            print(f"Assistant '{PINECONE_ASSISTANT_NAME}' accessed successfully with existing documents.")
            response = {
                "status": "success",
                "message": f"Assistant '{PINECONE_ASSISTANT_NAME}' accessed successfully with existing documents."
            }
            return response, 200
        else:
            # Proceed to upload local demo PDFs to the assistant
            # Assuming we have a function to upload local demo PDFs
            upload_demo_pdfs(assistant)
            is_ready = check_assistant_docs_ready(assistant)
            if is_ready:
                return f"<p>Assistant '{PINECONE_ASSISTANT_NAME}' accessed successfully and demo PDFs uploaded.</p>"
            else:
                return f"<p>Assistant '{PINECONE_ASSISTANT_NAME}' failed to upload documents.</p>"
    

    # In this case, assistant does not exist, so we have to create it and pre-load it with data
    


#def hello_bootstrap():
    # Call the ingest route internally
    #ingest_response = hello_ingest()
    # Return bootstrap's own message
    #return f"<p>Hello, bootstrap function! (Ingest called: {ingest_response})</p>"

@app.route("/api/ingest")
def hello_ingest():
    return "<p>Hello, ingest function!</p>"