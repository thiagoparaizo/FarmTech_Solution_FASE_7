# app/ml/model_trainer.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.ml.irrigation_predictor import IrrigationPredictor
from app.services.sql_db_service import SQLDatabaseService
from datetime import datetime, timedelta
import logging

class ModelTrainer:
    """
    Classe responsável pelo treinamento automático dos modelos ML
    """
    
    def __init__(self, sql_db_service):
        self.sql_db = sql_db_service
        self.predictor = IrrigationPredictor()
        self.logger = logging.getLogger(__name__)
    
    def collect_training_data(self, days_back=30, min_samples=50):
        """
        Coleta dados de treinamento do banco de dados
        
        Args:
            days_back (int): Dias anteriores para coletar dados
            min_samples (int): Número mínimo de amostras necessárias
            
        Returns:
            list: Dados formatados para treinamento
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Buscar leituras de todos os sensores ativos
        all_data = []
        
        try:
            # Obter sensores ativos
            session = self.sql_db.get_session()
            from app.models.sensor_models import Sensor, LeituraSensor
            
            sensors = session.query(Sensor).filter_by(ativo=True).all()
            
            for sensor in sensors:
                leituras = session.query(LeituraSensor).filter(
                    LeituraSensor.sensor_id == sensor.id,
                    LeituraSensor.data_hora >= start_date,
                    LeituraSensor.data_hora <= end_date
                ).order_by(LeituraSensor.data_hora).all()
                
                # Agrupar leituras por timestamp (assumindo que cada timestamp tem múltiplas leituras)
                grouped_data = {}
                
                for leitura in leituras:
                    timestamp = int(leitura.data_hora.timestamp() * 1000)
                    
                    if timestamp not in grouped_data:
                        grouped_data[timestamp] = {
                            'timestamp': timestamp,
                            'umidade': 0,
                            'ph': 7.0,
                            'fosforo': 0,
                            'potassio': 0,
                            'irrigacao': 0
                        }
                    
                    # Mapear leituras por unidade
                    if leitura.unidade == '%':
                        grouped_data[timestamp]['umidade'] = float(leitura.valor)
                    elif leitura.unidade == 'pH':
                        grouped_data[timestamp]['ph'] = float(leitura.valor)
                    elif leitura.unidade == 'ppm':
                        try:
                            import json
                            nutrientes = json.loads(leitura.valor)
                            grouped_data[timestamp]['fosforo'] = nutrientes.get('P', 0)
                            grouped_data[timestamp]['potassio'] = nutrientes.get('K', 0)
                        except:
                            pass
                
                # Adicionar dados agrupados
                all_data.extend(list(grouped_data.values()))
            
            session.close()
            
            if len(all_data) < min_samples:
                self.logger.warning(f"Dados insuficientes: {len(all_data)} < {min_samples}")
                return []
            
            self.logger.info(f"Coletados {len(all_data)} registros para treinamento")
            return all_data
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados de treinamento: {str(e)}")
            return []
    
    def train_with_climate_data(self, days_back=30):
        """
        Treina modelos incluindo dados climáticos históricos
        """
        # Coletar dados dos sensores
        sensor_data = self.collect_training_data(days_back)
        
        if not sensor_data:
            raise ValueError("Nenhum dado de sensor disponível para treinamento")
        
        # Enriquecer com dados climáticos
        enriched_data = self.predictor.enrich_with_climate_data(sensor_data)
        
        # Treinar modelos
        return self.predictor.train_models(enriched_data)