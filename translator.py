import logging
import time
from deep_translator import GoogleTranslator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QuestionTranslator:
    def __init__(self, target_lang='gu'):
        self.target_lang = target_lang
        self.translator = GoogleTranslator(source='auto', target=target_lang)

    def translate_text(self, text):
        """Safely translates text, handling empty strings and errors."""
        if not text or not isinstance(text, str):
            return ""
        
        try:
            # Google Translate has a char limit, split if necessary (simple approach)
            if len(text) > 4000:
                return text # Skip very long texts to avoid errors
            
            return self.translator.translate(text)
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return text  # Return original text if translation fails

    def translate_questions(self, questions_data):
        """
        Iterates through the list of question dictionaries and translates fields.
        Handles both IndiaBix (with options) and Pendulum (without options).
        """
        logging.info(f"Starting translation of {len(questions_data)} items...")
        translated_data = []

        for idx, item in enumerate(questions_data):
            # Create a copy to avoid modifying the original list in place
            translated_item = item.copy()
            
            # 1. Translate Question
            if 'question' in item:
                translated_item['question_translated'] = self.translate_text(item['question'])
            
            # 2. Translate Answer
            if 'answer' in item:
                translated_item['answer_translated'] = self.translate_text(item['answer'])

            # 3. Translate Options (Only if they exist and are a list)
            if 'options' in item and isinstance(item['options'], list) and item['options']:
                translated_options = []
                for opt in item['options']:
                    translated_options.append(self.translate_text(opt))
                translated_item['options_translated'] = translated_options
            
            translated_data.append(translated_item)
            
            # Log progress
            if (idx + 1) % 10 == 0:
                logging.info(f"Translated {idx + 1}/{len(questions_data)}...")
            
            # Sleep to be polite to the translation API
            time.sleep(0.2)

        return translated_data