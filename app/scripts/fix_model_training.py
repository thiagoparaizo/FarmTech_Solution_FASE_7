# app/scripts/fix_model_training.py

"""
FarmTech Solutions - CORREÇÃO CRÍTICA DO MODELO
Corrige o problema de classe única no treinamento ML
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Configuração de path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, BASE_DIR)

from config import Config
from app.services.sql_db_service import SQLDatabaseService

def gerar_dados_balanceados_realistas():
    """Gera dados realistas com AMBAS as classes para treinamento"""
    
    print("🔧 FarmTech - CORREÇÃO DO MODELO ML")
    print("=" * 50)
    
    # Conectar ao banco
    sql_db = SQLDatabaseService(Config.SQL_DATABASE_URI)
    session = sql_db.get_session()
    
    try:
        # Limpar dados antigos
        print("🧹 Limpando dados antigos...")
        from sqlalchemy import text
        session.execute(text("DELETE FROM leitura_sensor WHERE sensor_id > 0"))
        session.commit()
        
        registros = []
        
        # CENÁRIO 1: DEVE IRRIGAR (classe 1) - 150 amostras
        print("💧 Gerando dados: DEVE IRRIGAR...")
        for i in range(150):
            base_time = datetime.now() - timedelta(hours=i)
            
            # Condições que EXIGEM irrigação
            umidade = np.random.uniform(5, 25)      # Solo MUITO seco
            ph = np.random.uniform(6.0, 7.5)       # pH ideal
            fosforo = np.random.choice([0, 1])     # Varia
            potassio = np.random.choice([0, 1])    # Varia
            irrigacao = 1  # DEVE irrigar
            
            registros.extend([
                {
                    'sensor_id': 1, 'valor': umidade,
                    'data_hora': base_time, 'irrigacao': irrigacao
                },
                {
                    'sensor_id': 2, 'valor': ph,
                    'data_hora': base_time, 'irrigacao': irrigacao
                },
                {
                    'sensor_id': 3, 'valor': 1.0, 'P': fosforo, 'K': potassio,
                    'data_hora': base_time, 'irrigacao': irrigacao
                }
            ])
        
        # CENÁRIO 2: NÃO DEVE IRRIGAR (classe 0) - 150 amostras
        print("🚫 Gerando dados: NÃO DEVE IRRIGAR...")
        for i in range(150, 300):
            base_time = datetime.now() - timedelta(hours=i)
            
            # Condições que NÃO EXIGEM irrigação
            scenarios = [
                # Solo já úmido
                {'umidade': np.random.uniform(60, 95), 'ph': np.random.uniform(5.5, 8.5)},
                # pH muito ácido/básico (mesmo com solo seco)
                {'umidade': np.random.uniform(15, 40), 'ph': np.random.uniform(3.0, 5.5)},
                {'umidade': np.random.uniform(15, 40), 'ph': np.random.uniform(8.0, 10.0)},
                # Solo medianamente úmido
                {'umidade': np.random.uniform(35, 60), 'ph': np.random.uniform(6.0, 7.5)},
            ]
            
            scenario = np.random.choice(scenarios)
            fosforo = np.random.choice([0, 1])
            potassio = np.random.choice([0, 1])
            irrigacao = 0  # NÃO deve irrigar
            
            registros.extend([
                {
                    'sensor_id': 1, 'valor': scenario['umidade'],
                    'data_hora': base_time, 'irrigacao': irrigacao
                },
                {
                    'sensor_id': 2, 'valor': scenario['ph'],
                    'data_hora': base_time, 'irrigacao': irrigacao
                },
                {
                    'sensor_id': 3, 'valor': 1.0, 'P': fosforo, 'K': potassio,
                    'data_hora': base_time, 'irrigacao': irrigacao
                }
            ])
        
        # Inserir no banco
        print("💾 Inserindo dados balanceados...")
        
        from app.models.sensor_models import LeituraSensor
        import json
        
        for registro in registros:
            # Adaptar para estrutura real do LeituraSensor
            if registro['sensor_id'] == 1:  # Sensor umidade
                valor_str = str(registro['valor'])
                unidade = '%'
            elif registro['sensor_id'] == 2:  # Sensor pH
                valor_str = str(registro['valor'])
                unidade = 'pH'
            elif registro['sensor_id'] == 3:  # Sensor nutrientes
                # Criar JSON para nutrientes
                nutrientes = {
                    'P': int(registro.get('P', 0)),
                    'K': int(registro.get('K', 0)),
                    'irrigacao': int(registro['irrigacao'])
                }
                valor_str = json.dumps(nutrientes)
                unidade = 'ppm'
            
            leitura = LeituraSensor(
                sensor_id=registro['sensor_id'],
                data_hora=registro['data_hora'],
                valor=valor_str,
                unidade=unidade,
                valido=True
            )
            session.add(leitura)
        
        session.commit()
        
        # Verificar distribuição
        from sqlalchemy import text
        result = session.execute(text("""
            SELECT 
                JSON_EXTRACT(valor, '$.irrigacao') as irrigacao, 
                COUNT(*) as count 
            FROM leitura_sensor 
            WHERE sensor_id = 3 AND unidade = 'ppm'
            GROUP BY JSON_EXTRACT(valor, '$.irrigacao')
        """)).fetchall()
        
        print("📊 DISTRIBUIÇÃO FINAL:")
        for row in result:
            print(f"   Classe {row[0]}: {row[1]} amostras")
        
        print("\n✅ DADOS BALANCEADOS CRIADOS!")
        print("🚀 Execute: python app/scripts/train_model.py --days 30 --min-samples 50")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
    finally:
        session.close()

def verificar_modelo_atual():
    """Verifica se o modelo atual tem problema de classe única"""
    try:
        from app.ml.irrigation_predictor import IrrigationPredictor
        
        predictor = IrrigationPredictor()
        success = predictor.load_models()
        
        if success:
            classes = predictor.irrigation_classifier.classes_
            print(f"🔍 Classes no modelo atual: {classes}")
            print(f"🔍 Número de classes: {len(classes)}")
            
            if len(classes) < 2:
                print("❌ PROBLEMA CONFIRMADO: Modelo tem apenas uma classe!")
                return False
            else:
                print("✅ Modelo tem múltiplas classes")
                return True
        else:
            print("⚠️ Nenhum modelo encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar modelo: {e}")
        return False

def testar_predicao_corrigida():
    """Testa predição após correção"""
    try:
        from app.ml.irrigation_predictor import IrrigationPredictor
        
        predictor = IrrigationPredictor()
        success = predictor.load_models()
        
        if not success:
            print("❌ Não foi possível carregar modelos")
            return
        
        # Teste 1: Solo seco + pH ideal = DEVE irrigar
        test1 = {
            'umidade_atual': 15.0,  # Solo seco
            'ph_atual': 6.8,        # pH ideal
            'fosforo': 1,
            'potassio': 1,
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
        
        # Teste 2: Solo úmido = NÃO deve irrigar
        test2 = {
            'umidade_atual': 75.0,  # Solo úmido
            'ph_atual': 6.8,        # pH ideal
            'fosforo': 1,
            'potassio': 1,
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
        
        print("🧪 TESTANDO PREDIÇÕES:")
        
        result1 = predictor.predict_irrigation_need(test1)
        print(f"Test 1 (Solo Seco): {result1}")
        
        result2 = predictor.predict_irrigation_need(test2)
        print(f"Test 2 (Solo Úmido): {result2}")
        
        # Verificar se faz sentido
        if result1.get('irrigation_needed') and not result2.get('irrigation_needed'):
            print("✅ PREDIÇÕES CORRETAS!")
        else:
            print("❌ Predições ainda incorretas")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    print("🔧 INICIANDO CORREÇÃO DO MODELO ML...")
    
    # 1. Verificar problema atual
    print("\n" + "="*50)
    print("ETAPA 1: Verificando modelo atual")
    problema_confirmado = not verificar_modelo_atual()
    
    # 2. Gerar dados balanceados
    if problema_confirmado:
        print("\n" + "="*50)
        print("ETAPA 2: Gerando dados balanceados")
        gerar_dados_balanceados_realistas()
        
        print("\n" + "="*50)
        print("ETAPA 3: Retreine o modelo com:")
        print("python app/scripts/train_model.py --days 30 --min-samples 50")
        print("\nETAPA 4: Após retreinamento, execute novamente este script para testar")
    else:
        print("\n" + "="*50)
        print("ETAPA 3: Testando predições")
        testar_predicao_corrigida()