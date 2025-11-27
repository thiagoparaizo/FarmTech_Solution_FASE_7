import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/farmtech'
    
    # Configuração do banco de dados relacional
    SQL_DATABASE_URI = os.environ.get('SQL_DATABASE_URI') or 'mysql://user:password@localhost/farmtech_sensors'
    
    # Conexão com Oracle
    ORACLE_DATABASE_URI = os.environ.get('ORACLE_DATABASE_URI') or 'oracle+cx_oracle://usuario:senha@localhost:1521/XE'
    
    # Configuração do OpenWeatherMap
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY') or 'sua_chave_aqui'
    
    DEBUG = os.environ.get('FLASK_ENV') == 'development'