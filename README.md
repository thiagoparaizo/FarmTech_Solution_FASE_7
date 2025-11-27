# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="https://avatars.githubusercontent.com/u/70102670?s=200&v=4" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# EasyAgro - FarmTechSolutions

## Nome do grupo

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/thiagoparaizo/?originalSubdomain=br">Thiago Paraizo</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/company/inova-fusca">Leonardo Ruiz Orabona</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">Andre Godoy Chiovato</a>

## 📜 Descrição

O EasyAgro é uma aplicação web desenvolvida para a gestão agrícola digital, com foco na gestão de culturas e campos, cálculos de área, insumos, irrigação e plantio, e sensoriamento. A aplicação serve como uma solução completa para pequenos produtores rurais, agricultores familiares e cooperativas, permitindo o **controle produtivo, gestão de dados e apoio à decisão**.

Esta aplicação web leve implementada em Python integra controle de produção, rastreabilidade, análise de dados, monitoramento por sensores e apoio à gestão em uma plataforma única e amigável. Ela funciona como uma *porta de entrada digital* para o agricultor familiar, organizando suas informações e conectando-o a benefícios, sejam conhecimentos ou créditos.

## Documentação e Sreenshots do Sistema
[ Veja a Documentação e Sreenshots do Sistema em funcionamento ](doc/documentacao.md)

## Análise e Modelo de Dados usados no Sistema
[Veja a Análise e Modelo de Dados usados no Sistema](doc/farmtech_modelagem_dados.md)


## 🚀 **Novas Funcionalidades Implementadas FASE 4**

### **Machine Learning e Inteligência Artificial**
- **Modelos Preditivos**: RandomForestClassifier para decisões de irrigação e RandomForestRegressor para predição de umidade
- **Ensemble Learning**: Algoritmo robusto que combina múltiplas árvores de decisão, ideal para dados agrícolas
- **Balanceamento Automático**: Sistema detecta e corrige automaticamente problemas de classes desbalanceadas
- **Feature Engineering**: Engenharia de características avançada incluindo dados temporais e climáticos
- **Predições com Confiança**: Intervalos de confiança e análise de incerteza nas predições
- **Retreinamento Automático**: Sistema de retreinamento baseado em drift detection

### **Dashboard Streamlit Avançado**
- **Análises Preditivas**: Interface interativa para predições de irrigação em tempo real
- **Recomendações Inteligentes**: Sugestões contextuais baseadas em análise integrada de sensores
- **Análise de Tendências**: Monitoramento de padrões temporais e identificação de anomalias
- **Importância das Variáveis**: Visualização de quais sensores mais influenciam as decisões
- **Matriz de Correlação**: Análise de relacionamentos entre variáveis do sistema
- **Distribuições Estatísticas**: Histogramas e estatísticas descritivas dos dados
- **Padrões Temporais**: Identificação de ciclos diários e sazonais

### **APIs de Machine Learning**
- **Endpoint de Predição**: `/api/ml/predict` para predições em tempo real
- **Status do Modelo**: `/api/ml/status` para verificar métricas e estado do modelo
- **Treinamento via API**: `/api/ml/train` para retreinamento programático
- **Avaliação de Performance**: `/api/ml/evaluate` para análise de drift do modelo
- **Integração RESTful**: APIs completas para integração com sistemas externos



## 🚀 Novas Funcionalidades Implementadas FASE 3

### Sistema de Sensores Físicos (ESP32)
- **Integração com ESP32**: Sistema completo de monitoramento com sensores simulados no Wokwi
- **Sensores Implementados**:
  - Sensor de Fósforo (P): Simulado por botão físico
  - Sensor de Potássio (K): Simulado por botão físico  
  - Sensor de pH: Simulação com valores dinâmicos baseados em função senoidal
  - Sensor de umidade do solo: DHT22 para monitoramento em tempo real
- **Controle de Irrigação**: Relé automático com LED indicador baseado em lógica inteligente
- **Lógica de Controle**: Sistema ativa irrigação quando umidade < 30% E pH entre 6.0-7.5

### Upload e Importação de Dados CSV
- **Interface Web para Upload**: Formulário amigável para importação de dados do ESP32
- **Processamento Inteligente**: 
  - Detecção automática de separadores (`;` ou `,`)
  - Criação automática de sensores se necessário
  - Associação opcional com campos específicos
- **Timestamps Simulados**: Conversão automática de timestamps do ESP32 para dados realistas com intervalos de 5 minutos
- **Validação de Dados**: Verificação de formato e tratamento de erros
- **Preview de Arquivos**: Visualização das primeiras linhas antes da importação

