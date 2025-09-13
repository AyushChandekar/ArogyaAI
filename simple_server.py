#!/usr/bin/env python3
"""
Simple fallback server for healthcare chatbot
This can be used as a backup if Rasa fails to start properly.
"""
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple health responses
HEALTH_RESPONSES = {
    "hello": "Hello! I'm a basic healthcare assistant. How can I help you?",
    "hi": "Hi there! I'm here to help with basic health information.",
    "fever": "For fever, rest and stay hydrated. If temperature exceeds 101°F (38.3°C) or persists, consult a doctor.",
    "headache": "For headaches, try resting in a quiet, dark room and stay hydrated. If severe or persistent, see a healthcare provider.",
    "cough": "For cough, stay hydrated, use honey (if over 1 year old), and rest. If persistent or with fever, consult a doctor.",
    "default": "I'm a basic health assistant. Please consult a healthcare professional for specific medical advice."
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({"status": "healthy", "service": "healthcare-chatbot-fallback"}), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Healthcare Chatbot Fallback Server",
        "status": "running",
        "endpoints": {
            "/": "This endpoint",
            "/health": "Health check",
            "/webhooks/rest/webhook": "Chat endpoint"
        }
    }), 200

@app.route('/webhooks/rest/webhook', methods=['POST'])
def chat():
    """Simple chat endpoint that mimics Rasa webhook format"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify([{"text": HEALTH_RESPONSES["default"]}]), 200
        
        user_message = data['message'].lower()
        
        # Simple keyword matching
        response_text = HEALTH_RESPONSES["default"]
        for keyword, response in HEALTH_RESPONSES.items():
            if keyword != "default" and keyword in user_message:
                response_text = response
                break
        
        return jsonify([{"text": response_text}]), 200
        
    except Exception as e:
        return jsonify([{"text": "I'm having some technical difficulties. Please try again later."}]), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🏥 Starting Healthcare Chatbot Fallback Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)