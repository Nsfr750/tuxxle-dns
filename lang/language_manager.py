#!/usr/bin/env python3
"""
Language Manager for DNS Server Manager
Handles language detection, loading, and switching
"""

import os
import json
from typing import Dict, Optional, Any
from pathlib import Path
import locale
import sys

from .translations import Translations


class LanguageManager:
    """Manages language settings and translations for the application"""
    
    def __init__(self, lang_dir: Optional[str] = None):
        """
        Initialize the Language Manager
        
        Args:
            lang_dir: Path to the language directory (default: lang/ relative to main.py)
        """
        if lang_dir is None:
            # Get the directory containing this file
            self.lang_dir = Path(__file__).parent
        else:
            self.lang_dir = Path(lang_dir)
        
        self.current_language = 'en'
        self.fallback_language = 'en'
        self.translations = Translations()
        self.available_languages = self._get_available_languages()
        
        # Detect and set initial language
        self._detect_system_language()
        self.load_language(self.current_language)
    
    def _get_available_languages(self) -> Dict[str, str]:
        """
        Get list of available languages from translations
        
        Returns:
            Dictionary of language codes and their display names
        """
        return self.translations.get_available_languages()
    
    def _detect_system_language(self) -> None:
        """
        Detect system language and set it as current if available
        Falls back to English if system language is not supported
        """
        try:
            # Try to get system locale
            system_locale = locale.getdefaultlocale()
            if system_locale and system_locale[0]:
                lang_code = system_locale[0].split('_')[0].lower()
                if lang_code in self.available_languages:
                    self.current_language = lang_code
                    return
        except (locale.Error, AttributeError):
            pass
        
        # Fallback to environment variables
        env_lang = os.environ.get('LANG', '').split('.')[0].split('_')[0].lower()
        if env_lang in self.available_languages:
            self.current_language = env_lang
        else:
            self.current_language = self.fallback_language
    
    def load_language(self, language_code: str) -> bool:
        """
        Load translations for a specific language
        
        Args:
            language_code: ISO language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            True if language was loaded successfully, False otherwise
        """
        if language_code not in self.available_languages:
            print(f"Warning: Language '{language_code}' not available. Using '{self.fallback_language}'")
            language_code = self.fallback_language
        
        try:
            success = self.translations.load_language(language_code)
            if success:
                self.current_language = language_code
                return True
            else:
                print(f"Failed to load language '{language_code}'. Using '{self.fallback_language}'")
                return self.load_language(self.fallback_language)
        except Exception as e:
            print(f"Error loading language '{language_code}': {e}")
            return self.load_language(self.fallback_language)
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        Get translated text for a given key
        
        Args:
            key: Translation key
            **kwargs: Variables for string formatting
            
        Returns:
            Translated text
        """
        return self.translations.get_text(key, **kwargs)
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the current language
        
        Args:
            language_code: ISO language code
            
        Returns:
            True if language was set successfully
        """
        return self.load_language(language_code)
    
    def get_current_language(self) -> str:
        """
        Get the current language code
        
        Returns:
            Current language code
        """
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        Get available languages
        
        Returns:
            Dictionary of language codes and display names
        """
        return self.available_languages.copy()
    
    def is_language_available(self, language_code: str) -> bool:
        """
        Check if a language is available
        
        Args:
            language_code: ISO language code
            
        Returns:
            True if language is available
        """
        return language_code in self.available_languages
    
    def reload_translations(self) -> bool:
        """
        Reload current language translations
        
        Returns:
            True if reload was successful
        """
        return self.load_language(self.current_language)
    
    def add_translation(self, language_code: str, key: str, text: str) -> bool:
        """
        Add or update a translation
        
        Args:
            language_code: ISO language code
            key: Translation key
            text: Translation text
            
        Returns:
            True if translation was added successfully
        """
        return self.translations.add_translation(language_code, key, text)
    
    def export_translations(self, output_dir: str) -> bool:
        """
        Export all translations to JSON files
        
        Args:
            output_dir: Directory to save translation files
            
        Returns:
            True if export was successful
        """
        return self.translations.export_translations(output_dir)
    
    def import_translations(self, input_dir: str) -> bool:
        """
        Import translations from JSON files
        
        Args:
            input_dir: Directory containing translation files
            
        Returns:
            True if import was successful
        """
        success = self.translations.import_translations(input_dir)
        if success:
            self.available_languages = self._get_available_languages()
            # Reload current language if it still exists
            if self.current_language in self.available_languages:
                self.load_language(self.current_language)
            else:
                self.load_language(self.fallback_language)
        return success
    
    def get_language_info(self, language_code: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific language
        
        Args:
            language_code: ISO language code
            
        Returns:
            Dictionary with language information or None if not found
        """
        return self.translations.get_language_info(language_code)
    
    def validate_translations(self) -> Dict[str, list]:
        """
        Validate all translations for missing keys
        
        Returns:
            Dictionary with language codes as keys and lists of missing keys as values
        """
        return self.translations.validate_translations()
    
    def get_translation_coverage(self) -> Dict[str, float]:
        """
        Get translation coverage percentage for each language
        
        Returns:
            Dictionary with language codes as keys and coverage percentage as values
        """
        return self.translations.get_translation_coverage()