### Dashboard de Sensores com Streamlit
- **Dashboard Interativo**: Visualização avançada de dados dos sensores
- **Gráficos Dinâmicos**: 
  - Histórico de umidade do solo
  - Evolução do pH ao longo do tempo
  - Monitoramento de nutrientes (P e K)
- **Estatísticas em Tempo Real**: Médias, mínimos, máximos e desvios padrão
- **Filtros Avançados**: Seleção por sensor e período de análise
- **Execução Integrada**: Inicialização automática do dashboard a partir da aplicação web

### Integração com API Climática
- **OpenWeather Integration**: Consulta de dados meteorológicos em tempo real
- **Decisão Inteligente de Irrigação**: 
  - Considera previsão de chuva
  - Analisa temperatura e umidade do ar
  - Combina dados climáticos com leituras dos sensores
- **Recomendações Automáticas**: Sistema sugere quando irrigar com base no clima e solo
- **Interface Climática**: Botão na página de detalhes do campo para verificar condições

### Sistema de Relatórios Avançados
- **Relatórios por Sensor**: Análise detalhada de leituras individuais
- **Relatórios por Campo**: Visão consolidada de todos os sensores de um campo
- **Visualizações Gráficas**: Gráficos de linha, barras e indicadores
- **Exportação de Dados**: Dados formatados para análise externa
- **Estatísticas Históricas**: Geração automática de históricos por período

## 2. Arquitetura da Aplicação

A aplicação utiliza uma arquitetura de múltiplos bancos de dados:

- **MongoDB**: Armazenamento NoSQL para dados de culturas e campos
- **MySQL**: Banco relacional para dados de sensores e leituras
- **Oracle**: Banco relacional para catálogo de fabricantes e modelos de sensores

Esta abordagem híbrida permite aproveitar as vantagens de cada tecnologia:

- Flexibilidade do MongoDB para estruturas de dados variáveis
- Integridade referencial do MySQL para dados relacionados
- Robustez do Oracle para dados corporativos

### 2.1 Estrutura de Diretórios

```
FIAP-CAP1_FARMTECH_PY/
│
├── app/
│   ├── __init__.py             # Inicialização da aplicação Flask
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── web_routes.py       # Rotas para interface web
│   │   ├── api_routes.py       # Endpoints da API
│   │   ├── sensor_routes.py    # Rotas para o sistema de sensores
│   │   └── catalogo_routes.py  # Rotas para o catálogo de fabricantes/modelos
│   │   ├── ml_routes.py       # Endpoints da API para operações e fnuções do Machine Learning (ML)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cultura.py          # Modelo para culturas (MongoDB)
│   │   ├── campo.py            # Modelo para campos/áreas (MongoDB)
│   │   ├── sensor_models.py    # Modelos para sensores (MySQL)
│   │   └── oracle_models.py    # Modelos para catálogo (Oracle)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── calculo_area.py     # Cálculo de áreas
│   │   ├── calculo_insumos.py  # Cálculo de insumos
│   │   ├── db_service.py       # Interação com MongoDB
│   │   ├── sql_db_service.py   # Interação com MySQL
│   │   ├── oracle_db_service.py # Interação com Oracle
│   │   ├── weather_service.py  # 🆕 Integração com API climática
│   │   └── init_db.py          # Inicialização de dados
│   │
│   ├── scripts/               # 🆕 Scripts utilitários
│   │   ├── dashboard.py       # Dashboard Streamlit
│   │   ├── dashboard_modelo_ml.py  # Dashboard Streamlit do modelo ML
│   │   ├── importar_dados_esp32.py # Script de importação CSV
│   │   └── limpar_dados_sensor.py  # Limpeza de dados
│   │   └── fix_model_train.py  # algoritimo para ajuste nos dados de treinamento
│   │   └── train_model.py      # algoritimo de treinamento do modelo ML
│   │   └── gerar_dados_realistas.py  # algoritimo para gerar dados realistas (dados sinteticos)
│   │   └── verificar_distribuicao_dados.py  # algoritimo para verificar a distribuicao dos dados de treinamento
│   │
│   ├── static/
│   │   ├── css/style.css       # Estilos personalizados
│   │   └── js/app.js           # JavaScript da aplicação
│   │   └── images/
│   │
│   └── templates/
│       ├── base.html           # Template base
│       ├── calculadora.html    # Calculadora Agrícola
│       ├── campo_detalhes.html # Detalhes do campo (🆕 seção climática)
│       ├── campo_form.html     # Formulário de campo
│       ├── campos.html         # Lista de campos
│       ├── cultura_detalhes.html # Detalhes da cultura
│       ├── cultura_form.html   # Formulário de cultura
│       ├── index.html          # Página inicial
│       ├── culturas.html       # Lista de culturas
│       ├── sensores/           # Templates para sistema de sensores
│       │   ├── index.html      # Lista de sensores
│       │   ├── detalhe_sensor.html # Detalhes do sensor
│       │   ├── sensor_form.html    # Formulário de sensor
│       │   ├── sensores_campo.html # Sensores por campo
│       │   ├── upload_csv.html     # 🆕 Upload de dados CSV
│       │   └── relatorios.html     # Relatórios de sensores
│       ├── catalogo/           # Templates para catálogo
│       │   ├── index.html      # Catálogo de sensores
│       │   ├── detalhe_fabricante.html # Detalhes do fabricante
│       │   └── detalhe_modelo.html     # Detalhes do modelo
│       └── modo_simplificado.html # Modo Simplificado - Interface terminal
│
├── wokwi/                    # 🆕 Projeto ESP32
│   ├── screnshots/           # imagens screnshots
│   ├── sketch.ino            # Código do ESP32
|   ├── libraries.txt         # Bibliotecas do ESP32
│   ├── diagram.json          # Circuito Wokwi
│   └── README.md             # Documentação do circuito
│
├── cli/
│   └── cli_app.py              # Interface de linha de comando
|
├── logs/
│   └──                         # logs de treinamento
|
├── models/
│   └──                         # Arquivos de treinamento do modelo
|
├── doc/
│   └──                         # Arquivos de documentação, dados de exemplos (esp32), screenshots, etc
│
├── config.py                   # Configurações da aplicação
├── requirements.txt            # Dependências do projeto
├── Dockerfile                  # Configuração para Docker
├── docker-compose.yml          # Configuração para Docker Compose
└── run.py                      # Ponto de entrada da aplicação
```

