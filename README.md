# Current Affairs Scraper - Gujarati PDF Generator 📚

A Python application that scrapes current affairs questions from IndiaBix, translates them to Gujarati, and generates beautiful PDFs with mixed language support.

## 🎯 What This Does

- Scrapes weekly current affairs questions from IndiaBix.com
- Translates questions from English to Gujarati using Google Translate
- Generates professional PDFs with Gujarati + English mixed text
- Adds custom watermark (Pragati Setu logo) on every page
- Saves both English and Gujarati JSON files for backup

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python3 --version

# Install system fonts (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install fonts-noto-sans fonts-lohit-gujarati
Installation
bash
# Clone or download the project
cd current_affairs_scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Run
python3 main.py

📁 Project Structure

current_affairs_scraper/
├── .env                      # API keys (not needed for deep-translator)
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
├── pragati_setu.jpg        # Watermark logo
│
├── config.py               # Configuration settings
├── scraper.py              # Web scraping logic
├── translator.py           # Translation with retry logic
├── pdf_generator.py        # PDF generation with mixed fonts
├── main.py                 # Main orchestrator
│
└── output/                 # Generated files
    ├── questions_english.json
    ├── questions_gujarati.json
    └── current_affairs_YYYYMMDD_HHMMSS.pdf

🛠️ How It Works

1. Web Scraping
Scrapes IndiaBix.com for the last 7 days

Extracts questions, options, answers, and explanations

Saves raw English data to JSON

2. Translation Process
Uses deep-translator with Google Translate (free, no API key needed)

Translates each field with 3 retry attempts

If translation fails, keeps the original English text

Detects and prevents "box characters" (□) from appearing

3. PDF Generation
Uses mixed font support: Noto Sans Gujarati + Helvetica

Automatically detects Gujarati vs English characters

Applies correct font to each character to prevent boxes

Adds semi-transparent watermark on every page

🐛 The Box Problem Journey
What Was Happening?
When I first generated PDFs with Gujarati text, some words showed as boxes (□) instead of readable text. Here's the complete debugging journey:

Attempt 1: Font Installation ❌
Problem: Thought fonts weren't installed on the system.

Solution Tried:

sudo apt-get install fonts-gujarati
Result: Boxes still appeared. The fonts were installed, but ReportLab wasn't using them correctly.

Attempt 2: Register Gujarati Font ⚠️
Problem: ReportLab needed explicit font registration.

Solution Tried:

python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('GujaratiFont', 
    '/usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf'))
Result: Gujarati text worked, but English words in the middle of Gujarati sentences turned into boxes! The Gujarati font couldn't render English characters.

Attempt 3: Multiple Translation APIs 🔄
Problem: Started with Google Gemini API but hit various issues.

Solutions Tried:

3.1: Google Gemini API - gemini-1.5-flash
python
import google.generativeai as genai
model = genai.GenerativeModel('gemini-1.5-flash')
Result: Model not found (404 error). API was deprecated.

3.2: Google Gemini API - gemini-pro
python
model = genai.GenerativeModel('gemini-pro')
Result: Model not found (404 error). Also deprecated.

3.3: Google Gemini API - gemini-2.0-flash-exp
python
from google import genai
client = genai.Client(api_key=api_key)
model = 'gemini-2.0-flash-exp'
Result: Worked for 45 questions, then hit rate limits (429 RESOURCE_EXHAUSTED). Free tier has strict limits:

15 requests per minute

Limited daily quota

Translating 51 questions one-by-one exhausted the quota

3.4: Tried Batch Translation
python
# Translate 10 questions per API call
batch_size = 10
Result: Reduced API calls but still hit daily limits. Also, package was deprecated:

text
FutureWarning: All support for the `google.generativeai` package has ended.
Please switch to the `google.genai` package.
3.5: Argos Translate (Offline)

pip install argostranslate
argospm install translate-en_gu
Result:

Download got stuck

Translation was extremely slow (2-3 seconds per sentence)

Would take 10-15 minutes for 51 questions

Not practical for regular use

3.6: MyMemory Translation API
python
from deep_translator import MyMemoryTranslator
Result:

Also got stuck

Very slow response times

Free tier unreliable

3.7: LibreTranslate
python
requests.post("https://libretranslate.com/translate", data={...})
Result:

Free but slow

Unreliable availability

Translation quality not great for Gujarati

Attempt 4: Deep Translator - SUCCESS! ✅
Final Solution:

pip install deep-translator
python
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='en', target='gu')
translated = translator.translate(text)
Why This Worked:

Uses Google Translate behind the scenes (best quality)

No API key required

No rate limits on free tier (reasonable usage)

