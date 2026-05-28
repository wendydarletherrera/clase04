from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        #"postgresql+psycopg2://postgres:wendy123@localhost:5432/cafe_andino",
        "postgresql+psycopg2://user_cafe_andino:PeLD2cVjJGuFfvLaJPtVqlvkNKJrACcz@dpg-d8c2bgl7vvec73de3dr0-a.oregon-postgres.render.com/cafe_andino_0lq3"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@cafeandino.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")
    ADMIN_FULL_NAME = os.getenv("ADMIN_FULL_NAME", "Administrador Cafe Andino")

    CSV_UPLOAD_FOLDER = os.getenv("CSV_UPLOAD_FOLDER", str(BASE_DIR / "tmp" / "uploads"))
