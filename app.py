from flask import Flask, render_template, request, jsonify
from disease_info_system import DiseaseInfoSystem
import requests
import os

app = Flask(__name__)

# Initialize the disease information system (as fallback)
csv_file = "clean_disease_data.csv"
disease_system = DiseaseInfoSystem(csv_file)

# Rasa server configuration
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

@app.route('/')
def index():
    """Main page"""
    diseases = disease_system.get_available_diseases()
    return render_template('index.html', diseases=diseases)

@app.route('/api/query', methods=['POST'])
def query():
    """API endpoint to process disease queries via Rasa"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        user_id = data.get('user_id', 'web_user')  # For conversation tracking
        
        if not user_query:
            return jsonify({
                'status': 'error',
                'message': 'Please enter a question or disease name.'
            })
        
        # Try to get response from Rasa server first
        try:
            rasa_payload = {
                "sender": user_id,
                "message": user_query
            }
            
            rasa_response = requests.post(
                RASA_SERVER_URL, 
                json=rasa_payload,
                timeout=10
            )
            
            if rasa_response.status_code == 200:
                rasa_data = rasa_response.json()
                print(f"DEBUG: Rasa response: {rasa_data}")  # Debug log
                
                if rasa_data and len(rasa_data) > 0:
                    # Combine all responses from Rasa
                    bot_messages = []
                    for msg in rasa_data:
                        if msg.get('text'):
                            bot_messages.append(msg.get('text'))
                    
                    # Join all messages with newlines
                    bot_message = '\n\n'.join(bot_messages) if bot_messages else ''
                    
                    return jsonify({
                        'status': 'success',
                        'response': bot_message,
                        'query': user_query,
                        'source': 'rasa'
                    })
            
        except requests.exceptions.RequestException as rasa_error:
            print(f"Rasa server error: {rasa_error}")
            # Fall back to direct CSV processing
            pass
        
        # Fallback to direct disease system if Rasa is unavailable
        print("Falling back to direct CSV processing")
        response = disease_system.process_query(user_query)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'query': user_query,
            'source': 'fallback'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        })

@app.route('/api/diseases')
def get_diseases():
    """API endpoint to get all available diseases"""
    try:
        diseases = disease_system.get_available_diseases()
        return jsonify({
            'status': 'success',
            'diseases': diseases
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found!")
        print("Please ensure the file exists in the current directory.")
        exit(1)
    
    print("🏥 Starting ArogyaAI Web Application with Rasa Integration...")
    print(f"📊 Loaded {len(disease_system.get_available_diseases())} diseases")
    print("🤖 Rasa Integration: Primary (with CSV fallback)")
    print("🌐 Web Interface: http://localhost:5000")
    print("📝 Note: Make sure to start Rasa server (port 5005) and actions (port 5055)")
    print("   Command 1: rasa run --enable-api --cors='*'")
    print("   Command 2: rasa run actions")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
