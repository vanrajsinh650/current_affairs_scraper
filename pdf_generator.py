import os
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PDFGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate(self, data, filename):
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        # -- Font Registration (Optional for Gujarati Support) --
        # ReportLab needs a TTF font file to render Gujarati. 
        # If you have 'NotoSansGujarati.ttf' or 'ArialUnicode.ttf', put it in the project folder
        # and uncomment the lines below:
        # try:
        #     pdfmetrics.registerFont(TTFont('GujaratiFont', 'NotoSansGujarati.ttf'))
        #     font_name = 'GujaratiFont'
        # except:
        #     font_name = 'Helvetica' # Fallback to standard font (Gujarati will not show)
        
        font_name = 'Helvetica' 

        styles = getSampleStyleSheet()
        
        # Define Custom Styles
        title_style = styles['Heading1']
        title_style.alignment = 1 # Center
        
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=11,
            spaceAfter=6,
            textColor=colors.black,
            leading=14
        )

        translated_style = ParagraphStyle(
            'TranslatedStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            spaceAfter=8,
            textColor=colors.dimgrey,
            leading=14
        )
        
        option_style = ParagraphStyle(
            'OptionStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leftIndent=20,
            spaceAfter=2
        )

        answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=styles['Normal'],
            fontName=font_name + '-Bold' if font_name == 'Helvetica' else font_name,
            fontSize=10,
            textColor=colors.darkgreen,
            spaceBefore=6,
            spaceAfter=12
        )

        story = []
        
        # Add Title
        story.append(Paragraph("Weekly Current Affairs", title_style))
        story.append(Spacer(1, 24))

        for i, q in enumerate(data, 1):
            content_block = []
            
            # 1. Question (English)
            q_text = q.get('question', '')
            content_block.append(Paragraph(f"<b>Q{i}.</b> {q_text}", question_style))
            
            # 2. Question (Translated)
            q_trans = q.get('question_translated', '')
            if q_trans:
                content_block.append(Paragraph(f"<i>{q_trans}</i>", translated_style))

            # 3. Options (If they exist - IndiaBix style)
            options = q.get('options', [])
            options_trans = q.get('options_translated', [])
            
            if options:
                for idx, opt in enumerate(options):
                    letter = chr(65 + idx) # A, B, C...
                    opt_t = options_trans[idx] if idx < len(options_trans) else ""
                    
                    # Combine Eng and Trans in one line or separate
                    text = f"<b>{letter}.</b> {opt}"
                    content_block.append(Paragraph(text, option_style))
                    if opt_t:
                         content_block.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>({opt_t})</i>", translated_style))

            # 4. Answer
            ans = q.get('answer', 'N/A')
            ans_trans = q.get('answer_translated', '')
            
            ans_text = f"<b>Answer:</b> {ans}"
            if ans_trans:
                ans_text += f" | <i>{ans_trans}</i>"
            
            content_block.append(Paragraph(ans_text, answer_style))
            
            # 5. Source Metadata
            source = q.get('source', '')
            date_str = q.get('date', '')
            meta_text = f"<font size=8 color=grey>Source: {source} | Date: {date_str}</font>"
            content_block.append(Paragraph(meta_text, styles['Normal']))
            
            content_block.append(Spacer(1, 12))
            
            # Keep question block together on one page if possible
            story.append(KeepTogether(content_block))
            story.append(Spacer(1, 12))

        try:
            doc.build(story)
            return filepath
        except Exception as e:
            logging.error(f"Failed to build PDF: {e}")
            raise e