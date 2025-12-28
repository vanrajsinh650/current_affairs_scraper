import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import HEADERS, MAX_RETRIES, RETRY_DELAY, TIMEOUT, CURRENT_AFFAIRS_URL, BASE_URL

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


def create_session() -> requests.Session:
    """Create a requests session with retry strategy"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_DELAY,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def fetch_page(url: str, session: requests.Session) -> Optional[BeautifulSoup]:
    """Fetch and parse a webpage"""
    try:
        logger.info(f"Fetching: {url}")
        response = session.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        logger.info(f"Successfully fetched: {url}")
        return soup
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None


def extract_questions(soup: BeautifulSoup) -> List[Dict]:
    """Extract questions, options, and answers from IndiaBix current affairs page"""
    questions_data = []
    
    try:
        # Find main content area - try different selectors
        content = soup.find('div', class_='col-md-8')
        
        if not content:
            content = soup.find('section', class_='section')
        
        if not content:
            # Last resort: get main wrapper
            content = soup.find('main', class_='main-wrapper')
        
        if not content:
            logger.warning("No content div found on page")
            return questions_data
        
        # Find all paragraphs and headings
        all_elements = content.find_all(['p', 'h3', 'h4', 'h5'])
        
        current_question = None
        question_num = 0
        
        for elem in all_elements:
            text = elem.get_text(strip=True)
            
            # Skip empty or very short text
            if not text or len(text) < 10:
                continue
            
            # Check if this is a question (ends with ?)
            if '?' in text and len(text) > 20 and not text.startswith('Answer') and not text.startswith('Why'):
                # Save previous question if exists
                if current_question and current_question.get('question'):
                    questions_data.append(current_question)
                
                # Start new question
                question_num += 1
                current_question = {
                    'question_no': question_num,
                    'question': text,
                    'options': [],
                    'answer': 'Not available',
                    'explanation': '',
                    'category': ''
                }
                logger.info(f"Found question {question_num}: {text[:60]}...")
            
            # Check for Answer
            elif text.startswith('Answer:') and current_question:
                answer_text = text.replace('Answer:', '').strip()
                current_question['answer'] = answer_text if answer_text else 'Not available'
            
            # Check for Explanation
            elif text.startswith('Explanation:') and current_question:
                explanation = text.replace('Explanation:', '').strip()
                current_question['explanation'] = explanation
            
            # Check for Category
            elif text.startswith('Category :') and current_question:
                category = text.replace('Category :', '').strip()
                current_question['category'] = category
        
        # Add the last question
        if current_question and current_question.get('question'):
            questions_data.append(current_question)
        
        logger.info(f"Total questions extracted: {len(questions_data)}")
        return questions_data
    
    except Exception as e:
        logger.error(f"Error in extract_questions: {str(e)}")
        return questions_data


def scrape_date_wise(date_obj, session: requests.Session) -> List[Dict]:
    """Scrape questions for a specific date"""
    date_url = f"{BASE_URL}/current-affairs/{date_obj.strftime('%Y-%m-%d')}/"
    
    logger.info(f"Scraping for date: {date_obj.strftime('%Y-%m-%d')}")
    
    soup = fetch_page(date_url, session)
    if not soup:
        logger.warning(f"Failed to fetch page for {date_obj.strftime('%Y-%m-%d')}")
        return []
    
    # Check if page exists (look for 404 error)
    error_alert = soup.find('div', class_='alert-danger')
    if error_alert and 'not found' in error_alert.get_text().lower():
        logger.warning(f"Page not found for {date_obj.strftime('%Y-%m-%d')}")
        return []
    
    questions = extract_questions(soup)
    
    for question in questions:
        question['date'] = date_obj.strftime('%Y-%m-%d')
    
    time.sleep(1)
    return questions


def scrape_weekly_questions(dates: List) -> List[Dict]:
    """Scrape questions for the entire week"""
    all_questions = []
    session = create_session()
    
    logger.info(f"Starting scrape for {len(dates)} days (going backwards from today)")
    
    for date_obj in dates:
        questions = scrape_date_wise(date_obj, session)
        all_questions.extend(questions)
    
    logger.info(f"Scrape complete. Total questions: {len(all_questions)}")
    return all_questions


if __name__ == "__main__":
    from config import get_date_range
    
    # Get dates
    dates = get_date_range()
    
    print("\n" + "="*60)
    print("SCRAPING PAST 7 DAYS OF CURRENT AFFAIRS")
    print("="*60)
    print("\nWill scrape these dates:")
    for date in dates:
        print(f"  - {date.strftime('%Y-%m-%d (%A)')}")
    
    print("\nStarting scraper...\n")
    
    # Scrape questions
    questions = scrape_weekly_questions(dates)
    
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    print(f"Total questions scraped: {len(questions)}")
    
    if questions:
        print(f"\nSample question:")
        print(f"Q: {questions[0]['question'][:100]}...")
        print(f"Answer: {questions[0]['answer']}")
        print(f"Category: {questions[0].get('category', 'N/A')}")
        print(f"Date: {questions[0].get('date', 'N/A')}")
    else:
        print("\nNo questions found. Possible reasons:")
        print("   - IndiaBix hasn't published questions for these dates yet")
        print("   - HTML structure has changed")
        print("   - Network issues")
        print("\nTip: Run debug_html.py to inspect the page structure")
