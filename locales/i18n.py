"""
Internationalization (i18n) Manager for Call Analytics Streamlit Application
Provides centralized translation management and language switching functionality.
"""

import json
import os
from typing import Dict, Any, Optional
import streamlit as st


class I18nManager:
    """
    Centralized internationalization manager for handling translations
    and language switching in the Streamlit application.
    """
    
    def __init__(self):
        self.current_language = 'es'  # Default to Spanish
        self.translations: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.supported_languages = ['es', 'en']
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files from the locales directory."""
        locales_dir = os.path.dirname(__file__)
        
        for lang in self.supported_languages:
            self.translations[lang] = {}
            lang_dir = os.path.join(locales_dir, lang)
            
            # Create language directory if it doesn't exist
            if not os.path.exists(lang_dir):
                os.makedirs(lang_dir)
                continue
            
            # Load all JSON files in the language directory
            for file in os.listdir(lang_dir):
                if file.endswith('.json'):
                    module_name = file[:-5]  # Remove .json extension
                    file_path = os.path.join(lang_dir, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self.translations[lang][module_name] = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        print(f"Error loading translation file {file_path}: {e}")
                        self.translations[lang][module_name] = {}
    
    def set_language(self, language: str):
        """
        Set the current language and update session state.
        
        Args:
            language (str): Language code ('es' or 'en')
        """
        if language in self.supported_languages:
            self.current_language = language
            st.session_state.language = language
    
    def get_language(self) -> str:
        """
        Get current language from session state or return default.
        
        Returns:
            str: Current language code
        """
        return st.session_state.get('language', self.current_language)
    
    def t(self, key: str, module: str = 'common', **kwargs) -> str:
        """
        Translate a key with optional parameter interpolation.
        
        Args:
            key (str): Translation key
            module (str): Translation module/file name (default: 'common')
            **kwargs: Parameters for string interpolation
            
        Returns:
            str: Translated string or fallback
        """
        lang = self.get_language()
        
        # Try to get translation in current language
        try:
            translation = self.translations[lang][module][key]
            if kwargs:
                return translation.format(**kwargs)
            return translation
        except KeyError:
            pass
        
        # Fallback to Spanish if key not found in current language
        if lang != 'es':
            try:
                translation = self.translations['es'][module][key]
                if kwargs:
                    return translation.format(**kwargs)
                return translation
            except KeyError:
                pass
        
        # Return key itself if not found anywhere (without brackets to avoid Plotly errors)
        return key
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        Get available languages with their display names.
        
        Returns:
            Dict[str, str]: Language codes mapped to display names
        """
        return {
            'es': '🇪🇸 Español',
            'en': '🇺🇸 English'
        }
    
    def reload_translations(self):
        """Reload all translation files (useful for development)."""
        self.load_translations()


# Global instance
i18n = I18nManager()