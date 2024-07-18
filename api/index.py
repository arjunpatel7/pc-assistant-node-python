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
    print('upload_demo_pdfs')
    '''
    This function takes our existing demo pdfs and uploads them to the given assistant
    returns a message indicating the response after uploading the files 

    Takes in an assistant object, and returns the response from the upload
    '''
    from os import listdir
    from os.path import join, isfile, abspath, dirname
    print('post_import')

    # Sanity check: List all files in the project root
    project_root = abspath(dirname(__file__))
    root_files = listdir(project_root)
    print(f"Files in project root: {root_files}")

    docs_dir = join(project_root, 'docs')
    print(f"Looking for PDFs in: {docs_dir}")
    
    if not isfile(docs_dir):
        print(f"Error: {docs_dir} is not a valid directory")
        return f"Error: {docs_dir} is not a valid directory"

    pdf_files = [f for f in listdir(docs_dir) if isfile(join(docs_dir, f)) and f.endswith('.pdf')]
    print(f"PDF files found: {pdf_files}")
    
    errors = []
    for pdf_file in pdf_files:
        pdf_path = join(docs_dir, pdf_file)
        logging.info(f"Uploading file: {pdf_path}")
        print(f"Uploading file: {pdf_path}, print statement")
        try:
            response = assistant.upload_file(file_path=pdf_path, timeout=None)
            logging.info(f"Uploaded {pdf_path}: {response}")
            print(f"Uploaded {pdf_path}: {response}, print statement")
        except Exception as e:
            error_msg = f"Error uploading {pdf_path}: {str(e)}"
            logging.error(error_msg)
            print(error_msg + ", print statement")
            errors.append(pdf_file)

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
    print("Checking assistant prerequisites, print statement")
    
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ASSISTANT_NAME = os.getenv('PINECONE_ASSISTANT_NAME')

    logging.info(f"PINECONE_API_KEY exists: {bool(PINECONE_API_KEY)}")
    logging.info(f"PINECONE_ASSISTANT_NAME exists: {bool(PINECONE_ASSISTANT_NAME)}")

    if not PINECONE_API_KEY or not PINECONE_ASSISTANT_NAME:
        logging.error("Missing required environment variables")
        print("Missing required environment variables, print statement")
        return None, None, None

    try:
        logging.info("Initializing Pinecone client")
        pc = Pinecone(api_key=PINECONE_API_KEY)
        logging.info("Pinecone client initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing Pinecone client: {str(e)}")
        print(f"Error initializing Pinecone client: {str(e)}, print statement")
        return None, None, None

    try:
        logging.info("Listing assistants")
        assistants = pc.assistant.list_assistants()
        logging.info(f"Number of assistants found: {len(assistants)}")
    except Exception as e:
        logging.error(f"Error listing assistants: {str(e)}")
        print(f"Error listing assistants: {str(e)}, print statement")
        return pc, PINECONE_ASSISTANT_NAME, None

    assistant_exists = any(assistant.name == PINECONE_ASSISTANT_NAME for assistant in assistants)
    logging.info(f"Assistant '{PINECONE_ASSISTANT_NAME}' exists: {assistant_exists}")

    return pc, PINECONE_ASSISTANT_NAME, assistant_exists

def handle_new_assistant(pc, assistant_name):
    """Handle logic for creating a new assistant."""
    logging.info(f"Entering handle_new_assistant function for '{assistant_name}'")
    print(f"Entering handle_new_assistant function for '{assistant_name}', print statement")
    
    try:
        logging.info(f"Attempting to create assistant '{assistant_name}'")
        print(f"Attempting to create assistant '{assistant_name}', print statement")
        assistant = pc.assistant.create_assistant(
            assistant_name=assistant_name, 
            timeout=30
        )
        logging.info(f"Assistant '{assistant_name}' created successfully")
        print(f"Assistant '{assistant_name}' created successfully, print statement")
    except Exception as e:
        logging.error(f"Error creating assistant: {str(e)}")
        print(f"Error creating assistant: {str(e)}, print statement")
        raise  # Re-raise the exception to be caught in the bootstrap_thread

    logging.info("Starting PDF upload process")
    print("Starting PDF upload process, print statement")
    try:
        logging.info("Calling upload_demo_pdfs function")
        print("Calling upload_demo_pdfs function, print statement")
        upload_result = upload_demo_pdfs(assistant)
        logging.info(f"Upload result: {upload_result}")
        print(f"Upload result: {upload_result}, print statement")
    except Exception as e:
        logging.error(f"Error uploading demo PDFs: {str(e)}")
        print(f"Error uploading demo PDFs: {str(e)}, print statement")
        raise  # Re-raise the exception to be caught in the bootstrap_thread

    logging.info("Assistant creation and PDF upload completed successfully")
    print("Assistant creation and PDF upload completed successfully, print statement")

    return {
        "status": "success", 
        "message": f"Assistant '{assistant_name}' created successfully and demo PDFs uploaded."
    }

@app.route("/api/bootstrap")
def bootstrap():
    logging.info("Starting bootstrap process")
    print("Starting bootstrap process, print statement")

    pc, assistant_name, assistant_exists = check_assistant_prerequisites()
    
    logging.info(f"check_assistant_prerequisites returned: pc={bool(pc)}, assistant_name={bool(assistant_name)}, assistant_exists={assistant_exists}")
    print(f"check_assistant_prerequisites returned: pc={bool(pc)}, assistant_name={bool(assistant_name)}, assistant_exists={assistant_exists}, print statement")

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
            try:
                logging.info(f"Bootstrap thread started for assistant '{assistant_name}'")
                print(f"Bootstrap thread started for assistant '{assistant_name}', print statement")
                result = handle_new_assistant(pc, assistant_name)
                logging.info(f"Bootstrap thread completed: {result}")
                print(f"Bootstrap thread completed: {result}, print statement")
            except Exception as e:
                logging.error(f"Error in bootstrap thread: {str(e)}")
                print(f"Error in bootstrap thread: {str(e)}, print statement")
        
        print("Creating thread, print statement")
        try:
            thread = threading.Thread(target=bootstrap_thread, args=(pc, assistant_name))
            thread.start()
            logging.info("Bootstrap thread started successfully")
            print("Bootstrap thread started successfully, print statement")
        except Exception as e:
            logging.error(f"Error starting bootstrap thread: {str(e)}")
            print(f"Error starting bootstrap thread: {str(e)}, print statement")
            return jsonify({
                "status": "error",
                "message": f"Failed to start bootstrap process: {str(e)}"
            }), 500

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
