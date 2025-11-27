# app/ml/irrigation_predictor.py

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, mean_absolute_error, classification_report
import joblib
import json
from datetime import datetime, timedelta
import logging

class IrrigationPredictor:
    """
    CLASSE CONSOLIDADA - Inclui todas as funcionalidades:
    - Predição de irrigação
    - Processamento de dados
    - Serviços de predição
    - Integração climática
    
    Esta classe elimina a necessidade de:
    - data_preprocessor.py (funcionalidades integradas)
    - prediction_service.py (métodos incluídos aqui)
    """
    
    def __init__(self):
        # Modelos MENOS complexos para evitar overfitting
        self.irrigation_classifier = RandomForestClassifier(
            n_estimators=50,      # Reduzido de 100
            random_state=42,
            max_depth=5,          # Reduzido de 10  
            min_samples_split=10, # NOVO: Mínimo para split
            min_samples_leaf=5,   # NOVO: Mínimo por folha
            max_features='sqrt'   # NOVO: Reduzir features por árvore
        )
        self.humidity_regressor = RandomForestRegressor(
            n_estimators=50,      # Reduzido de 100
            random_state=42,
            max_depth=5,          # Reduzido de 10
            min_samples_split=10, # NOVO: Mínimo para split
            min_samples_leaf=5,   # NOVO: Mínimo por folha
            max_features='sqrt'   # NOVO: Reduzir features por árvore
        )
        
        # Preprocessadores consolidados
        self.scaler = StandardScaler()
        self.feature_columns = []
        
        # Métricas do modelo
        self.model_metrics = {
            'irrigation_accuracy': 0.0,
            'humidity_mae': 0.0,
            'last_trained': None,
            'training_samples': 0
        }
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    # ========== DATA PREPROCESSING (substituindo data_preprocessor.py) ==========
    
    def preprocess_sensor_data(self, raw_data):
        """
        Preprocessa dados brutos dos sensores
        SUBSTITUI: data_preprocessor.py
        """
        try:
            if not raw_data:
                return None
            
            # Converter para DataFrame se necessário
            if isinstance(raw_data, list):
                df = pd.DataFrame(raw_data)
            else:
                df = raw_data.copy()
            
            # Limpeza básica
            df = df.dropna(subset=['umidade', 'ph'])
            df = df[df['umidade'].between(0, 100)]
            df = df[df['ph'].between(0, 14)]
            
            # Conversões de tipo
            df['fosforo'] = df['fosforo'].astype(int)
            df['potassio'] = df['potassio'].astype(int)
            df['irrigacao'] = df['irrigacao'].astype(int)
            
            # Ordenar por timestamp
            df = df.sort_values('timestamp')
            
            # Remover duplicatas
            df = df.drop_duplicates(subset=['timestamp'], keep='last')
            
            self.logger.info(f"Dados preprocessados: {len(df)} registros limpos")
            return df
            
        except Exception as e:
            self.logger.error(f"Erro no preprocessamento: {str(e)}")
            return None
    
    def engineer_features(self, data):
        """
        Engenharia de features avançada
        SUBSTITUI: funcionalidades do data_preprocessor.py
        """
        features = pd.DataFrame()
        
        # Features básicas dos sensores
        features['umidade_atual'] = data['umidade']
        features['ph_atual'] = data['ph']
        features['fosforo'] = data['fosforo'].astype(int)
        features['potassio'] = data['potassio'].astype(int)
        
        # Features climáticas (se disponíveis)
        climate_features = ['temperature', 'humidity_air', 'precipitation', 'wind_speed', 'pressure']
        for feat in climate_features:
            features[feat] = data.get(feat, 0)
        
        # Features temporais
        data['datetime'] = pd.to_datetime(data['timestamp'], unit='ms')
        features['hora_do_dia'] = data['datetime'].dt.hour
        features['dia_da_semana'] = data['datetime'].dt.dayofweek
        features['mes_ano'] = data['datetime'].dt.month
        
        # Features de tendência (rolling)
        features['umidade_tendencia'] = data['umidade'].rolling(window=3, min_periods=1).mean()
        features['ph_tendencia'] = data['ph'].rolling(window=3, min_periods=1).mean()
        features['umidade_variacao'] = data['umidade'].rolling(window=3, min_periods=1).std().fillna(0)
        
        # Features derivadas climáticas
        if 'temperature' in data.columns:
            features['estresse_termico'] = (features['temperature'] > 30).astype(int)
            features['temp_tendencia'] = data['temperature'].rolling(window=3, min_periods=1).mean()
        
        if 'precipitation' in data.columns:
            features['chuva_recente'] = (features['precipitation'] > 0).astype(int)
            features['precipitacao_acumulada'] = data['precipitation'].rolling(window=6, min_periods=1).sum()
        
        # Features categóricas
        features['periodo_dia'] = features['hora_do_dia'].apply(self._get_periodo_dia)
        features['estacao'] = features['mes_ano'].apply(self._get_estacao)
        features['necessidade_nutrientes'] = (features['fosforo'] + features['potassio']).apply(
            lambda x: 'alta' if x >= 2 else 'media' if x == 1 else 'baixa'
        )
        features['ph_categoria'] = features['ph_atual'].apply(self._categorize_ph)
        
        # Codificação de categóricas
        le_periodo = LabelEncoder()
        le_estacao = LabelEncoder()
        le_nutrientes = LabelEncoder()
        le_ph = LabelEncoder()
        
        features['periodo_dia_encoded'] = le_periodo.fit_transform(features['periodo_dia'])
        features['estacao_encoded'] = le_estacao.fit_transform(features['estacao'])
        features['necessidade_nutrientes_encoded'] = le_nutrientes.fit_transform(features['necessidade_nutrientes'])
        features['ph_categoria_encoded'] = le_ph.fit_transform(features['ph_categoria'])
        
        # Remover categóricas originais
        features = features.drop(['periodo_dia', 'estacao', 'necessidade_nutrientes', 'ph_categoria'], axis=1)
        
        return features.fillna(0)
    
    # ========== PREDICTION SERVICES (substituindo prediction_service.py) ==========
    
    def predict_irrigation_batch(self, conditions_list):
        """
        Predições em lote
        SUBSTITUI: prediction_service.py
        """
        predictions = []
        
        for conditions in conditions_list:
            try:
                pred = self.predict_irrigation_need(conditions)
                predictions.append(pred)
            except Exception as e:
                self.logger.error(f"Erro na predição: {str(e)}")
                predictions.append({'error': str(e), 'irrigation_needed': False})
        
        return predictions
    
    def predict_with_confidence_intervals(self, current_conditions, n_estimators=100):
        """
        Predições com intervalos de confiança
        SUBSTITUI: funcionalidades avançadas do prediction_service.py
        """
        try:
            # Preparar dados
            current_df = pd.DataFrame([current_conditions])
            features = self.engineer_features(current_df)
            
            if len(features.columns) != len(self.feature_columns):
                features = features.reindex(columns=self.feature_columns, fill_value=0)
            
            features_scaled = self.scaler.transform(features)
            
            # Predições de todos os estimadores
            tree_predictions = []
            for estimator in self.irrigation_classifier.estimators_:
                pred = estimator.predict_proba(features_scaled)[0][1]
                tree_predictions.append(pred)
            
            # Calcular estatísticas
            mean_pred = np.mean(tree_predictions)
            std_pred = np.std(tree_predictions)
            
            # Intervalos de confiança (95%)
            ci_lower = max(0, mean_pred - 1.96 * std_pred)
            ci_upper = min(1, mean_pred + 1.96 * std_pred)
            
            return {
                'irrigation_probability': float(mean_pred),
                'confidence_interval': {
                    'lower': float(ci_lower),
                    'upper': float(ci_upper)
                },
                'prediction_std': float(std_pred),
                'irrigation_needed': mean_pred > 0.5
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição com IC: {str(e)}")
            return {'error': str(e)}
    
    def store_prediction_result(self, prediction, actual_result, sql_db_service, sensor_id):
        """
        Armazena resultado da predição para avaliação futura
        SUBSTITUI: funcionalidades do prediction_service.py
        """
        try:
            session = sql_db_service.get_session()
            
            # Importar modelo da tabela de predições
            from app.models.sensor_models import Base
            from sqlalchemy import Column, Integer, Boolean, Float, DateTime, ForeignKey
            
            class MLPrediction(Base):
                __tablename__ = 'ml_predictions'
                
                id = Column(Integer, primary_key=True)
                sensor_id = Column(Integer, ForeignKey('sensor.id'), nullable=False)
                predicted_irrigation = Column(Boolean, nullable=False)
                irrigation_probability = Column(Float)
                confidence = Column(Float)
                actual_irrigation = Column(Boolean)
                prediction_time = Column(DateTime, default=datetime.now)
                horizon_hours = Column(Integer, default=4)
            
            # Criar registro
            ml_pred = MLPrediction(
                sensor_id=sensor_id,
                predicted_irrigation=prediction.get('irrigation_needed', False),
                irrigation_probability=prediction.get('irrigation_probability', 0.0),
                confidence=prediction.get('confidence', 0.0),
                actual_irrigation=actual_result,
                prediction_time=datetime.now()
            )
            
            session.add(ml_pred)
            session.commit()
            session.close()
            
            self.logger.info("Resultado da predição armazenado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar resultado: {str(e)}")
            return False
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _get_periodo_dia(self, hora):
        """Categoriza hora do dia em períodos"""
        if 5 <= hora < 12:
            return 'manha'
        elif 12 <= hora < 18:
            return 'tarde'
        elif 18 <= hora < 22:
            return 'noite'
        else:
            return 'madrugada'
    
    def _get_estacao(self, mes):
        """Determina estação do ano (Hemisfério Sul)"""
        if mes in [12, 1, 2]:
            return 'verao'
        elif mes in [3, 4, 5]:
            return 'outono'
        elif mes in [6, 7, 8]:
            return 'inverno'
        else:
            return 'primavera'
    
    def _categorize_ph(self, ph):
        """Categoriza valores de pH"""
        if ph < 6.0:
            return 'acido'
        elif 6.0 <= ph <= 7.5:
            return 'ideal'
        else:
            return 'alcalino'
    
    # ========== MÉTODOS PRINCIPAIS (mantidos da implementação anterior) ==========
    
    def enrich_with_climate_data(self, sensor_data, lat=-3.763081, lon=-38.524465):
        """
        Enriquece dados dos sensores com informações climáticas históricas
        """
        from app.services.climate_service import ClimateDataService
        
        climate_service = ClimateDataService()
        
        if not sensor_data:
            return []
        
        # Determinar período dos dados
        timestamps = [d['timestamp'] for d in sensor_data]
        start_date = datetime.fromtimestamp(min(timestamps) / 1000)
        end_date = datetime.fromtimestamp(max(timestamps) / 1000)
        
        self.logger.info(f"Buscando dados climáticos de {start_date} a {end_date}")
        
        # Obter dados climáticos históricos
        climate_data = climate_service.get_historical_weather(lat, lon, start_date, end_date)
        
        if not climate_data:
            self.logger.warning("Não foi possível obter dados climáticos, usando dados apenas dos sensores")
            return sensor_data
        
        # Criar índice por timestamp para busca rápida
        climate_index = {c['timestamp']: c for c in climate_data}
        
        enriched_data = []
        
        for sensor_point in sensor_data:
            enriched_point = sensor_point.copy()
            
            # Encontrar dados climáticos mais próximos (tolerância de 1 hora = 3600000 ms)
            sensor_timestamp = sensor_point['timestamp']
            closest_climate = None
            min_diff = float('inf')
            
            for climate_timestamp, climate_point in climate_index.items():
                diff = abs(climate_timestamp - sensor_timestamp)
                if diff < min_diff and diff <= 3600000:  # 1 hora de tolerância
                    min_diff = diff
                    closest_climate = climate_point
            
            # Adicionar dados climáticos se encontrados
            if closest_climate:
                enriched_point.update({
                    'temperature': closest_climate.get('temperature', 25.0),
                    'humidity_air': closest_climate.get('humidity_air', 70.0),
                    'precipitation': closest_climate.get('precipitation', 0.0),
                    'wind_speed': closest_climate.get('wind_speed', 0.0),
                    'pressure': closest_climate.get('pressure', 1013.0),
                    'soil_temperature': closest_climate.get('soil_temperature', 25.0),
                    'soil_moisture_ref': closest_climate.get('soil_moisture_ref', 50.0)
                })
            else:
                # Usar valores padrão se não houver dados climáticos
                enriched_point.update({
                    'temperature': 25.0,
                    'humidity_air': 70.0,
                    'precipitation': 0.0,
                    'wind_speed': 0.0,
                    'pressure': 1013.0,
                    'soil_temperature': 25.0,
                    'soil_moisture_ref': 50.0
                })
            
            enriched_data.append(enriched_point)
        
        self.logger.info(f"Dados enriquecidos: {len(enriched_data)} pontos com informações climáticas")
        return enriched_data
    
    def prepare_training_data(self, sensor_data):
        """
        Prepara dados para treinamento dos modelos
        """
        # Preprocessar dados
        df = self.preprocess_sensor_data(sensor_data)
        if df is None:
            raise ValueError("Falha no preprocessamento dos dados")
        
        if len(df) < 10:
            raise ValueError("Dados insuficientes para treinamento (mínimo 10 amostras)")
        
        # Extrair features
        X = self.engineer_features(df)
        
        # Targets
        y_irrigation = df['irrigacao'].astype(int)
        y_humidity = df['umidade'].astype(float)
        
        self.feature_columns = X.columns.tolist()
        
        return X, y_irrigation, y_humidity
    
    def train_models(self, sensor_data):
        """
        Treina os modelos de ML com dados históricos
        """
        try:
            self.logger.info("Iniciando treinamento dos modelos ML...")
            
            # Preparar dados
            X, y_irrigation, y_humidity = self.prepare_training_data(sensor_data)
            
            # VERIFICAÇÃO CRÍTICA: Verificar distribuição das classes
            unique_classes = np.unique(y_irrigation)
            class_counts = pd.Series(y_irrigation).value_counts()
            
            self.logger.info(f"Classes encontradas: {unique_classes}")
            self.logger.info(f"Distribuição: {class_counts.to_dict()}")
            
            # Se há apenas uma classe, criar dados balanceados artificialmente
            if len(unique_classes) < 2:
                self.logger.warning("⚠️ APENAS UMA CLASSE DETECTADA - Criando dados balanceados")
                X, y_irrigation, y_humidity = self._create_balanced_data(X, y_irrigation, y_humidity)
                unique_classes = np.unique(y_irrigation)
                class_counts = pd.Series(y_irrigation).value_counts()
                self.logger.info(f"Após balanceamento - Classes: {unique_classes}")
                self.logger.info(f"Após balanceamento - Distribuição: {class_counts.to_dict()}")
            
            # Verificar se ainda temos classes insuficientes
            if len(unique_classes) < 2:
                raise ValueError("Impossível treinar modelo de classificação com apenas uma classe")
            
            # Balanceamento de classes se muito desbalanceado
            min_class_size = class_counts.min()
            max_class_size = class_counts.max()
            
            if max_class_size / min_class_size > 5:  # Muito desbalanceado
                self.logger.warning(f"⚠️ Classes desbalanceadas: {max_class_size}/{min_class_size}")
                # Usar class_weight='balanced' no modelo
                self.irrigation_classifier.set_params(class_weight='balanced')
            
            # Normalizar features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split para treino e teste com estratificação
            X_train, X_test, y_irr_train, y_irr_test, y_hum_train, y_hum_test = train_test_split(
                X_scaled, y_irrigation, y_humidity, 
                test_size=0.3, 
                random_state=42,
                stratify=y_irrigation  # Manter distribuição das classes
            )
            
            # Treinar modelo de classificação (irrigação)
            self.irrigation_classifier.fit(X_train, y_irr_train)
            irr_pred = self.irrigation_classifier.predict(X_test)
            irrigation_accuracy = accuracy_score(y_irr_test, irr_pred)
            
            # Verificar se modelo aprendeu múltiplas classes
            predicted_classes = np.unique(irr_pred)
            self.logger.info(f"Classes preditas pelo modelo: {predicted_classes}")
            
            # Treinar modelo de regressão (umidade)
            self.humidity_regressor.fit(X_train, y_hum_train)
            hum_pred = self.humidity_regressor.predict(X_test)
            humidity_mae = mean_absolute_error(y_hum_test, hum_pred)
            
            # Validação cruzada estratificada
            cv_irrigation = cross_val_score(
                self.irrigation_classifier, X_scaled, y_irrigation, 
                cv=min(5, min_class_size), # Ajustar CV se classes pequenas
                scoring='accuracy'
            )
            cv_humidity = cross_val_score(
                self.humidity_regressor, X_scaled, y_humidity, 
                cv=5, scoring='neg_mean_absolute_error'
            )
            
            # Atualizar métricas
            self.model_metrics = {
                'irrigation_accuracy': irrigation_accuracy,
                'irrigation_cv_mean': cv_irrigation.mean(),
                'irrigation_cv_std': cv_irrigation.std(),
                'humidity_mae': humidity_mae,
                'humidity_cv_mean': -cv_humidity.mean(),
                'humidity_cv_std': cv_humidity.std(),
                'last_trained': datetime.now().isoformat(),
                'training_samples': len(X),
                'class_distribution': class_counts.to_dict(),
                'predicted_classes': predicted_classes.tolist(),
                'feature_importance_irrigation': dict(zip(self.feature_columns, self.irrigation_classifier.feature_importances_)),
                'feature_importance_humidity': dict(zip(self.feature_columns, self.humidity_regressor.feature_importances_))
            }
            
            self.logger.info(f"Modelos treinados com sucesso!")
            self.logger.info(f"Acurácia Irrigação: {irrigation_accuracy:.3f}")
            self.logger.info(f"MAE Umidade: {humidity_mae:.3f}")
            self.logger.info(f"Classes no modelo: {len(predicted_classes)}")
            
            return self.model_metrics
            
        except Exception as e:
            self.logger.error(f"Erro durante treinamento: {str(e)}")
            raise
    
    def _create_balanced_data(self, X, y_irrigation, y_humidity):
        """Cria dados balanceados artificialmente quando há apenas uma classe"""
        
        # Duplicar dados existentes e modificar para criar a classe oposta
        X_new = X.copy()
        y_irr_new = y_irrigation.copy()
        y_hum_new = y_humidity.copy()
        
        # Identificar a classe existente
        existing_class = y_irrigation.iloc[0] if len(y_irrigation) > 0 else 0
        opposite_class = 1 - existing_class
        
        # Tomar 30% dos dados e modificá-los para criar a classe oposta
        n_samples = len(X)
        n_opposite = max(10, n_samples // 3)  # Pelo menos 10 amostras
        
        indices = np.random.choice(n_samples, n_opposite, replace=True)
        
        # Modificar features para criar comportamento da classe oposta
        for i in indices:
            # Modificar umidade de forma oposta
            if existing_class == 1:  # Se classe existente irriga
                # Criar casos que NÃO devem irrigar (umidade alta)
                X_new.iloc[i, X_new.columns.get_loc('umidade_atual')] = np.random.uniform(70, 95)
            else:  # Se classe existente não irriga
                # Criar casos que DEVEM irrigar (umidade baixa + pH ideal)
                X_new.iloc[i, X_new.columns.get_loc('umidade_atual')] = np.random.uniform(10, 25)
                if 'ph_atual' in X_new.columns:
                    X_new.iloc[i, X_new.columns.get_loc('ph_atual')] = np.random.uniform(6.0, 7.5)
            
            # Atribuir classe oposta
            y_irr_new.iloc[i] = opposite_class
        
        return X_new, y_irr_new, y_hum_new
    
    def predict_irrigation_need(self, current_conditions, horizon_hours=4):
        """
        Prediz necessidade de irrigação para as próximas horas
        """
        try:
            # Preparar dados atuais
            current_df = pd.DataFrame([current_conditions])
            features = self.engineer_features(current_df)
            
            if len(features.columns) != len(self.feature_columns):
                features = features.reindex(columns=self.feature_columns, fill_value=0)
            
            features_scaled = self.scaler.transform(features)
            
            # Predições
            irrigation_prob = self.irrigation_classifier.predict_proba(features_scaled)[0]
            irrigation_need = self.irrigation_classifier.predict(features_scaled)[0]
            humidity_forecast = self.humidity_regressor.predict(features_scaled)[0]
            
            # Análise de tendência
            trend_analysis = self._analyze_trend(current_conditions)
            
            # Recomendações inteligentes
            recommendations = self._generate_recommendations(
                current_conditions, irrigation_need, humidity_forecast, trend_analysis
            )
            
            result = {
                'irrigation_needed': bool(irrigation_need),
                'irrigation_probability': float(irrigation_prob[1]),
                'confidence': float(max(irrigation_prob)),
                'predicted_humidity_next_hour': float(humidity_forecast),
                'current_humidity': float(current_conditions.get('umidade', 0)),
                'trend_analysis': trend_analysis,
                'recommendations': recommendations,
                'prediction_time': datetime.now().isoformat(),
                'horizon_hours': horizon_hours
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na predição: {str(e)}")
            return {
                'error': str(e),
                'irrigation_needed': False,
                'irrigation_probability': 0.0,
                'confidence': 0.0
            }
    
    def predict_irrigation_with_weather(self, current_conditions, current_weather, forecast_data=None):
        """
        Predição avançada considerando condições climáticas atuais e previsão
        """
        # Combinar dados dos sensores com clima atual
        combined_conditions = {**current_conditions, **current_weather}
        
        # Predição base
        base_prediction = self.predict_irrigation_need(combined_conditions)
        
        # Ajustar predição com base na previsão do tempo
        if forecast_data:
            # Verificar se há previsão de chuva nas próximas 6 horas
            rain_forecast = any(f.get('precipitation', 0) > 2 for f in forecast_data[:2])
            
            if rain_forecast and base_prediction['irrigation_needed']:
                base_prediction['irrigation_needed'] = False
                base_prediction['irrigation_probability'] *= 0.3
                base_prediction['recommendations'].insert(0, "🌧️ Chuva prevista - adiar irrigação")
            
            # Considerar temperatura futura
            future_temp = [f.get('temperature', 25) for f in forecast_data[:4]]
            if future_temp and max(future_temp) > 35:
                base_prediction['recommendations'].insert(0, "🔥 Temperatura alta prevista - considerar irrigação preventiva")
        
        return base_prediction
    
    def _analyze_trend(self, conditions):
        """Analisa tendências dos dados atuais"""
        umidade = conditions.get('umidade', 50)
        ph = conditions.get('ph', 7)
        
        return {
            'humidity_status': 'low' if umidade < 30 else 'high' if umidade > 70 else 'normal',
            'ph_status': 'acidic' if ph < 6 else 'alkaline' if ph > 7.5 else 'ideal',
            'nutrient_status': 'sufficient' if conditions.get('fosforo', 0) and conditions.get('potassio', 0) else 'deficient'
        }
    
    def _generate_recommendations(self, conditions, irrigation_need, humidity_forecast, trend):
        """Gera recomendações baseadas nas predições"""
        recommendations = []
        
        # Recomendações de irrigação
        if irrigation_need:
            if trend['ph_status'] == 'ideal':
                recommendations.append("✅ Irrigação recomendada - pH ideal para absorção")
            else:
                recommendations.append("⚠️ Irrigação necessária, mas ajustar pH primeiro")
        else:
            recommendations.append("❌ Irrigação não necessária no momento")
        
        # Recomendações de pH
        if trend['ph_status'] == 'acidic':
            recommendations.append("🧪 Aplicar calcário para corrigir acidez")
        elif trend['ph_status'] == 'alkaline':
            recommendations.append("🧪 Aplicar matéria orgânica para reduzir pH")
        
        # Recomendações de nutrientes
        if trend['nutrient_status'] == 'deficient':
            if not conditions.get('fosforo', 0):
                recommendations.append("🌱 Aplicar fertilizante rico em fósforo")
            if not conditions.get('potassio', 0):
                recommendations.append("🌱 Aplicar fertilizante rico em potássio")
        
        # Recomendações de timing
        hour = datetime.now().hour
        if 6 <= hour <= 10:
            recommendations.append("🌅 Período ideal para irrigação (manhã)")
        elif 16 <= hour <= 18:
            recommendations.append("🌇 Período adequado para irrigação (final da tarde)")
        elif 11 <= hour <= 15:
            recommendations.append("☀️ Evitar irrigação - período muito quente")
        
        return recommendations
    
    def get_feature_importance(self):
        """Retorna importância das features dos modelos"""
        if not hasattr(self.irrigation_classifier, 'feature_importances_'):
            return None
            
        return {
            'irrigation_model': dict(zip(self.feature_columns, self.irrigation_classifier.feature_importances_)),
            'humidity_model': dict(zip(self.feature_columns, self.humidity_regressor.feature_importances_))
        }
    
    def save_models(self, path_prefix='models/farmtech'):
        """Salva os modelos treinados"""
        try:
            import os
            os.makedirs(os.path.dirname(path_prefix), exist_ok=True)
            
            joblib.dump(self.irrigation_classifier, f"{path_prefix}_irrigation.pkl")
            joblib.dump(self.humidity_regressor, f"{path_prefix}_humidity.pkl")
            joblib.dump(self.scaler, f"{path_prefix}_scaler.pkl")
            
            # Salvar metadados
            with open(f"{path_prefix}_metadata.json", 'w') as f:
                json.dump({
                    'feature_columns': self.feature_columns,
                    'metrics': self.model_metrics
                }, f, indent=2)
            
            self.logger.info(f"Modelos salvos em {path_prefix}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelos: {str(e)}")
            return False
    
    def load_models(self, path_prefix='models/farmtech'):
        """Carrega modelos salvos"""
        try:
            self.irrigation_classifier = joblib.load(f"{path_prefix}_irrigation.pkl")
            self.humidity_regressor = joblib.load(f"{path_prefix}_humidity.pkl")
            self.scaler = joblib.load(f"{path_prefix}_scaler.pkl")
            
            # Carregar metadados
            with open(f"{path_prefix}_metadata.json", 'r') as f:
                metadata = json.load(f)
                self.feature_columns = metadata['feature_columns']
                self.model_metrics = metadata['metrics']
            
            self.logger.info(f"Modelos carregados de {path_prefix}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelos: {str(e)}")
            return False