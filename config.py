from datetime import datetime, timedelta

# Base URL configuration
BASE_URL = "https://www.indiabix.com"
CURRENT_AFFAIRS_URL = f"{BASE_URL}/current-affairs/questions-and-answers/"

# Second Website URL
PENDULUM_URL = "https://pendulumedu.com/quiz/current-affairs"

# Request headers to avoid 403 errors (Mimics a real browser)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
TIMEOUT = 30  # seconds

# PDF configuration
PDF_OUTPUT_DIR = "output"
PDF_FONT_SIZE = 12
PDF_TITLE_FONT_SIZE = 16

# How many days to scrape backwards
DAYS_TO_SCRAPE = 6

def get_date_range():
    """
    Calculate the date range for PAST X days from today.
    """
    today = datetime.now()
    dates = []
    
    # Go backwards from today
    for i in range(DAYS_TO_SCRAPE + 1):
        date = today - timedelta(days=i)
        dates.append(date)
    
    return dates