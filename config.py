from datetime import datetime, timedelta

# Base URL configuration
BASE_URL = "https://www.indiabix.com"
CURRENT_AFFAIRS_URL = f"{BASE_URL}/current-affairs/questions-and-answers/"

# Request headers to avoid 403 errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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

# Scheduler configuration
SCHEDULE_DAY = "sun"  # Run every Sunday
SCHEDULE_HOUR = 23
SCHEDULE_MINUTE = 59

# How many days to scrape backwards
DAYS_TO_SCRAPE = 7


def get_date_range():
    """
    Calculate the date range for PAST 7 days from today (going backwards)
    
    Example: If today is Dec 28, 2025:
    - Returns: [Dec 28, Dec 27, Dec 26, Dec 25, Dec 24, Dec 23, Dec 22]
    """
    today = datetime.now()
    dates = []
    
    # Go backwards from today for DAYS_TO_SCRAPE days
    for i in range(DAYS_TO_SCRAPE):
        date = today - timedelta(days=i)
        dates.append(date)
    
    return dates
