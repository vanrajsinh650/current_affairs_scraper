from deep_translator import GoogleTranslator
import logging
import time

logger = logging.getLogger(__name__)


class Translator:
    """Handle translation using Deep Translator (free, no API key)"""
    
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self.translator = GoogleTranslator(source='en', target='gu')
        logger.info("Deep Translator initialized (free, no API key needed)")
    
    def translate(self, text: str) -> str:
        """Translate text to Gujarati"""
        if not text or not text.strip():
            return text
        
        # Split long text into chunks (Google Translate limit: 5000 chars)
        if len(text) > 4500:
            logger.warning(f"Text too long ({len(text)} chars), truncating...")
            text = text[:4500]
        
        # Try translation with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                translated = self.translator.translate(text)
                logger.debug(f"Translated: {text[:50]}...")
                time.sleep(0.3)  # Small delay to avoid rate limit
                return translated
                
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Attempt {attempt} failed, retrying...")
                    time.sleep(1)
                else:
                    logger.error(f"Translation failed: {str(e)[:100]}")
                    return text  # Return original text if translation fails
        
        return text
    
    def translate_question(self, question: dict) -> dict:
        """Translate entire question"""
        translated = question.copy()
        
        logger.info(f"Translating question {question.get('question_no', '?')}")
        
        try:
            # Translate question text
            if 'question' in question:
                translated['question'] = self.translate(question['question'])
            
            # Translate options
            if 'options' in question:
                translated['options'] = [
                    self.translate(option) for option in question['options']
                ]
            
            # Translate answer
            if 'answer' in question:
                translated['answer'] = self.translate(question['answer'])
            
            # Translate explanation
            if 'explanation' in question and question['explanation']:
                translated['explanation'] = self.translate(question['explanation'])
            
            # Translate category
            if 'category' in question and question['category']:
                translated['category'] = self.translate(question['category'])
            
            return translated
            
        except Exception as e:
            logger.error(f"Failed to translate question {question.get('question_no', '?')}: {e}")
            return question  # Return original if translation fails
