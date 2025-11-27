# app/scripts/dashboard_ml.py

import sys
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import json
import time
import asyncio

# Configuração de path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, BASE_DIR)

from config import Config
from app.services.sql_db_service import SQLDatabaseService
from app.ml.irrigation_predictor import IrrigationPredictor
from app.ml.model_trainer import ModelTrainer
from app.services.climate_service import ClimateDataService

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(
    page_title="🧠 FarmTech AI Dashboard - FASE 4",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhor visual
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #E8F5E8 0%, #F1F8E9 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .alert-high {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
        padding: 1rem;
        border-radius: 5px;
    }
    .alert-normal {
        background-color: #E8F5E8;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 5px;
    }
    .prediction-box {
        background: linear-gradient(45deg, #1976D2, #42A5F5);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ========== CONEXÕES E SERVIÇOS ==========
@st.cache_resource
def get_services():
    """Inicializa serviços necessários"""
    sql_db = SQLDatabaseService(Config.SQL_DATABASE_URI)
    predictor = IrrigationPredictor()
    trainer = ModelTrainer(sql_db)
    climate_service = ClimateDataService()
    return sql_db, predictor, trainer, climate_service

sql_db, predictor, trainer, climate_service = get_services()

# ========== FUNÇÕES AUXILIARES ==========
@st.cache_data(ttl=300)  # Cache por 5 minutos
def obter_sensores():
    """Obtém lista de sensores ativos"""
    session = sql_db.get_session()
    try:
        from app.models.sensor_models import Sensor
        sensores = session.query(Sensor).filter_by(ativo=True).all()
        return [(s.id, f"{s.tipo} - ID: {s.id}") for s in sensores]
    finally:
        session.close()

@st.cache_data(ttl=60)  # Cache por 1 minuto
def obter_leituras_otimizado(sensor_id, dias):
    """Obtém leituras de forma otimizada"""
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=dias)
    
    leituras = sql_db.obter_leituras_por_sensor(sensor_id, data_inicio, data_fim, limite=2000)
    
    # Processar dados
    dados_processados = {
        'umidade': [],
        'ph': [],
        'nutrientes': [],
        'irrigacao': []
    }
    
    for leitura in leituras:
        data_point = {
            'data_hora': leitura.data_hora,
            'timestamp': int(leitura.data_hora.timestamp() * 1000)
        }
        
        if leitura.unidade == '%':
            dados_processados['umidade'].append({
                **data_point,
                'valor': float(leitura.valor)
            })
        elif leitura.unidade == 'pH':
            dados_processados['ph'].append({
                **data_point,
                'valor': float(leitura.valor)
            })
        elif leitura.unidade == 'ppm':
            try:
                if leitura.valor.startswith('{'):
                    nutrientes = json.loads(leitura.valor)
                    dados_processados['nutrientes'].append({
                        **data_point,
                        'P': nutrientes.get('P', 0),
                        'K': nutrientes.get('K', 0)
                    })
            except:
                pass
    
    return {k: pd.DataFrame(v) for k, v in dados_processados.items()}

def preparar_dados_ml(sensor_id, dias=30):
    """Prepara dados para ML"""
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=dias)
    
    # Buscar dados históricos
    dados_historicos = trainer.collect_training_data(dias, min_samples=10)
    
    if not dados_historicos:
        return None, "Dados insuficientes para análise ML"
    
    # Enriquecer com dados climáticos
    try:
        dados_enriquecidos = predictor.enrich_with_climate_data(dados_historicos)
        return dados_enriquecidos, None
    except Exception as e:
        return dados_historicos, f"Aviso: Dados climáticos não disponíveis ({str(e)})"

