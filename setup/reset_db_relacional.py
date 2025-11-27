# setup/reset_db_relacional.py
import sys
import os

# Adicionar o diretório raiz ao caminho do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from app.models.sensor_models import Base
from config import Config

def recreate_tables():
    print("Recriando tabelas do banco de dados relacional...")
    
    # Obter URI de configuração
    from config import Config
    sql_database_uri = Config.SQL_DATABASE_URI
    
    # Criar engine com a URI
    engine = create_engine(sql_database_uri)
    
    # Criar todas as tabelas definidas no Base
    Base.metadata.create_all(engine)
    
    print("Tabelas do banco de dados relacional criadas com sucesso!")

if __name__ == "__main__":
    recreate_tables()