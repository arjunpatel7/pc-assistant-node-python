from flask import Flask, request
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env.local
load_dotenv('.env.local')

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_demo_pdfs(assistant):
    '''
    This function takes our existing demo pdfs and uploads them to the given assistant

    returns a message indicating the response after uploading the files 

    Takes in an assistant object, and returns the response from the upload
    '''
    from glob import glob

    # Use glob to find all PDF files in the ./docs directory
    pdf_paths = glob(os.path.join('docs', '*.pdf'))

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
    

@app.route("/api/bootstrap")
def bootstrap():
    from flask import jsonify
    import threading

    def run_bootstrap():
        result = bootstrap_assistant()
        print(f"Bootstrap completed: {result}")

    # Start the bootstrap_assistant function in a separate thread
    thread = threading.Thread(target=run_bootstrap)
    thread.start()

    # Return an immediate response to the client
    return jsonify({"status": "success", "message": "Bootstrap process started in the background."})


@app.route("/api/ingest")
def bootstrap_assistant():
    logging.info("Starting bootstrap_assistant function")

    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ASSISTANT_NAME = os.getenv('PINECONE_ASSISTANT_NAME')

    if not PINECONE_API_KEY or not PINECONE_ASSISTANT_NAME:
        logging.error(f"Missing required environment variables: PINECONE_API_KEY={PINECONE_API_KEY}, PINECONE_ASSISTANT_NAME={PINECONE_ASSISTANT_NAME}")
        return f"<p>Error: PINECONE_API_KEY and PINECONE_ASSISTANT_NAME are required.</p>"

    logging.info("Initializing Pinecone client")
    from pinecone import Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)

    logging.info("Checking if assistant exists")
    assistants = pc.assistant.list_assistants()
    assistant_exists = any(assistant.name == PINECONE_ASSISTANT_NAME for assistant in assistants)

    if assistant_exists:
        logging.info(f"Assistant '{PINECONE_ASSISTANT_NAME}' found")
        assistant = pc.assistant.describe_assistant(PINECONE_ASSISTANT_NAME)
        
        files = assistant.list_files()
        if len(files) > 0:
            logging.info(f"Assistant '{PINECONE_ASSISTANT_NAME}' has existing documents")
            response = {
                "status": "success",
                "message": f"Assistant '{PINECONE_ASSISTANT_NAME}' accessed successfully with existing documents."
            }
            return response, 200
        else:
            logging.info(f"Assistant '{PINECONE_ASSISTANT_NAME}' has no documents. Uploading demo PDFs")
            upload_result = upload_demo_pdfs(assistant)
            logging.info(f"Upload result: {upload_result}")
            
            logging.info("Checking if documents are ready")
            is_ready = check_assistant_docs_ready(assistant)
            if is_ready:
                logging.info("Documents are ready")
                return f"<p>Assistant '{PINECONE_ASSISTANT_NAME}' accessed successfully and demo PDFs uploaded.</p>"
            else:
                logging.error("Failed to upload documents")
                return f"<p>Assistant '{PINECONE_ASSISTANT_NAME}' failed to upload documents.</p>"
    else:
        logging.info(f"Assistant '{PINECONE_ASSISTANT_NAME}' does not exist")
        # Add code here to create the assistant and pre-load it with data
        logging.info("Creating new assistant and pre-loading data")
        # ... (add your implementation here)

    logging.info("bootstrap_assistant function completed")