Fast response times

Reliable and well-maintained

Added Retry Logic:

python
def translate_text_with_retry(self, text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            translated = self.translator.translate(text)
            if not self._has_boxes(translated):
                return translated
        except Exception as e:
            if attempt == max_retries - 1:
                return text  # Keep English
            time.sleep(1)
    return text
Attempt 5: The Font Solution! ✅
Root Cause Discovery:
Even with perfect translations, boxes appeared because:

Gujarati text translated correctly

But some English words (names, technical terms) stayed in English

When Gujarati font was applied to entire paragraph, English characters showed as boxes

NotoSansGujarati.ttf doesn't include Latin alphabet

Final Solution: Character-level font detection!

python
def _wrap_mixed_text(self, text: str) -> str:
    """Automatically wrap each character with the correct font"""
    result = []
    current_text = ""
    current_is_gujarati = None
    
    for char in text:
        is_gujarati = '\u0A80' <= char <= '\u0AFF'  # Gujarati Unicode range
        
        if current_is_gujarati is None:
            current_is_gujarati = is_gujarati
            current_text = char
        elif current_is_gujarati == is_gujarati:
            current_text += char
        else:
            # Switch detected - wrap with appropriate font
            if current_is_gujarati:
                result.append(f'<font name="GujaratiFont">{current_text}</font>')
            else:
                result.append(f'<font name="Helvetica">{current_text}</font>')
            
            current_text = char
            current_is_gujarati = is_gujarati
    
    # Add remaining text
    if current_text:
        if current_is_gujarati:
            result.append(f'<font name="GujaratiFont">{current_text}</font>')
        else:
            result.append(f'<font name="Helvetica">{current_text}</font>')
    
    return ''.join(result)
How It Works:

Scan through each character in the text

Check if character is Gujarati (Unicode range U+0A80 to U+0AFF)

Group consecutive characters of same type

Wrap Gujarati groups with <font name="GujaratiFont">

Wrap English groups with <font name="Helvetica">

Result: Perfect mixed-language rendering!

Example:

Input: "ભારતની capital એ Delhi છે"

Output:
<font name="GujaratiFont">ભારતની</font>
<font name="Helvetica"> capital </font>
<font name="GujaratiFont">એ</font>
<font name="Helvetica"> Delhi </font>
<font name="GujaratiFont">છે</font>
Result: Perfect rendering! No more boxes! Every character uses the right font! 🎉

🎨 Features
Smart Translation with Retry Logic
The translator attempts each translation 3 times before giving up:

python
# Attempt 1: Try translation
# Attempt 2: Wait 1 second, try again
# Attempt 3: Wait 1 second, try again
# If all fail: Keep original English text
This ensures:

✅ Handles temporary network issues

✅ No boxes in the final PDF

✅ Graceful fallback to English

Mixed Language Support
The PDF generator automatically handles:

Gujarati sentences with English words mixed in

Numbers and punctuation

Technical terms that don't translate well

Names and proper nouns

Watermark Background
Every page has the Pragati Setu logo:

Centered on the page

10% opacity (subtle, doesn't interfere with text)

Automatically scaled to fit

📊 Output Files
1. questions_english.json
Raw scraped data in English

2. questions_gujarati.json
Translated data with mixed English-Gujarati

3. PDF File
Professional PDF with:

Mixed Gujarati-English text

Proper font rendering

Watermark background

Organized layout

🔧 Dependencies

beautifulsoup4==4.12.3     # Web scraping
requests==2.31.0            # HTTP requests
reportlab==4.0.7            # PDF generation
lxml==5.1.0                 # HTML parsing
deep-translator==1.11.4     # Translation (FREE!)
python-dotenv==1.0.0        # Environment variables

🚨 Troubleshooting
Problem: Boxes still appearing in PDF
Solution:

Install Gujarati fonts:

sudo apt-get install fonts-noto-sans fonts-lohit-gujarati
fc-cache -f -v
Verify font exists:

ls /usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf
Problem: Translation too slow
Solution:

python
# In translator.py, reduce delay
time.sleep(1.0)  # Instead of 1.5
Problem: Import errors
Solution:

pip install --upgrade -r requirements.txt

💡 Key Lessons Learned
Free API tiers have limits - Google Gemini exhausted after 45 questions

Package deprecation happens - Had to migrate from old to new Google AI SDK

Font rendering is complex - One font can't handle all scripts

Character-level detection works - Unicode ranges are reliable

Deep-translator is the winner - Simple, free, reliable for this use case

Always add retry logic - Networks fail, translations timeout

Test with real data - Discovered boxes only with actual mixed text

Made with ❤️ for Gujarati learners