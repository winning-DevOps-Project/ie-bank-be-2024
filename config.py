import os
import urllib.parse
from azure.identity import DefaultAzureCredential

class Config(object): 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')

class LocalConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///local.db'
    DEBUG = True

class GithubCIConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    DEBUG = True

class DevelopmentConfig(Config):
    credential = DefaultAzureCredential()
    SQLALCHEMY_DATABASE_URI = 'postgresql://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=urllib.parse.quote(os.getenv('DBUSER')),
    dbpass=credential.get_token(
    'https://ossrdbms-aad.database.windows.net').token,
    dbhost=os.getenv('DBHOST'),
    dbname=os.getenv('DBNAME')
    )
    DEBUG = True

class UATConfig(Config):
    credential = DefaultAzureCredential()
    SQLALCHEMY_DATABASE_URI = 'postgresql://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=urllib.parse.quote(os.getenv('DBUSER')),
    dbpass=credential.get_token(
    'https://ossrdbms-aad.database.windows.net').token,
    dbhost=os.getenv('DBHOST'),
    dbname=os.getenv('DBNAME')
    )
    DEBUG = True