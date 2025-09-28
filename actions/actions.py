from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import sys
import os

# Add parent directory to path to import disease_info_system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from disease_info_system import DiseaseInfoSystem

# Initialize the disease information system
disease_system = DiseaseInfoSystem("clean_disease_data.csv")

def validate_and_extract_disease(tracker):
    """Helper function to validate and extract disease from tracker"""
    disease = tracker.get_slot("current_disease")
    latest_message = tracker.latest_message.get('text', '')
    entities = tracker.latest_message.get('entities', [])
    
    # Extract disease entity and validate
    extracted_disease = None
    for entity in entities:
        if entity.get('entity') == 'disease':
            extracted_disease = entity.get('value')
            break
    
    # Use improved disease validation
    if extracted_disease:
        validated_disease, confidence = disease_system.validate_and_find_disease(extracted_disease, latest_message)
        if validated_disease:
            return validated_disease
    elif not disease:
        found_disease, confidence = disease_system.find_disease(latest_message)
        if found_disease:
            return found_disease
    
    return disease

class ActionProvideHometreatment(Action):
    def name(self) -> Text:
        return "action_provide_home_treatment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = tracker.get_slot("current_disease")
        latest_message = tracker.latest_message.get('text', '')
        entities = tracker.latest_message.get('entities', [])
        
        # Extract disease entity and validate
        extracted_disease = None
        for entity in entities:
            if entity.get('entity') == 'disease':
                extracted_disease = entity.get('value')
                break
        
        # Use improved disease validation
        if extracted_disease:
            validated_disease, confidence = disease_system.validate_and_find_disease(extracted_disease, latest_message)
            if validated_disease:
                disease = validated_disease
        elif not disease:
            found_disease, confidence = disease_system.find_disease(latest_message)
            if found_disease:
                disease = found_disease
        
        if not disease:
            dispatcher.utter_message(text="I need to know which disease you're asking about. Could you please specify?")
            return []

        # Get disease info using existing system
        disease_info = disease_system.get_disease_info(disease)
        
        if disease_info and disease_info['home_treatment']:
            response = f"🏠 **Home Treatment for {disease.title()}:**\n\n{disease_info['home_treatment']}"
            dispatcher.utter_message(text=response)
            
            return [
                SlotSet("current_info_type", "home_treatment"),
                SlotSet("last_provided_info", "home_treatment"),
                SlotSet("conversation_context", f"provided_home_treatment_for_{disease}")
            ]
        else:
            dispatcher.utter_message(text=f"I don't have home treatment information for {disease}. Let me suggest other available diseases.")
            return [FollowupAction("utter_disease_options")]

class ActionProvideSymptoms(Action):
    def name(self) -> Text:
        return "action_provide_symptoms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = tracker.get_slot("current_disease")
        latest_message = tracker.latest_message.get('text', '')
        entities = tracker.latest_message.get('entities', [])
        
        print(f"DEBUG SYMPTOMS: User input: '{latest_message}'")
        print(f"DEBUG SYMPTOMS: Extracted entities: {entities}")
        print(f"DEBUG SYMPTOMS: Current disease slot: '{disease}'")
        
        # Extract disease entity from current message if available
        extracted_disease = None
        for entity in entities:
            if entity.get('entity') == 'disease':
                extracted_disease = entity.get('value')
                break
        
        # Use improved disease validation and finding
        if extracted_disease:
            validated_disease, confidence = disease_system.validate_and_find_disease(extracted_disease, latest_message)
            if validated_disease:
                disease = validated_disease
                print(f"DEBUG SYMPTOMS: Using validated disease: '{disease}' (confidence: {confidence})")
        elif not disease:
            # Try to find disease from the message itself
            found_disease, confidence = disease_system.find_disease(latest_message)
            if found_disease:
                disease = found_disease
                print(f"DEBUG SYMPTOMS: Found disease from message: '{disease}' (confidence: {confidence})")
        
        if not disease:
            dispatcher.utter_message(text="Which disease symptoms would you like to know about?")
            return []

        disease_info = disease_system.get_disease_info(disease)
        print(f"DEBUG SYMPTOMS: Looking for symptoms of '{disease}'")
        print(f"DEBUG SYMPTOMS: Disease info found: {disease_info is not None}")
        
        if disease_info and disease_info.get('symptoms'):
            symptoms_text = disease_info['symptoms']
            print(f"DEBUG: Symptoms text length: {len(symptoms_text)}")
            response = f"⚠️ **Symptoms of {disease.title()}:**\n\n{symptoms_text}"
            dispatcher.utter_message(text=response)
            
            return [
                SlotSet("current_info_type", "symptoms"),
                SlotSet("last_provided_info", "symptoms"),
                SlotSet("conversation_context", f"provided_symptoms_for_{disease}")
            ]
        else:
            dispatcher.utter_message(text=f"I don't have symptom information for {disease}. Let me suggest other available diseases.")
            return [FollowupAction("utter_disease_options")]