### 2.2 Componentes Principais

1. **Backend (Flask)**
    - Fornece APIs RESTful para processamento de dados
    - Gerencia a lógica de negócios e cálculos
    - Interação com múltiplos bancos de dados
    - Processamento de dados de sensores
    - 🆕 Integração com ESP32 e dados climáticos
2. **Frontend (HTML/CSS/JavaScript)**
    - Interface web para interação com o usuário
    - Visualizações gráficas com Plotly
    - Dashboards para monitoramento de sensores
    - 🆕 Interface para upload de dados CSV
3. **Banco de Dados**
    - **MongoDB**: Culturas e campos
    - **MySQL**: Sensores e leituras
    - **Oracle**: Catálogo de fabricantes e modelos
4. **ESP32 Integration**
    - 🆕 Simulação no Wokwi com sensores reais
    - 🆕 Coleta automática de dados de sensores
    - 🆕 Controle automático de irrigação
5. **External Services**
    - 🆕 OpenWeather API para dados climáticos
    - 🆕 Streamlit Dashboard para visualizações avançadas
6. **CLI (Interface de Linha de Comando)**
    - Fornece acesso às funcionalidades via terminal
    - Alternativa à interface web para operações rápidas

## 3. Modelos de Dados

### 3.1 Modelos MongoDB (NoSQL)

#### 3.1.1 Cultura

```json
{
  "_id": "unique_id_cultura",
  "nome_cultura": "Mandioca",
  "nome_cientifico": "Manihot esculenta",
  "descricao": "Descrição da cultura",
  "dados_agronomicos": {
    "densidade_plantio": {
      "espacamento_m": {
        "entre_linhas": 1.0,
        "entre_plantas": 1.0
      },
      "plantas_por_hectare": 10000
    },
    "ciclo_producao_dias": {
      "minimo": 240,
      "maximo": 540
    }
  },
  "clima_solo": {
    "temperatura_ideal_c": {
      "minima": 20,
      "maxima": 27
    },
    "precipitacao_minima_mm": 500,
    "precipitacao_maxima_mm": 800,
    "tipo_solo_ideal": "arenoso ou areno-argiloso",
    "ph_ideal": {
      "minimo": 5.5,
      "maximo": 6.5
    },
    "tolerancia_salinidade": "moderada",
    "estrategias_climaticas": [
      "cobertura morta",
      "plantio em camalhões"
    ]
  },
  "fertilizantes_insumos": {
    "adubacao_NPK_por_hectare_kg": {
      "N": 60,
      "P2O5": 40,
      "K2O": 50
    },
    "adubacao_organica_recomendada": "esterco bovino ou composto orgânico",
    "correcao_solo": {
      "calagem": "calcário dolomítico",
      "gessagem": "opcional"
    },
    "frequencia_adubacao": "Plantio e cobertura aos 3-4 meses"
  }
}
```

#### 3.1.2 Campo

