"""
RASA Custom Actions for Healthcare Chatbot with Groq AI Translation
Handles disease information, vaccination schedules, and multilingual support
"""

import yaml
import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq_translation_service import get_groq_translation_service

logger = logging.getLogger(__name__)

class HealthcareDataLoader:
    """Load and manage healthcare data from YAML files"""
    
    def __init__(self):
        self.data = None
        self.load_healthcare_data()
    
    def load_healthcare_data(self):
        """Load healthcare data from YAML file"""
        try:
            data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'healthcare_data.yml')
            with open(data_file, 'r', encoding='utf-8') as f:
                self.data = yaml.safe_load(f)
            logger.info("Healthcare data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading healthcare data: {e}")
            self.data = {}
    
    def get_disease_info(self, disease_name: str) -> Dict:
        """Get disease information by name"""
        if not self.data:
            return None
        
        disease_name = disease_name.lower().strip()
        diseases = self.data.get('diseases', {})
        
        # Direct match
        if disease_name in diseases:
            return diseases[disease_name]
        
        # Fuzzy matching for common variations
        mappings = {
            'tb': 'tuberculosis',
            'high bp': 'hypertension',
            'high blood pressure': 'hypertension',
            'sugar': 'diabetes',
            'sugar disease': 'diabetes',
            'corona': 'covid19',
            'coronavirus': 'covid19',
            'covid': 'covid19',
            'lung infection': 'pneumonia',
            'chest infection': 'pneumonia'
        }
        
        mapped_disease = mappings.get(disease_name)
        if mapped_disease and mapped_disease in diseases:
            return diseases[mapped_disease]
        
        # Partial matching
        for key in diseases.keys():
            if disease_name in key or key in disease_name:
                return diseases[key]
        
        return None
    
    def get_vaccination_schedule(self, age_group: str) -> Dict:
        """Get vaccination schedule for age group"""
        if not self.data:
            return None
        
        age_group = age_group.lower().strip()
        schedules = self.data.get('vaccination_schedules', {})
        
        # Age-based matching
        age_mappings = {
            'baby': 'newborn_0_2_months',
            'babies': 'infants_2_12_months',
            'newborn': 'newborn_0_2_months',
            'infant': 'infants_2_12_months',
            'child': 'children_1_5_years',
            'children': 'children_1_5_years',
            'kid': 'children_1_5_years',
            'kids': 'children_1_5_years',
            'adult': 'adults_20_64_years',
            'adults': 'adults_20_64_years'
        }
        
        # Direct match
        for key, value in schedules.items():
            if age_group in key.lower():
                return value
        
        mapped_age = age_mappings.get(age_group)
        if mapped_age and mapped_age in schedules:
            return schedules[mapped_age]
        
        return None
    
    def get_emergency_info(self) -> Dict:
        """Get emergency information"""
        if not self.data:
            return {}
        return self.data.get('emergency_info', {})
    
    def get_prevention_guidelines(self, category: str = None) -> Dict:
        """Get prevention guidelines"""
        if not self.data:
            return {}
        
        guidelines = self.data.get('prevention_guidelines', {})
        
        if category:
            category = category.lower().strip()
            for key, value in guidelines.items():
                if category in key.lower():
                    return {key: value}
        
        return guidelines

# Global healthcare data loader
healthcare_data = HealthcareDataLoader()

