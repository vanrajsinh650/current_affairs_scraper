from datetime import datetime, timedelta

# Base URL configuration
BASE_URL = "https://www.indiabix.com"
CURRENT_AFFAIRS_URL = f"{BASE_URL}/current-affairs/questions-and-answers/"

# Request headers to avoide 402 error
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2 # 2 Seconds
TIMEOUT = 30 # Seconds

# PDF configuration
PDF_OUTPUT_DIR = "output"
PDF_FONT_SIZE = 12
PDF_TITLE_FONT_SIZE = 16

# Scheduler configuration
SCHEDULE_DAY = "sun" # RUN every sunday
SCHEDULE_HOUR =  23
SCHEDULE_MINUTE = 59

# Data calculation - get last 7 days sunday to saturday
def get_date_range():
    todey = datetime.now()
    # Find last sunday ( 0 = Monday, 6 = Sunday in weekday())
    days_since_sunday = (todey.weekday() + 1) % 7
    last_sunday = todey - timedelta(days=days_since_sunday)

    dates = []
    for i in range(7):
        date = last_sunday + timedelta(days=i)
        dates.append(date)

    return dates