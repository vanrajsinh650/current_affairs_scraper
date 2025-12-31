import sys
import logging
from datetime import datetime
from config import get_date_range
from scraper import scrape_weekly_questions
from translator import translate_questions_with_ai
from pdf_generator import PDFGenerator


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)


logger = logging.getLogger(__name__)


def main():
    """Main function"""
    
    logger.info("="*60)
    logger.info("IndiaBix Current Affairs Scraper - AI Translation")
    logger.info("="*60)
    
    try:
        # Get date range
        dates = get_date_range()
        start_date = dates[-1].strftime('%Y-%m-%d')
        end_date = dates[0].strftime('%Y-%m-%d')
        
        logger.info(f"Date range: {start_date} to {end_date}")
        
        # Scrape questions
        logger.info("Scraping questions...")
        print("\n Scraping questions...")
        questions = scrape_weekly_questions(dates)
        
        if not questions:
            print("No questions found")
            return False
        
        logger.info(f"Scraped {len(questions)} questions")
        print(f"✓ Scraped {len(questions)} questions")
        
        # Translate using AI
        gujarati_questions = translate_questions_with_ai(questions)
        
        # Generate PDF with watermark
        logger.info("Generating PDF...")
        print("\nGenerating Gujarati PDF with watermark...")
        
        # Watermark image 
        watermark_path = "pragati_setu.jpg"
        
        pdf_gen = PDFGenerator(
            output_dir="output", 
            language='gu',
            watermark_image=watermark_path  # Added watermark!
        )
        
        pdf_path = pdf_gen.generate_pdf(
            gujarati_questions,
            start_date=start_date,
            end_date=end_date
        )
        
        if pdf_path:
            print(f"\n SUCCESS! Gujarati PDF created: {pdf_path}")
            print(f"Total questions: {len(gujarati_questions)}")
            print(f"\n Files created:")
            print(f"output/questions_english.json")
            print(f"output/questions_gujarati.json")
            print(f"{pdf_path}")
            return True
        else:
            print(" PDF generation failed")
            return False
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n Error: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
