#!/usr/bin/env python3
"""
Translations module for DNS Server Manager
Contains all translation strings and translation management functionality
"""

from typing import Dict, Optional, Any, List
import json
from pathlib import Path


class Translations:
    """
    Manages translation strings for multiple languages
    """
    
    def __init__(self):
        """Initialize the translations system"""
        self.translations_data: Dict[str, Dict[str, str]] = {}
        self.current_language = 'en'
        self.fallback_language = 'en'
        
        # Initialize with built-in translations
        self._initialize_translations()
    
    def _initialize_translations(self) -> None:
        """Initialize with built-in translation strings"""
        # English translations (base language)
        self.translations_data['en'] = {
            # Menu and UI
            'menu.title': 'DNS Server Manager',
            'menu.start_server': 'Start DNS Server',
            'menu.stop_server': 'Stop DNS Server',
            'menu.restart_server': 'Restart DNS Server',
            'menu.settings': 'Settings',
            'menu.about': 'About',
            'menu.help': 'Help',
            'menu.exit': 'Exit',
            
            # Server status
            'server.status.running': 'Server is running',
            'server.status.stopped': 'Server is stopped',
            'server.status.starting': 'Server is starting...',
            'server.status.stopping': 'Server is stopping...',
            'server.status.error': 'Server error',
            
            # DNS Records
            'dns.record.add': 'Add DNS Record',
            'dns.record.edit': 'Edit DNS Record',
            'dns.record.delete': 'Delete DNS Record',
            'dns.record.type.a': 'A Record',
            'dns.record.type.aaaa': 'AAAA Record',
            'dns.record.type.cname': 'CNAME Record',
            'dns.record.type.mx': 'MX Record',
            'dns.record.type.txt': 'TXT Record',
            'dns.record.type.ns': 'NS Record',
            'dns.record.type.soa': 'SOA Record',
            'dns.record.type.ptr': 'PTR Record',
            'dns.record.type.srv': 'SRV Record',
            
            # Form fields
            'form.domain': 'Domain',
            'form.ip_address': 'IP Address',
            'form.record_type': 'Record Type',
            'form.value': 'Value',
            'form.ttl': 'TTL (Time to Live)',
            'form.priority': 'Priority',
            'form.port': 'Port',
            'form.weight': 'Weight',
            'form.target': 'Target',
            'form.name': 'Name',
            'form.email': 'Email',
            'form.serial': 'Serial Number',
            'form.refresh': 'Refresh Interval',
            'form.retry': 'Retry Interval',
            'form.expire': 'Expire Time',
            'form.minimum': 'Minimum TTL',
            
            # Buttons
            'button.save': 'Save',
            'button.cancel': 'Cancel',
            'button.delete': 'Delete',
            'button.edit': 'Edit',
            'button.add': 'Add',
            'button.update': 'Update',
            'button.close': 'Close',
            'button.ok': 'OK',
            'button.yes': 'Yes',
            'button.no': 'No',
            'button.apply': 'Apply',
            'button.reset': 'Reset',
            'button.refresh': 'Refresh',
            'button.export': 'Export',
            'button.import': 'Import',
            'button.backup': 'Backup',
            'button.restore': 'Restore',
            
            # Messages
            'msg.success.saved': 'Saved successfully',
            'msg.success.deleted': 'Deleted successfully',
            'msg.success.updated': 'Updated successfully',
            'msg.success.started': 'Server started successfully',
            'msg.success.stopped': 'Server stopped successfully',
            'msg.success.restart': 'Server restarted successfully',
            'msg.success.imported': 'Imported successfully',
            'msg.success.exported': 'Exported successfully',
            
            'msg.error.save': 'Failed to save',
            'msg.error.delete': 'Failed to delete',
            'msg.error.update': 'Failed to update',
            'msg.error.start': 'Failed to start server',
            'msg.error.stop': 'Failed to stop server',
            'msg.error.restart': 'Failed to restart server',
            'msg.error.import': 'Failed to import',
            'msg.error.export': 'Failed to export',
            'msg.error.invalid_domain': 'Invalid domain name',
            'msg.error.invalid_ip': 'Invalid IP address',
            'msg.error.invalid_ttl': 'Invalid TTL value',
            'msg.error.record_exists': 'Record already exists',
            'msg.error.record_not_found': 'Record not found',
            'msg.error.database': 'Database error',
            'msg.error.network': 'Network error',
            'msg.error.permission': 'Permission denied',
            'msg.error.file_not_found': 'File not found',
            'msg.error.invalid_format': 'Invalid format',
            
            'msg.warning.unsaved_changes': 'You have unsaved changes',
            'msg.warning.confirm_delete': 'Are you sure you want to delete this item?',
            'msg.warning.confirm_restart': 'Are you sure you want to restart the server?',
            'msg.warning.backup_required': 'It is recommended to create a backup before making changes',
            
            'msg.info.loading': 'Loading...',
            'msg.info.please_wait': 'Please wait...',
            'msg.info.no_records': 'No records found',
            'msg.info.server_ready': 'Server is ready',
            
            # Settings
            'settings.title': 'Settings',
            'settings.general': 'General',
            'settings.server': 'Server',
            'settings.database': 'Database',
            'settings.logging': 'Logging',
            'settings.language': 'Language',
            'settings.theme': 'Theme',
            'settings.port': 'Server Port',
            'settings.host': 'Server Host',
            'settings.max_connections': 'Max Connections',
            'settings.timeout': 'Timeout',
            'settings.log_level': 'Log Level',
            'settings.log_file': 'Log File',
            'settings.backup_enabled': 'Enable Auto Backup',
            'settings.backup_interval': 'Backup Interval',
            'settings.backup_location': 'Backup Location',
            
            # About
            'about.title': 'About DNS Server Manager',
            'about.version': 'Version',
            'about.author': 'Author',
            'about.license': 'License',
            'about.description': 'A comprehensive DNS server management application',
            'about.website': 'Website',
            'about.github': 'GitHub',
            'about.email': 'Email',
            
            # Help
            'help.title': 'Help',
            'help.getting_started': 'Getting Started',
            'help.user_guide': 'User Guide',
            'help.faq': 'Frequently Asked Questions',
            'help.support': 'Support',
            'help.documentation': 'Documentation',
            'help.keyboard_shortcuts': 'Keyboard Shortcuts',
            
            # Logging
            'log.level.debug': 'Debug',
            'log.level.info': 'Info',
            'log.level.warning': 'Warning',
            'log.level.error': 'Error',
            'log.level.critical': 'Critical',
            
            # Themes
            'theme.light': 'Light',
            'theme.dark': 'Dark',
            'theme.auto': 'Auto',
            
            # Time units
            'time.seconds': 'seconds',
            'time.minutes': 'minutes',
            'time.hours': 'hours',
            'time.days': 'days',
            'time.weeks': 'weeks',
            'time.months': 'months',
            'time.years': 'years',
            
            # File operations
            'file.select': 'Select File',
            'file.open': 'Open File',
            'file.save_as': 'Save As',
            'file.export_csv': 'Export as CSV',
            'file.export_json': 'Export as JSON',
            'file.import_csv': 'Import from CSV',
            'file.import_json': 'Import from JSON',
            
            # Network
            'network.connected': 'Connected',
            'network.disconnected': 'Disconnected',
            'network.connecting': 'Connecting...',
            'network.connection_failed': 'Connection failed',
            'network.timeout': 'Connection timeout',
            'network.unreachable': 'Network unreachable',
            
            # Validation
            'validation.required': 'This field is required',
            'validation.invalid_format': 'Invalid format',
            'validation.too_short': 'Too short',
            'validation.too_long': 'Too long',
            'validation.out_of_range': 'Out of range',
            'validation.invalid_characters': 'Contains invalid characters',
            
            # Common
            'common.yes': 'Yes',
            'common.no': 'No',
            'common.ok': 'OK',
            'common.cancel': 'Cancel',
            'common.error': 'Error',
            'common.warning': 'Warning',
            'common.info': 'Information',
            'common.success': 'Success',
            'common.loading': 'Loading',
            'common.search': 'Search',
            'common.filter': 'Filter',
            'common.sort': 'Sort',
            'common.clear': 'Clear',
            'common.select_all': 'Select All',
            'common.deselect_all': 'Deselect All',
            'common.none': 'None',
            'common.all': 'All',
            'common.auto': 'Auto',
            'common.default': 'Default',
            'common.custom': 'Custom',
        }
        
        # Spanish translations
        self.translations_data['es'] = {
            'menu.title': 'Gestor de Servidor DNS',
            'menu.start_server': 'Iniciar Servidor DNS',
            'menu.stop_server': 'Detener Servidor DNS',
            'menu.restart_server': 'Reiniciar Servidor DNS',
            'menu.settings': 'Configuración',
            'menu.about': 'Acerca de',
            'menu.help': 'Ayuda',
            'menu.exit': 'Salir',
            
            'server.status.running': 'Servidor en ejecución',
            'server.status.stopped': 'Servidor detenido',
            'server.status.starting': 'Iniciando servidor...',
            'server.status.stopping': 'Deteniendo servidor...',
            'server.status.error': 'Error del servidor',
            
            'button.save': 'Guardar',
            'button.cancel': 'Cancelar',
            'button.delete': 'Eliminar',
            'button.edit': 'Editar',
            'button.add': 'Agregar',
            'button.close': 'Cerrar',
            'button.ok': 'OK',
            
            'msg.success.saved': 'Guardado exitosamente',
            'msg.success.deleted': 'Eliminado exitosamente',
            'msg.error.save': 'Error al guardar',
            'msg.error.delete': 'Error al eliminar',
            
            'settings.title': 'Configuración',
            'settings.language': 'Idioma',
            'about.title': 'Acerca de Gestor DNS',
            'help.title': 'Ayuda',
        }
        
        # French translations
        self.translations_data['fr'] = {
            'menu.title': 'Gestionnaire de Serveur DNS',
            'menu.start_server': 'Démarrer le Serveur DNS',
            'menu.stop_server': 'Arrêter le Serveur DNS',
            'menu.restart_server': 'Redémarrer le Serveur DNS',
            'menu.settings': 'Paramètres',
            'menu.about': 'À propos',
            'menu.help': 'Aide',
            'menu.exit': 'Quitter',
            
            'server.status.running': 'Serveur en cours d\'exécution',
            'server.status.stopped': 'Serveur arrêté',
            'server.status.starting': 'Démarrage du serveur...',
            'server.status.stopping': 'Arrêt du serveur...',
            'server.status.error': 'Erreur du serveur',
            
            'button.save': 'Enregistrer',
            'button.cancel': 'Annuler',
            'button.delete': 'Supprimer',
            'button.edit': 'Modifier',
            'button.add': 'Ajouter',
            'button.close': 'Fermer',
            'button.ok': 'OK',
            
            'msg.success.saved': 'Enregistré avec succès',
            'msg.success.deleted': 'Supprimé avec succès',
            'msg.error.save': 'Échec de l\'enregistrement',
            'msg.error.delete': 'Échec de la suppression',
            
            'settings.title': 'Paramètres',
            'settings.language': 'Langue',
            'about.title': 'À propos du Gestionnaire DNS',
            'help.title': 'Aide',
        }
        
        # German translations
        self.translations_data['de'] = {
            'menu.title': 'DNS-Server-Manager',
            'menu.start_server': 'DNS-Server starten',
            'menu.stop_server': 'DNS-Server stoppen',
            'menu.restart_server': 'DNS-Server neu starten',
            'menu.settings': 'Einstellungen',
            'menu.about': 'Über',
            'menu.help': 'Hilfe',
            'menu.exit': 'Beenden',
            
            'server.status.running': 'Server läuft',
            'server.status.stopped': 'Server gestoppt',
            'server.status.starting': 'Server wird gestartet...',
            'server.status.stopping': 'Server wird gestoppt...',
            'server.status.error': 'Serverfehler',
            
            'button.save': 'Speichern',
            'button.cancel': 'Abbrechen',
            'button.delete': 'Löschen',
            'button.edit': 'Bearbeiten',
            'button.add': 'Hinzufügen',
            'button.close': 'Schließen',
            'button.ok': 'OK',
            
            'msg.success.saved': 'Erfolgreich gespeichert',
            'msg.success.deleted': 'Erfolgreich gelöscht',
            'msg.error.save': 'Speichern fehlgeschlagen',
            'msg.error.delete': 'Löschen fehlgeschlagen',
            
            'settings.title': 'Einstellungen',
            'settings.language': 'Sprache',
            'about.title': 'Über DNS-Server-Manager',
            'help.title': 'Hilfe',
        }
        
        # Italian translations
        self.translations_data['it'] = {
            'menu.title': 'Gestore Server DNS',
            'menu.start_server': 'Avvia Server DNS',
            'menu.stop_server': 'Ferma Server DNS',
            'menu.restart_server': 'Riavvia Server DNS',
            'menu.settings': 'Impostazioni',
            'menu.about': 'Informazioni',
            'menu.help': 'Aiuto',
            'menu.exit': 'Esci',
            
            'server.status.running': 'Server in esecuzione',
            'server.status.stopped': 'Server fermato',
            'server.status.starting': 'Avvio del server...',
            'server.status.stopping': 'Arresto del server...',
            'server.status.error': 'Errore del server',
            
            'button.save': 'Salva',
            'button.cancel': 'Annulla',
            'button.delete': 'Elimina',
            'button.edit': 'Modifica',
            'button.add': 'Aggiungi',
            'button.close': 'Chiudi',
            'button.ok': 'OK',
            
            'msg.success.saved': 'Salvato con successo',
            'msg.success.deleted': 'Eliminato con successo',
            'msg.error.save': 'Salvataggio fallito',
            'msg.error.delete': 'Eliminazione fallita',
            
            'settings.title': 'Impostazioni',
            'settings.language': 'Lingua',
            'about.title': 'Informazioni su Gestore DNS',
            'help.title': 'Aiuto',
        }
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        Get list of available languages with their display names
        
        Returns:
            Dictionary of language codes and display names
        """
        language_names = {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'ja': '日本語',
            'zh': '中文',
            'ar': 'العربية',
            'hi': 'हिन्दी',
            'ko': '한국어',
            'nl': 'Nederlands',
            'pl': 'Polski',
            'tr': 'Türkçe',
        }
        
        available = {}
        for code in self.translations_data.keys():
            available[code] = language_names.get(code, code.upper())
        
        return available
    
    def load_language(self, language_code: str) -> bool:
        """
        Load translations for a specific language
        
        Args:
            language_code: ISO language code
            
        Returns:
            True if language was loaded successfully
        """
        if language_code in self.translations_data:
            self.current_language = language_code
            return True
        return False
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        Get translated text for a given key
        
        Args:
            key: Translation key (e.g., 'menu.title')
            **kwargs: Variables for string formatting
            
        Returns:
            Translated text, or key if not found
        """
        # Try current language first
        if self.current_language in self.translations_data:
            if key in self.translations_data[self.current_language]:
                text = self.translations_data[self.current_language][key]
                if kwargs:
                    try:
                        return text.format(**kwargs)
                    except (KeyError, ValueError):
                        return text
                return text
        
        # Try fallback language
        if self.fallback_language in self.translations_data:
            if key in self.translations_data[self.fallback_language]:
                text = self.translations_data[self.fallback_language][key]
                if kwargs:
                    try:
                        return text.format(**kwargs)
                    except (KeyError, ValueError):
                        return text
                return text
        
        # Return key if not found
        return key
    
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
        if language_code not in self.translations_data:
            self.translations_data[language_code] = {}
        
        self.translations_data[language_code][key] = text
        return True
    
    def export_translations(self, output_dir: str) -> bool:
        """
        Export all translations to JSON files
        
        Args:
            output_dir: Directory to save translation files
            
        Returns:
            True if export was successful
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for lang_code, translations in self.translations_data.items():
                file_path = output_path / f"{lang_code}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(translations, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def import_translations(self, input_dir: str) -> bool:
        """
        Import translations from JSON files
        
        Args:
            input_dir: Directory containing translation files
            
        Returns:
            True if import was successful
        """
        try:
            input_path = Path(input_dir)
            if not input_path.exists():
                return False
            
            for json_file in input_path.glob("*.json"):
                lang_code = json_file.stem
                with open(json_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    self.translations_data[lang_code] = translations
            
            return True
        except Exception:
            return False
    
    def get_language_info(self, language_code: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific language
        
        Args:
            language_code: ISO language code
            
        Returns:
            Dictionary with language information or None if not found
        """
        if language_code not in self.translations_data:
            return None
        
        translations = self.translations_data[language_code]
        available_languages = self.get_available_languages()
        
        return {
            'code': language_code,
            'name': available_languages.get(language_code, language_code.upper()),
            'total_keys': len(translations),
            'keys': list(translations.keys())
        }
    
    def validate_translations(self) -> Dict[str, List[str]]:
        """
        Validate all translations for missing keys
        
        Returns:
            Dictionary with language codes as keys and lists of missing keys as values
        """
        if self.fallback_language not in self.translations_data:
            return {}
        
        base_keys = set(self.translations_data[self.fallback_language].keys())
        missing_keys = {}
        
        for lang_code, translations in self.translations_data.items():
            if lang_code == self.fallback_language:
                continue
            
            lang_keys = set(translations.keys())
            missing = list(base_keys - lang_keys)
            if missing:
                missing_keys[lang_code] = missing
        
        return missing_keys
    
    def get_translation_coverage(self) -> Dict[str, float]:
        """
        Get translation coverage percentage for each language
        
        Returns:
            Dictionary with language codes as keys and coverage percentage as values
        """
        if self.fallback_language not in self.translations_data:
            return {}
        
        base_count = len(self.translations_data[self.fallback_language])
        coverage = {}
        
        for lang_code, translations in self.translations_data.items():
            if lang_code == self.fallback_language:
                coverage[lang_code] = 100.0
            else:
                count = len(translations)
                percentage = (count / base_count) * 100.0 if base_count > 0 else 0.0
                coverage[lang_code] = round(percentage, 2)
        
        return coverage