class ActionDiseaseInfo(Action):
    """Action to provide disease information with translation support"""
    
    def name(self) -> Text:
        return "action_disease_info_improved"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get disease from slot or latest message
        disease = tracker.get_slot("disease")
        if not disease:
            # Extract from latest message
            disease = self.extract_disease_from_message(tracker.latest_message.get('text', ''))
        
        if not disease:
            dispatcher.utter_message(text="I'd be happy to help with disease information. Could you please specify which disease you'd like to know about?")
            return []
        
        # Get user's detected language
        user_message = tracker.latest_message.get('text', '')
        translation_service = get_groq_translation_service()
        detected_lang, confidence = translation_service.detect_language(user_message)
        
        # Translate disease name to English if needed
        if detected_lang != 'en':
            translation_result = translation_service.translate_to_english(disease, detected_lang)
            disease_english = translation_result.translated_text
        else:
            disease_english = disease
            detected_lang = 'en'
        
        # Get disease information
        disease_info = healthcare_data.get_disease_info(disease_english)
        
        if not disease_info:
            response = f"I don't have detailed information about '{disease}'. I can help with diseases like malaria, dengue, diabetes, tuberculosis, COVID-19, pneumonia, and hypertension. Which one would you like to know about?"
        else:
            response = self.format_disease_response(disease_info)
        
        # Translate response back to user's language if needed
        if detected_lang != 'en':
            translation_result = translation_service.translate_from_english(response, detected_lang)
            response = translation_result.translated_text
        
        dispatcher.utter_message(text=response)
        
        return [SlotSet("disease", disease), SlotSet("language", detected_lang)]
    
    def extract_disease_from_message(self, message: str) -> str:
        """Extract disease name from user message"""
        message = message.lower()
        diseases = ['malaria', 'dengue', 'diabetes', 'tuberculosis', 'covid', 'pneumonia', 'hypertension', 'tb', 'corona', 'coronavirus']
        
        for disease in diseases:
            if disease in message:
                return disease
        return None
    
    def format_disease_response(self, disease_info: Dict) -> str:
        """Format disease information into readable response"""
        response = f"**{disease_info['name']}**\n\n"
        response += f"📋 **Overview**: {disease_info['overview']}\n\n"
        
        # Causes
        if disease_info.get('causes'):
            response += "🔍 **Main Causes**:\n"
            for cause in disease_info['causes'][:3]:  # Show top 3 causes
                response += f"• {cause}\n"
            response += "\n"
        
        # Symptoms
        if disease_info.get('symptoms'):
            symptoms = disease_info['symptoms']
            if isinstance(symptoms, dict):
                for symptom_type, symptom_list in symptoms.items():
                    response += f"🩺 **{symptom_type.title()} Symptoms**:\n"
                    for symptom in symptom_list[:4]:  # Show top 4 symptoms
                        response += f"• {symptom}\n"
                    response += "\n"
        
        # Prevention
        if disease_info.get('prevention'):
            response += "🛡️ **Prevention**:\n"
            for prevention in disease_info['prevention'][:4]:
                response += f"• {prevention}\n"
            response += "\n"
        
        # When to see doctor
        if disease_info.get('when_to_see_doctor'):
            response += "⚠️ **See a Doctor If**:\n"
            for warning in disease_info['when_to_see_doctor'][:3]:
                response += f"• {warning}\n"
            response += "\n"
        
        # WHO Guidelines
        if disease_info.get('who_guidelines'):
            response += f"🏥 **WHO Guidelines**: {disease_info['who_guidelines']}\n\n"
        
        response += "💡 Ask me about prevention, home treatment, or vaccination schedules for more detailed information!"
        
        return response

