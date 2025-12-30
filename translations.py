from google.cloud import translate_v2
import logging

logger = logging.getLogger(__name__)

class Translator:
    """Handle translations of text to gujarati"""

    def __init__(self):
        try:
            self.client = translate_v2
            logger.info("Google Translate client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize google translate: {e}")
            self.client = None

    def translate(self, text: str, target_language: str = 'gu') -> str:
        if not text or not text.strip():
            return text
        
        if not self.client:
            logger.warning("Google Translate not available, returning original text")
            return text
        
        try:
            result = self.client.translate_text(
                source_language='en',
                target_language=target_language,
                content_type='text/plain',
                values=[text]
            )

            if result and len(result['translations']) > 0:
                translated = result['translations'][0]['translatedText']
                logger.debug(f"Translated: {text[:50]}... ->  {translated[:50]}...")
                return translated
            else:
                logger.warning(f"No translation result for: {text[:50]}")
                return text
        
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
        
    def translate_question(self, question: dict) -> dict:
        translated = question.copy()

        if 'question' in question:
            translated['question'] = self.translate(question['question'])

        if 'options' in question:
            translated['options'] = [self.translate(option) for option in question['options']]

        if 'answer' in question:
            translated['answer'] = self.translate(question['answer'])

        if 'explanation' in question:
            translated['explanation'] = self.translate(question['explanation'])

        if 'category' in question:
            translated['category'] = self.translate(question['category'])

        return translated