```json
{
  "_id": "unique_id_campo",
  "nome_produtor": "Nome do Produtor",
  "localizacao": {
    "municipio": "Município",
    "regiao": "Região"
  },
  "campo": {
    "tipo_geometria": "retangular",
    "comprimento_m": 100,
    "largura_m": 50,
    "area_total_m2": 5000,
    "area_total_hectare": 0.5,
    "cultura_plantada": "Mandioca",
    "data_plantio": "2025-03-01",
    "dados_insumos": {
      "fertilizante_utilizado": "NPK 6-12-12",
      "quantidade_total_kg": 150,
      "quantidade_por_metro_linear_kg": 0.03,
      "irrigacao": {
        "metodo": "aspersão",
        "volume_litros_por_metro": 0.5,
        "quantidade_ruas": 50,
        "quantidade_total_litros": 2500
      }
    }
  }
}
```

### 3.2 Modelos MySQL (Relacional - Sensores)

#### 3.2.1 Sensor

```python
class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)  # S1, S2, S3
    modelo = Column(String(100))
    data_instalacao = Column(Date)
    ativo = Column(Boolean, default=True)
    ultima_manutencao = Column(DateTime)

    posicao = relationship("PosicaoSensor", back_populates="sensor", uselist=False)
    leituras = relationship("LeituraSensor", back_populates="sensor")
    alertas = relationship("AlertaSensor", back_populates="sensor")
    historicos = relationship("HistoricoSensor", back_populates="sensor")
```

#### 3.2.2 PosicaoSensor

```python
class PosicaoSensor(Base):
    __tablename__ = 'posicao_sensor'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    campo_id = Column(String(50), nullable=False)  # ID do MongoDB
    latitude = Column(Float)
    longitude = Column(Float)
    profundidade = Column(Float)

    sensor = relationship("Sensor", back_populates="posicao")
```

#### 3.2.3 LeituraSensor

```python
class LeituraSensor(Base):
    __tablename__ = 'leitura_sensor'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    data_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    valor = Column(Text, nullable=False)  # Armazena valores numéricos ou JSON
    unidade = Column(String(20), nullable=False)
    valido = Column(Boolean, default=True)

    sensor = relationship("Sensor", back_populates="leituras")
```

#### 3.2.4 Outras Entidades MySQL

- **AplicacaoRecurso**: Registro de aplicações de recursos (água, fertilizantes)
- **RecomendacaoAutomatica**: Recomendações geradas pelo sistema
- **AlertaSensor**: Alertas sobre condições anormais
- **HistoricoSensor**: Histórico estatístico de leituras por período

### 3.3 Modelos Oracle (Relacional - Catálogo)

#### 3.3.1 FabricanteSensor

```python
class FabricanteSensor(OracleBase):
    __tablename__ = 'fabricante_sensor'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    pais = Column(String(50))
    website = Column(String(255))
    descricao = Column(String(500))

    # Relacionamento M:N com ModeloSensor
    modelos = relationship("ModeloSensor", secondary=fabricante_modelo, back_populates="fabricantes")
```

#### 3.3.2 ModeloSensor

```python
class ModeloSensor(OracleBase):
    __tablename__ = 'modelo_sensor'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)  # S1, S2, S3
    precisao = Column(String(50))
    faixa_medicao = Column(String(100))
    preco_referencia = Column(String(50))
    descricao = Column(String(500))

    # Relacionamento M:N com FabricanteSensor
    fabricantes = relationship("FabricanteSensor", secondary=fabricante_modelo, back_populates="modelos")
```

## 4. Funcionalidades Principais

### 4.1 Gestão de Culturas

- **Listar Culturas**: Visualização de todas as culturas cadastradas
- **Detalhes da Cultura**: Informações detalhadas sobre uma cultura específica
- **Adicionar Cultura**: Cadastro de novas culturas com informações agronômicas
- **Editar Cultura**: Modificação de dados de culturas existentes
- **Remover Cultura**: Exclusão de culturas do sistema

### 4.2 Gestão de Campos

- **Listar Campos**: Visualização de todos os campos cadastrados
- **Detalhes do Campo**: Informações detalhadas sobre um campo específico
- **Adicionar Campo**: Cadastro de novos campos com geometrias variadas
- **Editar Campo**: Modificação de dados de campos existentes
- **Remover Campo**: Exclusão de campos do sistema
- 🆕 **Informações Climáticas**: Consulta de dados meteorológicos e recomendações de irrigação

### 4.3 Calculadoras

#### 4.3.1 Calculadora de Área

Suporta cálculos para diferentes geometrias:

- **Retangular**: Comprimento × Largura
- **Triangular**: (Base × Altura) / 2
- **Circular**: π × Raio²
- **Trapezoidal**: ((Base Maior + Base Menor) × Altura) / 2

#### 4.3.2 Calculadora de Insumos

- Cálculo de fertilizantes NPK com base na cultura e área
- Estimativa de custos de fertilizantes (*valor padrão R$ 5,00/Kg*)
- Visualização da distribuição de nutrientes (N, P, K)

#### 4.3.3 Calculadora de Irrigação

- Cálculo do número de linhas/ruas com base no espaçamento da cultura
- Determinação do volume de água necessário por linha
- Cálculo do volume total de irrigação
- Visualização do layout de irrigação

#### 4.3.4 Calculadora de Plantio

- Cálculo da quantidade de plantas com base na densidade e área
- Determinação da quantidade de sementes necessárias considerando taxa de germinação
- Visualização do padrão de plantio
- Informações sobre o período recomendado para plantio

### 4.4 Sistema de Sensores

- **Cadastro e monitoramento** de sensores em campos
- Três tipos de sensores:
    - **S1**: Sensores de umidade do solo
    - **S2**: Sensores de pH
    - **S3**: Sensores de nutrientes (N, P, K)
- **Registro de leituras** manuais ou automáticas
- **Análise de dados** e geração de estatísticas
- **Recomendações automáticas** com base nas leituras
- **Alertas** para condições anormais
- **Visualização** de leituras em gráficos
- 🆕 **Integração ESP32**: Coleta automática de dados de sensores físicos simulados
- 🆕 **Upload CSV**: Interface para importação de dados coletados
- 🆕 **Dashboard Avançado**: Visualizações interativas com Streamlit
- 🆕 **Controle de Irrigação**: Sistema automático baseado em lógica inteligente

### 4.5 Catálogo de Equipamentos

- Consulta de **fabricantes** de sensores
- Visualização de **modelos disponíveis** por tipo
- Informações técnicas sobre cada modelo
- Associação entre fabricantes e modelos

### 4.6 Visualizações

- Gráficos de área para diferentes geometrias
- Gráficos de distribuição de NPK
- Visualização de linhas de irrigação
- Padrões de espaçamento para plantio
- Gráficos de leituras de sensores
- Dashboards de monitoramento
- 🆕 **Dashboard Interativo**: Análise avançada com Streamlit
- 🆕 **Gráficos Temporais**: Evolução histórica dos dados dos sensores
- 🆕 **Indicadores Climáticos**: Visualização de dados meteorológicos

### 4.7 Sistema Físico de Sensores (ESP32)

- 🆕 **Circuito Simulado**: Projeto completo no Wokwi com componentes reais
- 🆕 **Sensores Físicos**:
  - Botões para simular presença de fósforo e potássio
  - DHT22 para monitoramento de umidade
  - Simulação dinâmica de pH com função senoidal
- 🆕 **Controle Automático**: Relé e LED para sistema de irrigação
- 🆕 **Coleta de Dados**: Export automático em formato CSV
- 🆕 **Lógica Inteligente**: Decisões baseadas em múltiplos parâmetros

### 4.8 Integração Climática

- 🆕 **API OpenWeather**: Dados meteorológicos em tempo real
- 🆕 **Decisão Inteligente**: Combina dados climáticos e sensores para irrigação
- 🆕 **Previsão de Chuva**: Evita irrigação desnecessária
- 🆕 **Interface Integrada**: Botão para consulta climática nas páginas de campo

### 4.9 Modo Terminal

- Interface de linha de comando para acesso às funcionalidades
- Comandos para listar, visualizar e calcular dados
- Exportação de dados para análise em R

### **4.10 Sistema de Machine Learning**
- **Predição Inteligente de Irrigação**: Análise de múltiplas variáveis (umidade, pH, nutrientes, clima)
- **Modelos Ensemble**: RandomForest com robustez contra overfitting e interpretabilidade
- **Dados Climáticos Integrados**: Enriquecimento com dados meteorológicos da OpenWeather API
- **Balanceamento Automático**: Detecção e correção de problemas de treinamento
- **Avaliação Contínua**: Monitoramento de drift e qualidade dos modelos
- **Recomendações Contextuais**: Sugestões inteligentes baseadas em análise integrada

### **4.11 Dashboard de Análise Avançada**
- **Interface Streamlit**: Dashboard interativo para análise ML
- **Predições em Tempo Real**: Teste de cenários e análise de resultados
- **Visualizações Avançadas**: Gráficos de correlação, distribuições e tendências
- **Métricas de Performance**: Acurácia, precisão, recall e importância das features
- **Análise Exploratória**: Ferramentas para entendimento profundo dos dados


## 5. APIs

### 5.1 API de Culturas

- `GET /api/culturas`: Lista todas as culturas
- `GET /api/culturas/<id>`: Obtém detalhes de uma cultura específica
- `POST /api/culturas`: Adiciona uma nova cultura
- `PUT /api/culturas/<id>`: Atualiza uma cultura existente
- `DELETE /api/culturas/<id>`: Remove uma cultura

