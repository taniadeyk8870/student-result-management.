"""Application configuration."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "database.db")
    PASSING_MARK = 35
    MIN_MARK = 0
    MAX_MARK = 100
    MIN_YEAR = 1
    MAX_YEAR = 4
    MIN_SEMESTER = 1
    MAX_SEMESTER = 8
    MIN_PASSWORD_LENGTH = 8
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
