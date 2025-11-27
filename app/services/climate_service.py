# app/services/climate_service.py

import requests
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import os

class ClimateDataService:
    """
    Serviço para integração com APIs climáticas para dados históricos e atuais
    Suporta OpenWeatherMap (já usado) e Open-Meteo (gratuito para histórico)
    """
    
    def __init__(self, openweather_api_key=None):
        self.openweather_api_key = openweather_api_key or os.getenv('OPENWEATHER_API_KEY')
        self.open_meteo_base_url = "https://archive-api.open-meteo.com/v1/archive"
        self.openweather_base_url = "https://api.openweathermap.org/data/2.5"
        self.logger = logging.getLogger(__name__)
        
        # Cache para evitar requisições desnecessárias
        self._cache = {}
    
    def get_historical_weather(self, lat: float, lon: float, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Obtém dados climáticos históricos usando Open-Meteo API (gratuita)
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de dados climáticos por data
        """
        try:
            # Cache key
            cache_key = f"historical_{lat}_{lon}_{start_date.date()}_{end_date.date()}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Parâmetros para Open-Meteo
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "hourly": [
                    "temperature_2m",
                    "relativehumidity_2m", 
                    "precipitation",
                    "windspeed_10m",
                    "pressure_msl",
                    "soil_temperature_0cm",
                    "soil_moisture_0_1cm"
                ],
                "timezone": "America/Sao_Paulo"  # Ajustar conforme localização
            }
            
            response = requests.get(self.open_meteo_base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Processar dados
            historical_data = []
            hourly = data.get('hourly', {})
            times = hourly.get('time', [])
            
            for i, time_str in enumerate(times):
                timestamp = datetime.fromisoformat(time_str.replace('T', ' '))
                
                weather_point = {
                    'timestamp': int(timestamp.timestamp() * 1000),
                    'datetime': timestamp,
                    'temperature': hourly.get('temperature_2m', [])[i] if i < len(hourly.get('temperature_2m', [])) else None,
                    'humidity_air': hourly.get('relativehumidity_2m', [])[i] if i < len(hourly.get('relativehumidity_2m', [])) else None,
                    'precipitation': hourly.get('precipitation', [])[i] if i < len(hourly.get('precipitation', [])) else None,
                    'wind_speed': hourly.get('windspeed_10m', [])[i] if i < len(hourly.get('windspeed_10m', [])) else None,
                    'pressure': hourly.get('pressure_msl', [])[i] if i < len(hourly.get('pressure_msl', [])) else None,
                    'soil_temperature': hourly.get('soil_temperature_0cm', [])[i] if i < len(hourly.get('soil_temperature_0cm', [])) else None,
                    'soil_moisture_ref': hourly.get('soil_moisture_0_1cm', [])[i] if i < len(hourly.get('soil_moisture_0_1cm', [])) else None
                }
                
                # Filtrar valores None
                weather_point = {k: v for k, v in weather_point.items() if v is not None}
                historical_data.append(weather_point)
            
            # Cache por 1 hora
            self._cache[cache_key] = historical_data
            
            self.logger.info(f"Coletados {len(historical_data)} pontos climáticos históricos")
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados históricos: {str(e)}")
            return []
    
    def get_current_weather(self, lat: float, lon: float) -> Dict:
        """
        Obtém dados climáticos atuais usando OpenWeatherMap (já integrado)
        """
        try:
            if not self.openweather_api_key:
                self.logger.warning("OpenWeather API key não configurada")
                return {}
            
            url = f"{self.openweather_base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.openweather_api_key,
                "units": "metric",
                "lang": "pt_br"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'humidity_air': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'precipitation': data.get('rain', {}).get('1h', 0),  # Chuva última hora
                'weather_condition': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter clima atual: {str(e)}")
            return {}
    
    def get_weather_forecast(self, lat: float, lon: float, hours: int = 24) -> List[Dict]:
        """
        Obtém previsão do tempo usando OpenWeatherMap
        """
        try:
            if not self.openweather_api_key:
                return []
            
            url = f"{self.openweather_base_url}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.openweather_api_key,
                "units": "metric",
                "cnt": min(hours // 3, 40)  # API retorna de 3 em 3 horas, max 40 pontos
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            forecast_data = []
            for item in data.get('list', []):
                forecast_point = {
                    'timestamp': item['dt'] * 1000,
                    'temperature': item['main']['temp'],
                    'humidity_air': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'precipitation': item.get('rain', {}).get('3h', 0),
                    'wind_speed': item['wind']['speed'],
                    'weather_condition': item['weather'][0]['main']
                }
                forecast_data.append(forecast_point)
            
            return forecast_data
            
        except Exception as e:
            self.logger.error(f"Erro ao obter previsão: {str(e)}")
            return []