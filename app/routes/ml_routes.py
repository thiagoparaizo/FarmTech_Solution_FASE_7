# app/routes/ml_routes.py

"""
Rotas Flask para APIs de Machine Learning
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import logging

from app.services.sql_db_service import SQLDatabaseService
from app.ml.irrigation_predictor import IrrigationPredictor
from app.ml.model_trainer import ModelTrainer
from app.services.climate_service import ClimateDataService

ml_bp = Blueprint('ml', __name__)
logger = logging.getLogger(__name__)

@ml_bp.route('/train', methods=['POST'])
def train_model():
    """
    API para treinar modelo ML
    
    POST /api/ml/train
    {
        "sensor_id": 1,
        "days_back": 30,
        "min_samples": 50,
        "location": "-3.763081,-38.524465"
    }
    """
    try:
        data = request.get_json()
        
        # Parâmetros
        sensor_id = data.get('sensor_id')
        days_back = data.get('days_back', 30)
        min_samples = data.get('min_samples', 50)
        location = data.get('location', '-3.763081,-38.524465')
        
        # Validações
        if not sensor_id:
            return jsonify({'error': 'sensor_id é obrigatório'}), 400
        
        # Inicializar serviços
        sql_db = SQLDatabaseService(current_app.config['SQL_DATABASE_URI'])
        predictor = IrrigationPredictor()
        trainer = ModelTrainer(sql_db)
        
        # Coletar dados
        training_data = trainer.collect_training_data(days_back, min_samples)
        
        if not training_data:
            return jsonify({
                'error': f'Dados insuficientes: precisa de pelo menos {min_samples} amostras'
            }), 400
        
        # Enriquecer com dados climáticos
        lat, lon = map(float, location.split(','))
        enriched_data = predictor.enrich_with_climate_data(training_data, lat, lon)
        
        # Treinar modelos
        metrics = predictor.train_models(enriched_data or training_data)
        
        # Salvar modelos
        predictor.save_models()
        
        return jsonify({
            'success': True,
            'message': 'Modelo treinado com sucesso',
            'metrics': metrics,
            'training_samples': len(enriched_data or training_data)
        })
        
    except Exception as e:
        logger.error(f"Erro no treinamento: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/predict', methods=['POST'])
def predict_irrigation():
    """
    API para predição de irrigação
    
    POST /api/ml/predict
    {
        "umidade": 25.5,
        "ph": 6.8,
        "fosforo": 1,
        "potassio": 0,
        "temperature": 28.5,
        "humidity_air": 75,
        "location": "-3.763081,-38.524465"
    }
    """
    try:
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['umidade', 'ph', 'fosforo', 'potassio']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        # Inicializar predictor
        predictor = IrrigationPredictor()
        
        # Carregar modelo
        if not predictor.load_models():
            return jsonify({'error': 'Modelo não treinado'}), 400
        
        # Preparar dados de entrada
        current_conditions = {
            'umidade': float(data['umidade']),
            'ph': float(data['ph']),
            'fosforo': int(data['fosforo']),
            'potassio': int(data['potassio']),
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
        
        # Dados climáticos (opcionais)
        current_weather = {}
        if 'temperature' in data:
            current_weather['temperature'] = float(data['temperature'])
        if 'humidity_air' in data:
            current_weather['humidity_air'] = float(data['humidity_air'])
        if 'precipitation' in data:
            current_weather['precipitation'] = float(data['precipitation'])
        
        # Se não fornecidos, buscar dados climáticos atuais
        if not current_weather and 'location' in data:
            climate_service = ClimateDataService()
            lat, lon = map(float, data['location'].split(','))
            current_weather = climate_service.get_current_weather(lat, lon)
        
        # Fazer predição
        if current_weather:
            prediction = predictor.predict_irrigation_with_weather(
                current_conditions, current_weather
            )
        else:
            prediction = predictor.predict_irrigation_need(current_conditions)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na predição: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/status', methods=['GET'])
def model_status():
    """
    API para verificar status do modelo
    
    GET /api/ml/status
    """
    try:
        predictor = IrrigationPredictor()
        
        if predictor.load_models():
            return jsonify({
                'success': True,
                'model_loaded': True,
                'metrics': predictor.model_metrics,
                'feature_importance': predictor.get_feature_importance()
            })
        else:
            return jsonify({
                'success': True,
                'model_loaded': False,
                'message': 'Modelo não treinado'
            })
            
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/retrain', methods=['POST'])
def schedule_retrain():
    """
    API para agendar retreinamento
    
    POST /api/ml/retrain
    {
        "immediate": true/false,
        "days_back": 30
    }
    """
    try:
        data = request.get_json() or {}
        immediate = data.get('immediate', False)
        
        if immediate:
            # Retreinamento imediato
            from app.scripts.train_model import main as train_main
            import threading
            
            def run_training():
                try:
                    # Executar treinamento em thread separada
                    train_main()
                except Exception as e:
                    logger.error(f"Erro no retreinamento: {str(e)}")
            
            thread = threading.Thread(target=run_training)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': 'Retreinamento iniciado em background'
            })
        else:
            # Agendar para próxima execução automática
            return jsonify({
                'success': True,
                'message': 'Retreinamento agendado para próxima execução'
            })
            
    except Exception as e:
        logger.error(f"Erro ao agendar retreinamento: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/evaluate', methods=['POST'])
def evaluate_model():
    """
    API para avaliar performance do modelo
    
    POST /api/ml/evaluate
    {
        "days_back": 7
    }
    """
    try:
        data = request.get_json() or {}
        days_back = data.get('days_back', 7)
        
        # Implementar avaliação de performance
        # (comparar predições históricas com resultados reais)
        
        return jsonify({
            'success': True,
            'message': 'Funcionalidade em desenvolvimento',
            'evaluation_period': f'{days_back} dias'
        })
        
    except Exception as e:
        logger.error(f"Erro na avaliação: {str(e)}")
        return jsonify({'error': str(e)}), 500