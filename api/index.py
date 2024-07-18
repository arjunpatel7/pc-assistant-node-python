from flask import Flask, request, jsonify, current_app
import os
from dotenv import load_dotenv
import logging
from pinecone import Pinecone

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
        logging.info(f"Uploading file: {pdf_path}")
        response = assistant.upload_file(file_path=pdf_path, timeout=None)
        logging.info(f"Uploaded {pdf_path}: {response}")

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
    import time

    start_time = time.time()
    timeout = 3 * 60  # 3 minutes

    completed_files = set([])
    done = False
    while not done:
        # get files
        files = assistant.list_files()
        logging.info(f"List of files: {files}")
        files = assistant.list_files()

        for file in files:
            if file.status == "ProcessingFailed":
                return f"File {file.name} failed to process"
            if file.status == "Available":
                # ids should be unique, so this should be fine
                completed_files.add(file.id)

        
        if len(completed_files) == len(files):
            done = True
            return True
        if time.time() - start_time > timeout:
            
            logging.error("Time out error: Files are not available within 3 minutes")
            return False
    return False
        


        # Wait for a short period before checking again
        # Refresh the file statuses
    

def check_assistant_prerequisites():
    """Check API key, assistant name, and assistant existence."""
    logging.info("Checking assistant prerequisites")
    
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ASSISTANT_NAME = os.getenv('PINECONE_ASSISTANT_NAME')

    if not PINECONE_API_KEY or not PINECONE_ASSISTANT_NAME:
        logging.error("Missing required environment variables")
        return None, None, None

    pc = Pinecone(api_key=PINECONE_API_KEY)
    assistants = pc.assistant.list_assistants()
    assistant_exists = any(assistant.name == PINECONE_ASSISTANT_NAME for assistant in assistants)

    return pc, PINECONE_ASSISTANT_NAME, assistant_exists

def handle_existing_assistant(pc, assistant_name):
    """Handle logic for an existing assistant."""
    logging.info(f"Handling existing assistant '{assistant_name}'")
    
    assistant = pc.assistant.describe_assistant(assistant_name)
    files = assistant.list_files()
    
    if len(files) > 0:
        logging.info(f"Assistant '{assistant_name}' has existing documents")
        return jsonify({"status": "success", "message": f"Assistant '{assistant_name}' accessed successfully with existing documents."}), 200

    return process_assistant_documents(assistant, assistant_name, is_new=False)

def handle_new_assistant(pc, assistant_name):
    """Handle logic for creating a new assistant."""
    logging.info(f"Creating new assistant '{assistant_name}'")
    
    metadata = {"author": "System", "version": "1.0"}
    assistant = pc.assistant.create_assistant(
        assistant_name=assistant_name, 
        metadata=metadata, 
        timeout=30
    )
    logging.info(f"Assistant '{assistant_name}' created successfully")

    return process_assistant_documents(assistant, assistant_name, is_new=True)

def process_assistant_documents(assistant, assistant_name, is_new):
    """Upload documents and check readiness."""
    logging.info(f"Processing documents for assistant '{assistant_name}'")
    
    upload_result = upload_demo_pdfs(assistant)
    logging.info(f"Upload result: {upload_result}")

    is_ready = check_assistant_docs_ready(assistant)
    if is_ready:
        logging.info("Documents are ready")
        action = "created" if is_new else "accessed"
        return jsonify({
            "status": "success", 
            "is_new": is_new,
            "message": f"Assistant '{assistant_name}' {action} successfully and demo PDFs uploaded."
        }), 200
    else:
        logging.error("Failed to upload documents")
        return jsonify({
            "status": "error", 
            "is_new": is_new,
            "message": f"Assistant '{assistant_name}' failed to upload documents."
        }), 500

@app.route("/api/bootstrap")
def bootstrap():
    from flask import jsonify
    import threading

    def run_bootstrap():
        with app.app_context():
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

    pc, assistant_name, assistant_exists = check_assistant_prerequisites()
    
    if not pc or not assistant_name:
        return jsonify({
            "status": "error", 
            "message": "PINECONE_API_KEY and PINECONE_ASSISTANT_NAME are required."
        }), 400

    if assistant_exists:
        return handle_existing_assistant(pc, assistant_name)
    else:
        return handle_new_assistant(pc, assistant_name)