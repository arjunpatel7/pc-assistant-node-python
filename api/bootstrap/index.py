from flask import Flask
app = Flask(__name__)

@app.route("/api/bootstrap")
def hello_bootstrap():
    return "<p>Hello, bootstrap function!</p>"

