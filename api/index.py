from flask import Flask, request, jsonify, Response, stream_with_context
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env.local
load_dotenv('.env.local')

app = Flask(__name__)

def check_assistant_prerequisites():
    """Check API key and assistant name."""
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ASSISTANT_NAME = os.getenv('PINECONE_ASSISTANT_NAME')

    print(f"Checking prerequisites: API Key: {'Set' if PINECONE_API_KEY else 'Not Set'}, Assistant Name: {PINECONE_ASSISTANT_NAME}")

    if not PINECONE_API_KEY or not PINECONE_ASSISTANT_NAME:
        print("Error: PINECONE_API_KEY or PINECONE_ASSISTANT_NAME is missing.")
        return None, None

    return PINECONE_API_KEY, PINECONE_ASSISTANT_NAME

@app.route("/api/check_assistant")
def check_assistant():
    api_key, assistant_name = check_assistant_prerequisites()
    
    if not api_key or not assistant_name:
        logger.error("Prerequisites check failed.")
        return jsonify({
            "status": "error", 
            "message": "PINECONE_API_KEY and PINECONE_ASSISTANT_NAME are required.",
            "exists": False
        }), 400

    logger.info(f"Initializing Pinecone with API key: {api_key[:5]}...")
    try:
        pc = Pinecone(api_key=api_key)
        logger.info("Pinecone initialized successfully.")
    except Exception as e:
        logger.exception(f"Error initializing Pinecone: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to initialize Pinecone: {str(e)}",
            "exists": False
        }), 500

    logger.info("Listing assistants...")
    try:
        assistants = pc.assistant.list_assistants()
        logger.info(f"Found {len(assistants)} assistants.")
    except Exception as e:
        logger.exception(f"Error listing assistants: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to list assistants: {str(e)}",
            "exists": False
        }), 500

    assistant_exists = any(assistant.name == assistant_name for assistant in assistants)

    if assistant_exists:
        print(f"Assistant '{assistant_name}' exists.")
    else:
        print(f"Assistant '{assistant_name}' does not exist.")

    return jsonify({
        "status": "success", 
        "message": f"Assistant '{assistant_name}' check completed.",
        "exists": assistant_exists,
        "assistant_name": assistant_name
    }), 200

@app.route("/api/list_assistant_files")
def list_assistant_files():
    api_key, assistant_name = check_assistant_prerequisites()
    
    if not api_key or not assistant_name:
        logger.error("Prerequisites check failed.")
        return jsonify({
            "status": "error", 
            "message": "PINECONE_API_KEY and PINECONE_ASSISTANT_NAME are required.",
            "files": []
        }), 400

    try:
        pc = Pinecone(api_key=api_key)
        
        # Get the assistant
        assistant = pc.assistant.Assistant(assistant_name=assistant_name)
        
        # List files in the assistant
        files = assistant.list_files()
        
        file_data = [{
            "id": file.id,
            "name": file.name,
            "size": file.size,
            "created_at": file.created_on  # Changed from created_at to created_on
        } for file in files]

        return jsonify({
            "status": "success",
            "message": f"Files for assistant '{assistant_name}' retrieved successfully.",
            "files": file_data
        }), 200

    except Exception as e:
        logger.exception(f"Error listing assistant files: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to list assistant files: {str(e)}",
            "files": []
        }), 500

@app.route("/api/chat", methods=['POST'])
def chat():
    api_key, assistant_name = check_assistant_prerequisites()
    
    if not api_key or not assistant_name:
        return jsonify({
            "status": "error", 
            "message": "PINECONE_API_KEY and PINECONE_ASSISTANT_NAME are required."
        }), 400

    try:
        pc = Pinecone(api_key=api_key)
        assistant = pc.assistant.describe_assistant(assistant_name)

        data = request.json
        user_message = data.get('message')
        chat_history = data.get('history', [])

        if not user_message:
            return jsonify({
                "status": "error",
                "message": "No message provided in the request."
            }), 400

        chat_context = [Message(content=msg['content'], role=msg['role']) for msg in chat_history]
        chat_context.append(Message(content=user_message, role='user'))

        def generate():
            response = assistant.chat_completions(messages=chat_context, stream=True)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
            yield "data: [DONE]\n\n"

        return Response(stream_with_context(generate()), content_type='text/event-stream')

    except Exception as e:
        logger.exception(f"Error in chat: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to process chat: {str(e)}"
        }), 500
