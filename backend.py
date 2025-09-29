from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from disease_info_system import DiseaseInfoSystem
from translation_service import get_translation_service
import requests
import os
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="ArogyaAI API",
    description="Intelligent Health Assistant API with Rasa Integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now - you can restrict this later
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the disease information system (as fallback)
csv_file = "clean_disease_data.csv"
disease_system = DiseaseInfoSystem(csv_file)

# Initialize translation service
translation_service = get_translation_service()

# Rasa server configuration
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    user_id: str = "web_user"

class QueryResponse(BaseModel):
    status: str
    response: str = ""
    query: str = ""
    source: str = ""
    message: str = ""
    detected_language: str = ""
    was_translated: bool = False
    english_query: str = ""

class DiseasesResponse(BaseModel):
    status: str
    diseases: list = []
    message: str = ""

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ArogyaAI API Server",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query (POST)",
            "diseases": "/api/diseases (GET)",
            "docs": "/docs"
        }
    }

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """API endpoint to process disease queries via Rasa with multilingual support"""
    try:
        user_query = request.query.strip()
        user_id = request.user_id
        
        if not user_query:
            raise HTTPException(
                status_code=400, 
                detail="Please enter a question or disease name."
            )
        
        # Define the processing function for existing logic
        def process_english_query(english_query: str) -> str:
            """Process the query in English using existing Rasa/CSV system"""
            # Try to get response from Rasa server first
            try:
                rasa_payload = {
                    "sender": user_id,
                    "message": english_query
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
                        if bot_message:
                            return bot_message
                
            except requests.exceptions.RequestException as rasa_error:
                print(f"Rasa server error: {rasa_error}")
                # Fall back to direct CSV processing
                pass
            
            # Fallback to direct disease system if Rasa is unavailable
            print("Falling back to direct CSV processing")
            return disease_system.process_query(english_query)
        
        # Use multilingual processing if translation service is available
        if translation_service:
            result = translation_service.process_multilingual_query(
                user_query, 
                process_english_query
            )
        else:
            # Fallback to English-only processing
            english_response = process_english_query(user_query)
            result = {
                'original_query': user_query,
                'detected_language': 'English',
                'english_query': user_query,
                'english_response': english_response,
                'final_response': english_response,
                'was_translated': False
            }
        
        # Determine source
        source = "multilingual-rasa" if not result.get('error') else "multilingual-fallback"
        
        return QueryResponse(
            status="success",
            response=result['final_response'],
            query=user_query,
            source=source,
            detected_language=result['detected_language'],
            was_translated=result['was_translated'],
            english_query=result['english_query']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred: {str(e)}"
        )

@app.get("/api/diseases", response_model=DiseasesResponse)
async def get_diseases():
    """API endpoint to get all available diseases"""
    try:
        diseases = disease_system.get_available_diseases()
        return DiseasesResponse(
            status="success",
            diseases=diseases
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rasa_available": await check_rasa_health(),
        "diseases_loaded": len(disease_system.get_available_diseases()),
        "multilingual_support": translation_service is not None,
        "groq_api_available": translation_service is not None
    }

@app.get("/api/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    supported_languages = [
        "English", "Spanish", "French", "German", "Italian", 
        "Chinese", "Japanese", "Korean", "Hindi", "Arabic", 
        "Portuguese", "Russian", "Dutch", "Swedish", "Turkish"
    ]
    return {
        "status": "success",
        "supported_languages": supported_languages,
        "note": "ArogyaAI can detect and respond in multiple languages automatically"
    }

async def check_rasa_health():
    """Check if Rasa server is available"""
    try:
        response = requests.get("http://localhost:5005/", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found!")
        print("Please ensure the file exists in the current directory.")
        exit(1)
    
    print("🏥 Starting ArogyaAI FastAPI Backend...")
    print(f"📊 Loaded {len(disease_system.get_available_diseases())} diseases")
    print("🤖 Rasa Integration: Primary (with CSV fallback)")
    print("🌍 Multilingual Support: Enabled (Groq API)")
    print("🌐 API Server: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🗣️ Supported Languages: English, Spanish, French, German, Italian, Chinese, Japanese, Korean, Hindi, Arabic, and more")
    print("📝 Note: Make sure to start Rasa server (port 5005) and actions (port 5055)")
    print("   Command 1: rasa run --enable-api --cors='*'")
    print("   Command 2: rasa run actions")
    
    uvicorn.run(
        "backend:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )