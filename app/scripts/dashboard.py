# scripts/dashboard.py

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, BASE_DIR)


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path para importar módulos da aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from app.services.sql_db_service import SQLDatabaseService

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions - Dashboard",
    page_icon="🌱",
    layout="wide"
)

# Título
st.title("🌱 FarmTech Solutions - Dashboard de Sensores")
st.markdown("*Use dashboard_ml.py para funcionalidades avançadas de IA*")

# Conexão com o banco de dados
@st.cache_resource
def get_sql_db():
    return SQLDatabaseService(Config.SQL_DATABASE_URI)

sql_db = get_sql_db()

# Obter lista de sensores
def obter_sensores():
    session = sql_db.get_session()
    try:
        from app.models.sensor_models import Sensor
        sensores = session.query(Sensor).filter_by(ativo=True).all()
        return [(s.id, f"{s.tipo} - ID: {s.id}") for s in sensores]
    finally:
        session.close()

# Obter leituras do sensor
def obter_leituras(sensor_id, dias):
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=dias)
    
    leituras = sql_db.obter_leituras_por_sensor(sensor_id, data_inicio, data_fim, limite=1000)
    
    # Separar por tipo de unidade
    leituras_umidade = []
    leituras_ph = []
    leituras_nutrientes = []
    
    for leitura in leituras:
        if leitura.unidade == '%':
            leituras_umidade.append({
                'data_hora': leitura.data_hora,
                'valor': float(leitura.valor)
            })
        elif leitura.unidade == 'pH':
            leituras_ph.append({
                'data_hora': leitura.data_hora,
                'valor': float(leitura.valor)
            })
        elif leitura.unidade in ['ppm', 'P_ppm', 'K_ppm']:
            # Tentar extrair valores de nutrientes
            try:
                import json
                if leitura.unidade == 'ppm' and leitura.valor.startswith('{'):
                    dados = json.loads(leitura.valor)
                    leituras_nutrientes.append({
                        'data_hora': leitura.data_hora,
                        'P': dados.get('P', 0),
                        'K': dados.get('K', 0)
                    })
                elif leitura.unidade == 'P_ppm':
                    leituras_nutrientes.append({
                        'data_hora': leitura.data_hora,
                        'P': float(leitura.valor),
                        'K': 0
                    })
                elif leitura.unidade == 'K_ppm':
                    leituras_nutrientes.append({
                        'data_hora': leitura.data_hora,
                        'P': 0,
                        'K': float(leitura.valor)
                    })
            except:
                # Ignorar leituras com formato inválido
                pass
    
    return {
        'umidade': pd.DataFrame(leituras_umidade),
        'ph': pd.DataFrame(leituras_ph),
        'nutrientes': pd.DataFrame(leituras_nutrientes)
    }

# Sidebar para seleção de filtros
st.sidebar.header("Filtros")

sensores = obter_sensores()
if not sensores:
    st.error("Nenhum sensor ativo encontrado no sistema.")
    st.stop()

sensor_id = st.sidebar.selectbox(
    "Selecione o Sensor",
    options=[s[0] for s in sensores],
    format_func=lambda x: next((s[1] for s in sensores if s[0] == x), x)
)

periodo = st.sidebar.slider(
    "Período (dias)",
    min_value=1,
    max_value=90,
    value=30
)

# Botão para dashboard avançado
st.info("💡 **Para análises de IA e ML, use:** `streamlit run dashboard_ml.py`")

# Botão para atualizar
if st.sidebar.button("Atualizar Dados"):
    st.rerun()

# Carregando dados
with st.spinner("Carregando dados dos sensores..."):
    dados = obter_leituras(sensor_id, periodo)

# Visualização dos dados
col1, col2 = st.columns(2)

with col1:
    st.subheader("Umidade do Solo")
    if not dados['umidade'].empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dados['umidade']['data_hora'], dados['umidade']['valor'], 'b-')
        ax.set_xlabel('Data/Hora')
        ax.set_ylabel('Umidade (%)')
        ax.grid(True)
        ax.set_ylim(0, 100)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Estatísticas de umidade
        if len(dados['umidade']) > 0:
            media_umidade = dados['umidade']['valor'].mean()
            min_umidade = dados['umidade']['valor'].min()
            max_umidade = dados['umidade']['valor'].max()
            
            st.metric("Umidade Média", f"{media_umidade:.1f}%")
            cols = st.columns(2)
            cols[0].metric("Mínima", f"{min_umidade:.1f}%")
            cols[1].metric("Máxima", f"{max_umidade:.1f}%")
    else:
        st.info("Nenhum dado de umidade disponível para o período selecionado.")

