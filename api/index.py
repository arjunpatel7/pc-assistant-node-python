from flask import Flask, request

app = Flask(__name__)

@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/bootstrap")
def hello_bootstrap():
    # Call the ingest route internally
    ingest_response = hello_ingest()
    # Return bootstrap's own message
    return f"<p>Hello, bootstrap function! (Ingest called: {ingest_response})</p>"

@app.route("/api/ingest")
def hello_ingest():
    return "<p>Hello, ingest function!</p>"