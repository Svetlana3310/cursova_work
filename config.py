import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    DEBUG = True

    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(
        os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 86400)))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'MASTER_DB_URI', 'postgresql://postgres:postgres@localhost:5432/course_db')

    # Репліка для читання (Slave)
    SQLALCHEMY_BINDS = {
        'replica': os.getenv('REPLICA_DB_URI', 'postgresql://replicator:replicator_password@localhost:5445/course_db')
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False
