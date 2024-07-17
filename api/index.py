from flask import Flask, request
import os


app = Flask(__name__)

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
        return "<p>Error: PINECONE_API_KEY and PINECONE_ASSISTANT_NAME are required.</p>"


    from pinecone import Pinecone

    # Initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # List assistants to check if the assistant with the given name exists
    assistants = pc.assistant.list_assistants()
    assistant_exists = any(assistant['name'] == PINECONE_ASSISTANT_NAME for assistant in assistants['assistants'])

    if assistant_exists:
        # Load the assistant for querying
        assistant = pc.assistant.get_assistant(PINECONE_ASSISTANT_NAME)
        
        # Check if the assistant has documents
        files = assistant.list_files()
        if len(files['files']) > 0:
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
            return f"<p>Assistant '{PINECONE_ASSISTANT_NAME}' accessed successfully and demo PDFs uploaded.</p>"
    

    # In this case, assistant does not exist, so we have to create it and pre-load it with data
    


#def hello_bootstrap():
    # Call the ingest route internally
    ingest_response = hello_ingest()
    # Return bootstrap's own message
    #return f"<p>Hello, bootstrap function! (Ingest called: {ingest_response})</p>"

@app.route("/api/ingest")
def hello_ingest():
    return "<p>Hello, ingest function!</p>"