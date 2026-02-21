import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import HEADERS, MAX_RETRIES, RETRY_DELAY, TIMEOUT, CURRENT_AFFAIRS_URL, PENDULUM_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()]
)

class BaseScraper:
    def __init__(self):
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=MAX_RETRIES, 
            backoff_factor=RETRY_DELAY, 
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(HEADERS)
        return session

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

class IndiaBixScraper(BaseScraper):
    def scrape(self, target_dates: List[datetime]) -> List[Dict]:
        all_questions = []
        logging.info("Starting IndiaBix scrap...")
        
        # Generate direct date links for IndiaBix
        daily_links = []
        for date_obj in target_dates:
            formatted_date_url = date_obj.strftime("%Y/%m/%d") # /2024/02/20/
            full_link = f"https://www.indiabix.com/current-affairs/{formatted_date_url}/"
            daily_links.append(full_link)

        for link in daily_links:
            logging.info(f"Checking IndiaBix URL: {link}")
            page_soup = self.fetch_page(link)
            if not page_soup:
                continue

            containers = page_soup.find_all('div', class_='bix-div-container')
            if not containers:
                logging.warning(f"No questions found at {link}")
                continue

            for container in containers:
                try:
                    question_elem = container.find('td', class_='bix-td-qtxt')
                    if not question_elem:
                        continue
                    
                    question_text = question_elem.get_text(strip=True)
                    
                    options = []
                    option_rows = container.find_all('tr', class_='bix-tbl-options')
                    for row in option_rows:
                        opt_val = row.find('td', class_='bix-td-option-val')
                        if opt_val:
                            options.append(opt_val.get_text(strip=True))
                    
                    answer_div = container.find('div', class_='bix-div-answer')
                    answer_text = "Refer to website"
                    if answer_div:
                         answer_text = answer_div.get_text(strip=True).replace("View Answer", "").strip()

                    all_questions.append({
                        "question": question_text,
                        "options": options,
                        "answer": answer_text,
                        "source": "IndiaBix",
                        "date": link.split('/')[-2]
                    })
                except Exception as e:
                    logging.error(f"Error parsing IndiaBix question: {e}")

        logging.info(f"IndiaBix: Found {len(all_questions)} questions.")
        return all_questions

class PendulumScraper(BaseScraper):
    def scrape(self, target_dates: List[datetime]) -> List[Dict]:
        all_questions = []
        logging.info("Starting PendulumEdu scrap...")
        
        soup = self.fetch_page(PENDULUM_URL)
        if not soup:
            return []

        quiz_links = []
        anchors = soup.find_all('a', href=True)
        
        for date_obj in target_dates:
            date_str = date_obj.strftime("%d %B %Y").lstrip("0") # "14 February 2024"
            
            for tag in anchors:
                if date_str.lower() in tag.get_text(strip=True).lower():
                    full_url = urljoin(PENDULUM_URL, tag['href'])
                    if full_url not in quiz_links:
                        quiz_links.append(full_url)
                        logging.info(f"Found match for {date_str}: {full_url}")

        for link in quiz_links:
            logging.info(f"Scraping Pendulum Quiz: {link}")
            q_soup = self.fetch_page(link)
            if not q_soup:
                continue
            
            # Heuristic parsing for PendulumEdu
            questions_containers = q_soup.find_all('div', class_='question-container') 
            if not questions_containers:
                questions_containers = q_soup.find_all('p')
            
            current_q = None
            
            for elem in questions_containers:
                text = elem.get_text(strip=True)
                
                # Check if it looks like a question
                if text and (text.startswith("Q") or "?" in text) and len(text) > 20:
                    if current_q:
                        all_questions.append(current_q)
                    
                    current_q = {
                        "question": text,
                        "options": [], # Options often hard to parse without specific class
                        "answer": "Check Link",
                        "source": "PendulumEdu",
                        "link": link
                    }
                # Check if it looks like an answer
                elif current_q and "Ans." in text:
                    current_q["answer"] = text
                
                # Try to capture options if they are simple bullet points immediately following question
                elif current_q and len(text) < 100 and text[0].isalpha() and text[1] == '.':
                     current_q["options"].append(text)
            
            if current_q:
                all_questions.append(current_q)

        logging.info(f"PendulumEdu: Found {len(all_questions)} questions.")
        return all_questions

def scrape_weekly_questions(date_range: List[datetime]) -> Dict[str, List[Dict]]:
    """
    Returns a dictionary separated by source.
    Example: {'IndiaBix': [...], 'PendulumEdu': [...]}
    """
    data_map = {}
    
    # Run IndiaBix
    ib_scraper = IndiaBixScraper()
    data_map["IndiaBix"] = ib_scraper.scrape(date_range)
    
    # Run Pendulum
    pd_scraper = PendulumScraper()
    data_map["PendulumEdu"] = pd_scraper.scrape(date_range)
    
    return data_map