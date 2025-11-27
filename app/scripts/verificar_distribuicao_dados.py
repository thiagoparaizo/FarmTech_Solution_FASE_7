# scripts/verificar_distribuicao_dados.py

# Adicionar path do projeto
import os
import sys


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, BASE_DIR)

from app.services.sql_db_service import SQLDatabaseService
from config import Config
from sqlalchemy import text

sql_db = SQLDatabaseService(Config.SQL_DATABASE_URI)
session = sql_db.get_session()

# Verificar distribuição de irrigação
result = session.execute(text("""
    SELECT 
        CASE 
            WHEN valor LIKE '%irrigation%' THEN 'irrigacao' 
            WHEN unidade = '%' THEN 'umidade'
            WHEN unidade = 'pH' THEN 'ph'
            ELSE 'nutrientes' 
        END AS tipo,
        COUNT(*) AS total
    FROM leitura_sensor 
    GROUP BY tipo
"""))

print('Distribuição dos dados:')
for row in result:
    print(f'{row[0]}: {row[1]} registros')

session.close()
