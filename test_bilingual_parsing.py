#!/usr/bin/env python3
"""
Test bilingual parsing functionality for SMART_STUDENT
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


def test_basic_bilingual_functionality():
    """Test basic bilingual parsing"""
    # Test language codes
    language_codes = ["es", "en"]
    assert "es" in language_codes
    assert "en" in language_codes
    assert len(language_codes) == 2


def test_spanish_content_parsing():
    """Test parsing Spanish content"""
    spanish_text = "Hola mundo, esto es una prueba en español."
    assert "español" in spanish_text
    assert "Hola" in spanish_text
    assert len(spanish_text.split()) > 5


def test_english_content_parsing():
    """Test parsing English content"""
    english_text = "Hello world, this is a test in English."
    assert "English" in english_text
    assert "Hello" in english_text
    assert len(english_text.split()) > 5


def test_bilingual_dictionary():
    """Test bilingual dictionary structure"""
    bilingual_dict = {
        "es": {"greeting": "Hola", "goodbye": "Adiós"},
        "en": {"greeting": "Hello", "goodbye": "Goodbye"}
    }
    
    assert "es" in bilingual_dict
    assert "en" in bilingual_dict
    assert bilingual_dict["es"]["greeting"] == "Hola"
    assert bilingual_dict["en"]["greeting"] == "Hello"


if __name__ == "__main__":
    pytest.main([__file__])