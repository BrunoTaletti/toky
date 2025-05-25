"""
Módulo de configuração do Toky
"""

import json
import os
import pyotp
from typing import Dict, List
from PyQt6.QtGui import QIcon

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "tokens_data.json")
TRANSLATIONS_DIR = os.path.join(BASE_DIR, "translations")
STYLES_DIR = os.path.join(BASE_DIR, "styles")
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")

class ThemeManager:
    """Gerenciador de temas"""
    THEMES = {
        "dark": os.path.join(STYLES_DIR, "dark.qss"),
        "light": os.path.join(STYLES_DIR, "light.qss")
    }
    
    @staticmethod
    def load_theme(theme_name):
        try:
            with open(ThemeManager.THEMES[theme_name], "r") as f:
                return f.read()
        except:
            return ""

class Translator:
    """Sistema de tradução"""
    _instances = {}  # Cache de instâncias

    def __new__(cls, lang="en_US"):
        if lang not in cls._instances:
            cls._instances[lang] = super().__new__(cls)
            cls._instances[lang].lang = lang
            cls._instances[lang].texts = cls._instances[lang]._load_translations()
        return cls._instances[lang]
    
    def _load_translations(self):
        translations = {}
        try:
            # Carrega inglês como fallback
            en_path = os.path.join(TRANSLATIONS_DIR, "en_US.json")
            with open(en_path, "r", encoding="utf-8") as f:
                translations.update(json.load(f))
            
            # Carrega idioma específico se não for inglês
            if self.lang != "en_US":
                lang_path = os.path.join(TRANSLATIONS_DIR, f"{self.lang}.json")
                with open(lang_path, "r", encoding="utf-8") as f:
                    translations.update(json.load(f))
        except Exception as e:
            print(f"Error loading translations: {e}")
        
        return translations
    
    def get(self, key):
        return self.texts.get(key, f"[{key}]")

class UIConfig:
    """Configurações de UI"""
    FONT_NAME = "Montserrat"
    FONT_SIZE = 10
    
    ICON_PATHS = {
        "copy": os.path.join(RESOURCES_DIR, "icons", "copy.svg"),
        "edit": os.path.join(RESOURCES_DIR, "icons", "edit.svg"),
        "delete": os.path.join(RESOURCES_DIR, "icons", "delete.svg"),
        "add": os.path.join(RESOURCES_DIR, "icons", "add.svg"),
        "sun": os.path.join(RESOURCES_DIR, "icons", "sun.svg"),
        "moon": os.path.join(RESOURCES_DIR, "icons", "moon.svg")
    }
    
    @staticmethod
    def init_translator(lang="en_US"):
        return Translator(lang)

class TokenUtils:
    """Utilitários para tokens"""
    @staticmethod
    def normalize_token(token):
        valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        cleaned = "".join(c for c in token.upper() if c in valid_chars)
        return cleaned if len(cleaned) >= 16 else ""
    
    @staticmethod
    def is_valid_token(token):
        try:
            pyotp.TOTP(token).now()
            return True
        except:
            return False

class DataManager:
    """Gerenciador de dados"""
    @staticmethod
    def save_tokens(tokens):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(tokens, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving tokens: {e}")
    
    @staticmethod
    def load_tokens():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []