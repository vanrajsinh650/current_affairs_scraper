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
    session.mount("https://", adapter)  # FIXED: was "htpps://"
    
    return session


def fetch_page(url: str, session: requests.Session) -> Optional[BeautifulSoup]:  # FIXED: was requests.sessions
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
    """Extract questions, options, and answers"""
    questions_data = []
    
    try:
        question_blocks = soup.find_all('div', class_='bix-div-container')
        
        if not question_blocks:
            logger.warning("No questions found on page")
            return questions_data
        
        for idx, block in enumerate(question_blocks, 1):
            try:
                question_div = block.find('td', class_='bix-td-qtxt')
                if not question_div:
                    continue
                
                question_text = question_div.get_text(strip=True)
                
                # Extract options
                options = []
                option_table = block.find('table', class_='notranslate')
                if option_table:
                    option_rows = option_table.find_all('tr')
                    for row in option_rows:
                        option_text = row.get_text(strip=True)
                        if option_text and len(option_text) > 2:
                            options.append(option_text)
                
                # Extract answer
                answer_div = block.find('div', class_='bix-answer-explain')
                answer = "Not available"
                explanation = ""
                
                if answer_div:
                    answer_span = answer_div.find('span', class_='jq-hdnakqb')
                    if answer_span:
                        answer = answer_span.get_text(strip=True)
                    
                    explanation_div = answer_div.find('div', class_='bix-ans-description')
                    if explanation_div:
                        explanation = explanation_div.get_text(strip=True)
                
                question_data = {
                    'question_no': idx,
                    'question': question_text,
                    'options': options,
                    'answer': answer,
                    'explanation': explanation
                }
                
                questions_data.append(question_data)
                logger.info(f"Extracted question {idx}: {question_text[:50]}...")
                
            except Exception as e:
                logger.error(f"Error extracting question {idx}: {str(e)}")
                continue
        
        logger.info(f"Total questions extracted: {len(questions_data)}")
        return questions_data
    
    except Exception as e:
        logger.error(f"Error in extract_questions: {str(e)}")
        return questions_data


def scrape_date_wise(date_obj, session: requests.Session) -> List[Dict]:
    """Scrape questions for a specific date"""
    date_url = f"{BASE_URL}/current-affairs/{date_obj.strftime('%Y-%m-%d')}"
    
    logger.info(f"Scraping for date: {date_obj.strftime('%Y-%m-%d')}")
    
    soup = fetch_page(date_url, session)
    if not soup:
        logger.warning(f"Failed to fetch page for {date_obj.strftime('%Y-%m-%d')}")
        return []
    
    questions = extract_questions(soup)
    
    for question in questions:
        question['date'] = date_obj.strftime('%Y-%m-%d')  # FIXED: was 'data'
    
    time.sleep(1)
    return questions


def scrape_weekly_questions(dates: List) -> List[Dict]:
    """Scrape questions for the entire week"""
    all_questions = []
    session = create_session()
    
    logger.info(f"Starting weekly scrape for {len(dates)} days")
    
    for date_obj in dates:
        questions = scrape_date_wise(date_obj, session)
        all_questions.extend(questions)
    
    logger.info(f"Weekly scrape complete. Total questions: {len(all_questions)}")
    return all_questions


if __name__ == "__main__":
    from config import get_date_range
    
    dates = get_date_range()
    questions = scrape_weekly_questions(dates)
    
    print(f"\nScraping Summary:")
    print(f"Total questions scraped: {len(questions)}")
    if questions:
        print(f"\nSample question:")
        print(f"Q: {questions[0]['question']}")
        print(f"Options: {questions[0]['options']}")
        print(f"Answer: {questions[0]['answer']}")
