import os
from datetime import timedelta

class Config:
    # Database — env var names match Helm deployment values
    DB_HOST     = os.environ.get('DB_HOST', 'mysql-service')
    DB_PORT     = int(os.environ.get('DB_PORT', 3306))
    DB_NAME     = os.environ.get('DB_NAME', 'samurai_db')
    DB_USER     = os.environ.get('DB_USER', 'samurai_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'samurai_pass')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-bushido-key-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # App
    SECRET_KEY = os.environ.get('SECRET_KEY', 'another-secret-key')
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    ITEMS_PER_PAGE = 12
