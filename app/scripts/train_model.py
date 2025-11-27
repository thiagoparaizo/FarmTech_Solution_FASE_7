# app/scripts/train_model.py

"""
FarmTech Solutions - FASE 4
Script de Treinamento Automático para Modelos de Machine Learning

Este script automatiza o processo de treinamento dos modelos ML,
incluindo coleta de dados, enriquecimento climático e avaliação.

Uso:
    python app/scripts/train_model.py
    python app/scripts/train_model.py --days 60 --min-samples 100
"""

import sys
import os
import argparse
import logging
from datetime import datetime

import sys
if sys.platform == "win32":
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configuração de path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, BASE_DIR)

from config import Config
from app.services.sql_db_service import SQLDatabaseService
from app.ml.irrigation_predictor import IrrigationPredictor
from app.ml.model_trainer import ModelTrainer
from app.services.climate_service import ClimateDataService

def setup_logging():
    """Configura logging para o script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/model_training.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Criar diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    os.makedirs('models', exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description='Treinar modelos ML para FarmTech Solutions')
    parser.add_argument('--days', type=int, default=30, 
                       help='Dias de dados históricos para treinamento (padrão: 30)')
    parser.add_argument('--min-samples', type=int, default=50,
                       help='Número mínimo de amostras necessárias (padrão: 50)')
    parser.add_argument('--location', type=str, default='-3.763081,-38.524465',
                       help='Coordenadas lat,lon para dados climáticos (padrão: São Paulo)')
    parser.add_argument('--save-models', action='store_true', default=True,
                       help='Salvar modelos treinados em disco')
    parser.add_argument('--evaluate-only', action='store_true',
                       help='Apenas avaliar modelos existentes')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== FarmTech Solutions - FASE 4: Treinamento ML ===")
    logger.info(f"Parâmetros: {args}")
    
    try:
        # Inicializar serviços
        logger.info("Inicializando serviços...")
        sql_db = SQLDatabaseService(Config.SQL_DATABASE_URI)
        predictor = IrrigationPredictor()
        trainer = ModelTrainer(sql_db)
        
        # Parsing de coordenadas
        lat, lon = map(float, args.location.split(','))
        logger.info(f"Localização: {lat}, {lon}")
        
        if args.evaluate_only:
            # Apenas avaliar modelos existentes
            logger.info("Modo avaliação: carregando modelos existentes...")
            success = predictor.load_models()
            if not success:
                logger.error("Não foi possível carregar modelos existentes")
                return 1
            
            # Avaliar com dados de teste
            evaluate_existing_models(predictor, trainer, args.days, logger)
            return 0
        
        # Processo completo de treinamento
        logger.info("Iniciando processo de treinamento completo...")
        
        # 1. Coletar dados de treinamento
        logger.info(f"Coletando dados dos últimos {args.days} dias...")
        training_data = trainer.collect_training_data(args.days, args.min_samples)
        
        if not training_data:
            logger.error(f"Dados insuficientes: precisa de pelo menos {args.min_samples} amostras")
            return 1
        
        logger.info(f"Coletados {len(training_data)} registros para treinamento")
        
        # 2. Enriquecer com dados climáticos
        logger.info("Enriquecendo dados com informações climáticas...")
        enriched_data = predictor.enrich_with_climate_data(training_data, lat, lon)
        
        if not enriched_data:
            logger.warning("Não foi possível enriquecer com dados climáticos, usando apenas dados dos sensores")
            enriched_data = training_data
        
        # 3. Treinar modelos
        logger.info("Iniciando treinamento dos modelos ML...")
        metrics = predictor.train_models(enriched_data)
        
        # 4. Exibir resultados
        logger.info("=== RESULTADOS DO TREINAMENTO ===")
        logger.info(f"Acurácia Irrigação: {metrics['irrigation_accuracy']:.3f}")
        logger.info(f"MAE Umidade: {metrics['humidity_mae']:.3f}")
        logger.info(f"CV Irrigação: {metrics['irrigation_cv_mean']:.3f} ± {metrics['irrigation_cv_std']:.3f}")
        logger.info(f"CV Umidade: {metrics['humidity_cv_mean']:.3f} ± {metrics['humidity_cv_std']:.3f}")
        logger.info(f"Amostras de Treino: {metrics['training_samples']}")
        
        # 5. Salvar modelos se solicitado
        if args.save_models:
            logger.info("Salvando modelos treinados...")
            success = predictor.save_models()
            if success:
                logger.info("Modelos salvos com sucesso!")
            else:
                logger.error("Erro ao salvar modelos")
        
        # 6. Teste de predição
        logger.info("Executando teste de predição...")
        test_prediction(predictor, logger)
        
        # 7. Análise de importância das features
        logger.info("Analisando importância das features...")
        analyze_feature_importance(predictor, logger)
        
        logger.info("=== TREINAMENTO CONCLUÍDO COM SUCESSO ===")
        return 0
        
    except Exception as e:
        logger.error(f"Erro durante treinamento: {str(e)}", exc_info=True)
        return 1

def evaluate_existing_models(predictor, trainer, days, logger):
    """Avalia modelos existentes com dados de teste"""
    try:
        # Coletar dados de teste
        test_data = trainer.collect_training_data(days, min_samples=10)
        if not test_data:
            logger.error("Dados insuficientes para avaliação")
            return
        
        # Preparar dados
        X, y_irrigation, y_humidity = predictor.prepare_training_data(test_data)
        X_scaled = predictor.scaler.transform(X)
        
        # Predições
        irr_pred = predictor.irrigation_classifier.predict(X_scaled)
        hum_pred = predictor.humidity_regressor.predict(X_scaled)
        
        # Métricas
        from sklearn.metrics import accuracy_score, mean_absolute_error, classification_report
        
        irr_accuracy = accuracy_score(y_irrigation, irr_pred)
        hum_mae = mean_absolute_error(y_humidity, hum_pred)
        
        logger.info("=== AVALIAÇÃO DE MODELOS EXISTENTES ===")
        logger.info(f"Acurácia Irrigação: {irr_accuracy:.3f}")
        logger.info(f"MAE Umidade: {hum_mae:.3f}")
        logger.info(f"Amostras de Teste: {len(test_data)}")
        
        # Relatório detalhado de classificação
        logger.info("\nRelatório de Classificação (Irrigação):")
        logger.info(f"\n{classification_report(y_irrigation, irr_pred)}")
        
    except Exception as e:
        logger.error(f"Erro na avaliação: {str(e)}")

def test_prediction(predictor, logger):
    """Testa predição com dados simulados"""
    try:
        # Cenários de teste
        test_scenarios = [
            {
                'name': 'Solo Seco + pH Ideal',
                'conditions': {
                    'umidade': 25.0,
                    'ph': 6.8,
                    'fosforo': 1,
                    'potassio': 1,
                    'temperature': 28.0,
                    'humidity_air': 65.0,
                    'precipitation': 0.0,
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }
            },
            {
                'name': 'Solo Úmido + pH Ácido',
                'conditions': {
                    'umidade': 75.0,
                    'ph': 5.2,
                    'fosforo': 0,
                    'potassio': 1,
                    'temperature': 22.0,
                    'humidity_air': 80.0,
                    'precipitation': 5.0,
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }
            },
            {
                'name': 'Condições Normais',
                'conditions': {
                    'umidade': 45.0,
                    'ph': 7.1,
                    'fosforo': 1,
                    'potassio': 0,
                    'temperature': 25.0,
                    'humidity_air': 70.0,
                    'precipitation': 0.0,
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }
            }
        ]
        
        logger.info("=== TESTES DE PREDIÇÃO ===")
        
        for scenario in test_scenarios:
            logger.info(f"\n--- {scenario['name']} ---")
            
            # Fazer predição
            prediction = predictor.predict_irrigation_need(scenario['conditions'])
            
            # Exibir resultados
            logger.info(f"Irrigação Necessária: {'SIM' if prediction['irrigation_needed'] else 'NÃO'}")
            logger.info(f"Probabilidade: {prediction['irrigation_probability']:.1%}")
            logger.info(f"Confiança: {prediction['confidence']:.1%}")
            logger.info(f"Umidade Prevista: {prediction['predicted_humidity_next_hour']:.1f}%")
            
            # Recomendações
            if prediction.get('recommendations'):
                logger.info("Recomendações:")
                for rec in prediction['recommendations'][:3]:  # Top 3
                    logger.info(f"  • {rec}")
                    
    except Exception as e:
        logger.error(f"Erro no teste de predição: {str(e)}")

def analyze_feature_importance(predictor, logger):
    """Analisa e exibe importância das features"""
    try:
        importance = predictor.get_feature_importance()
        if not importance:
            logger.warning("Importância das features não disponível")
            return
        
        logger.info("=== IMPORTÂNCIA DAS FEATURES ===")
        
        # Modelo de irrigação
        logger.info("\n--- Modelo de Irrigação ---")
        irr_importance = sorted(
            importance['irrigation_model'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for feature, importance_val in irr_importance[:10]:  # Top 10
            logger.info(f"{feature:25s}: {importance_val:.4f}")
        
        # Modelo de umidade
        logger.info("\n--- Modelo de Umidade ---")
        hum_importance = sorted(
            importance['humidity_model'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for feature, importance_val in hum_importance[:10]:  # Top 10
            logger.info(f"{feature:25s}: {importance_val:.4f}")
            
    except Exception as e:
        logger.error(f"Erro na análise de importância: {str(e)}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)