class ActionProvideCauses(Action):
    def name(self) -> Text:
        return "action_provide_causes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = tracker.get_slot("current_disease")
        latest_message = tracker.latest_message.get('text', '')
        entities = tracker.latest_message.get('entities', [])
        
        # Extract disease entity and validate
        extracted_disease = None
        for entity in entities:
            if entity.get('entity') == 'disease':
                extracted_disease = entity.get('value')
                break
        
        # Use improved disease validation
        if extracted_disease:
            validated_disease, confidence = disease_system.validate_and_find_disease(extracted_disease, latest_message)
            if validated_disease:
                disease = validated_disease
        elif not disease:
            found_disease, confidence = disease_system.find_disease(latest_message)
            if found_disease:
                disease = found_disease
        
        if not disease:
            dispatcher.utter_message(text="Which disease causes would you like to understand?")
            return []

        disease_info = disease_system.get_disease_info(disease)
        
        if disease_info and disease_info['causes']:
            response = f"🔍 **Causes of {disease.title()}:**\n\n{disease_info['causes']}"
            dispatcher.utter_message(text=response)
            
            return [
                SlotSet("current_info_type", "causes"),
                SlotSet("last_provided_info", "causes"),
                SlotSet("conversation_context", f"provided_causes_for_{disease}")
            ]
        else:
            dispatcher.utter_message(text=f"I don't have cause information for {disease}. Let me suggest other available diseases.")
            return [FollowupAction("utter_disease_options")]

class ActionProvidePrevention(Action):
    def name(self) -> Text:
        return "action_provide_prevention"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = validate_and_extract_disease(tracker)
        
        if not disease:
            dispatcher.utter_message(text="Which disease prevention methods would you like to know?")
            return []

        disease_info = disease_system.get_disease_info(disease)
        
        if disease_info and disease_info['precautions']:
            response = f"🛡️ **Prevention for {disease.title()}:**\n\n{disease_info['precautions']}"
            dispatcher.utter_message(text=response)
            
            return [
                SlotSet("current_info_type", "prevention"),
                SlotSet("last_provided_info", "prevention"),
                SlotSet("conversation_context", f"provided_prevention_for_{disease}")
            ]
        else:
            dispatcher.utter_message(text=f"I don't have prevention information for {disease}. Let me suggest other available diseases.")
            return [FollowupAction("utter_disease_options")]

class ActionProvideAwareness(Action):
    def name(self) -> Text:
        return "action_provide_awareness"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = validate_and_extract_disease(tracker)
        
        if not disease:
            dispatcher.utter_message(text="Which disease awareness information would you like?")
            return []

        disease_info = disease_system.get_disease_info(disease)
        
        if disease_info and disease_info['awareness']:
            response = f"💡 **Awareness about {disease.title()}:**\n\n{disease_info['awareness']}"
            dispatcher.utter_message(text=response)
            
            return [
                SlotSet("current_info_type", "awareness"),
                SlotSet("last_provided_info", "awareness"),
                SlotSet("conversation_context", f"provided_awareness_for_{disease}")
            ]
        else:
            dispatcher.utter_message(text=f"I don't have awareness information for {disease}. Let me suggest other available diseases.")
            return [FollowupAction("utter_disease_options")]

class ActionProvideWhoGuidelines(Action):
    def name(self) -> Text:
        return "action_provide_who_guidelines"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = validate_and_extract_disease(tracker)
        
        if not disease:
            dispatcher.utter_message(text="Which disease WHO guidelines would you like to know?")
            return []

        disease_info = disease_system.get_disease_info(disease)
        
        if disease_info and disease_info['who_guidelines']:
            response = f"🏛️ **WHO Guidelines for {disease.title()}:**\n\n{disease_info['who_guidelines']}"
            dispatcher.utter_message(text=response)
            
            return [
                SlotSet("current_info_type", "who_guidelines"),
                SlotSet("last_provided_info", "who_guidelines"),
                SlotSet("conversation_context", f"provided_who_guidelines_for_{disease}")
            ]
        else:
            dispatcher.utter_message(text=f"I don't have WHO guidelines for {disease}. Let me suggest other available diseases.")
            return [FollowupAction("utter_disease_options")]