class ActionVaccinationSchedule(Action):
    """Action to provide vaccination schedules with translation support"""
    
    def name(self) -> Text:
        return "action_vaccination_schedule"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get age group from slot or extract from message
        age_group = tracker.get_slot("age_group")
        if not age_group:
            age_group = self.extract_age_group_from_message(tracker.latest_message.get('text', ''))
        
        if not age_group:
            dispatcher.utter_message(text="I can provide vaccination schedules. Please specify the age group (babies, children, adults, etc.)")
            return []
        
        # Get user's detected language
        user_message = tracker.latest_message.get('text', '')
        translation_service = get_groq_translation_service()
        detected_lang, confidence = translation_service.detect_language(user_message)
        
        # Get vaccination schedule
        schedule_info = healthcare_data.get_vaccination_schedule(age_group)
        
        if not schedule_info:
            response = f"I don't have vaccination schedule information for '{age_group}'. I can provide schedules for babies, infants, children, and adults."
        else:
            response = self.format_vaccination_response(schedule_info)
        
        # Translate response back to user's language if needed
        if detected_lang != 'en':
            translation_result = translation_service.translate_from_english(response, detected_lang)
            response = translation_result.translated_text
        
        dispatcher.utter_message(text=response)
        
        return [SlotSet("age_group", age_group), SlotSet("language", detected_lang)]
    
    def extract_age_group_from_message(self, message: str) -> str:
        """Extract age group from user message"""
        message = message.lower()
        age_groups = ['baby', 'babies', 'newborn', 'infant', 'child', 'children', 'kid', 'adult', 'adults']
        
        for age_group in age_groups:
            if age_group in message:
                return age_group
        return None
    
    def format_vaccination_response(self, schedule_info: Dict) -> str:
        """Format vaccination schedule into readable response"""
        response = f"💉 **Vaccination Schedule for {schedule_info['age_range']}**\n\n"
        
        vaccines = schedule_info.get('vaccines', [])
        for i, vaccine in enumerate(vaccines[:5], 1):  # Show top 5 vaccines
            response += f"**{i}. {vaccine['name']}**\n"
            response += f"📅 **Timing**: {vaccine['timing']}\n"
            response += f"🛡️ **Protects Against**: {vaccine['protects_against']}\n"
            response += f"💊 **Dose**: {vaccine['dose']}\n"
            if vaccine.get('side_effects'):
                response += f"⚠️ **Side Effects**: {vaccine['side_effects']}\n"
            response += "\n"
        
        response += "📝 Always consult with your healthcare provider for personalized vaccination schedules."
        
        return response

class ActionEmergencyHelp(Action):
    """Action to provide emergency information with translation support"""
    
    def name(self) -> Text:
        return "action_emergency_help"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get user's detected language
        user_message = tracker.latest_message.get('text', '')
        translation_service = get_groq_translation_service()
        detected_lang, confidence = translation_service.detect_language(user_message)
        
        # Get emergency information
        emergency_info = healthcare_data.get_emergency_info()
        
        response = self.format_emergency_response(emergency_info)
        
        # Translate response back to user's language if needed
        if detected_lang != 'en':
            translation_result = translation_service.translate_from_english(response, detected_lang)
            response = translation_result.translated_text
        
        dispatcher.utter_message(text=response)
        
        return [SlotSet("language", detected_lang)]
    
    def format_emergency_response(self, emergency_info: Dict) -> str:
        """Format emergency information into readable response"""
        response = "🚨 **EMERGENCY CONTACT NUMBERS**\n\n"
        
        # India emergency numbers
        india_numbers = emergency_info.get('numbers', {}).get('india', {})
        if india_numbers:
            response += "🇮🇳 **India Emergency Numbers**:\n"
            response += f"🏥 Medical Emergency: {india_numbers.get('medical_emergency', '108')}\n"
            response += f"🚔 Police: {india_numbers.get('police', '100')}\n"
            response += f"🚒 Fire: {india_numbers.get('fire', '101')}\n"
            response += f"📞 Disaster Helpline: {india_numbers.get('disaster_helpline', '1078')}\n\n"
        
        # Emergency procedures
        procedures = emergency_info.get('procedures', {})
        if procedures.get('heart_attack'):
            response += "❤️ **Heart Attack Emergency**:\n"
            for step in procedures['heart_attack'][:3]:
                response += f"• {step}\n"
            response += "\n"
        
        if procedures.get('stroke'):
            response += "🧠 **Stroke Emergency**:\n"
            for step in procedures['stroke'][:3]:
                response += f"• {step}\n"
            response += "\n"
        
        response += "⚡ **Remember**: In any life-threatening emergency, call your local emergency number immediately!"
        
        return response

