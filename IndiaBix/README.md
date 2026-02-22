# Current Affairs Scraper - Gujarati PDF Generator 📚

A Python application that scrapes current affairs questions from IndiaBix, translates them to Gujarati, and generates beautiful PDFs with proper Indic script rendering.

## 🎯 What This Does

- Scrapes weekly current affairs questions from IndiaBix.com
- Translates questions from English to Gujarati using Google Translate
- Generates professional PDFs with proper Gujarati conjunct rendering
- Adds custom watermark (Pragati Setu logo) on every page
- Saves both English and Gujarati JSON files for backup

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python3 --version

# Install system fonts and WeasyPrint dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install fonts-noto-core fonts-lohit-gujr
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0
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
bash
python3 main.py
📁 Project Structure
text
current_affairs_scraper/
├── .env                      # API keys (not needed for deep-translator)
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
├── pragati_setu.jpg        # Watermark logo
│
├── config.py               # Configuration settings
├── scraper.py              # Web scraping logic
├── translator.py           # Translation with retry logic
├── pdf_generator.py        # PDF generation with WeasyPrint
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

Protects English terms (Article 21, proper nouns) from translation

3. PDF Generation with WeasyPrint
Uses WeasyPrint for proper Gujarati conjunct rendering

Gujarati text rendered with Noto Sans Gujarati / Lohit Gujarati fonts

English text rendered with Helvetica / Arial fonts

Adds semi-transparent watermark on every page using CSS positioning

🐛 The Gujarati Rendering Problem - SOLVED!
The Journey from ReportLab to WeasyPrint
Problem: Broken Gujarati Conjuncts
When using ReportLab, Gujarati conjuncts (combined characters) rendered incorrectly[web:143][web:147]:

Expected: બંધારણના (Constitution)
Got: બ ં ધ ા ર ણ ન ા (broken characters)

Root Cause: ReportLab lacks OpenType shaping support needed for complex Indic scripts that use conjuncts, half-letters, and ligatures[web:147].

Attempts That Failed ❌
Font Registration in ReportLab

python
pdfmetrics.registerFont(TTFont('GujaratiFont', 'NotoSansGujarati.ttf'))
Result: Conjuncts still broken because ReportLab doesn't process OpenType ligature tables[web:143].

Character-level Font Switching

python
def _wrap_mixed_text(text):
    # Detect Gujarati vs English characters
    # Apply GujaratiFont or Helvetica accordingly
Result: Still broken - the issue wasn't font selection, it was text shaping[web:147].

Multiple Font Libraries
Tried: Lohit Gujarati, Noto Sans Gujarati, Mukta
Result: All showed same problem - ReportLab limitation, not font issue[web:149].

The Solution: WeasyPrint ✅
Why WeasyPrint Works:

Uses Pango text layout engine for proper text shaping[web:143][web:145]

Full OpenType feature support (ligatures, conjuncts, half-letters)

CSS-based styling (easier than ReportLab's manual positioning)[web:143]

HTML/CSS to PDF conversion with web standards compliance[web:145]

Implementation:

python
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Generate PDF with proper Gujarati rendering
HTML(string=html_content).write_pdf(
    filepath,
    stylesheets=[css],
    font_config=font_config
)
CSS for Mixed Language Support:

css
body {
    font-family: "Noto Sans Gujarati", "Lohit Gujarati", sans-serif;
}
.english {
    font-family: "Helvetica", "Arial", sans-serif;
}
Result: Perfect Gujarati conjuncts! બંધારણના renders correctly with proper half-letters and ligatures[web:143][web:145].

Translation API Journey
Attempts That Failed/Had Issues:
Google Gemini API - gemini-1.5-flash ❌

Error: Model not found (404)

Status: Deprecated

Google Gemini API - gemini-pro ❌

Error: Model not found (404)

Status: Deprecated

Google Gemini API - gemini-2.0-flash-exp ⚠️

Worked for 45 questions, then hit rate limits (429 RESOURCE_EXHAUSTED)

Free tier limits: 15 requests/minute, strict daily quota

Warning: Package deprecated, migrate to google.genai

Argos Translate (Offline) ❌

Download got stuck

Extremely slow (2-3 seconds per sentence)

Would take 10-15 minutes for 51 questions

MyMemory Translation API ❌

Got stuck frequently

Very slow response times

Free tier unreliable

LibreTranslate ❌

Free but slow

Unreliable availability

Poor translation quality for Gujarati

Final Solution: deep-translator ✅
bash
pip install deep-translator
python
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='en', target='gu')
translated = translator.translate(text)
Why This Works:

