# This configuration file sets up environment variables, database connection, and password hashing for the Flask application.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
UPLOAD_FOLDER = 'uploads/'

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

bcrypt = Bcrypt()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