class ActionPreventionTips(Action):
    """Action to provide prevention guidelines with translation support"""
    
    def name(self) -> Text:
        return "action_prevention_tips"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get user's detected language
        user_message = tracker.latest_message.get('text', '')
        translation_service = get_groq_translation_service()
        detected_lang, confidence = translation_service.detect_language(user_message)
        
        # Get prevention guidelines
        guidelines = healthcare_data.get_prevention_guidelines()
        
        response = self.format_prevention_response(guidelines)
        
        # Translate response back to user's language if needed
        if detected_lang != 'en':
            translation_result = translation_service.translate_from_english(response, detected_lang)
            response = translation_result.translated_text
        
        dispatcher.utter_message(text=response)
        
        return [SlotSet("language", detected_lang)]
    
    def format_prevention_response(self, guidelines: Dict) -> str:
        """Format prevention guidelines into readable response"""
        response = "🛡️ **HEALTH PREVENTION GUIDELINES**\n\n"
        
        # Hand hygiene
        infectious = guidelines.get('infectious_disease_prevention', {})
        hand_hygiene = infectious.get('hand_hygiene', [])
        if hand_hygiene:
            response += "🤲 **Hand Hygiene**:\n"
            for tip in hand_hygiene[:3]:
                response += f"• {tip}\n"
            response += "\n"
        
        # Respiratory etiquette
        respiratory = infectious.get('respiratory_etiquette', [])
        if respiratory:
            response += "😷 **Respiratory Etiquette**:\n"
            for tip in respiratory[:3]:
                response += f"• {tip}\n"
            response += "\n"
        
        # Vector control
        vector = guidelines.get('vector_borne_disease_prevention', {}).get('mosquito_control', [])
        if vector:
            response += "🦟 **Mosquito Control**:\n"
            for tip in vector[:3]:
                response += f"• {tip}\n"
            response += "\n"
        
        # Cardiovascular health
        cardio = guidelines.get('chronic_disease_prevention', {}).get('cardiovascular_health', [])
        if cardio:
            response += "❤️ **Heart Health**:\n"
            for tip in cardio[:3]:
                response += f"• {tip}\n"
            response += "\n"
        
        response += "💡 Ask about specific disease prevention for more detailed information!"
        
        return response

class ActionLanguageSupport(Action):
    """Action to provide language support information"""
    
    def name(self) -> Text:
        return "action_language_info_improved"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        translation_service = get_groq_translation_service()
        supported_languages = translation_service.get_supported_languages()
        
        # Get user's detected language
        user_message = tracker.latest_message.get('text', '')
        detected_lang, confidence = translation_service.detect_language(user_message)
        
        response = "🌍 **Supported Languages**: I can understand and respond in the following languages:\n\n"
        
        for code, name in supported_languages.items():
            response += f"• {name} ({code})\n"
        
        response += "\n💬 Just type your question in any of these languages, and I'll respond in the same language!"
        response += "\n\n🎯 **Current Language Detected**: " + supported_languages.get(detected_lang, detected_lang)
        
        # Translate response back to user's language if needed
        if detected_lang != 'en':
            translation_result = translation_service.translate_from_english(response, detected_lang)
            response = translation_result.translated_text
        
        dispatcher.utter_message(text=response)
        
        return [SlotSet("language", detected_lang)]

class ActionDefaultFallback(Action):
    """Custom fallback action with translation support"""
    
    def name(self) -> Text:
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get user's detected language
        user_message = tracker.latest_message.get('text', '')
        translation_service = get_groq_translation_service()
        detected_lang, confidence = translation_service.detect_language(user_message)
        
        response = "I'm sorry, I didn't understand that. I'm a healthcare chatbot that can help with:\n\n"
        response += "🩺 Disease information (malaria, dengue, diabetes, etc.)\n"
        response += "💉 Vaccination schedules\n"
        response += "🛡️ Prevention tips\n"
        response += "🚨 Emergency information\n"
        response += "🌍 Multiple language support\n\n"
        response += "Try asking: 'Tell me about malaria' or 'Vaccination for babies'"
        
        # Translate response back to user's language if needed
        if detected_lang != 'en':
            translation_result = translation_service.translate_from_english(response, detected_lang)
            response = translation_result.translated_text
        
        dispatcher.utter_message(text=response)
        
        return [SlotSet("language", detected_lang)]
