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

# Enhanced health responses with more medical knowledge
HEALTH_RESPONSES = {
    # Greetings
    "hello": "Hello! I'm Dr.Doom, your friendly health education companion. I can help with prevention tips, symptoms, and vaccination schedules. I support many languages—just type in your preferred language and I'll switch. What would you like to know today?",
    "hi": "Hi there! I'm here to help with health information, disease prevention, and symptoms guidance. How can I assist you?",
    "greet": "Hello! I'm Dr.Doom, your friendly health education companion. I can help with prevention tips, symptoms, and vaccination schedules. What would you like to know today?",
    
    # Disease Information
    "malaria": "Malaria is transmitted by infected mosquitoes. Symptoms include fever, chills, headache, and nausea. Prevention: Use mosquito nets, wear long sleeves, and eliminate stagnant water. Seek immediate medical attention if symptoms occur.",
    "dengue": "Dengue is spread by Aedes mosquitoes. Symptoms: High fever, severe headache, eye pain, muscle pain, rash. Prevention: Remove standing water, use mosquito repellent. Warning signs include persistent vomiting and difficulty breathing - seek immediate care.",
    "diabetes": "Diabetes affects blood sugar control. Type 2 can be prevented with healthy diet, regular exercise, and weight management. Symptoms include excessive thirst, frequent urination, and fatigue. Regular checkups are important.",
    "tuberculosis": "TB is a bacterial infection affecting lungs. Symptoms: Persistent cough (>3 weeks), fever, night sweats, weight loss. It's curable with proper medication. Always complete the full course of treatment.",
    "covid": "COVID-19 prevention: Wear masks, maintain social distance, wash hands frequently, get vaccinated. Symptoms range from mild to severe. Seek medical care if breathing difficulties occur.",
    "hypertension": "High blood pressure prevention: Reduce salt intake, exercise regularly, maintain healthy weight, limit alcohol, manage stress. Often called 'silent killer' - regular checkups important.",
    
    # Symptoms
    "fever": "Fever is body's response to infection. Management: Rest, stay hydrated, use paracetamol if needed. Seek medical care if fever >101°F (38.3°C) persists >3 days or with severe symptoms.",
    "headache": "Common causes: dehydration, stress, eye strain. Management: Rest in quiet dark room, stay hydrated, gentle head massage. Seek care for severe, sudden, or recurring headaches.",
    "cough": "Cough types: Dry (viral) or productive (bacterial). Management: Stay hydrated, honey for throat, rest. See doctor if persistent >3 weeks, bloody sputum, or with fever.",
    "stomach pain": "Stomach pain can have many causes. Mild pain: Rest, light foods, stay hydrated. Seek immediate care for severe pain, vomiting blood, or signs of appendicitis.",
    "chest pain": "Chest pain needs evaluation. Could be heart, lung, or muscle related. Seek immediate emergency care for crushing pain, shortness of breath, or pain radiating to arm/jaw.",
    
    # Vaccination
    "vaccine": "Vaccines are safe and effective. Children need vaccines for polio, measles, hepatitis, etc. Adults need flu shots, COVID boosters. Follow your local vaccination schedule.",
    "vaccination schedule": "Vaccination schedules vary by age. Infants: BCG, Hepatitis B, Polio at birth. Children: Multiple doses of DPT, MMR, etc. Consult healthcare provider for personalized schedule.",
    
    # Emergency
    "emergency": "For medical emergencies in India, call 108. Signs needing immediate care: Difficulty breathing, chest pain, severe bleeding, unconsciousness, severe allergic reactions.",
    
    # Prevention
    "prevention": "General health tips: Balanced diet, regular exercise, adequate sleep, stress management, regular checkups, avoid smoking/excessive alcohol, maintain hygiene.",
    
    # Hindi responses
    "मलेरिया": "मलेरिया मच्छरों से फैलता है। लक्षण: बुखार, ठंड लगना, सिरदर्द। बचाव: मच्छरदानी का उप्योग करें, पानी जमा न होने दें। तुरंत डॉक्टर से मिलें।",
    "डेंगू": "डेंगू एडीज मच्छर से फैलता है। लक्षण: तेज बुखार, सिरदर्द, मांसपेशियों में दर्द। बचाव: पानी जमा न होने दें, मच्छर भगाने वाली दवा का प्रयोग करें।",
    "हिंदी": "मैं हिंदी में आपकी सहायता कर सकता हूं। स्वास्थ्य संबंधी कोई भी प्रश्न पूछें - बीमारियों, लक्षणों, या बचाव के बारे में।",
    
    # Default
    "default": "I'm a health education assistant. I can help with disease information, symptoms, prevention tips, and vaccination schedules. Please consult healthcare professionals for specific medical advice."
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
        
        # Intelligent keyword matching with priority
        response_text = HEALTH_RESPONSES["default"]
        
        # Check for exact matches first
        if user_message in HEALTH_RESPONSES:
            response_text = HEALTH_RESPONSES[user_message]
        else:
            # Check for partial matches with priority scoring
            best_match = None
            best_score = 0
            
            for keyword, response in HEALTH_RESPONSES.items():
                if keyword == "default":
                    continue
                
                # Calculate match score
                score = 0
                keyword_lower = keyword.lower()
                
                if keyword_lower in user_message:
                    score = len(keyword_lower)  # Longer keywords get priority
                elif any(word in user_message for word in keyword_lower.split()):
                    score = len(keyword_lower) * 0.5  # Partial word match
                
                if score > best_score:
                    best_score = score
                    best_match = response
            
            if best_match:
                response_text = best_match
        
        return jsonify([{"text": response_text}]), 200
        
    except Exception as e:
        return jsonify([{"text": "I'm having some technical difficulties. Please try again later."}]), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🏥 Starting Healthcare Chatbot Fallback Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)