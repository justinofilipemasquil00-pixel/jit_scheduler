import os 
from datetime import timedelta 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-jit-scheduler-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///jit_scheduler.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações de Email - SEGURAS
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # ← REMOVA o email padrão
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # ← REMOVA a senha padrão
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')  # ← REMOVA o email padrão

    # Assunto dos emails
    EMAIL_SUBJECT_PREFIX = '[Sistema JIT] '