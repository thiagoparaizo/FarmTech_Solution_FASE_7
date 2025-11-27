# scripts/gerar_dados_realistas.py

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Adicionar path do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, BASE_DIR)

from config import Config
from app.services.sql_db_service import SQLDatabaseService

def gerar_dados_super_realistas():
    """Gera dados com MÁXIMA diversidade e situações reais complexas"""
    
    print("🎯 Gerando dados SUPER realistas...")
    
    np.random.seed(None)  # Usar seed verdadeiramente aleatória
    
    # MUITO MAIS AMOSTRAS com cenários diversos
    scenarios = []
    base_time = datetime.now() - timedelta(days=60)  # 60 dias para mais variedade
    
    # Cenário 1: Agricultura normal (40%)
    for i in range(300):
        timestamp = base_time + timedelta(hours=i*0.5)  # A cada 30 minutos
        hora = timestamp.hour
        
        # Padrões naturais mais complexos
        umidade = np.random.beta(2, 5) * 100  # Distribuição beta (mais realística)
        ph = np.random.normal(6.8, 0.8)  # Normal com média 6.8
        ph = np.clip(ph, 4.0, 9.5)
        
        fosforo = np.random.choice([0, 1], p=[0.65, 0.35])
        potassio = np.random.choice([0, 1], p=[0.70, 0.30])
        
        # Lógica de irrigação MUITO mais complexa e humana
        irrigacao = decidir_irrigacao_complexa(umidade, ph, fosforo, potassio, hora, 'normal')
        
        scenarios.append({
            'timestamp': int(timestamp.timestamp() * 1000),
            'datetime': timestamp,
            'umidade': round(umidade, 2),
            'ph': round(ph, 2),
            'fosforo': fosforo,
            'potassio': potassio,
            'irrigacao': irrigacao,
            'scenario': 'normal'
        })
    
    # Cenário 2: Período de seca (20%)
    for i in range(150):
        timestamp = base_time + timedelta(days=15, hours=i*0.8)
        hora = timestamp.hour
        
        # Durante seca: umidade mais baixa, pH pode variar
        umidade = np.random.beta(1, 4) * 60  # Tendência mais baixa
        ph = np.random.normal(7.2, 1.0)  # pH pode variar mais
        ph = np.clip(ph, 4.5, 9.0)
        
        fosforo = np.random.choice([0, 1], p=[0.80, 0.20])  # Menos nutrientes
        potassio = np.random.choice([0, 1], p=[0.75, 0.25])
        
        irrigacao = decidir_irrigacao_complexa(umidade, ph, fosforo, potassio, hora, 'seca')
        
        scenarios.append({
            'timestamp': int(timestamp.timestamp() * 1000),
            'datetime': timestamp,
            'umidade': round(umidade, 2),
            'ph': round(ph, 2),
            'fosforo': fosforo,
            'potassio': potassio,
            'irrigacao': irrigacao,
            'scenario': 'seca'
        })
    
    # Cenário 3: Período chuvoso (20%)
    for i in range(150):
        timestamp = base_time + timedelta(days=35, hours=i*0.7)
        hora = timestamp.hour
        
        # Durante chuvas: umidade alta, pH pode mudar
        umidade = np.random.beta(5, 2) * 100  # Tendência mais alta
        ph = np.random.normal(6.5, 0.6)  # pH mais ácido
        ph = np.clip(ph, 5.0, 8.5)
        
        fosforo = np.random.choice([0, 1], p=[0.50, 0.50])  # Mais equilibrado
        potassio = np.random.choice([0, 1], p=[0.60, 0.40])
        
        irrigacao = decidir_irrigacao_complexa(umidade, ph, fosforo, potassio, hora, 'chuva')
        
        scenarios.append({
            'timestamp': int(timestamp.timestamp() * 1000),
            'datetime': timestamp,
            'umidade': round(umidade, 2),
            'ph': round(ph, 2),
            'fosforo': fosforo,
            'potassio': potassio,
            'irrigacao': irrigacao,
            'scenario': 'chuva'
        })
    
    # Cenário 4: Situações problemáticas/erro humano (10%)
    for i in range(75):
        timestamp = base_time + timedelta(days=50, hours=i)
        hora = timestamp.hour
        
        # Dados mais caóticos (simula problemas reais)
        umidade = np.random.uniform(5, 95)  # Completamente aleatório
        ph = np.random.uniform(4.0, 9.5)    # pH problemático
        
        fosforo = np.random.choice([0, 1])
        potassio = np.random.choice([0, 1])
        
        # Decisões menos lógicas (simula erro humano)
        irrigacao = decidir_irrigacao_complexa(umidade, ph, fosforo, potassio, hora, 'problematico')
        
        scenarios.append({
            'timestamp': int(timestamp.timestamp() * 1000),
            'datetime': timestamp,
            'umidade': round(umidade, 2),
            'ph': round(ph, 2),
            'fosforo': fosforo,
            'potassio': potassio,
            'irrigacao': irrigacao,
            'scenario': 'problematico'
        })
    
    # Cenário 5: Noites (10%) - Geralmente sem irrigação
    for i in range(75):
        timestamp = base_time + timedelta(days=10, hours=i*0.3)
        timestamp = timestamp.replace(hour=np.random.choice([22, 23, 0, 1, 2, 3, 4, 5]))
        hora = timestamp.hour
        
        umidade = np.random.normal(50, 20)
        umidade = np.clip(umidade, 10, 90)
        ph = np.random.normal(6.8, 0.5)
        ph = np.clip(ph, 5.5, 8.0)
        
        fosforo = np.random.choice([0, 1], p=[0.60, 0.40])
        potassio = np.random.choice([0, 1], p=[0.65, 0.35])
        
        # À noite raramente irriga
        irrigacao = decidir_irrigacao_complexa(umidade, ph, fosforo, potassio, hora, 'noite')
        
        scenarios.append({
            'timestamp': int(timestamp.timestamp() * 1000),
            'datetime': timestamp,
            'umidade': round(umidade, 2),
            'ph': round(ph, 2),
            'fosforo': fosforo,
            'potassio': potassio,
            'irrigacao': irrigacao,
            'scenario': 'noite'
        })
    
    # Embaralhar todos os cenários
    np.random.shuffle(scenarios)
    
    print(f"✅ Gerados {len(scenarios)} registros SUPER diversos")
    
    # Analisar distribuição
    df_temp = pd.DataFrame(scenarios)
    print(f"📊 Irrigação: {df_temp['irrigacao'].value_counts().to_dict()}")
    print(f"🌡️ Umidade: {df_temp['umidade'].min():.1f}% - {df_temp['umidade'].max():.1f}%")
    print(f"🧪 pH: {df_temp['ph'].min():.2f} - {df_temp['ph'].max():.2f}")
    
    by_scenario = df_temp.groupby('scenario')['irrigacao'].mean()
    print(f"🎭 Por cenário:")
    for scenario, rate in by_scenario.items():
        print(f"   {scenario}: {rate:.1%} irrigação")
    
    return scenarios