Uses Google Translate behind the scenes (best quality)

No API key required

No rate limits on free tier (reasonable usage)

Fast response times

Reliable and well-maintained

Built-in retry logic for network issues

🎨 Features
Smart Translation with Retry Logic
python
def translate_text_with_retry(self, text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            translated = self.translator.translate(text)
            if translated and '□' not in translated:
                return translated
        except Exception as e:
            if attempt == max_retries - 1:
                return text  # Keep English
            time.sleep(1)
    return text
This ensures:

✅ Handles temporary network issues

✅ No boxes in the final PDF

✅ Graceful fallback to English

Entity Protection
Protects English terms from translation:

Article numbers (Article 21, Article 370)

Numbers with units ($500 million, 2,500 km)

Years and dates (2024, 2024-01-15)

Organization abbreviations (UN, NASA, WHO)

Watermark Background
Every page has the Pragati Setu logo:

Centered on the page via CSS position: fixed

8% opacity (subtle, doesn't interfere with text)

Automatically scaled to fit

Uses file:// URI for WeasyPrint compatibility

📊 Output Files
questions_english.json - Raw scraped data in English

questions_gujarati.json - Translated data with protected English terms

PDF File - Professional PDF with:

Proper Gujarati conjunct rendering

Mixed Gujarati-English text

Watermark background

Clean typography

🔧 Dependencies
text
beautifulsoup4==4.12.3     # Web scraping
requests==2.31.0           # HTTP requests
weasyprint==62.3           # PDF generation with Pango
lxml==5.1.0                # HTML parsing
deep-translator==1.11.4    # Translation (FREE!)
python-dotenv==1.0.0       # Environment variables
🚨 Troubleshooting
Problem: Gujarati conjuncts still broken
Solution:

bash
# Install WeasyPrint dependencies
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libcairo2

# Install Gujarati fonts
sudo apt-get install fonts-noto-core fonts-lohit-gujr
fc-cache -f -v

# Verify Pango is working
python3 -c "from weasyprint import HTML; print('WeasyPrint OK!')"
Problem: Watermark not appearing
Solution:

python
# Use absolute path with file:// URI
watermark_path = os.path.abspath("pragati_setu.jpg")
image_uri = f"file://{watermark_path}"
Problem: Translation too slow
Solution:

python
# In translator.py, reduce delay
time.sleep(1.0)  # Instead of 1.5
Problem: Import errors
Solution:

bash
pip install --upgrade -r requirements.txt
💡 Key Lessons Learned
ReportLab can't handle Indic scripts properly - Lacks OpenType shaping[web:143][web:147]

WeasyPrint uses Pango for text layout - Proper conjunct support[web:145]

CSS is easier than manual positioning - WeasyPrint advantage[web:143]

Free API tiers have limits - Google Gemini exhausted after 45 questions

deep-translator is reliable - Simple, free, no rate limits

Always add retry logic - Networks fail, translations timeout

Test with real Indic text - Discovered conjunct issues only with actual Gujarati

📚 Technical Comparison
Feature	ReportLab	WeasyPrint
Gujarati Conjuncts	❌ Broken	✅ Perfect
Text Shaping	Manual	Pango (automatic)
Styling Approach	Python code	HTML/CSS
Learning Curve	Steep	Easy (if you know HTML)
Complex Layouts	✅ Excellent	✅ Good
Indic Scripts	❌ Poor	✅ Excellent
Recommendation: Use WeasyPrint for any project involving Indic scripts (Gujarati, Hindi, Bengali, Tamil, etc.)[web:143][web:145][web:147]

Made with ❤️ for Gujarati learners