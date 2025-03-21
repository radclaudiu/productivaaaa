import os
import logging
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Config:
    """Base configuration."""
    # Base configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-key-for-development')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configure SQLAlchemy database connection
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-key-for-development')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Ensure upload directory exists
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
