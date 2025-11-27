# scripts/importar_dados_esp32.py
import sys
import os
import csv
import time
import sqlite3
from datetime import datetime

# Adicionar o diretório raiz ao path para importar módulos da aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from app.services.sql_db_service import SQLDatabaseService

def ler_arquivo_csv(caminho_arquivo):
    """Lê um arquivo CSV com dados do ESP32"""
    dados = []
    with open(caminho_arquivo, 'r') as arquivo:
        leitor = csv.reader(arquivo)
        # Pular a primeira linha se for cabeçalho
        cabecalho = next(leitor, None)
        if cabecalho and cabecalho[0] == 'timestamp':
            # É um cabeçalho, continuar
            pass
        else:
            # Não é um cabeçalho, adicionar aos dados
            dados.append(cabecalho)
        
        # Ler o restante do arquivo
        for linha in leitor:
            dados.append(linha)
    
    return dados

def importar_dados_para_db(dados, sensor_id, sql_db_service):
    """Importa os dados para o banco de dados SQL"""
    print(f"Importando {len(dados)} registros para o sensor ID {sensor_id}...")
    
    for linha in dados:
        try:
            if len(linha) != 6:
                print(f"Linha ignorada (formato inválido): {linha}")
                continue
                
            timestamp = int(linha[0])
            fosforo = linha[1] == '1'
            potassio = linha[2] == '1'
            ph = float(linha[3])
            umidade = float(linha[4])
            irrigacao = linha[5] == '1'
            
            # Criar data/hora a partir do timestamp
            data_hora = datetime.fromtimestamp(timestamp/1000 if timestamp > 1000000000000 else timestamp)
            
            # Registrar leituras
            nutrientes = {
                'P': 1 if fosforo else 0,
                'K': 1 if potassio else 0
            }
            
            # Adicionar cada leitura com seu timestamp correto
            sql_db_service.adicionar_leitura(
                sensor_id=sensor_id,
                valor=umidade,
                unidade='%',
                data_hora=data_hora
            )
            
            sql_db_service.adicionar_leitura(
                sensor_id=sensor_id,
                valor=ph,
                unidade='pH',
                data_hora=data_hora
            )
            
            sql_db_service.adicionar_leitura(
                sensor_id=sensor_id,
                valor=str(nutrientes),
                unidade='ppm',
                data_hora=data_hora
            )
            
            print(f"Registro importado: {data_hora} - Umidade: {umidade}%, pH: {ph}")
            
        except Exception as e:
            print(f"Erro ao importar linha {linha}: {str(e)}")
    
    print("Importação concluída!")

def main():
    if len(sys.argv) < 3:
        print("Uso: python importar_dados_esp32.py <caminho_arquivo_csv> <sensor_id>")
        sys.exit(1)
    
    caminho_arquivo = sys.argv[1]
    sensor_id = int(sys.argv[2])
    
    if not os.path.exists(caminho_arquivo):
        print(f"Arquivo não encontrado: {caminho_arquivo}")
        sys.exit(1)
    
    # Configurar conexão com o banco de dados
    sql_db = SQLDatabaseService(Config.SQL_DATABASE_URI)
    #sql_db = SQLDatabaseService("mysql://farmtech:senha@localhost/farmtech_sensors")
    
    # Verificar se o sensor existe
    sensor = sql_db.obter_sensor(sensor_id)
    if not sensor:
        print(f"Sensor com ID {sensor_id} não encontrado no banco de dados.")
        criar_sensor = input("Deseja criar um novo sensor com este ID? (s/n): ").lower() == 's'
        
        if criar_sensor:
            tipo = input("Tipo do sensor (S1=Umidade, S2=pH, S3=Nutrientes): ")
            modelo = input("Modelo do sensor (opcional): ")
            
            sql_db.adicionar_sensor(tipo, modelo)
            print(f"Sensor criado com ID: {sensor_id}")
        else:
            sys.exit(1)
    
    # Ler e importar os dados
    dados = ler_arquivo_csv(caminho_arquivo)
    importar_dados_para_db(dados, sensor_id, sql_db)

if __name__ == "__main__":
    main()