def decidir_irrigacao_complexa(umidade, ph, fosforo, potassio, hora, scenario):
    """Lógica MUITO mais complexa e realística para decisão de irrigação"""
    
    # Base score mais sutil
    score = 0.0
    
    # Umidade (principal fator, mas não linear)
    if umidade < 15:
        score += 3.0  # Crítico
    elif umidade < 25:
        score += 2.5  # Muito baixo
    elif umidade < 35:
        score += 2.0  # Baixo
    elif umidade < 50:
        score += 1.0  # Médio-baixo
    elif umidade < 70:
        score += 0.2  # OK
    else:
        score -= 1.0  # Muito úmido
    
    # pH (influência moderada)
    if 6.0 <= ph <= 7.5:
        score += 1.0  # Ideal
    elif 5.5 <= ph <= 8.0:
        score += 0.3  # Aceitável
    else:
        score -= 0.8  # Problemático
    
    # Nutrientes (influência menor)
    if fosforo and potassio:
        score += 0.5
    elif fosforo or potassio:
        score += 0.2
    else:
        score -= 0.3
    
    # Horário (muito importante)
    if 6 <= hora <= 9:
        score += 1.5  # Manhã ideal
    elif 17 <= hora <= 19:
        score += 1.0  # Tarde boa
    elif 10 <= hora <= 16:
        score -= 1.0  # Meio-dia quente
    elif 20 <= hora <= 5:
        score -= 2.0  # Noite
    
    # Ajustes por cenário
    if scenario == 'seca':
        score += 1.0  # Mais propenso a irrigar
    elif scenario == 'chuva':
        score -= 1.5  # Menos propenso
    elif scenario == 'noite':
        score -= 1.5  # Raramente irriga
    elif scenario == 'problematico':
        score += np.random.normal(0, 1.0)  # Caótico
    
    # Adicionar aleatoriedade substancial (simula fatores não medidos)
    noise = np.random.normal(0, 0.8)
    score += noise
    
    # Conversão para probabilidade (sigmoide)
    probability = 1 / (1 + np.exp(-score))
    
    # Decisão final com threshold variável
    threshold = np.random.uniform(0.35, 0.65)  # Threshold dinâmico
    
    return 1 if probability > threshold else 0