# ========== INTERFACE PRINCIPAL ==========
def main():
    # Cabeçalho principal
    st.markdown('<h1 class="main-header">🧠 FarmTech AI Dashboard - FASE 4</h1>', unsafe_allow_html=True)
    st.markdown("**Sistema Inteligente de Agricultura de Precisão com Machine Learning**")
    
    # Sidebar para controles
    with st.sidebar:
        st.header("🎛️ Controles")
        
        # Seleção de sensor
        sensores = obter_sensores()
        if not sensores:
            st.error("❌ Nenhum sensor encontrado!")
            return
        
        sensor_id = st.selectbox(
            "📡 Selecione o Sensor",
            options=[s[0] for s in sensores],
            format_func=lambda x: next((s[1] for s in sensores if s[0] == x), x)
        )
        
        # Período de análise
        periodo = st.slider("📅 Período (dias)", 1, 90, 30)
        
        # Controles ML
        st.subheader("🤖 Machine Learning")
        
        if st.button("🔄 Treinar Modelo", type="primary"):
            with st.spinner("Treinando modelo ML..."):
                treinar_modelo_ml(sensor_id, periodo)
        
        if st.button("🔮 Nova Predição"):
            st.session_state['force_prediction'] = True
        
        # Auto-refresh
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=True)
        if auto_refresh:
            time.sleep(30)
            st.rerun()
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard Principal", 
        "🤖 Predições ML", 
        "📈 Análises Avançadas",
        "🌤️ Integração Climática",
        "⚙️ Sistema"
    ])
    
    with tab1:
        dashboard_principal(sensor_id, periodo)
    
    with tab2:
        dashboard_predicoes_ml(sensor_id, periodo)
    
    with tab3:
        dashboard_analises_avancadas(sensor_id, periodo)
    
    with tab4:
        dashboard_climatico(sensor_id, periodo)
    
    with tab5:
        dashboard_sistema(sensor_id)

# ========== DASHBOARD PRINCIPAL ==========
def dashboard_principal(sensor_id, periodo):
    st.header("📊 Monitoramento em Tempo Real")
    
    # Carregar dados
    dados = obter_leituras_otimizado(sensor_id, periodo)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not dados['umidade'].empty:
            umidade_atual = dados['umidade']['valor'].iloc[-1]
            delta_umidade = umidade_atual - dados['umidade']['valor'].iloc[-2] if len(dados['umidade']) > 1 else 0
            st.metric(
                "💧 Umidade Solo", 
                f"{umidade_atual:.1f}%", 
                delta=f"{delta_umidade:+.1f}%"
            )
        else:
            st.metric("💧 Umidade Solo", "N/A")
    
    with col2:
        if not dados['ph'].empty:
            ph_atual = dados['ph']['valor'].iloc[-1]
            delta_ph = ph_atual - dados['ph']['valor'].iloc[-2] if len(dados['ph']) > 1 else 0
            st.metric(
                "🧪 pH Solo", 
                f"{ph_atual:.2f}", 
                delta=f"{delta_ph:+.2f}"
            )
        else:
            st.metric("🧪 pH Solo", "N/A")
    
    with col3:
        if not dados['nutrientes'].empty:
            p_atual = dados['nutrientes']['P'].iloc[-1] if 'P' in dados['nutrientes'].columns else 0
            st.metric("🌱 Fósforo (P)", "Presente" if p_atual else "Ausente")
        else:
            st.metric("🌱 Fósforo (P)", "N/A")
    
    with col4:
        if not dados['nutrientes'].empty:
            k_atual = dados['nutrientes']['K'].iloc[-1] if 'K' in dados['nutrientes'].columns else 0
            st.metric("🌿 Potássio (K)", "Presente" if k_atual else "Ausente")
        else:
            st.metric("🌿 Potássio (K)", "N/A")
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        if not dados['umidade'].empty:
            fig_umidade = px.line(
                dados['umidade'], 
                x='data_hora', 
                y='valor',
                title="💧 Histórico de Umidade do Solo",
                labels={'valor': 'Umidade (%)', 'data_hora': 'Data/Hora'}
            )
            fig_umidade.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Limite Mín (30%)")
            fig_umidade.add_hline(y=70, line_dash="dash", line_color="blue", annotation_text="Limite Máx (70%)")
            st.plotly_chart(fig_umidade, use_container_width=True)
        else:
            st.info("Dados de umidade não disponíveis")
    
    with col2:
        if not dados['ph'].empty:
            fig_ph = px.line(
                dados['ph'], 
                x='data_hora', 
                y='valor',
                title="🧪 Histórico de pH do Solo",
                labels={'valor': 'pH', 'data_hora': 'Data/Hora'}
            )
            fig_ph.add_hline(y=6.0, line_dash="dash", line_color="red", annotation_text="pH Mín (6.0)")
            fig_ph.add_hline(y=7.5, line_dash="dash", line_color="red", annotation_text="pH Máx (7.5)")
            st.plotly_chart(fig_ph, use_container_width=True)
        else:
            st.info("Dados de pH não disponíveis")