class ActionProvideDiseaseInfo(Action):
    def name(self) -> Text:
        return "action_provide_disease_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = tracker.get_slot("current_disease")
        
        if not disease:
            dispatcher.utter_message(text="Which disease would you like to know about?")
            return []

        disease_info = disease_system.get_disease_info(disease)
        
        if disease_info:
            # Provide complete information using the existing system's logic
            response = disease_system.format_response(disease_info, 'overview', disease)
            dispatcher.utter_message(text=response)
            
            return [
                SlotSet("current_info_type", "overview"),
                SlotSet("last_provided_info", "overview"),
                SlotSet("conversation_context", f"provided_complete_info_for_{disease}")
            ]
        else:
            dispatcher.utter_message(text=f"I don't have information about {disease}. Let me show you what diseases I can help with.")
            return [FollowupAction("utter_disease_options")]

class ActionProvideComprehensiveInfo(Action):
    def name(self) -> Text:
        return "action_provide_comprehensive_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = tracker.get_slot("current_disease")
        latest_message = tracker.latest_message.get('text', '')
        entities = tracker.latest_message.get('entities', [])
        
        # Extract disease entity and validate
        extracted_disease = None
        for entity in entities:
            if entity.get('entity') == 'disease':
                extracted_disease = entity.get('value')
                break
        
        # Use improved disease validation
        if extracted_disease:
            validated_disease, confidence = disease_system.validate_and_find_disease(extracted_disease, latest_message)
            if validated_disease:
                disease = validated_disease
        elif not disease:
            found_disease, confidence = disease_system.find_disease(latest_message)
            if found_disease:
                disease = found_disease
        
        if not disease:
            dispatcher.utter_message(text="Which disease would you like comprehensive information about?")
            return []

        disease_info = disease_system.get_disease_info(disease)
        
        if disease_info:
            # Format comprehensive response with all 7 aspects
            response_parts = []
            
            # Header
            response_parts.append(f"📚 **COMPREHENSIVE INFORMATION ABOUT {disease.upper()}** 📚\n")
            response_parts.append("=" * 60 + "\n")
            
            # All aspects in order: overview, causes, symptoms, precautions, home_treatment, awareness, who_guidelines
            aspects = [
                ('overview', '📋 **OVERVIEW**'),
                ('causes', '🔍 **CAUSES**'),
                ('symptoms', '⚠️ **SYMPTOMS**'),
                ('precautions', '🛡️ **PRECAUTIONS**'),
                ('home_treatment', '🏠 **HOME TREATMENT**'),
                ('awareness', '💡 **AWARENESS**'),
                ('who_guidelines', '🏛️ **WHO GUIDELINES**')
            ]
            
            for aspect, title in aspects:
                if aspect in disease_info and disease_info[aspect] and str(disease_info[aspect]).strip():
                    content = str(disease_info[aspect]).strip()
                    if content and content != 'nan':
                        response_parts.append(f"\n{title}")
                        response_parts.append("-" * 40)
                        response_parts.append(f"{content}\n")
            
            # Footer
            response_parts.append("\n" + "=" * 60)
            response_parts.append("\n🩺 **IMPORTANT NOTE:**")
            response_parts.append("This information is for educational purposes only.")
            response_parts.append("Please consult with healthcare professionals for proper diagnosis and treatment.\n")
            response_parts.append("💬 You can ask me about specific aspects like:")
            response_parts.append(f"• 'Home treatment for {disease}'")
            response_parts.append(f"• 'Causes of {disease}'")
            response_parts.append(f"• 'Prevention of {disease}'")
            
            final_response = "\n".join(response_parts)
            dispatcher.utter_message(text=final_response)
            
            return [
                SlotSet("current_info_type", "comprehensive"),
                SlotSet("last_provided_info", "comprehensive"),
                SlotSet("conversation_context", f"provided_comprehensive_info_for_{disease}")
            ]
        else:
            dispatcher.utter_message(text=f"I don't have comprehensive information about {disease}. Let me show you what diseases I can help with.")
            return [FollowupAction("utter_disease_options")]

