import os
import logging
from datetime import datetime
from typing import List, Dict
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self, output_dir: str = "output", language: str = 'en', watermark_image: str = None):
        self.output_dir = output_dir
        self.language = language
        self.watermark_image = watermark_image
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_pdf(self, questions: List[Dict], start_date: str, end_date: str) -> str:
        """Generate PDF using WeasyPrint (proper Gujarati rendering)"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"current_affairs_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            logger.info(f"Generating PDF: {filename}")
            print("Building PDF with WeasyPrint...")
            
            # Build HTML content
            html_content = self._build_html(questions, start_date, end_date)
            
            # Configure fonts
            font_config = FontConfiguration()
            
            # CSS styling
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 2cm;
                }
                
                body {
                    font-family: "Noto Sans Gujarati", "Lohit Gujarati", sans-serif;
                    font-size: 11pt;
                    line-height: 1.6;
                    color: #333;
                    position: relative;
                }
                
                .english {
                    font-family: "Helvetica", "Arial", sans-serif;
                }
                
                .watermark-container {
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    opacity: 0.08;
                    width: 350px;
                    height: auto;
                    z-index: 0;
                    pointer-events: none;
                }
                
                .watermark-container img {
                    width: 100%;
                    height: auto;
                }
                
                .content {
                    position: relative;
                    z-index: 10;
                }
                
                .title-bar {
                    text-align: center;
                    border-bottom: 2px solid #1a4d8f;
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                }
                
                .english-title {
                    font-family: "Helvetica", "Arial", sans-serif;
                    font-size: 18pt;
                    font-weight: bold;
                    color: #1a4d8f;
                    margin: 0;
                }
                
                .date-range {
                    text-align: center;
                    color: #666;
                    font-size: 10pt;
                    margin-bottom: 20px;
                    font-family: "Helvetica", "Arial", sans-serif;
                }
                
                .question {
                    margin-bottom: 20px;
                    page-break-inside: avoid;
                }
                
                .question-header {
                    color: #1a4d8f;
                    font-weight: bold;
                    margin-bottom: 8px;
                    font-size: 11pt;
                }
                
                .question-text {
                    margin-bottom: 10px;
                }
                
                .options {
                    margin-left: 20px;
                    margin-bottom: 10px;
                }
                
                .option {
                    margin-bottom: 5px;
                }
                
                .answer {
                    color: #2d5f2e;
                    font-weight: bold;
                    margin-left: 10px;
                    margin-bottom: 8px;
                }
                
                .explanation {
                    color: #4a4a4a;
                    font-size: 9pt;
                    margin-left: 20px;
                    margin-right: 10px;
                    text-align: justify;
                    margin-bottom: 15px;
                }
            ''', font_config=font_config)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(
                filepath,
                stylesheets=[css],
                font_config=font_config
            )
            
            logger.info(f"PDF generated successfully: {filepath}")
            print(f"PDF created: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            print(f"Error generating PDF: {str(e)}")
            return None
    
    def _build_html(self, questions: List[Dict], start_date: str, end_date: str) -> str:
        """Build HTML content for PDF"""
        
        # Start HTML
        html = '''<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <title>Current Affairs - Pragati Setu</title>
</head>
<body>
'''
        
        # Add Pragati Setu logo watermark - USE file:// URI for WeasyPrint
        if self.watermark_image and os.path.exists(self.watermark_image):
            # Convert to file URI
            image_uri = f"file://{os.path.abspath(self.watermark_image)}"
            print(f"Using watermark: {image_uri}")
            html += f'''<div class="watermark-container">
    <img src="{image_uri}" alt="Logo" />
</div>
'''
        else:
            print(f"No watermark image found")
        
        # Content wrapper
        html += '<div class="content">'
        
        html += '''<div class="title-bar">
    <p class="english-title">Current Affairs Questions & Answers</p>
</div>'''
        
        # Date range in English
        html += f'<div class="date-range">{start_date} to {end_date}</div>'
        
        # Questions
        for idx, q in enumerate(questions, 1):
            html += '<div class="question">'
            
            # Question header
            html += f'<div class="question-header"><span class="english">Q. {idx}</span></div>'
            
            # Question text
            question_text = self._escape_html(q.get('question', ''))
            html += f'<div class="question-text">{question_text}</div>'
            
            # Options
            html += '<div class="options">'
            options = q.get('options', [])
            option_letters = ['A', 'B', 'C', 'D', 'E', 'F']
            for opt_idx, option in enumerate(options):
                if opt_idx < len(option_letters):
                    option_text = self._escape_html(option)
                    html += f'<div class="option"><span class="english">❍ {option_letters[opt_idx]})</span> {option_text}</div>'
            html += '</div>'
            
            # Answer
            answer = self._escape_html(q.get('answer', 'Not available'))
            html += f'<div class="answer"><span class="english">✓</span> {answer}</div>'
            
            # Explanation
            explanation = q.get('explanation', '')
            if explanation and explanation.strip():
                exp_text = self._escape_html(explanation)
                html += f'<div class="explanation">સમજૂતી: {exp_text}</div>'
            
            html += '</div>'  # Close question
        
        # Close content wrapper
        html += '</div>'
        html += '</body>\n</html>'
        
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))
