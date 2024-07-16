from flask import Flask
import os

app = Flask(__name__)

# This route uses a "fire and forget" pattern in order to:
# 1. Return a response to the client quickly
# 2. Allow a long-running background task to complete
@app.route("/api/bootstrap", methods=["POST"])
def bootstrap():
    # Assuming initiate_bootstrapping is an async function

    #initiate_bootstrapping(os.environ.get("PINECONE_INDEX"))
    return {"success": True}, 200

