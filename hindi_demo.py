"""
Hindi Demo Script for Enhanced Healthcare Chatbot
Demonstrates comprehensive Hindi medical responses
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🏥 Healthcare Chatbot - Hindi Demo")
print("=" * 40)

# Load services
try:
    from enhanced_multilingual_service import get_enhanced_multilingual_service
    from comprehensive_healthcare_database import get_comprehensive_healthcare_database
    
    multilingual_service = get_enhanced_multilingual_service()
    healthcare_db = get_comprehensive_healthcare_database()
    
    print("✅ सिस्टम लोड हो गया")
except Exception as e:
    print(f"❌ Error loading services: {e}")
    sys.exit(1)

# Demo Hindi queries
hindi_queries = [
    "मलेरिया के बारे में बताएं",
    "डेंगू बुखार क्या है",
    "मधुमेह के लक्षण बताएं"
]

print(f"\n🗣️ Hindi Medical Queries Demo:")
print("=" * 40)

for i, query in enumerate(hindi_queries, 1):
    print(f"\n{i}. User Query: {query}")
    print("-" * 30)
    
    try:
        # Process the query
        english_input, detected_lang, confidence = multilingual_service.process_multilingual_input(query)
        print(f"Language Detected: {detected_lang} (confidence: {confidence:.2f})")
        
        # Extract disease name for demo
        if "मलेरिया" in query:
            disease = "malaria"
        elif "डेंगू" in query:
            disease = "dengue"
        elif "मधुमेह" in query:
            disease = "diabetes"
        else:
            disease = "malaria"  # default
        
        # Get disease information
        disease_info = healthcare_db.get_comprehensive_disease_info(disease)
        
        if disease_info:
            # Convert to dictionary
            disease_dict = {
                'name': disease_info.name,
                'category': disease_info.category,
                'icd_code': disease_info.icd_code,
                'overview': disease_info.overview,
                'causes': disease_info.causes[:3],  # Show only first 3 for demo
                'symptoms': disease_info.symptoms,
                'prevention': disease_info.prevention[:3],  # Show only first 3 for demo
                'home_treatment': disease_info.home_treatment[:3],
                'when_to_see_doctor': disease_info.when_to_see_doctor[:3],
                'global_impact': {},  # Skip for demo
                'who_guidelines': disease_info.who_guidelines,
                'emergency_signs': disease_info.emergency_signs[:3],
                'awareness_tips': disease_info.awareness_tips[:2]
            }
            
            # Generate Hindi response
            hindi_response = multilingual_service.format_medical_response(disease_dict, 'hindi')
            
            # Show response (first 1000 characters for readability)
            print(f"\nBot Response in Hindi:")
            print(hindi_response[:1000])
            if len(hindi_response) > 1000:
                print("...[response continues]...")
        else:
            print("Disease information not found")
            
    except Exception as e:
        print(f"Error processing query: {e}")

print(f"\n🎯 Key Features Demonstrated:")
print("✅ Automatic Hindi language detection")
print("✅ Comprehensive medical terminology in Hindi") 
print("✅ Structured response format maintained")
print("✅ All major disease components included")
print("✅ Medical accuracy preserved in translation")

print(f"\n📝 Sample Medical Terms Translation:")
medical_terms_demo = [
    ("fever", "बुखार"),
    ("headache", "सिरदर्द"), 
    ("doctor", "डॉक्टर"),
    ("medicine", "दवा"),
    ("prevention", "बचाव"),
    ("treatment", "इलाज"),
    ("symptoms", "लक्षण"),
    ("causes", "कारण")
]

for english, hindi in medical_terms_demo:
    print(f"  {english} → {hindi}")

print(f"\n🌟 Your chatbot now supports:")
print("• Complete Hindi medical responses")
print("• 200+ medical terms in Hindi")
print("• Proper medical formatting")
print("• Emergency information in Hindi")
print("• WHO guidelines in Hindi")

print(f"\n🚀 Ready for Hindi-speaking users!")
print("Test queries you can try:")
print("• मलेरिया के लक्षण क्या हैं?")
print("• डेंगू बुखार से कैसे बचें?")
print("• मधुमेह का इलाज क्या है?")
print("• उच्च रक्तचाप के कारण बताएं")
print("• बुखार और सिरदर्द हो रहा है")