class ActionSuggestInfoTypes(Action):
    def name(self) -> Text:
        return "action_suggest_info_types"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = tracker.get_slot("current_disease")
        
        if not disease:
            dispatcher.utter_message(text="I can help with information about various diseases. Which disease interests you?")
            return [FollowupAction("utter_disease_options")]

        # Check if disease exists in our database
        disease_info = disease_system.get_disease_info(disease)
        
        if not disease_info:
            dispatcher.utter_message(text=f"I don't have information about {disease}. Let me show you available diseases.")
            return [FollowupAction("utter_disease_options")]

        response = f"I can help with {disease.title()}! What would you like to know about it?\n\n"
        response += "• **🏠 Home treatments** - Natural remedies and traditional treatments\n"
        response += "• **⚠️ Symptoms** - Signs and symptoms to look for\n"
        response += "• **🔍 Causes** - What causes this condition\n"
        response += "• **🛡️ Prevention** - How to prevent or avoid it\n"
        response += "• **💡 Awareness** - Important facts and awareness\n"
        response += "• **🏛️ WHO Guidelines** - Official health organization recommendations\n\n"
        response += "Just tell me what aspect interests you most!"

        dispatcher.utter_message(text=response)
        
        return [SlotSet("conversation_context", f"suggested_info_types_for_{disease}")]

class ActionCompareiseases(Action):
    def name(self) -> Text:
        return "action_compare_diseases"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease1 = tracker.get_slot("current_disease")
        disease2 = next(tracker.get_latest_entity_values("comparison_disease"), None)
        
        if not disease1 or not disease2:
            dispatcher.utter_message(text="I need two diseases to compare. Could you specify both diseases?")
            return []

        disease1_info = disease_system.get_disease_info(disease1)
        disease2_info = disease_system.get_disease_info(disease2)
        
        if not disease1_info:
            dispatcher.utter_message(text=f"I don't have information about {disease1}.")
            return []
            
        if not disease2_info:
            dispatcher.utter_message(text=f"I don't have information about {disease2}.")
            return []

        response = f"🔍 **Comparison between {disease1.title()} and {disease2.title()}:**\n\n"
        
        # Compare symptoms
        if disease1_info['symptoms'] and disease2_info['symptoms']:
            response += f"**⚠️ Symptoms:**\n"
            response += f"• **{disease1.title()}:** {disease1_info['symptoms'][:100]}...\n"
            response += f"• **{disease2.title()}:** {disease2_info['symptoms'][:100]}...\n\n"
        
        # Compare causes
        if disease1_info['causes'] and disease2_info['causes']:
            response += f"**🔍 Causes:**\n"
            response += f"• **{disease1.title()}:** {disease1_info['causes'][:100]}...\n"
            response += f"• **{disease2.title()}:** {disease2_info['causes'][:100]}...\n\n"

        response += f"Would you like detailed information about any specific aspect of {disease1} or {disease2}?"
        
        dispatcher.utter_message(text=response)
        
        return [
            SlotSet("conversation_context", f"compared_{disease1}_and_{disease2}"),
            SlotSet("last_provided_info", "comparison")
        ]

class ActionFallbackWithSuggestions(Action):
    def name(self) -> Text:
        return "action_fallback_with_suggestions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        response = "I'm not sure I understood that. I'm here to help with disease information!\n\n"
        response += "You can ask me things like:\n"
        response += "• 'Tell me about asthma'\n"
        response += "• 'Home treatment for acne'\n"
        response += "• 'What causes anxiety?'\n"
        response += "• 'Symptoms of diabetes'\n"
        response += "• 'How to prevent cold?'\n\n"
        response += "What would you like to know?"

        dispatcher.utter_message(text=response)
        
        return [FollowupAction("utter_disease_options")]

class ActionHandleFollowUp(Action):
    def name(self) -> Text:
        return "action_handle_follow_up"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the new disease from the follow-up
        new_disease = next(tracker.get_latest_entity_values("disease"), None)
        current_disease = tracker.get_slot("current_disease")
        
        if new_disease and new_disease != current_disease:
            # User is asking about a different disease
            return [
                SlotSet("current_disease", new_disease),
                FollowupAction("action_suggest_info_types")
            ]
        else:
            # Continue with current disease context
            return [FollowupAction("action_suggest_info_types")]

class ValidateDiseaseForm(Action):
    def name(self) -> Text:
        return "validate_disease_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # This action validates if the disease exists in our database
        disease = tracker.get_slot("current_disease")
        
        if disease:
            disease_info = disease_system.get_disease_info(disease)
            if not disease_info:
                dispatcher.utter_message(text=f"I don't have information about {disease}. Let me show you available diseases.")
                return [
                    SlotSet("current_disease", None),
                    FollowupAction("utter_disease_options")
                ]
        
        return []