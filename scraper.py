import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import HEADERS, MAX_RETRIES, RETRY_DELAY, TIMEOUT, CURRENT_AFFAIRS_URL, BASE_URL

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """create a requests session with retry strategy"""
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
    """fetch and parse a webpage"""
    try:
        logger.info(f"fetching: {url}")
        response = session.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        logger.info(f"successfully fetched: {url}")
        return soup
    
    except requests.exceptions.RequestException as e:
        logger.error(f"error fetching {url}: {str(e)}")
        return None


def extract_questions(soup: BeautifulSoup) -> List[Dict]:
    """extract questions, options, and answers from indiabix current affairs page"""
    questions_data = []
    
    try:
        # find all question containers
        question_blocks = soup.find_all('div', class_='bix-div-container')
        
        if not question_blocks:
            logger.warning("no question blocks found on page")
            return questions_data
        
        logger.info(f"found {len(question_blocks)} question blocks")
        
        for idx, block in enumerate(question_blocks, 1):
            try:
                # extract question number and text
                q_num_div = block.find('div', class_='bix-td-qno')
                q_text_div = block.find('div', class_='bix-td-qtxt')
                
                if not q_text_div:
                    continue
                
                question_text = q_text_div.get_text(strip=True)
                
                # extract options
                options = []
                option_container = block.find('div', class_='bix-tbl-options')
                if option_container:
                    option_divs = option_container.find_all('div', class_='bix-td-option-val')
                    for opt_div in option_divs:
                        opt_text = opt_div.get_text(strip=True)
                        if opt_text:
                            options.append(opt_text)
                
                # extract answer - it's in a hidden input
                answer = "Not available"
                answer_input = block.find('input', class_='jq-hdnakq')
                if answer_input:
                    answer_value = answer_input.get('value', '')
                    # answer is like "A", "B", "C", "D"
                    if answer_value and len(options) >= ord(answer_value) - ord('A') + 1:
                        answer_index = ord(answer_value) - ord('A')
                        answer = f"Option {answer_value}: {options[answer_index]}"
                    else:
                        answer = f"Option {answer_value}"
                
                # extract explanation
                explanation = ""
                exp_div = block.find('div', class_='bix-ans-description')
                if exp_div:
                    explanation = exp_div.get_text(strip=True)
                
                # extract category
                category = ""
                cat_link = block.find('div', class_='explain-link')
                if cat_link:
                    cat_a = cat_link.find('a')
                    if cat_a:
                        category = cat_a.get_text(strip=True)
                
                question_data = {
                    'question_no': idx,
                    'question': question_text,
                    'options': options,
                    'answer': answer,
                    'explanation': explanation,
                    'category': category
                }
                
                questions_data.append(question_data)
                # log snippet length limit
                logger.info(f"extracted q{idx}: {question_text[:60]}...")
                
            except Exception as e:
                logger.error(f"error extracting question {idx}: {str(e)}")
                continue
        
        logger.info(f"total questions extracted: {len(questions_data)}")
        return questions_data
    
    except Exception as e:
        logger.error(f"error in extract_questions: {str(e)}")
        return questions_data


def scrape_date_wise(date_obj, session: requests.Session) -> List[Dict]:
    """scrape questions for a specific date"""
    date_url = f"{BASE_URL}/current-affairs/{date_obj.strftime('%Y-%m-%d')}/"
    
    logger.info(f"scraping for date: {date_obj.strftime('%Y-%m-%d')}")
    
    soup = fetch_page(date_url, session)
    if not soup:
        logger.warning(f"failed to fetch page for {date_obj.strftime('%Y-%m-%d')}")
        return []
    
    # check if page exists (look for 404 error)
    error_alert = soup.find('div', class_='alert-danger')
    if error_alert and 'not found' in error_alert.get_text().lower():
        logger.warning(f"page not found for {date_obj.strftime('%Y-%m-%d')}")
        return []
    
    questions = extract_questions(soup)
    
    # add date metadata to each question
    for question in questions:
        question['date'] = date_obj.strftime('%Y-%m-%d')
    
    time.sleep(1)
    return questions


def scrape_weekly_questions(dates: List) -> List[Dict]:
    """scrape questions for all dates (no translation - just scraping)"""
    all_questions = []
    session = create_session()
    
    logger.info(f"starting scrape for {len(dates)} days (going backwards from today)")
    
    for date_obj in dates:
        questions = scrape_date_wise(date_obj, session)
        all_questions.extend(questions)
    
    logger.info(f"scrape complete. total questions: {len(all_questions)}")
    return all_questions