with col2:
    st.subheader("pH do Solo")
    if not dados['ph'].empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dados['ph']['data_hora'], dados['ph']['valor'], 'g-')
        ax.set_xlabel('Data/Hora')
        ax.set_ylabel('pH')
        ax.grid(True)
        ax.set_ylim(0, 14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Estatísticas de pH
        if len(dados['ph']) > 0:
            media_ph = dados['ph']['valor'].mean()
            min_ph = dados['ph']['valor'].min()
            max_ph = dados['ph']['valor'].max()
            
            st.metric("pH Médio", f"{media_ph:.1f}")
            cols = st.columns(2)
            cols[0].metric("Mínimo", f"{min_ph:.1f}")
            cols[1].metric("Máximo", f"{max_ph:.1f}")
    else:
        st.info("Nenhum dado de pH disponível para o período selecionado.")

# Visualização de nutrientes
st.subheader("Níveis de Nutrientes")
if not dados['nutrientes'].empty:
    # Converter dados para formato adequado
    df_nutrientes = dados['nutrientes'].copy()
    if len(df_nutrientes) > 0:
        # Calcular presença/ausência de P e K ao longo do tempo
        fig, ax = plt.subplots(figsize=(10, 4))
        
        if 'P' in df_nutrientes.columns:
            ax.plot(df_nutrientes['data_hora'], df_nutrientes['P'], 'r-', label='Fósforo (P)')
        
        if 'K' in df_nutrientes.columns:
            ax.plot(df_nutrientes['data_hora'], df_nutrientes['K'], 'b-', label='Potássio (K)')
        
        ax.set_xlabel('Data/Hora')
        ax.set_ylabel('Presença (1) / Ausência (0)')
        ax.grid(True)
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Estatísticas de nutrientes
        cols = st.columns(2)
        
        if 'P' in df_nutrientes.columns:
            presenca_p = df_nutrientes['P'].mean() * 100
            cols[0].metric("Presença de Fósforo (P)", f"{presenca_p:.1f}%")
        
        if 'K' in df_nutrientes.columns:
            presenca_k = df_nutrientes['K'].mean() * 100
            cols[1].metric("Presença de Potássio (K)", f"{presenca_k:.1f}%")
else:
    st.info("Nenhum dado de nutrientes disponível para o período selecionado.")

# Tabela com os dados mais recentes
st.subheader("Últimas Leituras")
tab1, tab2, tab3 = st.tabs(["Umidade", "pH", "Nutrientes"])

with tab1:
    if not dados['umidade'].empty:
        st.dataframe(
            dados['umidade'].sort_values('data_hora', ascending=False).head(10),
            column_config={
                "data_hora": "Data/Hora",
                "valor": st.column_config.NumberColumn("Umidade (%)", format="%.1f")
            }
        )
    else:
        st.info("Nenhum dado disponível")

with tab2:
    if not dados['ph'].empty:
        st.dataframe(
            dados['ph'].sort_values('data_hora', ascending=False).head(10),
            column_config={
                "data_hora": "Data/Hora",
                "valor": st.column_config.NumberColumn("pH", format="%.1f")
            }
        )
    else:
        st.info("Nenhum dado disponível")

with tab3:
    if not dados['nutrientes'].empty:
        st.dataframe(
            dados['nutrientes'].sort_values('data_hora', ascending=False).head(10)
        )
    else:
        st.info("Nenhum dado disponível")

# Informações adicionais
with st.expander("Sobre o Dashboard"):
    st.markdown("""
        Este dashboard apresenta os dados coletados pelos sensores da FarmTech Solutions:
        
        - **Sensor de Umidade do Solo**: Mostra a porcentagem de umidade presente no solo.
        - **Sensor de pH**: Indica o nível de acidez ou alcalinidade do solo (escala de 0 a 14).
        - **Sensores de Nutrientes**: Indica a presença (1) ou ausência (0) de fósforo (P) e potássio (K) no solo.
        
        Os dados são atualizados conforme as leituras são registradas no sistema.
    """)
    st.markdown("---")
    st.markdown("**Para funcionalidades avançadas de Machine Learning, execute:**")
    st.code("streamlit run app/scripts/dashboard_ml.py")