### 5.2 API de Campos

- `GET /api/campos`: Lista todos os campos
- `GET /api/campos/<id>`: Obtém detalhes de um campo específico
- `POST /api/campos`: Adiciona um novo campo
- `PUT /api/campos/<id>`: Atualiza um campo existente
- `DELETE /api/campos/<id>`: Remove um campo

### 5.3 API de Cálculos

- `POST /api/calculos/area`: Calcula a área com base na geometria
- `POST /api/calculos/insumos`: Calcula insumos com base na cultura e área
- `POST /api/calculos/plantas`: Calcula a quantidade de plantas com base na cultura e área

### 5.4 API de Sensores

- `GET /sensores/api/sensores`: Lista todos os sensores
- `GET /sensores/api/relatorio/sensor/<id>`: Gera relatório para um sensor
- `GET /sensores/api/relatorio/campo/<id>`: Gera relatório para um campo
- `POST /sensores/api/analisar-campo/<id>`: Analisa dados de sensores e gera recomendações
- `POST /sensores/api/aplicar-recomendacao/<id>`: Registra aplicação de uma recomendação
- `POST /sensores/api/registrar-leitura`: Registra uma nova leitura de sensor
- `POST /sensores/api/simular-leituras`: Simula leituras para testes (apenas em modo DEBUG)
- 🆕 `POST /sensores/processar-upload-csv`: Processa upload de arquivo CSV do ESP32
- 🆕 `GET /sensores/upload-csv`: Interface para upload de dados CSV
- 🆕 `POST /sensores/api/receber-dados-esp32`: Recebe dados diretamente do ESP32

### 5.5 API Climática

- 🆕 `GET /sensores/api/verificar-irrigacao-clima/<campo_id>`: Verifica necessidade de irrigação com dados climáticos
- 🆕 `POST /sensores/api/ativar-irrigacao/<campo_id>`: Ativa sistema de irrigação

### **5.6 API de Machine Learning**
- `GET /api/ml/status`: Verifica status e métricas do modelo
- `POST /api/ml/predict`: Realiza predições com dados atuais
- `POST /api/ml/train`: Inicia treinamento com parâmetros personalizados
- `POST /api/ml/retrain`: Agenda retreinamento automático
- `POST /api/ml/evaluate`: Avalia performance do modelo


## 6. Tecnologias Utilizadas

### 6.1 Backend

- **Python**: Linguagem de programação principal
- **Flask**: Framework web para o backend
- **SQLAlchemy**: ORM para bancos de dados relacionais
- **PyMongo**: Interface para MongoDB
- **cx_Oracle**: Interface para Oracle Database
- **NumPy/Pandas**: Processamento numérico para cálculos
- 🆕 **Requests**: Para integração com APIs externas (OpenWeather)

### 6.2 Frontend

- **HTML/CSS/JavaScript**: Tecnologias web padrão
- **Bootstrap**: Framework CSS para interface responsiva
- **Plotly**: Biblioteca para visualizações interativas
- **Fetch API**: Para comunicação com o backend
- 🆕 **Streamlit**: Dashboard interativo para análise avançada

### 6.3 Hardware/IoT

- 🆕 **ESP32**: Microcontrolador para coleta de dados
- 🆕 **Wokwi**: Plataforma de simulação de circuitos
- 🆕 **Sensores Simulados**: DHT22, botões, LDR
- 🆕 **Atuadores**: Relé e LED para controle de irrigação

### 6.4 Armazenamento de Dados

- **MongoDB**: Banco de dados NoSQL para armazenamento flexível de documentos
- **MySQL**: Banco de dados relacional para sensores e leituras
- **Oracle Database**: Banco de dados relacional para catálogo de equipamentos

### 6.5 Serviços Externos

- 🆕 **OpenWeather API**: Dados meteorológicos em tempo real
- 🆕 **Streamlit Cloud**: Dashboard em nuvem (opcional)

### 6.6 Implantação

- **Docker**: Contêinerização da aplicação
- **Docker Compose**: Orquestração de múltiplos contêineres

### **6.7 Machine Learning**
- **Scikit-learn**: Biblioteca principal para modelos de ML
- **Pandas/NumPy**: Processamento e análise de dados
- **Joblib**: Serialização e carregamento de modelos
- **Matplotlib/Seaborn**: Visualizações estatísticas
- **SciPy**: Computação científica avançada

### **6.8 Dashboard e Análise**
- **Streamlit**: Interface interativa para análise ML
- **Plotly**: Gráficos interativos avançados
- **Streamlit-autorefresh**: Atualizações em tempo real

## 7. Guia de Implantação

### 7.1 Requisitos

