"""
Internationalization (i18n) helper utilities for the Call Analytics application.
Provides language selector component and translation shortcuts.
"""

import streamlit as st
from locales.i18n import I18nManager

# Initialize the i18n manager
i18n = I18nManager()

def init_language():
    """Initialize language settings in session state."""
    if 'language' not in st.session_state:
        st.session_state.language = 'es'  # Default to Spanish
    
    # Set the language in the i18n manager
    i18n.set_language(st.session_state.language)

def get_current_language():
    """Get the current language from session state."""
    return st.session_state.get('language', 'es')

def set_language(lang_code):
    """Set the current language and update session state."""
    st.session_state.language = lang_code
    i18n.set_language(lang_code)

def t(key, module='common', **kwargs):
    """
    Translate a key with optional parameter interpolation.
    
    Args:
        key (str): Translation key
        module (str): Module name (common, dashboard, management, reports, settings)
        **kwargs: Variables for string formatting
    
    Returns:
        str: Translated text
    """
    return i18n.t(key, module, **kwargs)

def language_selector():
    """
    Create a language selector component with flag icons.
    Should be placed in the sidebar.
    """
    # Language options with flag emojis
    languages = {
        'es': {'name': 'Español', 'flag': '🇪🇸'},
        'en': {'name': 'English', 'flag': '🇺🇸'}
    }
    
    current_lang = get_current_language()
    
    # Create columns for better layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.write("🌐")
    
    with col2:
        # Create selectbox with flag and language name
        options = [f"{lang_data['flag']} {lang_data['name']}" 
                  for lang_data in languages.values()]
        
        current_index = 0 if current_lang == 'es' else 1
        
        selected = st.selectbox(
            label="Language",
            options=options,
            index=current_index,
            key="language_selector",
            label_visibility="collapsed"
        )
        
        # Extract language code from selection
        if "🇪🇸" in selected:
            new_lang = 'es'
        else:
            new_lang = 'en'
        
        # Update language if changed
        if new_lang != current_lang:
            set_language(new_lang)
            st.rerun()

def format_language_dependent_text(text_dict):
    """
    Format text based on current language from a dictionary.
    
    Args:
        text_dict (dict): Dictionary with language codes as keys
    
    Returns:
        str: Text in current language
    """
    current_lang = get_current_language()
    return text_dict.get(current_lang, text_dict.get('es', ''))

def get_language_flag():
    """Get the flag emoji for the current language."""
    flags = {'es': '🇪🇸', 'en': '🇺🇸'}
    return flags.get(get_current_language(), '🇪🇸')

def get_language_name():
    """Get the name of the current language."""
    names = {'es': 'Español', 'en': 'English'}
    return names.get(get_current_language(), 'Español')

def bilingual_metric(label_es=None, label_en=None, value=None, delta=None, delta_color="normal", help_es=None, help_en=None):
    """
    Create a metric with bilingual labels.
    
    Args:
        label_es (str): Spanish label (deprecated, use translation key instead)
        label_en (str): English label (deprecated, use translation key instead)
        value: Metric value
        delta: Delta value for the metric
        delta_color (str): Delta color
        help_es (str): Spanish help text (deprecated)
        help_en (str): English help text (deprecated)
    """
    # Handle both old and new calling patterns
    if isinstance(label_es, str) and not label_es.startswith('t('):
        # Old pattern: direct strings
        current_lang = get_current_language()
        if current_lang == 'es':
            label = label_es
            help_text = help_es
        else:
            label = label_en or label_es
            help_text = help_en or help_es
    else:
        # New pattern: translation key
        label = label_es  # This should be the translated text
        help_text = help_es
    
    return st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )

def bilingual_header(title_es=None, title_en=None, divider=True):
    """
    Create a header with bilingual titles.
    
    Args:
        title_es (str): Spanish title (deprecated, use translation key instead)
        title_en (str): English title (deprecated, use translation key instead)
        divider (bool): Whether to show divider
    """
    # Handle both old and new calling patterns
    if isinstance(title_es, str) and not title_es.startswith('t('):
        # Old pattern: direct strings
        current_lang = get_current_language()
        if current_lang == 'es':
            title = title_es
        else:
            title = title_en or title_es
    else:
        # New pattern: translation key
        title = title_es  # This should be the translated text
    
    st.header(title, divider=divider)

def bilingual_subheader(title_es=None, title_en=None, divider=False):
    """
    Create a subheader with bilingual titles.
    
    Args:
        title_es (str): Spanish title (deprecated, use translation key instead)
        title_en (str): English title (deprecated, use translation key instead)
        divider (bool): Whether to show divider
    """
    # Handle both old and new calling patterns
    if isinstance(title_es, str) and not title_es.startswith('t('):
        # Old pattern: direct strings
        current_lang = get_current_language()
        if current_lang == 'es':
            title = title_es
        else:
            title = title_en or title_es
    else:
        # New pattern: translation key
        title = title_es  # This should be the translated text
    
    st.subheader(title, divider=divider)

def bilingual_selectbox(label_es=None, label_en=None, options=None, key=None, **kwargs):
    """
    Create a selectbox with bilingual labels.
    
    Args:
        label_es (str): Spanish label (deprecated, use translation key instead)
        label_en (str): English label (deprecated, use translation key instead)
        options: Selectbox options
        key: Streamlit key
        **kwargs: Additional selectbox parameters
    """
    # Handle both old and new calling patterns
    if isinstance(label_es, str) and not label_es.startswith('t('):
        # Old pattern: direct strings
        current_lang = get_current_language()
        if current_lang == 'es':
            label = label_es
        else:
            label = label_en or label_es
    else:
        # New pattern: translation key
        label = label_es  # This should be the translated text
    
    return st.selectbox(label, options, key=key, **kwargs)

def create_bilingual_button(label_key, module='common', **kwargs):
    """
    Create a button with bilingual label.
    
    Args:
        label_key (str): Translation key for the label
        module (str): Translation module
        **kwargs: Additional button parameters
    """
    label = t(label_key, module)
    return st.button(label, **kwargs)

def create_bilingual_checkbox(label_key, module='common', **kwargs):
    """
    Create a checkbox with bilingual label.
    
    Args:
        label_key (str): Translation key for the label
        module (str): Translation module
        **kwargs: Additional checkbox parameters
    """
    label = t(label_key, module)
    return st.checkbox(label, **kwargs)

def show_success_message(message_key, module='common', **kwargs):
    """Show a success message with translation."""
    message = t(message_key, module, **kwargs)
    st.success(message)

def show_error_message(message_key, module='common', **kwargs):
    """Show an error message with translation."""
    message = t(message_key, module, **kwargs)
    st.error(message)

def show_warning_message(message_key, module='common', **kwargs):
    """Show a warning message with translation."""
    message = t(message_key, module, **kwargs)
    st.warning(message)

def show_info_message(message_key, module='common', **kwargs):
    """Show an info message with translation."""
    message = t(message_key, module, **kwargs)
    st.info(message)


def init_i18n():
    """Initialize i18n system - should be called at the start of each page."""
    init_language()
    return i18n

# Alias functions for backward compatibility
def create_bilingual_metric(label_key, value, module='common', delta=None, delta_color="normal"):
    """Create a metric with bilingual label using translation key."""
    label = t(label_key, module)
    return st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def create_bilingual_header(title_key, module='common', divider=True):
    """Create a header with bilingual title using translation key."""
    title = t(title_key, module)
    st.header(title, divider=divider)

def create_bilingual_subheader(title_key, module='common', divider=False):
    """Create a subheader with bilingual title using translation key."""
    title = t(title_key, module)
    st.subheader(title, divider=divider)

def create_bilingual_selectbox(label_key, options, module='common', **kwargs):
    """Create a selectbox with bilingual label using translation key."""
    label = t(label_key, module)
    return st.selectbox(label, options, **kwargs)