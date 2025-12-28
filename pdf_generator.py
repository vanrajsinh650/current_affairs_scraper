import os
from datetime import datetime
from typing import List, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF from scraped current affairs questions"""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize PDF generator"""
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Create output directory if not exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Question number style
        self.styles.add(ParagraphStyle(
            name='QuestionNum',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c5aa0'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
        
        # Question text style
        self.styles.add(ParagraphStyle(
            name='QuestionText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Option style
        self.styles.add(ParagraphStyle(
            name='OptionStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            leftIndent=0.3*inch,
            spaceAfter=4
        ))
        
        # Answer style
        self.styles.add(ParagraphStyle(
            name='AnswerStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#228B22'),
            fontName='Helvetica-Bold',
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
            alignment=TA_JUSTIFY
        ))
        
        # Category style
        self.styles.add(ParagraphStyle(
            name='CategoryStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#0066cc'),
            fontName='Helvetica-Oblique',
            leftIndent=0.3*inch,
            spaceAfter=8
        ))
    
    def _format_question(self, question: Dict) -> List:
        """Format a single question for PDF"""
        elements = []
        
        # Question number
        q_num = f"Q. {question['question_no']}"
        elements.append(Paragraph(q_num, self.styles['QuestionNum']))
        
        # Question text
        question_text = question['question'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Paragraph(question_text, self.styles['QuestionText']))
        
        # Options
        for option in question.get('options', []):
            option_text = option.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(f"• {option_text}", self.styles['OptionStyle']))
        
        # Answer
        answer = question.get('answer', 'Not available')
        answer = answer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(f"<b>Answer:</b> {answer}", self.styles['AnswerStyle']))
        
        # Category (if available)
        category = question.get('category', '')
        if category:
            category = category.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(f"<b>Category:</b> {category}", self.styles['CategoryStyle']))
        
        # Explanation (if available)
        explanation = question.get('explanation', '')
        if explanation:
            explanation = explanation.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Truncate very long explanations
            if len(explanation) > 500:
                explanation = explanation[:500] + "..."
            elements.append(Paragraph(f"<b>Explanation:</b> {explanation}", self.styles['ExplanationStyle']))
        
        # Separator
        elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def generate_pdf(self, questions: List[Dict], start_date: str = None, end_date: str = None) -> str:
        """
        Generate PDF from list of questions
        
        Args:
            questions: List of question dictionaries
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Path to generated PDF file
        """
        if not questions:
            logger.warning("No questions to generate PDF")
            return None
        
        # Generate filename with date
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
        
        # Build content
        elements = []
        
        # Title
        title_text = "Current Affairs Questions &amp; Answers"
        elements.append(Paragraph(title_text, self.styles['CustomTitle']))
        
        # Date range subtitle
        if start_date and end_date:
            date_text = f"<i>Week of {start_date} to {end_date}</i>"
        else:
            date_text = f"<i>Generated on {datetime.now().strftime('%B %d, %Y')}</i>"
        
        elements.append(Paragraph(date_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add all questions
        for question in questions:
            elements.extend(self._format_question(question))
        
        # Add summary page at end
        elements.append(PageBreak())
        elements.append(Paragraph("Summary", self.styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        summary_text = f"""
        <b>Total Questions:</b> {len(questions)}<br/>
        <b>Generated Date:</b> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}<br/>
        <b>Document Type:</b> Weekly Current Affairs Quiz<br/>
        """
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        
        # Build PDF
        try:
            doc.build(elements)
            logger.info(f"PDF generated successfully: {filepath}")
            print(f"\n✓ PDF created: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None