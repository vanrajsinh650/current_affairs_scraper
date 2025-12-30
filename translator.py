import translators as ts
import logging
import time

logger = logging.getLogger(__name__)


class Translator:
    """Handle translation of text to Gujarati using free APIs"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        logger.info(f"Translator initialized (max retries: {max_retries})")
    
    def translate(self, text: str, target_language: str = 'gu') -> str:
        """Translate text with retry logic"""
        if not text or not text.strip():
            return text
        
        # Try translating with retries
        for attempt in range(1, self.max_retries + 1):
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
                if attempt < self.max_retries:
                    logger.warning(f"Translation attempt {attempt} failed for '{text[:50]}...': {e}")
                    logger.info(f"Retrying... ({attempt}/{self.max_retries})")
                    time.sleep(1)  # Wait before retry
                else:
                    logger.error(f"Translation failed after {self.max_retries} attempts for '{text[:50]}...': {e}")
                    return None  # Return None to mark as failed
        
        return None
    
    def translate_question(self, question: dict) -> dict:
        """Translate question with retry logic, return None if critical parts fail"""
        translated = question.copy()
        
        logger.info(f"Translating question {question.get('question_no', '?')}")
        
        # Translate question text (critical)
        if 'question' in question:
            translated_q = self.translate(question['question'])
            if translated_q is None:
                logger.error(f"Failed to translate question {question.get('question_no', '?')} - skipping")
                return None  # Skip this question
            translated['question'] = translated_q
        
        # Translate options (critical)
        if 'options' in question:
            translated_options = []
            for option in question['options']:
                translated_opt = self.translate(option)
                if translated_opt is None:
                    logger.error(f"Failed to translate option in question {question.get('question_no', '?')} - skipping")
                    return None  # Skip this question
                translated_options.append(translated_opt)
            translated['options'] = translated_options
        
        # Translate answer (critical)
        if 'answer' in question:
            translated_ans = self.translate(question['answer'])
            if translated_ans is None:
                logger.error(f"Failed to translate answer in question {question.get('question_no', '?')} - skipping")
                return None  # Skip this question
            translated['answer'] = translated_ans
        
        # Translate explanation (optional - keep original if fails)
        if 'explanation' in question and question['explanation']:
            translated_exp = self.translate(question['explanation'])
            if translated_exp is None:
                logger.warning(f"Failed to translate explanation - keeping original")
                translated['explanation'] = question['explanation']
            else:
                translated['explanation'] = translated_exp
        
        # Translate category (optional - keep original if fails)
        if 'category' in question and question['category']:
            translated_cat = self.translate(question['category'])
            if translated_cat is None:
                logger.warning(f"Failed to translate category - keeping original")
                translated['category'] = question['category']
            else:
                translated['category'] = translated_cat
        
        return translated
