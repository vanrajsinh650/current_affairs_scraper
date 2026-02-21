import sys
import logging
import os
import json
from datetime import datetime
from config import get_date_range, PDF_OUTPUT_DIR
from scraper import scrape_weekly_questions
from translator import QuestionTranslator
from pdf_generator import PDFGenerator

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    try:
        logging.info("=== Starting Weekly Current Affairs Job ===")
        
        # 1. Get Date Range
        dates = get_date_range()
        logging.info(f"Targeting dates: {[d.strftime('%Y-%m-%d') for d in dates]}")
        
        # 2. Scrape Data (Returns a Dictionary now)
        logging.info("Step 1: Scraping data from websites...")
        scraped_data_map = scrape_weekly_questions(dates)
        
        # Check if we found anything at all
        if not any(scraped_data_map.values()):
            logging.warning("No questions found from any source for the given date range. Exiting.")
            return

        # Ensure output directory exists
        if not os.path.exists(PDF_OUTPUT_DIR):
            os.makedirs(PDF_OUTPUT_DIR)

        # 3. Process each website separately
        for source_name, questions in scraped_data_map.items():
            if not questions:
                logging.warning(f"Skipping {source_name} (No data found).")
                continue

            logging.info(f"--- Processing {source_name} ({len(questions)} items) ---")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # A. Save separate JSON file
            json_filename = f"{source_name}_Data_{timestamp}.json"
            json_path = os.path.join(PDF_OUTPUT_DIR, json_filename)
            
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=4)
                logging.info(f"JSON saved: {json_path}")
            except Exception as e:
                logging.error(f"Failed to save JSON for {source_name}: {e}")

            # B. Translate
            logging.info(f"Translating {source_name} data...")
            try:
                translator = QuestionTranslator(target_lang='gu')
                questions = translator.translate_questions(questions)
            except Exception as e:
                logging.error(f"Translation failed for {source_name}: {e}. Proceeding with original text.")

            # C. Generate separate PDF
            logging.info(f"Generating PDF for {source_name}...")
            pdf_filename = f"{source_name}_Current_Affairs_{timestamp}.pdf"
            
            try:
                pdf_gen = PDFGenerator(PDF_OUTPUT_DIR)
                output_path = pdf_gen.generate(questions, pdf_filename)
                logging.info(f"PDF saved: {output_path}")
            except Exception as e:
                logging.error(f"PDF generation failed for {source_name}: {e}")

        logging.info("=== Job Completed Successfully ===")

    except Exception as e:
        logging.error(f"An error occurred in main execution: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()