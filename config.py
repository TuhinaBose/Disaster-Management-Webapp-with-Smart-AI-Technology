import os

# Base Directory of Application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Application Configuration
    Supports both SQLite (default for easy out-of-the-box local testing)
    and MySQL (for production database deployment).
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'disaster-management-secret-key-2026-super-secure'
    
    # MySQL Database Connection String Example:
    # MYSQL_URI = 'mysql+pymysql://root:password@localhost/disaster_db'
    # To switch to MySQL, set USE_MYSQL = True and update database URI below.
    USE_MYSQL = os.environ.get('USE_MYSQL', 'False').lower() in ['true', '1']

    if USE_MYSQL:
        DB_USER = os.environ.get('DB_USER', 'root')
        DB_PASS = os.environ.get('DB_PASS', 'password')
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '3306')
        DB_NAME = os.environ.get('DB_NAME', 'disaster_db')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Default SQLite DB for instant out-of-the-box local execution
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'disaster_app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Path to serialized Machine Learning Model
    MODEL_PATH = os.path.join(BASE_DIR, 'static', 'model', 'disaster_model.joblib')
