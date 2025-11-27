# app/services/weather_service.py
import requests
import json
from datetime import datetime

class WeatherService:
    def __init__(self, api_key, lang='pt_br', units='metric'):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.lang = lang
        self.units = units
    
    def obter_clima_atual(self, cidade):
        """Obtém dados do clima atual para uma cidade"""
        url = f"{self.base_url}/weather"
        params = {
            'q': cidade,
            'appid': self.api_key,
            'lang': self.lang,
            'units': self.units
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Lança exceção para códigos de erro HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter dados climáticos: {str(e)}")
            return None
    
    def obter_previsao(self, cidade, cnt=5):
        """Obtém previsão do tempo para uma cidade (cnt = número de previsões)"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': cidade,
            'appid': self.api_key,
            'lang': self.lang,
            'units': self.units,
            'cnt': cnt  # Número de previsões (máximo 40, uma a cada 3 horas por 5 dias)
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter previsão do tempo: {str(e)}")
            return None
    
    def verificar_necessidade_irrigacao(self, campo_id, cidade, sql_db, mongo_db):
        """
        Verifica se é necessário irrigar com base nos dados climáticos
        e leituras dos sensores
        """
        # Obter dados do campo
        campo = mongo_db.obter_campo_por_id(campo_id)
        if not campo:
            return {
                'irrigar': False,
                'motivo': 'Campo não encontrado'
            }
        
        # Obter sensores do campo
        sensores = sql_db.obter_sensores_por_campo(campo_id)
        
        # Verificar leituras recentes de umidade (se existirem)
        sensor_umidade = next((s for s in sensores if s.tipo == 'S1'), None)
        media_umidade = None
        
        if sensor_umidade:
            from datetime import datetime, timedelta
            data_fim = datetime.now()
            data_inicio = data_fim - timedelta(hours=6)  # Últimas 6 horas
            leituras = sql_db.obter_leituras_por_sensor(sensor_umidade.id, data_inicio, data_fim)
            
            if leituras:
                # Calcular média das leituras de umidade
                valores_umidade = []
                for leitura in leituras:
                    try:
                        valores_umidade.append(float(leitura.valor))
                    except (ValueError, TypeError):
                        continue
                
                if valores_umidade:
                    media_umidade = sum(valores_umidade) / len(valores_umidade)
        
        # Obter dados climáticos atuais
        clima_atual = self.obter_clima_atual(cidade)
        if not clima_atual:
            return {
                'irrigar': media_umidade is not None and media_umidade < 30,  # Usar apenas dados do sensor
                'motivo': 'Dados climáticos não disponíveis'
            }
        
        # Obter previsão do tempo (próximas 15 horas)
        previsao = self.obter_previsao(cidade, cnt=5)
        
        # Extrair dados relevantes
        temperatura_atual = clima_atual.get('main', {}).get('temp', 0)
        umidade_ar = clima_atual.get('main', {}).get('humidity', 0)
        condicao_atual = clima_atual.get('weather', [{}])[0].get('main', '')
        descricao_atual = clima_atual.get('weather', [{}])[0].get('description', '')
        
        # Verificar se vai chover nas próximas horas
        vai_chover = False
        if previsao and 'list' in previsao:
            for periodo in previsao['list']:
                condicao = periodo.get('weather', [{}])[0].get('main', '')
                if condicao.lower() in ['rain', 'thunderstorm', 'drizzle', 'shower rain']:
                    vai_chover = True
                    break
        
        # Lógica para decidir se deve irrigar
        # 1. Se vai chover em breve, não irrigar
        if vai_chover:
            return {
                'irrigar': False,
                'motivo': 'Previsão de chuva nas próximas horas',
                'clima_atual': {
                    'temperatura': temperatura_atual,
                    'umidade_ar': umidade_ar,
                    'condicao': condicao_atual,
                    'descricao': descricao_atual
                }
            }
        
        # 2. Se a umidade do solo for baixa E não vai chover, irrigar
        if media_umidade is not None:
            if media_umidade < 30:
                return {
                    'irrigar': True,
                    'motivo': f'Umidade do solo baixa ({media_umidade:.1f}%) e sem previsão de chuva',
                    'clima_atual': {
                        'temperatura': temperatura_atual,
                        'umidade_ar': umidade_ar,
                        'condicao': condicao_atual,
                        'descricao': descricao_atual
                    }
                }
            else:
                return {
                    'irrigar': False,
                    'motivo': f'Umidade do solo adequada ({media_umidade:.1f}%)',
                    'clima_atual': {
                        'temperatura': temperatura_atual,
                        'umidade_ar': umidade_ar,
                        'condicao': condicao_atual,
                        'descricao': descricao_atual
                    }
                }
        
        # 3. Se não temos dados de umidade do solo, decidir pelo clima
        # Se está muito quente e seco, considerar irrigação
        if temperatura_atual > 30 and umidade_ar < 50:
            return {
                'irrigar': True,
                'motivo': f'Clima quente e seco (Temp: {temperatura_atual}°C, Umidade do ar: {umidade_ar}%)',
                'clima_atual': {
                    'temperatura': temperatura_atual,
                    'umidade_ar': umidade_ar,
                    'condicao': condicao_atual,
                    'descricao': descricao_atual
                }
            }
        
        # 4. Padrão: não irrigar sem informações suficientes
        return {
            'irrigar': False,
            'motivo': 'Sem dados suficientes para decisão automática',
            'clima_atual': {
                'temperatura': temperatura_atual,
                'umidade_ar': umidade_ar,
                'condicao': condicao_atual,
                'descricao': descricao_atual
            }
        }