def inserir_dados_diversos(data):
    """Insere os dados diversos no banco"""
    
    print("\n💾 Inserindo dados diversos no banco...")
    
    sql_db = SQLDatabaseService(Config.SQL_DATABASE_URI)
    session = sql_db.get_session()
    
    try:
        from sqlalchemy import text
        
        # Limpar dados antigos
        print("🧹 Limpando dados antigos...")
        session.execute(text("DELETE FROM leitura_sensor WHERE sensor_id = 1"))
        session.commit()
        
        # Inserir leituras diversas
        print("📝 Inserindo leituras diversas...")
        
        for i, record in enumerate(data):
            # Inserir umidade
            session.execute(text("""
                INSERT INTO leitura_sensor (sensor_id, valor, unidade, data_hora) 
                VALUES (1, :valor, '%', :data_hora)
            """), {
                "valor": str(record['umidade']),
                "data_hora": record['datetime']
            })
            
            # Inserir pH
            session.execute(text("""
                INSERT INTO leitura_sensor (sensor_id, valor, unidade, data_hora) 
                VALUES (1, :valor, 'pH', :data_hora)
            """), {
                "valor": str(record['ph']),
                "data_hora": record['datetime']
            })
            
            # Inserir nutrientes
            nutrientes = {"P": record['fosforo'], "K": record['potassio']}
            session.execute(text("""
                INSERT INTO leitura_sensor (sensor_id, valor, unidade, data_hora) 
                VALUES (1, :valor, 'ppm', :data_hora)
            """), {
                "valor": str(nutrientes),
                "data_hora": record['datetime']
            })
            
            if (i + 1) % 200 == 0:
                print(f"   📊 Inseridos {i + 1}/{len(data)} registros...")
        
        session.commit()
        print(f"✅ {len(data)} registros diversos inseridos!")
        
        # Verificar
        result = session.execute(text("SELECT COUNT(*) FROM leitura_sensor WHERE sensor_id = 1"))
        total = result.fetchone()[0]
        print(f"📊 Total leituras: {total}")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

def main():
    print("🌱 FarmTech Solutions - Gerador de Dados SUPER Realistas")
    print("=" * 60)
    
    try:
        # Gerar dados super diversos
        data = gerar_dados_super_realistas()
        
        # Inserir no banco
        inserir_dados_diversos(data)
        
        print("\n🎉 Dados super realistas criados!")
        print("🚀 Execute: python app/scripts/train_model.py --days 60 --min-samples 50")
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())