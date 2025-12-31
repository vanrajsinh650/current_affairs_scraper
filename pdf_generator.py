from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
import os
import logging
import re
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


class PDFGenerator:
    def __init__(self, output_dir: str = "output", language: str = 'en', watermark_image: str = None):
        self.output_dir = output_dir
        self.language = language
        self.watermark_image = watermark_image
        os.makedirs(output_dir, exist_ok=True)
        
        # Register fonts for mixed text
        if language == 'gu':
            self._register_fonts()
    
    def _register_fonts(self):
        """Register both Gujarati and English fonts"""
        try:
            # Register Gujarati font
            gujarati_font_paths = [
                '/usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf',
                '/usr/share/fonts/truetype/lohit-gujarati/Lohit-Gujarati.ttf',
            ]
            
            for font_path in gujarati_font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('GujaratiFont', font_path))
                    logger.info(f"✓ Registered Gujarati font: {font_path}")
                    break
            
            logger.info("Fonts registered for mixed Gujarati-English text")
                
        except Exception as e:
            logger.error(f"Error registering fonts: {e}")
    
    def _add_watermark(self, canvas, doc):
        """Add watermark/background image to every page"""
        if not self.watermark_image or not os.path.exists(self.watermark_image):
            return
        
        try:
            # Get page dimensions
            page_width, page_height = A4
            
            # Load image
            img = ImageReader(self.watermark_image)
            img_width, img_height = img.getSize()
            
            # Calculate centered position and size
            # Make watermark large but semi-transparent
            max_size = min(page_width, page_height) * 0.6
            aspect = img_width / img_height
            
            if aspect > 1:
                # Landscape image
                w = max_size
                h = max_size / aspect
            else:
                # Portrait image
                h = max_size
                w = max_size * aspect
            
            # Center the image
            x = (page_width - w) / 2
            y = (page_height - h) / 2
            
            # Save canvas state
            canvas.saveState()
            
            # Set transparency (0.1 = 10% opacity for subtle watermark)
            canvas.setFillAlpha(0.1)
            
            # Draw image
            canvas.drawImage(self.watermark_image, x, y, width=w, height=h, 
                           preserveAspectRatio=True, mask='auto')
            
            # Restore canvas state
            canvas.restoreState()
            
        except Exception as e:
            logger.error(f"Error adding watermark: {e}")
    
    def _wrap_mixed_text(self, text: str) -> str:
        """Wrap text with proper font tags for mixed Gujarati-English"""
        if not text:
            return text
        
        # Detect if text has Gujarati characters
        has_gujarati = bool(re.search(r'[\u0A80-\u0AFF]', text))
        
        if not has_gujarati:
            # Pure English - use Helvetica
            return f'<font name="Helvetica">{text}</font>'
        
        # Mixed text - wrap each part appropriately
        result = []
        current_text = ""
        current_is_gujarati = None
        
        for char in text:
            is_gujarati = '\u0A80' <= char <= '\u0AFF'
            
            if current_is_gujarati is None:
                current_is_gujarati = is_gujarati
                current_text = char
            elif current_is_gujarati == is_gujarati:
                current_text += char
            else:
                # Switch detected
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
    
    def generate_pdf(self, questions: List[Dict], start_date: str, end_date: str) -> str:
        """Generate PDF from questions with watermark background"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"current_affairs_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            logger.info(f"Generating PDF: {filename}")
            
            # Create PDF document with custom page template
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            # Build content
            story = []
            
            # Title style
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=getSampleStyleSheet()['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a4d8f'),
                spaceAfter=6,
                alignment=TA_CENTER,
                leading=24
            )
            
            title_text = self._wrap_mixed_text("Current Affairs Questions & Answers")
            title = Paragraph(title_text, title_style)
            story.append(title)
            
            # Date range
            date_style = ParagraphStyle(
                'DateStyle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=20,
                leading=14
            )
            
            date_text = self._wrap_mixed_text(f"Week of {start_date} to {end_date}")
            story.append(Paragraph(date_text, date_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Question styles
            q_style = ParagraphStyle(
                'QuestionStyle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#1a4d8f'),
                spaceAfter=8,
                leading=16
            )
            
            opt_style = ParagraphStyle(
                'OptionStyle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=10,
                leftIndent=20,
                spaceAfter=4,
                leading=14
            )
            
            ans_style = ParagraphStyle(
                'AnswerStyle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#2d5f2e'),
                leftIndent=10,
                spaceAfter=6,
                leading=14
            )
            
            exp_style = ParagraphStyle(
                'ExplanationStyle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#4a4a4a'),
                leftIndent=20,
                rightIndent=10,
                spaceAfter=12,
                alignment=TA_JUSTIFY,
                leading=13
            )
            
            # Add questions
            for idx, q in enumerate(questions, 1):
                # Question
                q_text = self._wrap_mixed_text(f"Q. {idx}")
                q_text += "<br/>"
                q_text += self._wrap_mixed_text(q.get('question', ''))
                story.append(Paragraph(q_text, q_style))
                
                # Options
                options = q.get('options', [])
                option_letters = ['A', 'B', 'C', 'D', 'E', 'F']
                for opt_idx, option in enumerate(options):
                    if opt_idx < len(option_letters):
                        opt_text = f'<font name="Helvetica">❍ {option_letters[opt_idx]}) </font>'
                        opt_text += self._wrap_mixed_text(option)
                        story.append(Paragraph(opt_text, opt_style))
                
                story.append(Spacer(1, 0.1*inch))
                
                # Answer
                answer = q.get('answer', 'Not available')
                ans_text = '<font name="Helvetica"><b>Answer: ✓</b> </font>'
                ans_text += self._wrap_mixed_text(answer)
                story.append(Paragraph(ans_text, ans_style))
                
                # Explanation
                explanation = q.get('explanation', '')
                if explanation and explanation.strip():
                    exp_text = '<font name="Helvetica"><b>Explanation:</b> </font>'
                    exp_text += self._wrap_mixed_text(explanation)
                    story.append(Paragraph(exp_text, exp_style))
                
                # Spacing
                story.append(Spacer(1, 0.2*inch))
                
                # Page break every 5 questions
                if idx % 5 == 0 and idx < len(questions):
                    story.append(PageBreak())
            
            # Build PDF with watermark on every page
            doc.build(story, onFirstPage=self._add_watermark, onLaterPages=self._add_watermark)
            
            logger.info(f"PDF generated successfully: {filepath}")
            print(f"\nPDF created: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            print(f"Error generating PDF: {str(e)}")
            return None
