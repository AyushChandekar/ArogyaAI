import pandas as pd
import re
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz, process
import warnings
warnings.filterwarnings('ignore')

class DiseaseInfoSystem:
    def __init__(self, csv_file_path):
        """Initialize the disease information system with CSV data"""
        self.csv_file_path = csv_file_path
        self.df = None
        self.load_data()
        
        # Define feature priorities for different query types
        self.feature_priorities = {
            'comprehensive': ['overview', 'causes', 'symptoms', 'precautions', 'home_treatment', 'awareness', 'who_guidelines'],
            'home_treatment': ['home_treatment', 'causes', 'symptoms', 'precautions', 'awareness', 'who_guidelines', 'overview'],
            'treatment': ['home_treatment', 'who_guidelines', 'precautions', 'causes', 'symptoms', 'awareness', 'overview'],
            'causes': ['causes', 'symptoms', 'precautions', 'home_treatment', 'awareness', 'who_guidelines', 'overview'],
            'symptoms': ['symptoms', 'causes', 'precautions', 'home_treatment', 'awareness', 'who_guidelines', 'overview'],
            'precautions': ['precautions', 'symptoms', 'causes', 'home_treatment', 'awareness', 'who_guidelines', 'overview'],
            'prevention': ['precautions', 'causes', 'symptoms', 'home_treatment', 'awareness', 'who_guidelines', 'overview'],
            'awareness': ['awareness', 'overview', 'symptoms', 'causes', 'precautions', 'home_treatment', 'who_guidelines'],
            'guidelines': ['who_guidelines', 'awareness', 'precautions', 'home_treatment', 'symptoms', 'causes', 'overview'],
            'overview': ['overview', 'symptoms', 'causes', 'precautions', 'home_treatment', 'awareness', 'who_guidelines']
        }
        
        # Keywords for different query types
        self.query_keywords = {
            'comprehensive': ['everything', 'comprehensive', 'complete', 'full', 'brief', 'all about', 'all information', 'detailed', 'complete guide', 'full details', 'overview', 'comprehensive information', 'complete information', 'full information', 'all details', 'everything about', 'tell me all', 'comprehensive guide'],
            'home_treatment': ['home treatment', 'home remedy', 'natural treatment', 'home cure', 'traditional treatment', 'ayurvedic', 'herbal'],
            'treatment': ['treatment', 'cure', 'medicine', 'therapy', 'heal'],
            'causes': ['causes', 'reason', 'why', 'how does', 'what causes'],
            'symptoms': ['symptoms', 'signs', 'feel', 'experience'],
            'precautions': ['precautions', 'prevention', 'avoid', 'prevent', 'protect'],
            'prevention': ['prevention', 'prevent', 'avoid', 'protect'],
            'awareness': ['awareness', 'know', 'understand', 'facts'],
            'guidelines': ['guidelines', 'who guidelines', 'medical guidelines', 'recommendations'],
            'overview': ['what is', 'about', 'general', 'information']
        }
    
    def load_data(self):
        """Load disease data from CSV file"""
        try:
            self.df = pd.read_csv(self.csv_file_path)
            # Clean column names
            self.df.columns = [col.strip() for col in self.df.columns]
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            self.df = pd.DataFrame()
    
    def find_disease(self, user_input):
        """Find the best matching disease using fuzzy matching"""
        if self.df.empty:
            return None, 0
        
        diseases = self.df['disease'].tolist()
        user_input_lower = user_input.lower()
        
        # Try exact match first (case insensitive)
        for disease in diseases:
            if disease.lower() == user_input_lower or disease.lower() in user_input_lower:
                return disease, 100
        
        # Try exact word match for disease names
        words = user_input_lower.split()
        for disease in diseases:
            disease_lower = disease.lower()
            # Check if disease name appears as whole word(s)
            if disease_lower in user_input_lower:
                return disease, 95
            # Check if all words of disease name appear in input
            disease_words = disease_lower.split()
            if all(word in user_input_lower for word in disease_words):
                return disease, 90
        
        # Use fuzzy matching with multiple algorithms
        best_score = 0
        best_disease = None
        
        for disease in diseases:
            # Try different fuzzy matching approaches
            scores = [
                fuzz.ratio(user_input_lower, disease.lower()),
                fuzz.partial_ratio(user_input_lower, disease.lower()),
                fuzz.token_sort_ratio(user_input_lower, disease.lower()),
                fuzz.token_set_ratio(user_input_lower, disease.lower())
            ]
            max_score = max(scores)
            if max_score > best_score:
                best_score = max_score
                best_disease = disease
        
        if best_score >= 75:  # Increased threshold to reduce false matches
            return best_disease, best_score
        
        # Try individual words from user input
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                for disease in diseases:
                    if word in disease.lower():
                        return disease, 75
        
        return None, 0
    
    def validate_and_find_disease(self, extracted_entity, user_input):
        """Validate extracted entity and find correct disease if needed"""
        if not extracted_entity:
            return self.find_disease(user_input)
        
        # First check if extracted entity exists exactly
        disease_info = self.get_disease_info(extracted_entity)
        if disease_info:
            return extracted_entity, 100
        
        # If not found, try to find the best match
        return self.find_disease(user_input)
    
    def identify_query_type(self, user_input):
        """Identify what type of information the user is asking for"""
        user_input_lower = user_input.lower()
        
        # Score each query type based on keyword matches
        scores = {}
        for query_type, keywords in self.query_keywords.items():
            scores[query_type] = 0
            for keyword in keywords:
                if keyword in user_input_lower:
                    scores[query_type] += 1
        
        # Return the query type with highest score, default to overview
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'overview'
    
    def get_disease_info(self, disease_name):
        """Get all information for a specific disease"""
        if self.df.empty:
            return None
        
        disease_row = self.df[self.df['disease'].str.lower() == disease_name.lower()]
        
        if disease_row.empty:
            return None
        
        return disease_row.iloc[0].to_dict()
    
    def format_response(self, disease_info, query_type='overview', disease_name=''):
        """Format the response based on query type and priority"""
        if not disease_info:
            return f"❌ Sorry, I couldn't find information about '{disease_name}'. Please check the spelling or try another disease name."
        
        # Get priority order for this query type
        priority_order = self.feature_priorities.get(query_type, self.feature_priorities['overview'])
        
        response_parts = []
        
        # Add header based on query type
        if query_type == 'overview':
            response_parts.append(f"🏥 **Complete Information about {disease_info['disease']}**\n")
        else:
            response_parts.append(f"🔍 **{query_type.replace('_', ' ').title()} for {disease_info['disease']}**\n")
        
        # Add information in priority order
        feature_titles = {
            'overview': '📋 **Overview**',
            'causes': '🔍 **Causes**',
            'symptoms': '⚠️ **Symptoms**',
            'precautions': '🛡️ **Precautions**',
            'home_treatment': '🏠 **Home Treatment**',
            'awareness': '💡 **Awareness**',
            'who_guidelines': '🏛️ **WHO Guidelines**'
        }
        
        for feature in priority_order:
            if feature in disease_info and disease_info[feature] and str(disease_info[feature]).strip():
                content = str(disease_info[feature]).strip()
                if content and content != 'nan':
                    response_parts.append(f"\n{feature_titles.get(feature, f'**{feature.title()}**')}")
                    response_parts.append(f"{content}")
        
        # Add separator
        response_parts.append("\n" + "="*50)
        response_parts.append("💬 Ask me about specific aspects like 'home treatment for asthma' or 'causes of baldness'!")
        
        return "\n".join(response_parts)
    
    def process_query(self, user_input):
        """Process user query and return appropriate response"""
        if not user_input.strip():
            return "❓ Please enter a disease name or ask a question about a specific disease."
        
        # Check for greetings and general queries FIRST
        user_input_lower = user_input.lower().strip()
        general_queries = ['hello', 'hi', 'hey', 'who are you', 'what are you', 'about', 'help', 'what can you do', 'introduce', 'start']
        
        if any(greeting in user_input_lower for greeting in general_queries):
            return """🏥 **Hello! I'm ArogyaAI - Your AI Health Assistant**

🤖 **What I can do:**
• Provide detailed information about 340+ diseases
• Explain symptoms, causes, and precautions
• Suggest home treatments and remedies
• Share WHO guidelines and medical awareness
• Support multiple languages automatically

💬 **How to use me:**
• Ask about any disease: "diabetes symptoms"
• Ask about treatments: "home treatment for asthma"
• Ask about causes: "what causes heart disease"
• Ask in your language: "मधुमेह के लक्षण" (Hindi)

⚠️ **Important:** I provide information for educational purposes. Always consult healthcare professionals for medical advice.

🌟 **Try asking:** "What are the symptoms of diabetes?" or "Home treatment for headache"

==================================================
💬 Ask me about any health condition!"""
        
        # Find disease in the query
        disease_name, confidence = self.find_disease(user_input)
        
        if not disease_name:
            # Suggest available diseases
            diseases_list = ', '.join(self.df['disease'].tolist() if not self.df.empty else [])
            return f"❌ I couldn't find a matching disease. Available diseases include:\n{diseases_list}\n\n💡 Try asking: 'Tell me about asthma' or 'Home treatment for acne'"
        
        # Identify query type
        query_type = self.identify_query_type(user_input)
        
        # Get disease information
        disease_info = self.get_disease_info(disease_name)
        
        # Format and return response
        return self.format_response(disease_info, query_type, disease_name)
    
    def get_available_diseases(self):
        """Get list of all available diseases"""
        if self.df.empty:
            return []
        return self.df['disease'].tolist()
    
    def add_disease(self, disease_data):
        """Add new disease to the dataset (for future expansion)"""
        if self.df.empty:
            self.df = pd.DataFrame([disease_data])
        else:
            self.df = pd.concat([self.df, pd.DataFrame([disease_data])], ignore_index=True)
        
        # Save back to CSV
        self.df.to_csv(self.csv_file_path, index=False)
        print(f"✅ Added new disease: {disease_data.get('disease', 'Unknown')}")