# ========== DASHBOARD PREDIÇÕES ML ==========
def dashboard_predicoes_ml(sensor_id, periodo):
    st.header("🤖 Predições e Inteligência Artificial")
    
    # Verificar se modelo está treinado
    if not hasattr(predictor.irrigation_classifier, 'feature_importances_'):
        st.warning("⚠️ Modelo não treinado. Clique em 'Treinar Modelo' na sidebar.")
        return
    
    # Obter dados atuais para predição
    dados_atuais = obter_dados_atuais_sensor(sensor_id)
    if not dados_atuais:
        st.error("❌ Não foi possível obter dados atuais do sensor")
        return
    
    # Obter dados climáticos atuais
    dados_clima = climate_service.get_current_weather(-3.763081, -38.524465)  # Fortaleza
    
    # Fazer predição
    predicao = predictor.predict_irrigation_with_weather(dados_atuais, dados_clima)
    
    # Exibir predição principal
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
        st.markdown(f"### 🔮 Predição de Irrigação")
        if predicao['irrigation_needed']:
            st.markdown("# ✅ IRRIGAÇÃO RECOMENDADA")
        else:
            st.markdown("# ❌ IRRIGAÇÃO NÃO NECESSÁRIA")
        st.markdown(f"**Confiança:** {predicao['confidence']:.1%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.metric(
            "🎯 Probabilidade", 
            f"{predicao['irrigation_probability']:.1%}",
            delta=f"Conf: {predicao['confidence']:.1%}"
        )
    
    with col3:
        umidade_prevista = predicao.get('predicted_humidity_next_hour', 0)
        umidade_atual = predicao.get('current_humidity', 0)
        delta_umidade = umidade_prevista - umidade_atual
        st.metric(
            "💧 Umidade Prevista", 
            f"{umidade_prevista:.1f}%",
            delta=f"{delta_umidade:+.1f}%"
        )
    
    # Recomendações do modelo
    st.subheader("💡 Recomendações Inteligentes")
    for i, recomendacao in enumerate(predicao.get('recommendations', [])):
        if '✅' in recomendacao:
            st.success(recomendacao)
        elif '⚠️' in recomendacao:
            st.warning(recomendacao)
        elif '❌' in recomendacao:
            st.info(recomendacao)
        else:
            st.write(f"• {recomendacao}")
    
    # Análise de tendências
    st.subheader("📈 Análise de Tendências")
    trend_analysis = predicao.get('trend_analysis', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status = trend_analysis.get('humidity_status', 'normal')
        color = 'red' if status == 'low' else 'blue' if status == 'high' else 'green'
        st.markdown(f"**Status Umidade:** <span style='color:{color}'>{status.upper()}</span>", unsafe_allow_html=True)
    
    with col2:
        status = trend_analysis.get('ph_status', 'ideal')
        color = 'red' if status in ['acidic', 'alkaline'] else 'green'
        st.markdown(f"**Status pH:** <span style='color:{color}'>{status.upper()}</span>", unsafe_allow_html=True)
    
    with col3:
        status = trend_analysis.get('nutrient_status', 'sufficient')
        color = 'red' if status == 'deficient' else 'green'
        st.markdown(f"**Status Nutrientes:** <span style='color:{color}'>{status.upper()}</span>", unsafe_allow_html=True)
    
    # Importância das features
    st.subheader("🎯 Importância das Variáveis no Modelo")
    importance = predictor.get_feature_importance()
    
    if importance:
        # Gráfico de importância para irrigação
        irr_importance = importance['irrigation_model']
        features = list(irr_importance.keys())
        values = list(irr_importance.values())
        
        fig_importance = px.bar(
            x=values, 
            y=features, 
            orientation='h',
            title="🤖 Importância das Features - Modelo de Irrigação",
            labels={'x': 'Importância', 'y': 'Variáveis'}
        )
        fig_importance.update_layout(height=400)
        st.plotly_chart(fig_importance, use_container_width=True)

# ========== DASHBOARD ANÁLISES AVANÇADAS ==========
def dashboard_analises_avancadas(sensor_id, periodo):
    st.header("📈 Análises Avançadas e Correlações")
    
    # Preparar dados para análise
    dados_ml, erro_msg = preparar_dados_ml(sensor_id, periodo)
    
    if erro_msg:
        st.warning(f"⚠️ {erro_msg}")
    
    if dados_ml is None:
        st.error("❌ Dados insuficientes para análises avançadas")
        return
    
    df = pd.DataFrame(dados_ml)
    
    # Análise de correlação
    st.subheader("🔗 Matriz de Correlação")
    
    # Selecionar colunas numéricas para correlação
    cols_numericas = ['umidade', 'ph', 'fosforo', 'potassio', 'irrigacao']
    if 'temperature' in df.columns:
        cols_numericas.extend(['temperature', 'humidity_air', 'precipitation'])
    
    df_corr = df[cols_numericas].corr()
    
    fig_corr = px.imshow(
        df_corr,
        title="Matriz de Correlação entre Variáveis",
        color_continuous_scale="RdBu",
        aspect="auto"
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Distribuições
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição de Umidade")
        fig_dist_umidade = px.histogram(
            df, 
            x='umidade', 
            nbins=30,
            title="Distribuição da Umidade do Solo",
            marginal="box"
        )
        fig_dist_umidade.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="Limite Min")
        fig_dist_umidade.add_vline(x=70, line_dash="dash", line_color="blue", annotation_text="Limite Max")
        st.plotly_chart(fig_dist_umidade, use_container_width=True)
    
    with col2:
        st.subheader("🧪 Distribuição de pH")
        fig_dist_ph = px.histogram(
            df, 
            x='ph', 
            nbins=30,
            title="Distribuição do pH do Solo",
            marginal="box"
        )
        fig_dist_ph.add_vline(x=6.0, line_dash="dash", line_color="red", annotation_text="pH Min")
        fig_dist_ph.add_vline(x=7.5, line_dash="dash", line_color="red", annotation_text="pH Max")
        st.plotly_chart(fig_dist_ph, use_container_width=True)
    
    # Análise temporal avançada
    st.subheader("⏰ Padrões Temporais")
    
    # Converter timestamp para datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['hora'] = df['datetime'].dt.hour
    df['dia_semana'] = df['datetime'].dt.dayofweek
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Padrão por hora do dia
        hourly_pattern = df.groupby('hora').agg({
            'umidade': 'mean',
            'ph': 'mean',
            'irrigacao': 'sum'
        }).reset_index()
        
        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Scatter(
            x=hourly_pattern['hora'], 
            y=hourly_pattern['umidade'],
            mode='lines+markers',
            name='Umidade Média',
            yaxis='y'
        ))
        fig_hourly.add_trace(go.Scatter(
            x=hourly_pattern['hora'], 
            y=hourly_pattern['ph'] * 10,  # Escalar para visualização
            mode='lines+markers',
            name='pH Médio (x10)',
            yaxis='y'
        ))
        fig_hourly.add_trace(go.Bar(
            x=hourly_pattern['hora'], 
            y=hourly_pattern['irrigacao'],
            name='Irrigações',
            yaxis='y2',
            opacity=0.6
        ))
        
        fig_hourly.update_layout(
            title="Padrões por Hora do Dia",
            xaxis_title="Hora",
            yaxis=dict(title="Umidade (%) / pH (x10)", side="left"),
            yaxis2=dict(title="Número de Irrigações", side="right", overlaying="y"),
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        # Padrão por dia da semana
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        weekly_pattern = df.groupby('dia_semana').agg({
            'umidade': 'mean',
            'irrigacao': 'sum'
        }).reset_index()
        weekly_pattern['dia_nome'] = [dias_semana[i] for i in weekly_pattern['dia_semana']]
        
        fig_weekly = px.bar(
            weekly_pattern, 
            x='dia_nome', 
            y=['umidade', 'irrigacao'],
            title="Padrões por Dia da Semana",
            barmode='group'
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Estatísticas descritivas
    st.subheader("📋 Estatísticas Descritivas")
    
    stats_cols = ['umidade', 'ph']
    if 'temperature' in df.columns:
        stats_cols.extend(['temperature', 'humidity_air'])
    
    stats_df = df[stats_cols].describe()
    st.dataframe(stats_df, use_container_width=True)

# ========== DASHBOARD CLIMÁTICO ==========
def dashboard_climatico(sensor_id, periodo):
    st.header("🌤️ Integração Climática")
    
    # Coordenadas (Fortaleza como padrão)
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("📍 Latitude", value=-3.763081, format="%.4f")
    with col2:
        lon = st.number_input("📍 Longitude", value=-38.524465, format="%.4f")
    
    # Dados climáticos atuais
    st.subheader("☀️ Condições Atuais")
    
    dados_clima_atual = climate_service.get_current_weather(lat, lon)
    
    if dados_clima_atual:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌡️ Temperatura", f"{dados_clima_atual.get('temperature', 0):.1f}°C")
        with col2:
            st.metric("💨 Umidade do Ar", f"{dados_clima_atual.get('humidity_air', 0)}%")
        with col3:
            st.metric("🌧️ Precipitação", f"{dados_clima_atual.get('precipitation', 0):.1f}mm")
        with col4:
            st.metric("💨 Vento", f"{dados_clima_atual.get('wind_speed', 0):.1f}km/h")
        
        # Condição climática
        condicao = dados_clima_atual.get('description', 'N/A')
        st.info(f"**Condição Atual:** {condicao}")
    else:
        st.warning("⚠️ Dados climáticos atuais não disponíveis")
    
    # Previsão do tempo
    st.subheader("🔮 Previsão do Tempo (24h)")
    
    previsao = climate_service.get_weather_forecast(lat, lon, 24)
    
    if previsao:
        # Converter para DataFrame
        df_previsao = pd.DataFrame(previsao)
        df_previsao['datetime'] = pd.to_datetime(df_previsao['timestamp'], unit='ms')
        
        # Gráfico de previsão
        fig_previsao = make_subplots(
            rows=3, cols=1,
            subplot_titles=("Temperatura", "Precipitação", "Umidade do Ar"),
            vertical_spacing=0.1
        )
        
        fig_previsao.add_trace(
            go.Scatter(x=df_previsao['datetime'], y=df_previsao['temperature'], 
                      mode='lines+markers', name='Temperatura'),
            row=1, col=1
        )
        
        fig_previsao.add_trace(
            go.Bar(x=df_previsao['datetime'], y=df_previsao['precipitation'], 
                   name='Precipitação'),
            row=2, col=1
        )
        
        fig_previsao.add_trace(
            go.Scatter(x=df_previsao['datetime'], y=df_previsao['humidity_air'], 
                      mode='lines+markers', name='Umidade do Ar'),
            row=3, col=1
        )
        
        fig_previsao.update_layout(height=600, title_text="Previsão Meteorológica")
        st.plotly_chart(fig_previsao, use_container_width=True)
    else:
        st.warning("⚠️ Previsão do tempo não disponível")
    
    # Dados históricos climáticos
    st.subheader("📊 Dados Climáticos Históricos")
    
    if st.button("🔄 Carregar Dados Históricos"):
        with st.spinner("Carregando dados climáticos históricos..."):
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)  # Última semana
            
            dados_historicos = climate_service.get_historical_weather(lat, lon, start_date, end_date)
            
            if dados_historicos:
                df_historico = pd.DataFrame(dados_historicos)
                df_historico['datetime'] = pd.to_datetime(df_historico['datetime'])
                
                # Gráfico histórico
                fig_historico = px.line(
                    df_historico, 
                    x='datetime', 
                    y=['temperature', 'humidity_air'],
                    title="Histórico Climático (7 dias)"
                )
                st.plotly_chart(fig_historico, use_container_width=True)
                
                # Estatísticas
                st.write("**Estatísticas da Semana:**")
                stats = df_historico[['temperature', 'humidity_air', 'precipitation']].describe()
                st.dataframe(stats)
            else:
                st.warning("⚠️ Não foi possível carregar dados históricos")

# ========== DASHBOARD SISTEMA ==========
def dashboard_sistema(sensor_id):
    st.header("⚙️ Status do Sistema")
    
    # Informações do modelo ML
    st.subheader("🤖 Status do Modelo ML")
    
    if hasattr(predictor.irrigation_classifier, 'feature_importances_'):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            accuracy = predictor.model_metrics.get('irrigation_accuracy', 0)
            st.metric("🎯 Acurácia Irrigação", f"{accuracy:.1%}")
        
        with col2:
            mae = predictor.model_metrics.get('humidity_mae', 0)
            st.metric("📊 MAE Umidade", f"{mae:.2f}")
        
        with col3:
            samples = predictor.model_metrics.get('training_samples', 0)
            st.metric("📋 Amostras Treino", f"{samples}")
        
        # Data do último treinamento
        last_trained = predictor.model_metrics.get('last_trained')
        if last_trained:
            st.info(f"**Último Treinamento:** {last_trained}")
        
        # Métricas detalhadas
        with st.expander("📈 Métricas Detalhadas"):
            st.json(predictor.model_metrics)
    else:
        st.warning("⚠️ Modelo não treinado")
    
    # Status dos sensores
    st.subheader("📡 Status dos Sensores")
    
    sensores = obter_sensores()
    for sensor_id, sensor_nome in sensores:
        with st.expander(f"Sensor {sensor_nome}"):
            # Última leitura
            dados = obter_leituras_otimizado(sensor_id, 1)
            
            if any(not df.empty for df in dados.values()):
                st.success("✅ Sensor ativo")
                
                # Mostrar última leitura de cada tipo
                for tipo, df in dados.items():
                    if not df.empty:
                        ultima_leitura = df.iloc[-1]
                        st.write(f"**{tipo.title()}:** {ultima_leitura.get('valor', 'N/A')} ({ultima_leitura['data_hora']})")
            else:
                st.error("❌ Sem dados recentes")
    
    # Logs do sistema
    st.subheader("📜 Logs do Sistema")
    
    with st.expander("Ver Logs"):
        # Simular logs (em implementação real, ler de arquivo de log)
        logs = [
            f"{datetime.now() - timedelta(minutes=5)} - INFO - Dashboard atualizado",
            f"{datetime.now() - timedelta(minutes=15)} - INFO - Predição ML executada",
            f"{datetime.now() - timedelta(hours=1)} - INFO - Dados climáticos atualizados",
            f"{datetime.now() - timedelta(hours=2)} - WARNING - Sensor umidade fora do range",
        ]
        
        for log in logs:
            st.text(log)

# ========== FUNÇÕES AUXILIARES ==========
def obter_dados_atuais_sensor(sensor_id):
    """Obtém dados mais recentes do sensor para predição"""
    dados = obter_leituras_otimizado(sensor_id, 1)
    
    resultado = {
        'umidade': 50.0,
        'ph': 7.0,
        'fosforo': 0,
        'potassio': 0,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }
    
    # Pegar valores mais recentes
    if not dados['umidade'].empty:
        resultado['umidade'] = dados['umidade']['valor'].iloc[-1]
    
    if not dados['ph'].empty:
        resultado['ph'] = dados['ph']['valor'].iloc[-1]
    
    if not dados['nutrientes'].empty:
        if 'P' in dados['nutrientes'].columns:
            resultado['fosforo'] = dados['nutrientes']['P'].iloc[-1]
        if 'K' in dados['nutrientes'].columns:
            resultado['potassio'] = dados['nutrientes']['K'].iloc[-1]
    
    return resultado

def treinar_modelo_ml(sensor_id, periodo):
    """Treina o modelo ML com dados disponíveis"""
    try:
        # Coletar dados de treinamento
        dados_treino = trainer.collect_training_data(periodo, min_samples=20)
        
        if not dados_treino:
            st.error("❌ Dados insuficientes para treinamento (mínimo 20 amostras)")
            return
        
        # Enriquecer com dados climáticos
        dados_enriquecidos = predictor.enrich_with_climate_data(dados_treino)
        
        # Treinar modelos
        metricas = predictor.train_models(dados_enriquecidos)
        
        # Salvar modelos
        predictor.save_models()
        
        st.success("✅ Modelo treinado com sucesso!")
        st.json(metricas)
        
        # Forçar recarregamento da página
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro no treinamento: {str(e)}")

# ========== EXECUÇÃO PRINCIPAL ==========
if __name__ == "__main__":
    main()
    
    
# ### ------VERSÃO SIMPLIFICADA

# """
# Dashboard Streamlit SIMPLIFICADO - para compatibilidade com implementação anterior
# Este arquivo mantém funcionalidade básica enquanto o dashboard_ml.py oferece funcionalidades avançadas
# """

# import sys
# import os
# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta

# # Configuração de path
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
# sys.path.insert(0, BASE_DIR)

# from config import Config
# from app.services.sql_db_service import SQLDatabaseService

# # Configuração da página
# st.set_page_config(
#     page_title="FarmTech Solutions - Dashboard Básico",
#     page_icon="🌱",
#     layout="wide"
# )

# # Título
# st.title("🌱 FarmTech Solutions - Dashboard Básico")
# st.markdown("*Use dashboard_ml.py para funcionalidades avançadas de IA*")

# # Conexão com o banco de dados
# @st.cache_resource
# def get_sql_db():
#     return SQLDatabaseService(Config.SQL_DATABASE_URI)

# sql_db = get_sql_db()

# # Obter lista de sensores
# def obter_sensores():
#     session = sql_db.get_session()
#     try:
#         from app.models.sensor_models import Sensor
#         sensores = session.query(Sensor).filter_by(ativo=True).all()
#         return [(s.id, f"{s.tipo} - ID: {s.id}") for s in sensores]
#     finally:
#         session.close()

# # Interface básica
# sensores = obter_sensores()
# if not sensores:
#     st.error("Nenhum sensor ativo encontrado no sistema.")
#     st.stop()

# sensor_id = st.selectbox(
#     "Selecione o Sensor",
#     options=[s[0] for s in sensores],
#     format_func=lambda x: next((s[1] for s in sensores if s[0] == x), x)
# )

# periodo = st.slider("Período (dias)", min_value=1, max_value=90, value=30)

# # Botão para dashboard avançado
# st.info("💡 **Para análises de IA e ML, use:** `streamlit run dashboard_ml.py`")

# # Dados básicos
# data_fim = datetime.now()
# data_inicio = data_fim - timedelta(days=periodo)

# leituras = sql_db.obter_leituras_por_sensor(sensor_id, data_inicio, data_fim, limite=1000)

# if leituras:
#     # Separar por tipo
#     dados_umidade = []
#     dados_ph = []
    
#     for leitura in leituras:
#         if leitura.unidade == '%':
#             dados_umidade.append({
#                 'data_hora': leitura.data_hora,
#                 'valor': float(leitura.valor)
#             })
#         elif leitura.unidade == 'pH':
#             dados_ph.append({
#                 'data_hora': leitura.data_hora,
#                 'valor': float(leitura.valor)
#             })
    
#     # Gráficos básicos
#     col1, col2 = st.columns(2)
    
#     with col1:
#         if dados_umidade:
#             df_umidade = pd.DataFrame(dados_umidade)
#             st.subheader("💧 Umidade do Solo")
#             fig, ax = plt.subplots(figsize=(10, 6))
#             ax.plot(df_umidade['data_hora'], df_umidade['valor'], 'b-')
#             ax.set_xlabel('Data/Hora')
#             ax.set_ylabel('Umidade (%)')
#             ax.grid(True)
#             ax.set_ylim(0, 100)
#             plt.xticks(rotation=45)
#             plt.tight_layout()
#             st.pyplot(fig)
            
#             # Estatísticas
#             media = df_umidade['valor'].mean()
#             st.metric("Umidade Média", f"{media:.1f}%")
    
#     with col2:
#         if dados_ph:
#             df_ph = pd.DataFrame(dados_ph)
#             st.subheader("🧪 pH do Solo")
#             fig, ax = plt.subplots(figsize=(10, 6))
#             ax.plot(df_ph['data_hora'], df_ph['valor'], 'g-')
#             ax.set_xlabel('Data/Hora')
#             ax.set_ylabel('pH')
#             ax.grid(True)
#             ax.set_ylim(0, 14)
#             plt.xticks(rotation=45)
#             plt.tight_layout()
#             st.pyplot(fig)
            
#             # Estatísticas
#             media_ph = df_ph['valor'].mean()
#             st.metric("pH Médio", f"{media_ph:.2f}")

# else:
#     st.warning("Nenhum dado encontrado para o período selecionado.")

# st.markdown("---")
# st.markdown("**Para funcionalidades avançadas de Machine Learning, execute:**")
# st.code("streamlit run app/scripts/dashboard_ml.py")


# RESPOSTA PARA AS PERGUNTAS:

# 1. Arquivos não utilizados:
# - real_time_dashboard.py: REMOVIDO - funcionalidade integrada no dashboard_ml.py
# - data_preprocessor.py: REMOVIDO - funcionalidades consolidadas na classe IrrigationPredictor
# - prediction_service.py: REMOVIDO - métodos integrados na classe IrrigationPredictor

# 2. A função evaluate_model_drift foi COMPLETAMENTE IMPLEMENTADA com:
# - Query SQL para buscar predições históricas vs resultados reais
# - Cálculo de métricas de drift (accuracy, precision, recall, F1, Brier Score)
# - Detecção automática de drift com limiares configuráveis
# - Geração de relatórios de avaliação
# - Integração com sistema de retreinamento automático