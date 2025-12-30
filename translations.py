TRANSLATIONS = {
    'en': {
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
    },
    'gu': {
        'title': 'વર્તમાન બાબતોના પ્રશ્નો અને જવાબો',
        'week_of': '{start_date} થી {end_date} સુધીનો સપ્તાહ',
        'generated_on': '{date} પર તૈયાર કરવામાં આવ્યું',
        'question': 'પ્રશ્ન. {num}',
        'answer': 'જવાબ',
        'explanation': 'સમજૂતી',
        'category': 'શ્રેણી',
        'summary': 'સારાંશ',
        'total_questions': 'કુલ પ્રશ્નો',
        'generated_date': 'તૈયાર કરવાની તારીખ',
        'document_type': 'દસ્તાવેજ પ્રકાર',
        'quiz_type': 'સાપ્તાહિક વર્તમાન બાબતોના પ્રશ્નો',
    }
}


def get_text(language: str, key: str, **kwargs) -> str:
    """Get translated label for PDF"""
    lang_dict = TRANSLATIONS.get(language, TRANSLATIONS['en'])
    text = lang_dict.get(key, key)
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    
    return text