- Docker e Docker Compose
- Acesso à internet para download de dependências
- Pelo menos 4GB de RAM para execução do Oracle Database
- 🆕 **Chave API OpenWeather** (gratuita em https://openweathermap.org/api)
- 🆕 **Streamlit** (para dashboard avançado)

### 7.2 Variáveis de Ambiente

```bash
# Configurações básicas
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta

# Bancos de dados
MONGO_URI=mongodb://localhost:27017/farmtech
SQL_DATABASE_URI=mysql://farmtech:senha@localhost/farmtech_sensors
ORACLE_DATABASE_URI=oracle+cx_oracle://system:senha@localhost:1521/XE

# 🆕 API Externa
OPENWEATHER_API_KEY=sua_chave_openweather_aqui
```

### 7.3 Passos para Implantação com Docker

1. Clone o repositório:
    
    ```bash
    git clone https://github.com/thiagoparaizo/FIAP_CAP1_FarmTech_py.git
    cd FIAP_CAP1_FarmTech_py
    ```
    
2. Configure as variáveis de ambiente:
    
    ```bash
    cp .env.example .env
    # Edite o arquivo .env com suas configurações
    ```
    
3. Execute com Docker Compose:
    
    ```bash
    docker-compose up -d
    ```
    
4. Acesse a aplicação:
    
    ```
    http://localhost:5000
    ```

### 7.4 Implantação Manual

1. Configure os bancos de dados:
    
    ```bash
    
    bash
    # Iniciar MongoDB
    docker run --name farmtech-mongo -p 27017:27017 -d mongo:latest
    
    # Iniciar MySQL
    docker run --name farmtech-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=rootsenha -e MYSQL_DATABASE=farmtech_sensors -e MYSQL_USER=farmtech -e MYSQL_PASSWORD=senha -d mysql:8.0
    
    # Iniciar Oracle (opcional)
    docker run --name farmtech-oracle -p 1521:1521 -p 5500:5500 -e ORACLE_PWD=senha -e ORACLE_CHARACTERSET=AL32UTF8 -d container-registry.oracle.com/database/express:latest
    
    ```
    
2. Crie um ambiente virtual e instale as dependências:
    
    ```bash
    
    bash
    python -m venv venv
    source venv/bin/activate # No Windows: venv\Scripts\activate
    pip install -r requirements.txt
    
    ```
    
3. Configure as variáveis de ambiente:
    
    ```bash
    
    bash
    # Linux/Mac
    export FLASK_APP=run.py
    export FLASK_ENV=development
    export MONGO_URI=mongodb://localhost:27017/farmtech
    export SQL_DATABASE_URI=mysql://farmtech:senha@localhost/farmtech_sensors
    export ORACLE_DATABASE_URI=oracle+cx_oracle://system:senha@localhost:1521/XE
    
    # Windows (PowerShell)
    $env:FLASK_APP = "run.py"
    $env:FLASK_ENV = "development"
    $env:MONGO_URI = "mongodb://localhost:27017/farmtech"
    $env:SQL_DATABASE_URI = "mysql://farmtech:senha@localhost/farmtech_sensors"
    $env:ORACLE_DATABASE_URI = "oracle+cx_oracle://system:senha@localhost:1521/XE"
    
    ```
    
4. Execute a aplicação:
    
    ```bash
    
    bash
    flask run
    
    ```

## 🚀 **Execução - COMANDOS**

### **Dashboard ML Streamlit:**
```bash
# Iniciar dashboard de análise ML
streamlit run app/scripts/dashboard_ml.py

# Acesso: http://localhost:8501
```

### **Treinamento de Modelos:**
```bash
# Treinamento básico
python app/scripts/train_model.py

# Treinamento com parâmetros personalizados
python app/scripts/train_model.py --days 60 --min-samples 100

# Corrigir problemas de dados balanceados
python app/scripts/fix_model_training.py
```

    

## 8. Próximos Desenvolvimentos

O EasyAgro está em evolução constante, com módulos adicionais planejados para as próximas versões:

### 8.1 Registro de Atividades (Caderno de Campo Digital)

- **Registro de Plantio**: dados sobre cultura, data, área, variedade e quantidade
- **Registro de Tratos e Insumos**: aplicações de fertilizantes, defensivos e ocorrências
- **Registro de Colheita**: data, quantidade e rastreabilidade por lote
- **Registro de Vendas**: data, produto, quantidade, preço e comprador

### 8.2 Análise Integrada

- **Produtividade**: cálculos por hectare e cultura
- **Custos vs. Receitas**: análise financeira por safra
- **Calendário de Atividades**: linha do tempo da safra
- **Alertas Automáticos**: notificações para colheita, plantio e manutenção
- **Indicadores de Perdas**: comparação entre colhido e previsto
- **Relatório Climático**: integração com dados meteorológicos

### 8.3 Expansão de IoT

- **Monitoramento Ambiental Ampliado**: mais tipos de sensores
- **Atuadores Automatizados**: controle remoto de irrigação e equipamentos
- **Integração com Drones**: mapeamento aéreo e detecção de problemas
- **Alertas em Tempo Real**: notificação imediata para condições críticas

### 8.4 Módulo de Crédito e Documentos

- **Ficha do Produtor**: relatório resumido da propriedade
- **Porta-documentos Digital**: armazenamento seguro de documentos importantes
- **Integração com Programas de Financiamento**: facilitação de acesso a crédito
- **Apoio à Certificação**: suporte a processos de certificação orgânica e outras

### 8.5 Usabilidade e Treinamento

- **Design Centrado no Usuário**: melhorias contínuas na interface
- **Sistema de Ajuda Integrado**: tutoriais passo a passo
- **Material de Treinamento**: guias e vídeos explicativos
- **Gamificação**: sistema de recompensas para engajamento contínuo

### **8.6 Inteligência Artificial Avançada**
- **Deep Learning**: Redes neurais para padrões complexos
- **Computer Vision**: Análise de imagens de plantações via drones
- **NLP para Agricultura**: Processamento de relatórios e recomendações
- **IoT Intelligence**: Fusão de dados de múltiplos sensores
- **Previsão Sazonal**: Modelos preditivos de longo prazo
- **Otimização Automática**: Ajuste automático de parâmetros de irrigação

## 9. Exemplos de Uso

### 9.1 Exemplo - Sistema de Cultura e Campo

1. Cadastrar uma nova cultura (ex: Mandioca)
2. Adicionar um campo com geometria retangular
3. Visualizar os cálculos automáticos de área e insumos
4. Usar as calculadoras para planejamento de plantio

### 9.2 Exemplo - Sistema de Sensores

1. Adicionar sensores a um campo existente
2. Registrar leituras manuais ou usar o simulador
3. Analisar dados e gerar recomendações
4. Visualizar histórico de leituras em gráficos

### 9.3 Exemplo - Catálogo de Equipamentos

1. Explorar fabricantes de sensores
2. Visualizar modelos disponíveis por tipo
3. Comparar especificações técnicas
4. Verificar compatibilidade com o sistema

### **9.4 Exemplo - Sistema de Machine Learning**

1. **Gerar dados balanceados para treinamento:**
```bash
python app/scripts/fix_model_training.py
```

2. **Treinar modelo com dados históricos:**
```bash
python app/scripts/train_model.py --days 30 --min-samples 20
```

3. **Verificar status do modelo via API:**
```bash
curl http://localhost:5000/api/ml/status
```

4. **Fazer predição de irrigação:**
```bash
curl -X POST http://localhost:5000/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{"umidade": 25.5, "ph": 6.8, "fosforo": 1, "potassio": 0}'
```

5. **Acessar dashboard de análise:**
```bash
streamlit run app/scripts/dashboard_ml.py
# Acesse: http://localhost:8501
```

## 10. Resolução de Problemas

### 10.1 Problemas Comuns

1. **Erro de conexão com bancos de dados**:
    - Verifique se os serviços de banco de dados estão em execução
    - Confirme se as credenciais estão corretas nas variáveis de ambiente
2. **Erro ao instalar dependências**:
    - Para o Oracle, você pode precisar do Oracle Instant Client
    - Para o MySQL, pode ser necessário instalar bibliotecas de desenvolvimento
3. **Erro no sistema de sensores**:
    - Verifique se as tabelas foram criadas corretamente
    - Para erros de formato de dados, o tipo Text pode ser necessário

### 10.2 Logs e Diagnóstico

- Verifique os logs do servidor Flask para detalhes sobre erros
- Use o console do navegador para verificar erros de JavaScript
- Em caso de problemas com Docker, verifique os logs dos contêineres

## 11. Conclusão

O EasyAgro é uma plataforma completa para gestão agrícola digital, com foco especial em pequenos produtores rurais. Combinando gestão de culturas, campos, monitoramento por sensores e análise de dados, a aplicação oferece ferramentas poderosas em uma interface acessível.

Com sua arquitetura multi-banco de dados, a plataforma demonstra como diferentes tecnologias podem ser combinadas para criar soluções robustas e escaláveis, mantendo a simplicidade necessária para seu público-alvo.

O projeto está em constante evolução, com novas funcionalidades planejadas para tornar a plataforma ainda mais completa e útil no dia a dia do produtor rural.

[Leia a pesquisa completa ](setup/search.md)

## 🗃 Histórico de lançamentos

* 1.0.0 - 27/03/2025
    * 
* 1.1.0 - 22/04/2025
    * 


## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
