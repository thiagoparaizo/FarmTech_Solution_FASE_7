# app/scripts/evaluate_model.py

"""
Script para avaliação contínua dos modelos ML
Monitora performance e sugere retreinamento quando necessário
"""

import json
import sys
import os
import logging
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, BASE_DIR)

from config import Config
from app.services.sql_db_service import SQLDatabaseService
from app.ml.irrigation_predictor import IrrigationPredictor

def evaluate_model_drift():
    """
    Avalia drift do modelo comparando predições com resultados reais
    IMPLEMENTAÇÃO COMPLETA da função que estava pendente
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Carregar modelo existente
        predictor = IrrigationPredictor()
        if not predictor.load_models():
            logger.error("Modelo não encontrado")
            return False
        
        # Conectar ao banco
        sql_db = SQLDatabaseService(Config.SQL_DATABASE_URI)
        session = sql_db.get_session()
        
        # Buscar predições e resultados reais dos últimos 7 dias
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        try:
            # Query para buscar predições históricas vs resultados reais
            from sqlalchemy import text
            
            query = text("""
                SELECT 
                    p.predicted_irrigation,
                    p.irrigation_probability,
                    p.confidence,
                    p.actual_irrigation,
                    p.prediction_time,
                    s.tipo as sensor_tipo
                FROM ml_predictions p
                JOIN sensor s ON p.sensor_id = s.id
                WHERE p.prediction_time >= :start_date 
                    AND p.prediction_time <= :end_date
                    AND p.actual_irrigation IS NOT NULL
                ORDER BY p.prediction_time
            """)
            
            result = session.execute(query, {
                'start_date': start_date,
                'end_date': end_date
            })
            
            predictions_data = result.fetchall()
            
            if not predictions_data:
                logger.warning("Nenhuma predição histórica encontrada para avaliação")
                return False
            
            # Calcular métricas de drift
            correct_predictions = 0
            total_predictions = len(predictions_data)
            
            true_positives = 0
            false_positives = 0
            true_negatives = 0
            false_negatives = 0
            
            probability_errors = []
            
            for row in predictions_data:
                predicted = bool(row.predicted_irrigation)
                actual = bool(row.actual_irrigation)
                probability = float(row.irrigation_probability)
                
                # Accuracy
                if predicted == actual:
                    correct_predictions += 1
                
                # Confusion matrix
                if predicted and actual:
                    true_positives += 1
                elif predicted and not actual:
                    false_positives += 1
                elif not predicted and actual:
                    false_negatives += 1
                else:
                    true_negatives += 1
                
                # Probability calibration
                expected_prob = 1.0 if actual else 0.0
                probability_errors.append(abs(probability - expected_prob))
            
            # Calcular métricas finais
            accuracy = correct_predictions / total_predictions
            
            # Precision, Recall, F1
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Calibração de probabilidade (Brier Score)
            brier_score = sum(probability_errors) / len(probability_errors) if probability_errors else 1.0
            
            # Limiares para detecção de drift
            accuracy_threshold = 0.75  # Mínimo aceitável
            brier_threshold = 0.25     # Máximo aceitável para Brier Score
            
            # Avaliação de drift
            drift_detected = False
            drift_reasons = []
            
            if accuracy < accuracy_threshold:
                drift_detected = True
                drift_reasons.append(f"Acurácia baixa: {accuracy:.3f} < {accuracy_threshold}")
            
            if brier_score > brier_threshold:
                drift_detected = True
                drift_reasons.append(f"Calibração pobre: {brier_score:.3f} > {brier_threshold}")
            
            if f1_score < 0.7:
                drift_detected = True
                drift_reasons.append(f"F1-Score baixo: {f1_score:.3f}")
            
            # Log dos resultados
            logger.info("=== AVALIAÇÃO DE DRIFT DO MODELO ===")
            logger.info(f"Período: {start_date.date()} a {end_date.date()}")
            logger.info(f"Total de predições avaliadas: {total_predictions}")
            logger.info(f"Acurácia: {accuracy:.3f}")
            logger.info(f"Precisão: {precision:.3f}")
            logger.info(f"Recall: {recall:.3f}")
            logger.info(f"F1-Score: {f1_score:.3f}")
            logger.info(f"Brier Score: {brier_score:.3f}")
            
            if drift_detected:
                logger.warning("🚨 DRIFT DETECTADO!")
                for reason in drift_reasons:
                    logger.warning(f"  - {reason}")
                logger.warning("Recomendação: Executar retreinamento do modelo")
            else:
                logger.info("✅ Modelo estável - sem drift detectado")
            
            # Salvar resultados da avaliação
            drift_evaluation = {
                'evaluation_date': datetime.now().isoformat(),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_predictions': total_predictions,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'brier_score': brier_score,
                'drift_detected': drift_detected,
                'drift_reasons': drift_reasons,
                'confusion_matrix': {
                    'true_positives': true_positives,
                    'false_positives': false_positives,
                    'true_negatives': true_negatives,
                    'false_negatives': false_negatives
                }
            }
            
            # Salvar em arquivo de log de avaliações
            import json
            os.makedirs('logs', exist_ok=True)
            with open('logs/model_drift_evaluation.json', 'w') as f:
                json.dump(drift_evaluation, f, indent=2)
            
            return not drift_detected  # True se modelo está OK
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Erro na avaliação de drift: {str(e)}")
        return False

def scheduled_retraining():
    """
    Retreinamento automático agendado baseado em avaliação de drift
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Primeiro, avaliar se há drift
        model_is_stable = evaluate_model_drift()
        
        # Verificar outros critérios para retreinamento
        predictor = IrrigationPredictor()
        needs_retraining = False
        reasons = []
        
        if not model_is_stable:
            needs_retraining = True
            reasons.append("Drift detectado no modelo")
        
        if not predictor.load_models():
            needs_retraining = True
            reasons.append("Modelo não encontrado")
        else:
            # Verificar idade do modelo
            last_trained = predictor.model_metrics.get('last_trained')
            if last_trained:
                last_trained_date = datetime.fromisoformat(last_trained)
                days_old = (datetime.now() - last_trained_date).days
                
                if days_old > 7:
                    needs_retraining = True
                    reasons.append(f"Modelo antigo ({days_old} dias)")
            
            # Verificar se há dados novos suficientes
            sql_db = SQLDatabaseService(Config.SQL_DATABASE_URI)
            from app.ml.model_trainer import ModelTrainer
            trainer = ModelTrainer(sql_db)
            
            recent_data = trainer.collect_training_data(days_back=3, min_samples=10)
            if len(recent_data) > 20:  # Se há dados novos suficientes
                needs_retraining = True
                reasons.append(f"Novos dados disponíveis ({len(recent_data)} amostras)")
        
        if needs_retraining:
            logger.info(f"Retreinamento necessário: {', '.join(reasons)}")
            logger.info("Iniciando retreinamento automático...")
            
            # Executar script de treinamento
            import subprocess
            result = subprocess.run([
                sys.executable, 
                os.path.join(BASE_DIR, 'app/scripts/train_model.py'),
                '--days', '30',
                '--min-samples', '50'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Retreinamento automático concluído com sucesso")
                
                # Re-avaliar após retreinamento
                logger.info("Executando nova avaliação pós-retreinamento...")
                model_is_stable = evaluate_model_drift()
                
                if model_is_stable:
                    logger.info("✅ Modelo retreinado está estável")
                else:
                    logger.warning("⚠️ Modelo retreinado ainda apresenta problemas")
                
                return True
            else:
                logger.error(f"❌ Erro no retreinamento: {result.stderr}")
                return False
        else:
            logger.info("✅ Retreinamento não necessário - modelo estável")
            return True
            
    except Exception as e:
        logger.error(f"Erro no retreinamento agendado: {str(e)}")
        return False

def create_drift_monitoring_report():
    """
    Cria relatório completo de monitoramento de drift
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Carregar histórico de avaliações
        drift_history = []
        try:
            with open('logs/model_drift_evaluation.json', 'r') as f:
                latest_evaluation = json.load(f)
                drift_history.append(latest_evaluation)
        except:
            pass
        
        # Executar nova avaliação
        current_stable = evaluate_model_drift()
        
        # Criar relatório
        report = {
            'report_date': datetime.now().isoformat(),
            'current_model_status': 'stable' if current_stable else 'drift_detected',
            'evaluation_history': drift_history,
            'recommendations': []
        }
        
        if not current_stable:
            report['recommendations'].extend([
                "Executar retreinamento imediato",
                "Investigar causas do drift",
                "Aumentar frequência de monitoramento"
            ])
        
        # Salvar relatório
        with open('logs/drift_monitoring_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Relatório de drift gerado em: logs/drift_monitoring_report.json")
        return report
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return None

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Executar avaliação completa
    logger = logging.getLogger(__name__)
    logger.info("=== INICIANDO AVALIAÇÃO DE DRIFT ===")
    
    # Avaliar drift
    stable = evaluate_model_drift()
    
    # Executar retreinamento se necessário
    if not stable:
        logger.info("Executando retreinamento automático...")
        scheduled_retraining()
    
    # Gerar relatório
    create_drift_monitoring_report()
    
    logger.info("=== AVALIAÇÃO CONCLUÍDA ===")