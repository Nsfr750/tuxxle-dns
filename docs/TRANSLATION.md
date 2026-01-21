# Translation Guide

This document provides comprehensive guidelines for translating the DNS Server Manager application. It covers the translation system structure, contribution process, and best practices for maintaining multilingual support.

## Table of Contents

- [Translation System Overview](#translation-system-overview)
- [Supported Languages](#supported-languages)
- [Translation Structure](#translation-structure)
- [Adding New Translations](#adding-new-translations)
- [Translation Guidelines](#translation-guidelines)
- [Quality Assurance](#quality-assurance)
- [Tools and Resources](#tools-and-resources)
- [Maintenance](#maintenance)

## Translation System Overview

### Architecture

The translation system consists of three main components:

1. **Language Manager** (`lang/language_manager.py`)
   - Handles language detection and switching
   - Manages translation loading and caching
   - Provides fallback mechanisms

2. **Translations Module** (`lang/translations.py`)
   - Contains all translation strings
   - Provides translation access methods
   - Manages language metadata

3. **Language Files** (embedded in translations.py)
   - Stores translation strings for each language
   - Follows key-value structure
   - Supports string formatting

### Features

- **Automatic Language Detection**: Detects system language on startup
- **Runtime Language Switching**: Change language without restart
- **Fallback Support**: Falls back to English for missing translations
- **Validation**: Checks for missing keys and consistency
- **Export/Import**: Supports translation file management

## Supported Languages

### Currently Supported

| Language | Code | Status | Coverage |
|----------|------|--------|----------|
| English | `en` | Complete | 100% |
| Spanish | `es` | Partial | 80% |
| French | `fr` | Partial | 80% |
| German | `de` | Partial | 80% |
| Italian | `it` | Partial | 80% |

### Planned Languages

| Language | Code | Priority | Notes |
|----------|------|----------|-------|
| Portuguese | `pt` | High | Large user base |
| Russian | `ru` | Medium | Cyrillic script support |
| Japanese | `ja` | Medium | Asian language support |
| Chinese (Simplified) | `zh` | Medium | Large user base |
| Arabic | `ar` | Low | RTL support needed |

## Translation Structure

### Translation Keys

Translation keys follow a hierarchical structure:

```
category.subcategory.item
```

Examples:
- `menu.title` - Main menu title
- `button.save` - Save button text
- `msg.error.save` - Save error message
- `settings.language` - Language setting label

### Key Categories

#### UI Elements
- `menu.*` - Menu items and navigation
- `button.*` - Button labels
- `form.*` - Form field labels
- `dialog.*` - Dialog titles and messages

#### Server Status
- `server.status.*` - Server status messages
- `server.error.*` - Server error messages

#### DNS Records
- `dns.record.*` - DNS record types and operations
- `dns.type.*` - DNS record type names

#### Messages
- `msg.success.*` - Success messages
- `msg.error.*` - Error messages
- `msg.warning.*` - Warning messages
- `msg.info.*` - Information messages

#### Settings
- `settings.*` - Configuration options
- `settings.general.*` - General settings
- `settings.server.*` - Server settings

#### Common
- `common.*` - Commonly used terms
- `time.*` - Time-related terms
- `validation.*` - Validation messages

### Translation Values

Translation values support:

1. **Plain Text**: Simple string translations
2. **String Formatting**: Variables using `{placeholder}` syntax
3. **Special Characters**: Unicode characters and symbols
4. **Context**: Different translations based on context

```python
# Plain text
'menu.title': 'DNS Server Manager'

# String formatting
'msg.success.saved': 'Saved {count} records successfully'

# Special characters
'common.copyright': '© Copyright 2024-2026 Nsfr750'
```

## Adding New Translations

### Step 1: Add Language Support

1. **Add Language Code** to `translations.py`:

```python
# Add to available languages mapping
language_names = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',  # New language
}
```

2. **Create Translation Dictionary**:

```python
# Add new language translations
self.translations_data['pt'] = {
    'menu.title': 'Gestor de Servidor DNS',
    'button.save': 'Guardar',
    'msg.success.saved': 'Guardado com sucesso',
    # ... add all translations
}
```

### Step 2: Translate All Keys

Ensure **all** keys from the base language (English) are translated:

```python
def get_missing_translations(language_code: str) -> List[str]:
    """Get list of missing translations for a language"""
    base_keys = set(self.translations_data['en'].keys())
    lang_keys = set(self.translations_data[language_code].keys())
    return list(base_keys - lang_keys)
```

### Step 3: Validate Translations

Run validation to ensure completeness:

```python
# Check for missing keys
missing = translations.validate_translations()
if language_code in missing:
    print(f"Missing keys for {language_code}: {missing[language_code]}")

# Check coverage
coverage = translations.get_translation_coverage()
print(f"Coverage for {language_code}: {coverage[language_code]}%")
```

### Step 4: Test the Translation

1. **Set Language**:

```python
language_manager = LanguageManager()
language_manager.set_language('pt')
```

2. **Verify Display**:

```python
# Test key translations
assert language_manager.get_text('menu.title') == 'Gestor de Servidor DNS'
assert language_manager.get_text('button.save') == 'Guardar'
```

## Translation Guidelines

### General Principles

1. **Be Accurate**: Translate meaning, not just words
2. **Be Consistent**: Use same terminology throughout
3. **Be Natural**: Use idiomatic expressions
4. **Be Concise**: Keep text length reasonable for UI
5. **Be Culturally Appropriate**: Consider cultural context

### UI Text Guidelines

#### Buttons and Labels
- Keep button text short and action-oriented
- Use consistent terminology
- Avoid abbreviations unless common

```python
# Good
'button.save': 'Save'
'button.cancel': 'Cancel'
'button.delete': 'Delete'

# Bad
'button.save': 'Save the current record'
'button.cancel': 'Cancel the operation'
```

#### Messages
- Use clear, user-friendly language
- Provide context when helpful
- Use appropriate tone (formal vs informal)

```python
# Good
'msg.success.saved': 'Record saved successfully'
'msg.error.invalid_domain': 'Please enter a valid domain name'

# Bad
'msg.success.saved': 'The record has been saved to the database'
'msg.error.invalid_domain': 'Domain validation failed'
```

#### Technical Terms
- Keep technical terms in English when appropriate
- Provide explanations for complex concepts
- Use established translations for common terms

```python
# Good
'dns.record.type.a': 'A Record'
'dns.record.type.cname': 'CNAME Record'
'dns.record.type.mx': 'MX Record'

# Consider translating
'dns.record.type.a': 'Registro A'
'dns.record.type.cname': 'Registro CNAME'
```

### String Formatting

#### Placeholders
- Use meaningful placeholder names
- Maintain placeholder order when possible
- Test formatted strings

```python
# Good
'msg.records.imported': 'Imported {count} records from {filename}'
'msg.server.started': 'Server started on {host}:{port}'

# Bad
'msg.records.imported': 'Imported {0} records from {1}'
'msg.server.started': 'Server started'
```

#### Pluralization
- Handle plural forms appropriately
- Consider language-specific plural rules
- Use separate keys when necessary

```python
# English (simple plural)
'msg.records.count': '{count} record'
'msg.records.count_plural': '{count} records'

# Language-specific handling might be needed
```

### Character Encoding

- Use UTF-8 encoding for all translation files
- Support Unicode characters and emojis
- Test display on different systems

```python
# Good
'common.copyright': '© Copyright 2024-2026 Nsfr750'
'common.check': '✓'
'common.cross': '✗'

# Special characters for different languages
'menu.about': 'Über'  # German
'menu.help': 'Ajuda'  # Portuguese
```

## Quality Assurance

### Validation Process

#### Automated Checks

1. **Completeness Check**: All keys must be translated
2. **Format Validation**: No formatting errors
3. **Character Encoding**: Valid UTF-8 encoding
4. **Placeholder Consistency**: All placeholders preserved

```python
def validate_translation(language_code: str) -> Dict[str, List[str]]:
    """Validate translation for a language"""
    issues = {
        'missing_keys': [],
        'invalid_format': [],
        'missing_placeholders': []
    }
    
    base_translations = translations.translations_data['en']
    lang_translations = translations.translations_data[language_code]
    
    # Check missing keys
    for key in base_translations:
        if key not in lang_translations:
            issues['missing_keys'].append(key)
    
    # Check placeholder consistency
    for key in base_translations:
        if key in lang_translations:
            base_placeholders = extract_placeholders(base_translations[key])
            lang_placeholders = extract_placeholders(lang_translations[key])
            if base_placeholders != lang_placeholders:
                issues['missing_placeholders'].append(key)
    
    return issues
```

#### Manual Review

1. **Context Review**: Ensure translations fit context
2. **Consistency Check**: Verify terminology consistency
3. **Length Check**: Ensure text fits UI elements
4. **Cultural Review**: Verify cultural appropriateness

### Testing Process

#### Unit Tests

```python
def test_translation_completeness():
    """Test that all languages have complete translations"""
    missing = translations.validate_translations()
    
    for lang_code, missing_keys in missing.items():
        assert len(missing_keys) == 0, f"Missing keys in {lang_code}: {missing_keys}"

def test_placeholder_consistency():
    """Test that placeholders are preserved in translations"""
    base_text = translations.get_text('msg.records.imported', language='en')
    es_text = translations.get_text('msg.records.imported', language='es')
    
    base_placeholders = extract_placeholders(base_text)
    es_placeholders = extract_placeholders(es_text)
    
    assert base_placeholders == es_placeholders
```

#### Integration Tests

```python
def test_language_switching():
    """Test language switching functionality"""
    lang_manager = LanguageManager()
    
    # Switch to Spanish
    lang_manager.set_language('es')
    assert lang_manager.get_text('menu.title') == 'Gestor de Servidor DNS'
    
    # Switch to French
    lang_manager.set_language('fr')
    assert lang_manager.get_text('menu.title') == 'Gestionnaire de Serveur DNS'
```

#### UI Tests

```python
def test_ui_display_with_translations():
    """Test that UI displays correctly with different languages"""
    app = QApplication([])
    
    for lang_code in ['en', 'es', 'fr', 'de', 'it']:
        lang_manager = LanguageManager()
        lang_manager.set_language(lang_code)
        
        window = MainWindow(mock_server, mock_config)
        window.show()
        
        # Verify UI elements display correctly
        assert window.windowTitle() == lang_manager.get_text('menu.title')
```

## Tools and Resources

### Translation Tools

#### Online Tools
- **Google Translate**: For initial translations
- **DeepL**: High-quality machine translation
- **Crowdin**: Collaborative translation platform
- **POEditor**: Translation management system

#### Development Tools
- **Translation Validator**: Custom validation scripts
- **Coverage Reporter**: Translation coverage analysis
- **String Extractor**: Extract translatable strings from code

### Helpful Resources

#### Translation Guidelines
- [GNU Translation Guidelines](https://www.gnu.org/software/gettext/manual/html_node/Translators.html)
- [Microsoft Localization Guide](https://docs.microsoft.com/en-us/windows/win32/intl/localization-best-practices)
- [W3C Internationalization](https://www.w3.org/International/)

#### Language-Specific Resources
- **Spanish**: RAE (Real Academia Española) dictionary
- **French**: Académie française guidelines
- **German**: Duden dictionary
- **Italian**: Accademia della Crusca guidelines

### Community Resources

#### Translation Communities
- **Translators Without Borders**: Volunteer translation community
- **GitHub Translators**: Open source translation community
- **Localize.org**: Translation resource center

#### Forums and Groups
- **r/translation**: Reddit translation community
- **ProZ.com**: Professional translator community
- **Translator Café**: Translation discussion forum

## Maintenance

### Regular Tasks

#### Weekly
- Review new translation contributions
- Update translation coverage reports
- Address validation issues

#### Monthly
- Review translation quality metrics
- Update language priority list
- Plan new language additions

#### Quarterly
- Comprehensive translation audit
- User feedback review
- Translation system improvements

### Version Control

#### Translation Files
- Track translation changes in version control
- Use descriptive commit messages
- Separate translation commits from code changes

```bash
# Good commit messages
git commit -m "feat(translation): add Portuguese language support"
git commit -m "fix(translation): missing Spanish translations for settings"
git commit -m "docs(translation): update translation guidelines"
```

#### Branch Strategy
- Use feature branches for new languages
- Create pull requests for translation updates
- Review translations before merging

### Monitoring

#### Metrics to Track
- Translation coverage percentage
- Missing translation count
- User language preferences
- Translation quality feedback

#### Alerts
- Low translation coverage (< 80%)
- High number of missing keys
- User-reported translation issues

### Updates Process

#### When Adding New Features

1. **Identify New Strings**: Extract new translatable strings
2. **Update Base Language**: Add English translations
3. **Update Other Languages**: Add translations for supported languages
4. **Validate**: Run validation checks
5. **Test**: Verify display in UI

#### When Updating Existing Features

1. **Review Changed Strings**: Identify modified text
2. **Update Translations**: Update affected translations
3. **Verify Context**: Ensure translations still fit context
4. **Test**: Verify UI display

### Backup and Recovery

#### Export Translations

```python
# Export all translations to JSON files
translations.export_translations('backup/translations/')
```

#### Import Translations

```python
# Import translations from backup
translations.import_translations('backup/translations/')
```

#### Version History

Maintain translation version history:

```python
{
    "version": "1.0.0",
    "languages": ["en", "es", "fr", "de", "it"],
    "coverage": {
        "en": 100,
        "es": 80,
        "fr": 80,
        "de": 80,
        "it": 80
    },
    "last_updated": "2024-01-01T00:00:00Z"
}
```

## Contributing Translations

### How to Contribute

1. **Choose Language**: Select a language you're fluent in
2. **Review Guidelines**: Read this translation guide
3. **Contact Maintainers**: Discuss translation plans
4. **Translate**: Provide translations for all keys
5. **Validate**: Run validation checks
6. **Submit**: Create pull request with translations

### Translation Quality Standards

#### Accuracy
- Translations must accurately convey the original meaning
- Technical terms should be translated correctly
- Context must be preserved

#### Consistency
- Use consistent terminology throughout
- Follow established translation patterns
- Maintain style consistency

#### Completeness
- All keys must be translated
- No placeholders should be missing
- Formatting must be preserved

#### Cultural Appropriateness
- Consider cultural context
- Use appropriate formality level
- Avoid culturally sensitive content

### Review Process

#### Automated Review
- Validation checks run automatically
- Coverage requirements enforced
- Format validation performed

#### Human Review
- Native speaker review required
- Technical accuracy verification
- UI compatibility testing

#### Approval Process
- Maintainer approval required
- Quality standards must be met
- Documentation must be updated

## Troubleshooting

### Common Issues

#### Missing Translations
```python
# Check for missing keys
missing = translations.validate_translations()
print(f"Missing keys: {missing}")
```

#### Encoding Issues
```python
# Ensure UTF-8 encoding
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

#### Placeholder Issues
```python
# Check placeholder consistency
def check_placeholders(base_text, translated_text):
    base_placeholders = re.findall(r'\{(\w+)\}', base_text)
    trans_placeholders = re.findall(r'\{(\w+)\}', translated_text)
    return base_placeholders == trans_placeholders
```

#### Display Issues
- Check UI element sizes
- Verify font support
- Test on different platforms

### Debug Tools

#### Translation Inspector
```python
def inspect_translations(language_code: str):
    """Inspect translations for debugging"""
    translations_data = translations.translations_data[language_code]
    
    for key, value in translations_data.items():
        print(f"{key}: {value}")
        
        # Check for potential issues
        if len(value) > 100:
            print(f"  Warning: Long text for {key}")
        
        if '{' in value and '}' in value:
            placeholders = re.findall(r'\{(\w+)\}', value)
            print(f"  Placeholders: {placeholders}")
```

#### Coverage Reporter
```python
def generate_coverage_report():
    """Generate translation coverage report"""
    coverage = translations.get_translation_coverage()
    
    print("Translation Coverage Report:")
    print("=" * 40)
    
    for lang_code, percentage in coverage.items():
        status = "✓" if percentage >= 80 else "✗"
        print(f"{lang_code}: {percentage:5.1f}% {status}")
```

## Future Enhancements

### Planned Features

#### Advanced Translation Management
- Web-based translation interface
- Collaborative translation platform
- Automated translation suggestions
- Translation memory system

#### Enhanced Validation
- Grammar checking
- Style consistency validation
- Cultural appropriateness checking
- Automated quality scoring

#### Better User Experience
- Language detection improvement
- Regional dialect support
- Custom translation packs
- Real-time translation updates

### Technical Improvements

#### Performance
- Translation caching optimization
- Lazy loading of translations
- Memory usage optimization
- Faster language switching

#### Extensibility
- Plugin system for translation tools
- API for external translation services
- Custom translation formats support
- Integration with translation platforms

This translation guide provides comprehensive information for maintaining and extending the multilingual support in the DNS Server Manager application. Following these guidelines ensures high-quality translations and a smooth experience for international users.
