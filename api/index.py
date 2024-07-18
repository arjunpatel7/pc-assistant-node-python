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

        for file in files:
            if file.status == "ProcessingFailed":
                return f"File {file.name} failed to process"
            if file.status == "Available":
                completed_files.add(file.id)

        if len(completed_files) == len(files):
            done = True
            return True
        if time.time() - start_time > timeout:
            logging.error("Time out error: Files are not available within 3 minutes")
            return False
        time.sleep(3)  # Wait for a short period before checking again

    return False

def check_assistant_prerequisites():
    """Check API key and assistant name."""
    logging.info("Checking assistant prerequisites")
    
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ASSISTANT_NAME = os.getenv('PINECONE_ASSISTANT_NAME')

    if not PINECONE_API_KEY or not PINECONE_ASSISTANT_NAME:
        logging.error("Missing required environment variables")
        return None, None

    pc = Pinecone(api_key=PINECONE_API_KEY)
    assistants = pc.assistant.list_assistants()
    assistant_exists = any(assistant.name == PINECONE_ASSISTANT_NAME for assistant in assistants)

    return pc, PINECONE_ASSISTANT_NAME, assistant_exists

def handle_new_assistant(pc, assistant_name):
    """Handle logic for creating a new assistant."""
    logging.info(f"Creating new assistant '{assistant_name}'")
    
    assistant = pc.assistant.create_assistant(
        assistant_name=assistant_name, 
        timeout=30
    )

    logging.info(f"Assistant '{assistant_name}' created successfully")

    upload_result = upload_demo_pdfs(assistant)
    logging.info(f"Upload result: {upload_result}")
    
    logging.info("Assistant created successfully")
    with app.app_context():
        return jsonify({
            "status": "success", 
            "message": f"Assistant '{assistant_name}' created successfully."
        }), 200

@app.route("/api/bootstrap")
def bootstrap():
    logging.info("Starting bootstrap process")

    pc, assistant_name, assistant_exists = check_assistant_prerequisites()
    
    if not pc or not assistant_name:
        return jsonify({
            "status": "error", 
            "message": "PINECONE_API_KEY and PINECONE_ASSISTANT_NAME are required."
        }), 400

    if assistant_exists:
        logging.info(f"Assistant '{assistant_name}' already exists. Bootstrapping not required.")
        return jsonify({
            "status": "success", 
            "message": f"Assistant '{assistant_name}' already exists. Bootstrapping not required."
        }), 200
    else:
        import threading
        def bootstrap_thread(pc, assistant_name):
            handle_new_assistant(pc, assistant_name)
        
        threading.Thread(target=bootstrap_thread, args=(pc, assistant_name)).start()
        return jsonify({
            "status": "success", 
            "message": f"Assistant '{assistant_name}' is being created and demo PDFs are being uploaded."
        }), 202

@app.route("/api/done")
def check_done():
    logging.info("Checking if documents are done processing")

    pc, assistant_name, assistant_exists = check_assistant_prerequisites()
    
    if not pc or not assistant_name:
        return jsonify({
            "status": "error", 
            "message": "PINECONE_API_KEY and PINECONE_ASSISTANT_NAME are required."
        }), 400

    if not assistant_exists:
        return jsonify({
            "status": "error", 
            "message": f"Assistant '{assistant_name}' does not exist."
        }), 404

    assistant = pc.assistant.describe_assistant(assistant_name)
    is_ready = check_assistant_docs_ready(assistant)
    if is_ready:
        return jsonify({
            "status": "success", 
            "message": "All documents are processed and available."
        }), 200
    else:
        return jsonify({
            "status": "processing", 
            "message": "Documents are still processing."
        }), 202

