"""
Módulo de configuração do Toky
"""

import sys
import json
import os
import base64
import pyotp
from pathlib import Path
from cryptography.fernet import Fernet


# =========================
# BASE DIR (PyInstaller)
# =========================

def get_base_dir():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()


# =========================
# APPDATA
# =========================

def get_app_data_dir():
    if sys.platform != "win32":
        return Path.home() / ".toky"

    local = os.getenv("LOCALAPPDATA", str(Path.home() / "AppData/Local"))
    return Path(local) / "Toky"


APP_DIR = get_app_data_dir()
APP_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# FILES
# =========================

DATA_FILE = APP_DIR / "tokens_data.json"
CONFIG_FILE = APP_DIR / "config.json"


TRANSLATIONS_DIR = os.path.join(BASE_DIR, "translations")
STYLES_DIR = os.path.join(BASE_DIR, "styles")
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")


# =========================
# CRYPTO (TOKENS)
# =========================

KEY_FILE = APP_DIR / "secret.key"


def get_key():
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()

    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    return key


FERNET = Fernet(get_key())


def encrypt(text: str) -> str:
    return FERNET.encrypt(text.encode()).decode()


def decrypt(text: str) -> str:
    return FERNET.decrypt(text.encode()).decode()


# =========================
# THEME MANAGER
# =========================

class ThemeManager:
    THEMES = {
        "dark": os.path.join(STYLES_DIR, "dark.qss"),
        "light": os.path.join(STYLES_DIR, "light.qss")
    }

    @staticmethod
    def load_theme(theme_name):
        try:
            with open(ThemeManager.THEMES[theme_name], "r", encoding="utf-8") as f:
                return f.read()
        except:
            return ""


# =========================
# TRANSLATOR
# =========================

class Translator:
    _instances = {}

    def __new__(cls, lang="en_US"):
        if lang not in cls._instances:
            cls._instances[lang] = super().__new__(cls)
            cls._instances[lang].lang = lang
            cls._instances[lang].texts = cls._instances[lang]._load_translations()
        return cls._instances[lang]

    def _load_translations(self):
        translations = {}

        try:
            en_path = os.path.join(TRANSLATIONS_DIR, "en_US.json")
            with open(en_path, "r", encoding="utf-8") as f:
                translations.update(json.load(f))

            if self.lang != "en_US":
                lang_path = os.path.join(TRANSLATIONS_DIR, f"{self.lang}.json")
                with open(lang_path, "r", encoding="utf-8") as f:
                    translations.update(json.load(f))

        except Exception as e:
            print(f"Error loading translations: {e}")

        return translations

    def get(self, key):
        return self.texts.get(key, f"[{key}]")


# =========================
# UI CONFIG
# =========================

class UIConfig:
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


# =========================
# TOKEN UTILS (UPDATED - ENCRYPTED)
# =========================

class TokenUtils:

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


# =========================
# DATA MANAGER (ENCRYPTED)
# =========================

class DataManager:

    @staticmethod
    def save_tokens(tokens):
        try:
            safe_tokens = []

            for t in tokens:
                safe_tokens.append({
                    "service": t["service"],
                    "token": encrypt(t["token"])
                })

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(safe_tokens, f, indent=4)

        except Exception as e:
            print(f"Error saving tokens: {e}")

    @staticmethod
    def load_tokens():
        try:
            if not DATA_FILE.exists():
                return []

            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            result = []
            for t in data:
                try:
                    result.append({
                        "service": t["service"],
                        "token": decrypt(t["token"])
                    })
                except:
                    continue

            return result

        except Exception:
            return []


# =========================
# APP CONFIG (THEME + LANGUAGE)
# =========================

class AppConfig:
    DEFAULT = {
        "theme": "dark",
        "language": "en_US"
    }

    @staticmethod
    def load():
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass

        return AppConfig.DEFAULT.copy()

    @staticmethod
    def save(data):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")