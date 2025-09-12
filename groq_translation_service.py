"""
Groq AI Translation Service
Provides language detection and translation using Groq API
"""

import os
import json
import logging
from typing import Dict, Optional, Tuple, List
import requests
from dataclasses import dataclass
import langdetect
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    """Structure for translation results"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float

class GroqTranslationService:
    """
    Translation service using Groq AI API
    Handles language detection and translation for the healthcare chatbot
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Groq translation service"""
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Language mappings
        self.language_names = {
            'en': 'English',
            'hi': 'Hindi',
            'bn': 'Bengali', 
            'te': 'Telugu',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'or': 'Odia',
            'ur': 'Urdu',
            'as': 'Assamese'
        }
        
        # Common medical terms that should be preserved
        self.medical_terms = [
            'malaria', 'dengue', 'diabetes', 'tuberculosis', 'covid', 'pneumonia',
            'hypertension', 'hepatitis', 'anemia', 'diarrhea', 'fever', 'cough',
            'WHO', 'BCG', 'vaccine', 'symptoms', 'prevention', 'treatment'
        ]
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language of input text
        Returns (language_code, confidence)
        """
        try:
            # Remove medical terms for better detection
            cleaned_text = text.lower()
            for term in self.medical_terms:
                cleaned_text = cleaned_text.replace(term.lower(), '')
            
            # Use langdetect for initial detection
            if len(cleaned_text.strip()) > 10:
                detected_lang = langdetect.detect(cleaned_text)
                confidence = 0.9  # Default confidence for langdetect
            else:
                # For short text, use Groq AI
                detected_lang, confidence = self._groq_detect_language(text)
                
            return detected_lang, confidence
            
        except LangDetectException:
            logger.warning(f"Language detection failed for text: {text[:50]}...")
            return 'en', 0.5  # Default to English with low confidence
        except Exception as e:
            logger.error(f"Error in language detection: {e}")
            return 'en', 0.3
    
    def _groq_detect_language(self, text: str) -> Tuple[str, float]:
        """Use Groq AI to detect language"""
        try:
            prompt = f"""
            Detect the language of this text and respond with just the ISO language code (like 'en', 'hi', 'bn', etc.):
            
            Text: "{text}"
            
            Respond with only the language code, nothing else.
            """
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": "llama-3.1-8b-instant",
                "temperature": 0.1,
                "max_tokens": 10
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result['choices'][0]['message']['content'].strip().lower()
                
                # Validate the detected language code
                if detected_lang in self.language_names:
                    return detected_lang, 0.8
                else:
                    return 'en', 0.5
            else:
                logger.error(f"Groq API error: {response.status_code}")
                return 'en', 0.3
                
        except Exception as e:
            logger.error(f"Error in Groq language detection: {e}")
            return 'en', 0.3
    
    def translate_to_english(self, text: str, source_language: str = None) -> TranslationResult:
        """
        Translate text to English using Groq AI
        """
        if not source_language:
            source_language, _ = self.detect_language(text)
        
        if source_language == 'en':
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language='en',
                target_language='en',
                confidence=1.0
            )
        
        try:
            source_lang_name = self.language_names.get(source_language, 'Unknown')
            
            prompt = f"""
            Translate the following {source_lang_name} text to English. 
            Keep medical terms and disease names in their commonly used English forms.
            Preserve the meaning and context accurately.
            
            Text: "{text}"
            
            Provide only the English translation, nothing else.
            """
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": "llama-3.1-70b-versatile",
                "temperature": 0.2,
                "max_tokens": 1000
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                
                return TranslationResult(
                    original_text=text,
                    translated_text=translated_text,
                    source_language=source_language,
                    target_language='en',
                    confidence=0.9
                )
            else:
                logger.error(f"Translation API error: {response.status_code}")
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language=source_language,
                    target_language='en',
                    confidence=0.1
                )
                
        except Exception as e:
            logger.error(f"Error in translation to English: {e}")
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language,
                target_language='en',
                confidence=0.1
            )
    
    def translate_from_english(self, text: str, target_language: str) -> TranslationResult:
        """
        Translate English text to target language using Groq AI
        """
        if target_language == 'en':
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language='en',
                target_language='en',
                confidence=1.0
            )
        
        try:
            target_lang_name = self.language_names.get(target_language, 'Unknown')
            
            prompt = f"""
            Translate the following English text to {target_lang_name}.
            This is healthcare information, so maintain accuracy and clarity.
            Keep medical terms recognizable and use commonly understood terms.
            
            Text: "{text}"
            
            Provide only the {target_lang_name} translation, nothing else.
            """
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": "llama-3.1-70b-versatile",
                "temperature": 0.2,
                "max_tokens": 2000
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                
                return TranslationResult(
                    original_text=text,
                    translated_text=translated_text,
                    source_language='en',
                    target_language=target_language,
                    confidence=0.9
                )
            else:
                logger.error(f"Translation API error: {response.status_code}")
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language='en',
                    target_language=target_language,
                    confidence=0.1
                )
                
        except Exception as e:
            logger.error(f"Error in translation from English: {e}")
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language='en',
                target_language=target_language,
                confidence=0.1
            )
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.language_names.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.language_names

# Global instance
_groq_translation_service = None

def get_groq_translation_service() -> GroqTranslationService:
    """Get singleton instance of Groq translation service"""
    global _groq_translation_service
    if _groq_translation_service is None:
        _groq_translation_service = GroqTranslationService()
    return _groq_translation_service
