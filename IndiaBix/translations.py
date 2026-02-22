TRANSLATIONS = {
    'gu': {
        'title': 'Current Affairs Questions & Answers',
        'week_of': 'Week of {start_date} to {end_date}',
        'generated_on': 'Generated on {date}',
        'question': 'Q. {num}',
        'answer': 'Answer',
        'explanation': 'Explanation',
        'category': 'Category',
        'summary': 'Summary',
        'total_questions': 'Total Questions',
        'generated_date': 'Generated Date',
        'document_type': 'Document Type',
        'quiz_type': 'Weekly Current Affairs Quiz',
    }
}


def get_text(language: str, key: str, **kwargs) -> str:
    """Get label text"""
    lang_dict = TRANSLATIONS.get(language, TRANSLATIONS['gu'])
    text = lang_dict.get(key, key)
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    
    return text