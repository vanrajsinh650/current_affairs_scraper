import os
from datetime import datetime
from typing import List, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging
from translations import get_text

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF from current affairs questions"""
    
    def __init__(self, output_dir: str = "output", language: str = 'gu'):
        """Initialize PDF generator with output directory and language"""
        self.output_dir = output_dir
        self.language = language
        self.styles = getSampleStyleSheet()
        
        # Create output folder if doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
        
        # Setup fonts and styles
        self._register_fonts()
        self._setup_custom_styles()
    
    def _register_fonts(self):
        """Register Gujarati fonts for PDF"""
        try:
            # Try Noto Sans Gujarati font first
            pdfmetrics.registerFont(TTFont('NotoSansGujarati', '/usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf'))
            pdfmetrics.registerFont(TTFont('NotoSansGujarati-Bold', '/usr/share/fonts/truetype/noto/NotoSansGujarati-Bold.ttf'))
            self.font_name = 'NotoSansGujarati'
            self.font_name_bold = 'NotoSansGujarati-Bold'
            logger.info("Noto Sans Gujarati fonts registered")
        except Exception as e:
            # Fallback to general Noto Sans
            logger.warning(f"Could not register Gujarati fonts: {e}")
            try:
                pdfmetrics.registerFont(TTFont('NotoSans', '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'))
                pdfmetrics.registerFont(TTFont('NotoSans-Bold', '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'))
                self.font_name = 'NotoSans'
                self.font_name_bold = 'NotoSans-Bold'
                logger.info("Noto Sans fonts registered as fallback")
            except Exception as e2:
                # Last resort: use default fonts
                logger.error(f"Could not register any fonts: {e2}")
                self.font_name = 'Helvetica'
                self.font_name_bold = 'Helvetica-Bold'
    
    def _setup_custom_styles(self):
        """Setup custom text styles for PDF"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName=self.font_name_bold
        ))
        
        # Question number style
        self.styles.add(ParagraphStyle(
            name='QuestionNum',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c5aa0'),
            fontName=self.font_name_bold,
            spaceAfter=6
        ))
        
        # Question text style
        self.styles.add(ParagraphStyle(
            name='QuestionText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            fontName=self.font_name
        ))
        
        # Option style
        self.styles.add(ParagraphStyle(
            name='OptionStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            leftIndent=0.3*inch,
            spaceAfter=4,
            fontName=self.font_name
        ))
        
        # Answer style (green color)
        self.styles.add(ParagraphStyle(
            name='AnswerStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#228B22'),
            fontName=self.font_name_bold,
            leftIndent=0.3*inch,
            spaceAfter=3
        ))
        
        # Explanation style
        self.styles.add(ParagraphStyle(
            name='ExplanationStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            leftIndent=0.6*inch,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            fontName=self.font_name
        ))
        
        # Category style
        self.styles.add(ParagraphStyle(
            name='CategoryStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#0066cc'),
            fontName=self.font_name,
            leftIndent=0.3*inch,
            spaceAfter=8
        ))
    
    def _format_question(self, question: Dict) -> List:
        """Format a single question for PDF"""
        elements = []
        
        # Add question number
        q_num = get_text(self.language, 'question', num=question['question_no'])
        elements.append(Paragraph(q_num, self.styles['QuestionNum']))
        
        # Add question text
        question_text = question['question'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Paragraph(question_text, self.styles['QuestionText']))
        
        # Add all options
        for option in question.get('options', []):
            option_text = option.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(f"• {option_text}", self.styles['OptionStyle']))
        
        # Add answer
        answer = question.get('answer', 'Not available')
        answer = answer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Spacer(1, 0.1*inch))
        answer_label = get_text(self.language, 'answer')
        elements.append(Paragraph(f"<b>{answer_label}:</b> {answer}", self.styles['AnswerStyle']))
        
        # Add category if available
        category = question.get('category', '')
        if category:
            category = category.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            category_label = get_text(self.language, 'category')
            elements.append(Paragraph(f"<b>{category_label}:</b> {category}", self.styles['CategoryStyle']))
        
        # Add explanation if available
        explanation = question.get('explanation', '')
        if explanation:
            explanation = explanation.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if len(explanation) > 500:
                explanation = explanation[:500] + "..."
            explanation_label = get_text(self.language, 'explanation')
            elements.append(Paragraph(f"<b>{explanation_label}:</b> {explanation}", self.styles['ExplanationStyle']))
        
        # Add separator between questions
        elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def generate_pdf(self, questions: List[Dict], start_date: str = None, end_date: str = None) -> str:
        """Generate PDF file from questions list"""
        if not questions:
            logger.warning("No questions to generate PDF")
            return None
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"current_affairs_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"Generating PDF: {filename}")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        elements = []
        
        # Add title
        title_text = get_text(self.language, 'title')
        elements.append(Paragraph(title_text, self.styles['CustomTitle']))
        
        # Add date range
        if start_date and end_date:
            date_text = get_text(self.language, 'week_of', start_date=start_date, end_date=end_date)
        else:
            date_text = get_text(self.language, 'generated_on', date=datetime.now().strftime('%B %d, %Y'))
        
        elements.append(Paragraph(f"<i>{date_text}</i>", self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add all questions
        for question in questions:
            elements.extend(self._format_question(question))
        
        # Add summary page
        elements.append(PageBreak())
        summary_title = get_text(self.language, 'summary')
        elements.append(Paragraph(summary_title, self.styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Get translated labels
        total_q = get_text(self.language, 'total_questions')
        gen_date = get_text(self.language, 'generated_date')
        doc_type = get_text(self.language, 'document_type')
        quiz_type = get_text(self.language, 'quiz_type')
        
        # Add summary content
        summary_text = f"""
        <b>{total_q}:</b> {len(questions)}<br/>
        <b>{gen_date}:</b> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}<br/>
        <b>{doc_type}:</b> {quiz_type}<br/>
        """
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        
        # Build the PDF
        try:
            doc.build(elements)
            logger.info(f"PDF generated successfully: {filepath}")
            print(f"\n✓ PDF created: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None
