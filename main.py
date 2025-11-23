from flask import Flask, render_template, request, redirect, jsonify
import json
import logging

from dashboard.backend_api import api_blueprint

app = Flask(__name__)

# Register API blueprint  
app.register_blueprint(api_blueprint, url_prefix="/api")


@app.route("/")
def home():
    return "RFQ Level 6 Backend is Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
