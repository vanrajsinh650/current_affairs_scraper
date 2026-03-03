import json
import logging
import os
import re
import time
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class ImprovedGujaratiTranslator:
    """Enhanced Google Translator with pre/post-processing"""
    
    def __init__(self):
        try:
            self.translator = GoogleTranslator(source='en', target='gu')
            print("✓ Enhanced Gujarati Translator Ready")
            logger.info("✓ Translator initialized")
        except Exception as e:
            logger.error(f"Failed: {e}")
            self.translator = None
    
    def preprocess_text(self, text: str) -> tuple[str, dict]:
        """Clean English before translation & extract entities"""
        if not text:
            return text, {}
        
        # Store proper nouns and special terms to restore later
        entities = {}
        counter = 0
        
        # Protect proper nouns (capitalized words)
        def protect_entity(match):
            nonlocal counter
            placeholder = f"__ENTITY{counter}__"
            entities[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        # Protect: Article numbers
        text = re.sub(r'\bArticle \d+(?:\(\d+\))?', protect_entity, text)
        
        # Protect: Numbers with units ($, km, %, kg, etc.)
        text = re.sub(r'\$[\d,\.]+\s*(?:billion|million|thousand)?', protect_entity, text)
        text = re.sub(r'\d+[\d,\.]*\s*(?:km|kg|crore|lakh|million|billion|%|feet|tonnes?)', protect_entity, text, flags=re.IGNORECASE)
        
        # Protect: Years and dates
        text = re.sub(r'\b(19|20)\d{2}(?:-\d{2}-\d{2})?\b', protect_entity, text)
        
        # Protect: Organization abbreviations
        text = re.sub(r'\b[A-Z]{2,}(?:-[A-Z]{2,})?\b', protect_entity, text)
        
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Fix common punctuation
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text, entities
    
    def postprocess_text(self, gujarati: str, entities: dict) -> str:
        """Restore entities after translation"""
        if not gujarati:
            return gujarati
        
        # Restore protected entities
        for placeholder, original in entities.items():
            gujarati = gujarati.replace(placeholder, original)
        
        # Fix spacing around punctuation
        gujarati = re.sub(r'\s+([?,\.!।])', r'\1', gujarati)
        gujarati = re.sub(r'([?,\.!।])\s*', r'\1 ', gujarati)
        gujarati = gujarati.strip()
        
        return gujarati
    
    def translate_text(self, text: str, max_retries: int = 3) -> str:
        """Translate with pre/post processing"""
        if not text or not text.strip():
            return text
        
        # Preprocess
        clean_text, entities = self.preprocess_text(text)
        
        # Translate
        for attempt in range(max_retries):
            try:
                if len(clean_text) > 4500:
                    chunks = [clean_text[i:i+4500] for i in range(0, len(clean_text), 4500)]
                    result = ' '.join([self.translator.translate(chunk) for chunk in chunks])
                else:
                    result = self.translator.translate(clean_text)
                
                if result and '□' not in result:
                    # Postprocess
                    result = self.postprocess_text(result, entities)
                    return result
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    return text
                time.sleep(1)
        
        return text
    
    def translate_question(self, question: dict, q_num: int) -> dict:
        """Translate question with special handling"""
        if not self.translator:
            return question
            
        translated = question.copy()
        
        try:
            # Question text
            if 'question' in question:
                translated['question'] = self.translate_text(question['question'])
            
            # Options - keep format clean
            if 'options' in question:
                translated['options'] = [
                    self.translate_text(opt) for opt in question['options']
                ]
            
            # Answer - keep option letter
            if 'answer' in question:
                # Extract "Option A: " part and translate rest
                match = re.match(r'(Option [A-D]:\s*)(.*)', question['answer'])
                if match:
                    prefix, answer_text = match.groups()
                    translated['answer'] = f"{prefix}{self.translate_text(answer_text)}"
                else:
                    translated['answer'] = self.translate_text(question['answer'])
            
            # Explanation
            if 'explanation' in question and question['explanation']:
                translated['explanation'] = self.translate_text(question['explanation'])
            
            # Category - keep English
            if 'category' in question:
                translated['category'] = question['category']  # Keep English
            
            # Date - keep English format
            if 'date' in question:
                translated['date'] = question['date']  # Keep YYYY-MM-DD
            
            return translated
            
        except Exception as e:
            logger.error(f"Q{q_num} translation failed: {e}")
            return question
    
    def translate_all(self, questions: list) -> list:
        """Translate all questions"""
        if not self.translator:
            return questions
        
        translated = []
        total = len(questions)
        
        print(f"Translating {total} questions with preprocessing...")
        
        for i, q in enumerate(questions, 1):
            print(f"Q{i}/{total}...", end=" ", flush=True)
            translated.append(self.translate_question(q, i))
            print("DONE!")
            time.sleep(1.5)  # Rate limit
        
        return translated

def save_questions_json(questions: list, filename: str):
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"{filename}")
    return filepath

def translate_questions_with_ai(questions: list) -> list:
    print(f"\nEnhanced Google Translate (with Pre/Post Processing)")
    start = time.time()
    
    print("\nSaving English...")
    save_questions_json(questions, "questions_english.json")
    
    print("\nTranslating to Gujarati...")
    translator = ImprovedGujaratiTranslator()
    
    if not translator.translator:
        save_questions_json(questions, "questions_gujarati.json")
        return questions
    
    gujarati = translator.translate_all(questions)
    
    print("\nSaving Gujarati...")
    save_questions_json(gujarati, "questions_gujarati.json")
    
    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.0f}s")
    
    # Show comparison
    if gujarati and len(gujarati) > 0:
        print("\nSample Translation:")
        print(f"EN: {questions[0]['question'][:70]}...")
        print(f"GU: {gujarati[0]['question'][:70]}...")
    
    return gujarati
