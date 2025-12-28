import sys
import logging
from datetime import datetime
from config import get_date_range
from scraper import scrape_weekly_questions
from pdf_generator import PDFGenerator

# Configure logging
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
    """Main function to scrape and generate PDF"""
    
    logger.info("="*60)
    logger.info("IndiaBix Current Affairs Scraper Started")
    logger.info("="*60)
    
    try:
        # Get date range (past 7 days)
        dates = get_date_range()
        start_date = dates[-1].strftime('%Y-%m-%d')  # Oldest date
        end_date = dates[0].strftime('%Y-%m-%d')     # Today
        
        logger.info(f"Date range: {start_date} to {end_date}")
        
        # Scrape questions
        logger.info("Starting web scraping...")
        questions = scrape_weekly_questions(dates)
        
        if not questions:
            logger.warning("No questions found during scraping")
            print("No questions found. PDF generation skipped.")
            return False
        
        logger.info(f"Successfully scraped {len(questions)} questions")
        
        # Generate PDF
        logger.info("Generating PDF...")
        pdf_gen = PDFGenerator(output_dir="output")
        pdf_path = pdf_gen.generate_pdf(
            questions,
            start_date=start_date,
            end_date=end_date
        )
        
        if pdf_path:
            logger.info(f"PDF generated successfully: {pdf_path}")
            print(f"\nSUCCESS! PDF created: {pdf_path}")
            print(f"Total questions: {len(questions)}")
            return True
        else:
            logger.error("Failed to generate PDF")
            print("PDF generation failed")
            return False
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
