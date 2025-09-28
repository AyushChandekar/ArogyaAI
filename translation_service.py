import os
from groq import Groq
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self, api_key: str):
        """Initialize the Translation Service with Groq API"""
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.language_cache = {}  # Cache for detected languages
        
    def _make_groq_request(self, content: str, max_retries: int = 3, delay: float = 1.0):
        """Make a request to Groq API with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": content}],
                    model=self.model,
                    temperature=0.1,  # Low temperature for more consistent translations
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Groq API attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All Groq API attempts failed: {str(e)}")
                    raise e

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text
        Returns language name in English (e.g., 'Japanese', 'Spanish', 'English')
        """
        # Check cache first
        text_hash = hash(text[:100])  # Use first 100 chars for caching
        if text_hash in self.language_cache:
            return self.language_cache[text_hash]
        
        try:
            # Create prompt for language detection
            prompt = f"Just tell me in one word which language this text is in English. Don't include anything else in response: {text}"
            
            detected_language = self._make_groq_request(prompt)
            
            # Clean and standardize the response
            detected_language = detected_language.lower().strip()
            
            # Map common variations to standard names
            language_mapping = {
                'japanese': 'Japanese',
                'spanish': 'Spanish',
                'french': 'French',
                'german': 'German',
                'italian': 'Italian',
                'chinese': 'Chinese',
                'korean': 'Korean',
                'hindi': 'Hindi',
                'arabic': 'Arabic',
                'portuguese': 'Portuguese',
                'russian': 'Russian',
                'english': 'English'
            }
            
            standardized_language = language_mapping.get(detected_language, detected_language.capitalize())
            
            # Cache the result
            self.language_cache[text_hash] = standardized_language
            
            logger.info(f"Detected language: {standardized_language} for text: {text[:50]}...")
            return standardized_language
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return "English"  # Default to English if detection fails

    def translate_to_english(self, text: str, source_language: str = None) -> str:
        """
        Translate text to English
        """
        try:
            # If already English, return as is
            if source_language and source_language.lower() == 'english':
                return text
            
            # Create translation prompt
            prompt = f"Just convert this text into English language and give me output don't include anything else in response: {text}"
            
            translated_text = self._make_groq_request(prompt)
            
            logger.info(f"Translated to English: {text[:50]}... -> {translated_text[:50]}...")
            return translated_text
            
        except Exception as e:
            logger.error(f"Error translating to English: {str(e)}")
            return text  # Return original text if translation fails

    def translate_from_english(self, text: str, target_language: str) -> str:
        """
        Translate English text to target language
        """
        try:
            # If target is English, return as is
            if target_language.lower() == 'english':
                return text
            
            # Create translation prompt
            prompt = f"Just convert this text into {target_language} language and give me output don't include anything else in response: {text}"
            
            translated_text = self._make_groq_request(prompt)
            
            logger.info(f"Translated to {target_language}: {text[:50]}... -> {translated_text[:50]}...")
            return translated_text
            
        except Exception as e:
            logger.error(f"Error translating to {target_language}: {str(e)}")
            return text  # Return original text if translation fails

    def process_multilingual_query(self, user_input: str, process_function):
        """
        Complete multilingual workflow:
        1. Detect user's language
        2. Translate to English
        3. Process with existing system
        4. Translate response back to user's language
        """
        try:
            # Step 1: Detect language
            logger.info(f"Processing multilingual query: {user_input[:50]}...")
            detected_language = self.detect_language(user_input)
            
            # Step 2: Translate to English (if needed)
            english_query = self.translate_to_english(user_input, detected_language)
            
            # Step 3: Process with existing system
            logger.info(f"Processing English query: {english_query}")
            english_response = process_function(english_query)
            
            # Step 4: Translate response back to user's language (if needed)
            final_response = self.translate_from_english(english_response, detected_language)
            
            return {
                'original_query': user_input,
                'detected_language': detected_language,
                'english_query': english_query,
                'english_response': english_response,
                'final_response': final_response,
                'was_translated': detected_language.lower() != 'english'
            }
            
        except Exception as e:
            logger.error(f"Error in multilingual processing: {str(e)}")
            # Fallback: process in English
            try:
                english_response = process_function(user_input)
                return {
                    'original_query': user_input,
                    'detected_language': 'English',
                    'english_query': user_input,
                    'english_response': english_response,
                    'final_response': english_response,
                    'was_translated': False,
                    'error': str(e)
                }
            except Exception as fallback_error:
                return {
                    'original_query': user_input,
                    'detected_language': 'Unknown',
                    'english_query': user_input,
                    'english_response': f"Sorry, I encountered an error processing your request: {str(fallback_error)}",
                    'final_response': f"Sorry, I encountered an error processing your request: {str(fallback_error)}",
                    'was_translated': False,
                    'error': str(e)
                }

# Initialize the translation service
def get_translation_service():
    """Get the global translation service instance"""
    import os
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        logger.warning("GROQ_API_KEY not found in environment variables. Translation service may not work.")
        return None
    return TranslationService(groq_api_key)
