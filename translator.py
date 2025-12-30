import translators as ts
import logging
import time

logger = logging.getLogger(__name__)


class Translator:
    """Handle translation of text to Gujarati using free APIs"""
    
    def __init__(self):
        logger.info("Translator initialized (using free translators API)")
    
    def translate(self, text: str, target_language: str = 'gu') -> str:
        if not text or not text.strip():
            return text
        
        try:
            translated = ts.translate_text(
                query_text=text,
                translator='google',
                from_language='en',
                to_language=target_language
            )
            
            logger.debug(f"Translated: {text[:50]}... -> {translated[:50]}...")
            time.sleep(0.1)
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation error for '{text[:50]}...': {e}")
            logger.warning("Returning original text")
            return text
    
    def translate_question(self, question: dict) -> dict:
        translated = question.copy()
        
        logger.info(f"Translating question {question.get('question_no', '?')}")
        
        if 'question' in question:
            translated['question'] = self.translate(question['question'])
        
        if 'options' in question:
            translated['options'] = [
                self.translate(option) for option in question['options']
            ]
        
        if 'answer' in question:
            translated['answer'] = self.translate(question['answer'])
        
        if 'explanation' in question and question['explanation']:
            translated['explanation'] = self.translate(question['explanation'])
        
        if 'category' in question and question['category']:
            translated['category'] = self.translate(question['category'])
        
        return translated
