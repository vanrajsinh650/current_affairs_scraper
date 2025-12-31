import json
import logging
import os
import time
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DeepTranslatorGU:
    """Gujarati translator with retry logic and fallback to English"""
    
    def __init__(self):
        """Initialize Google Translator"""
        try:
            self.translator = GoogleTranslator(source='en', target='gu')
            logger.info("Deep Translator initialized")
            print("✓ Deep Translator connected (Google Translate - FREE)")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            print(f"Failed: {e}")
            self.translator = None
    
    def translate_text_with_retry(self, text: str, max_retries: int = 3) -> str:
        """Translate text with retry logic"""
        if not text or not text.strip():
            return text
        
        # Try translating multiple times
        for attempt in range(max_retries):
            try:
                # Google Translate has 5000 char limit per request
                if len(text) > 4500:
                    # Split long text
                    chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
                    translated_chunks = []
                    
                    for chunk in chunks:
                        translated = self.translator.translate(chunk)
                        # If translation returns boxes or fails, keep English
                        if self._has_boxes(translated) or not translated:
                            translated_chunks.append(chunk)
                        else:
                            translated_chunks.append(translated)
                    
                    return ' '.join(translated_chunks)
                else:
                    translated = self.translator.translate(text)
                    
                    # Check if translation has boxes (failed words)
                    if self._has_boxes(translated):
                        logger.warning(f"Translation has boxes, keeping original: {text[:50]}")
                        return text  # Return original English
                    
                    return translated
                    
            except Exception as e:
                logger.warning(f"Translation attempt {attempt + 1} failed: {e}")
                
                # Last attempt failed, return original English text
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed, keeping English: {text[:50]}")
                    return text
                
                # Wait before retry
                time.sleep(1)
        
        # Fallback: return original English
        return text
    
    def _has_boxes(self, text: str) -> bool:
        """Check if translated text has box characters (failed translation)"""
        # Box characters appear when font can't render
        box_chars = ['□', '▯', '◻', '▢']
        return any(char in text for char in box_chars)
    
    def translate_question(self, question: dict, q_num: int) -> dict:
        """Translate entire question with retry logic"""
        translated = question.copy()
        
        try:
            # Translate question
            if 'question' in question:
                original = question['question']
                translated['question'] = self.translate_text_with_retry(original, max_retries=3)
                
                # Log if kept in English
                if translated['question'] == original:
                    logger.info(f"Q{q_num} question kept in English")
            
            # Translate options
            if 'options' in question:
                translated['options'] = []
                for idx, opt in enumerate(question['options']):
                    trans_opt = self.translate_text_with_retry(opt, max_retries=3)
                    translated['options'].append(trans_opt)
                    
                    if trans_opt == opt:
                        logger.info(f"Q{q_num} option {idx+1} kept in English")
            
            # Translate answer
            if 'answer' in question:
                original = question['answer']
                translated['answer'] = self.translate_text_with_retry(original, max_retries=3)
                
                if translated['answer'] == original:
                    logger.info(f"Q{q_num} answer kept in English")
            
            # Translate explanation
            if 'explanation' in question and question['explanation']:
                original = question['explanation']
                translated['explanation'] = self.translate_text_with_retry(original, max_retries=3)
                
                if translated['explanation'] == original:
                    logger.info(f"Q{q_num} explanation kept in English")
            
            # Translate category
            if 'category' in question and question['category']:
                original = question['category']
                translated['category'] = self.translate_text_with_retry(original, max_retries=3)
                
                if translated['category'] == original:
                    logger.info(f"Q{q_num} category kept in English")
            
            return translated
            
        except Exception as e:
            logger.error(f"Failed to translate question {q_num}: {e}")
            return question  # Return original if everything fails
    
    def translate_all(self, questions: list) -> list:
        """Translate all questions"""
        if not self.translator:
            return questions
        
        translated_questions = []
        total = len(questions)
        
        print(f"Translating {total} questions to Gujarati...")
        print(f"(With 3 retries per field, ~{total * 2} seconds)")
        
        for i, question in enumerate(questions, 1):
            print(f"Translating Q{i}/{total}...", end=" ")
            
            translated_q = self.translate_question(question, i)
            translated_questions.append(translated_q)
            
            print("DONE!")
            
            # Small delay to avoid rate limits
            time.sleep(1.5)
        
        return translated_questions


def save_questions_json(questions: list, filename: str):
    """Save questions to JSON file"""
    try:
        os.makedirs("output", exist_ok=True)
        filepath = os.path.join("output", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved to {filepath}")
        print(f"Saved: {filename}")
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to save: {e}")
        print(f"Failed to save: {e}")
        return None


def translate_questions_with_ai(questions: list) -> list:
    """Main translation function with retry logic"""
    print(f"\n Starting Translation (Deep Translator with 3 retries)")
    start_time = time.time()
    
    # Step 1: Save English
    print("\n Saving English questions...")
    save_questions_json(questions, "questions_english.json")
    
    # Step 2: Translate to Gujarati
    print("\n Translating to Gujarati (with retry)...")
    translator = DeepTranslatorGU()
    
    if not translator.translator:
        print("Translation skipped")
        save_questions_json(questions, "questions_gujarati.json")
        return questions
    
    gujarati_questions = translator.translate_all(questions)
    
    # Save Gujarati
    print("\n Saving Gujarati questions...")
    save_questions_json(gujarati_questions, "questions_gujarati.json")
    
    elapsed = time.time() - start_time
    print(f"\n Translation complete in {elapsed:.1f} seconds")
    
    # Count successful translations
    success_count = sum(1 for i, q in enumerate(gujarati_questions) 
                       if q['question'] != questions[i]['question'])
    
    print(f"\n Translation Stats:")
    print(f"Total questions: {len(questions)}")
    print(f"Successfully translated: {success_count}")
    print(f"Kept in English: {len(questions) - success_count}")
    
    # Show sample
    print(f"\n Sample (Q1):")
    print(f"English:  {questions[0]['question'][:70]}...")
    print(f"Gujarati: {gujarati_questions[0]['question'][:70]}...")
    
    return gujarati_questions
