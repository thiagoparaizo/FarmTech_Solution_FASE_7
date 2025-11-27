import sys
import os

# Adicionar path do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, BASE_DIR)

from app.services.climate_service import ClimateDataService
from datetime import datetime, timedelta

fortaleza = { 'latitude': -3.763081, 'longitude': -38.524465 }
localizacao = fortaleza

climate = ClimateDataService()
current = climate.get_current_weather(localizacao['latitude'], localizacao['longitude'])
print('Clima atual:', current)

# Teste dados históricos
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
historical = climate.get_historical_weather(localizacao['latitude'], localizacao['longitude'], start_date, end_date)
print(f'Dados históricos: {len(historical)} registros')
#print(historical)

## python.exe .\app\tests\integracao_clima.py
