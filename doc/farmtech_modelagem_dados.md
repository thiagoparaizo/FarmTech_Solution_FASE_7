# Análise da Modelagem de Dados - FarmTech Solutions

## 📋 Índice
1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Estrutura dos Bancos de Dados](#estrutura-dos-bancos-de-dados)
3. [MongoDB - Dados Principais](#mongodb---dados-principais)
4. [MySQL - Dados de Sensores](#mysql---dados-de-sensores)
5. [Oracle - Catálogo de Produtos](#oracle---catálogo-de-produtos)
6. [Benefícios da Arquitetura Poliglota](#benefícios-da-arquitetura-poliglota)
7. [Justificativas Técnicas](#justificativas-técnicas)
8. [Padrões de Design Utilizados](#padrões-de-design-utilizados)

---

## 🏗️ Visão Geral da Arquitetura

O projeto FarmTech Solutions adota uma **arquitetura poliglota de persistência**, utilizando três diferentes sistemas de banco de dados, cada um otimizado para tipos específicos de dados e operações:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     MongoDB     │    │      MySQL      │    │     Oracle      │
│  (NoSQL/Doc)    │    │  (Relacional)   │    │  (Relacional)   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Culturas      │    │ • Sensores      │    │ • Fabricantes   │
│ • Campos        │    │ • Leituras      │    │ • Modelos       │
│ • Insumos       │    │ • Alertas       │    │ • Catálogo      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🗄️ Estrutura dos Bancos de Dados

### MongoDB - Dados Principais

#### Modelo de Cultura
```javascript
{
  "_id": "ObjectId",
  "nome_cultura": "Mandioca",
  "nome_cientifico": "Manihot esculenta",
  "descricao": "Descrição da cultura...",
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
    "ph_ideal": {
      "minimo": 5.5,
      "maximo": 6.5
    }
  },
  "fertilizantes_insumos": {
    "adubacao_NPK_por_hectare_kg": {
      "N": 60,
      "P2O5": 40,
      "K2O": 50
    }
  }
}
```

#### Modelo de Campo
```javascript
{
  "_id": "ObjectId",
  "nome_produtor": "João Silva",
  "localizacao": {
    "municipio": "Fortaleza",
    "regiao": "Litoral Cearense"
  },
  "campo": {
    "tipo_geometria": "retangular",
    "comprimento_m": 100,
    "largura_m": 50,
    "area_total_m2": 5000,
    "area_total_hectare": 0.5,
    "cultura_plantada": "Mandioca",
    "data_plantio": "2025-01-01",
    "dados_insumos": {
      "fertilizante_recomendado": {
        "N": 30,
        "P2O5": 20,
        "K2O": 25
      },
      "irrigacao": {
        "metodo": "gotejamento",
        "quantidade_total_litros": 5000
      }
    }
  }
}
```

### MySQL - Dados de Sensores

#### Estrutura Relacional
```sql
-- Tabela principal de sensores
CREATE TABLE sensor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tipo VARCHAR(50) NOT NULL,
    modelo VARCHAR(100),
    data_instalacao DATE,
    ativo BOOLEAN DEFAULT TRUE,
    ultima_manutencao DATETIME
);

-- Posicionamento dos sensores
CREATE TABLE posicao_sensor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sensor_id INT,
    campo_id VARCHAR(50),  -- Referência ao MongoDB
    latitude FLOAT,
    longitude FLOAT,
    profundidade FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES sensor(id)
);

-- Leituras dos sensores
CREATE TABLE leitura_sensor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sensor_id INT,
    data_hora DATETIME NOT NULL,
    valor TEXT NOT NULL,
    unidade VARCHAR(20) NOT NULL,
    valido BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (sensor_id) REFERENCES sensor(id)
);

-- Aplicações de recursos
CREATE TABLE aplicacao_recurso (
    id INT PRIMARY KEY AUTO_INCREMENT,
    campo_id VARCHAR(50) NOT NULL,
    data_hora DATETIME NOT NULL,
    tipo_recurso VARCHAR(50) NOT NULL,
    quantidade FLOAT NOT NULL,
    unidade VARCHAR(20) NOT NULL,
    metodo_aplicacao VARCHAR(100)
);
```

### Oracle - Catálogo de Produtos

#### Estrutura Enterprise
```sql
-- Fabricantes de sensores
CREATE TABLE fabricante_sensor (
    id NUMBER PRIMARY KEY,
    nome VARCHAR2(100) NOT NULL,
    pais VARCHAR2(50),
    website VARCHAR2(200),
    descricao CLOB
);

-- Modelos de sensores
CREATE TABLE modelo_sensor (
    id NUMBER PRIMARY KEY,
    nome VARCHAR2(100) NOT NULL,
    tipo VARCHAR2(10) NOT NULL,
    precisao VARCHAR2(50),
    faixa_medicao VARCHAR2(50),
    preco_referencia VARCHAR2(50),
    descricao CLOB
);

-- Relacionamento N:N
CREATE TABLE fabricante_modelo (
    fabricante_id NUMBER,
    modelo_id NUMBER,
    PRIMARY KEY (fabricante_id, modelo_id),
    FOREIGN KEY (fabricante_id) REFERENCES fabricante_sensor(id),
    FOREIGN KEY (modelo_id) REFERENCES modelo_sensor(id)
);
```

---

## 📊 MongoDB - Dados Principais

### ✅ Por que MongoDB?

**1. Flexibilidade de Schema**
- Estruturas aninhadas complexas (culturas com dados agronômicos, climáticos e de insumos)
- Evolução natural do schema sem migrations complexas
- Documentos auto-descritivos

**2. Modelagem Natural de Domínio**
- Culturas e campos são entidades complexas com múltiplas propriedades
- Relacionamentos naturally embedded (dados de insumos dentro do campo)
- Queries intuitivas para dados hierárquicos

**3. Escalabilidade Horizontal**
- Sharding nativo para crescimento de dados
- Replicação automática para alta disponibilidade
- Performance em leituras complexas

### 🎯 Casos de Uso Específicos

```python
# Busca complexa facilitada
campos_mandioca = db.campos.find({
    "campo.cultura_plantada": "Mandioca",
    "campo.area_total_hectare": {"$gte": 1.0},
    "localizacao.regiao": "Litoral Cearense"
})

# Aggregation para relatórios
pipeline = [
    {"$group": {
        "_id": "$campo.cultura_plantada",
        "total_area": {"$sum": "$campo.area_total_hectare"},
        "media_area": {"$avg": "$campo.area_total_hectare"}
    }}
]
```

---

## 🔗 MySQL - Dados de Sensores

### ✅ Por que MySQL?

**1. ACID Compliance**
- Leituras de sensores precisam de consistência transacional
- Histórico de dados crítico não pode ser perdido
- Integridade referencial garantida

**2. Otimização para Time Series**
- Índices otimizados para consultas temporais
- Particionamento por data
- Agregações estatísticas eficientes

**3. Relacionamentos Complexos**
- FKs entre sensores, posições e leituras
- Joins eficientes para relatórios
- Constraints de integridade

### 🎯 Casos de Uso Específicos

```sql
-- Consulta temporal otimizada
SELECT 
    s.id, s.tipo,
    AVG(CAST(l.valor AS DECIMAL(10,2))) as media_valor,
    COUNT(*) as total_leituras
FROM sensor s
JOIN leitura_sensor l ON s.id = l.sensor_id
WHERE l.data_hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND l.valido = TRUE
GROUP BY s.id, s.tipo;

-- Análise de tendências
SELECT 
    DATE(data_hora) as dia,
    AVG(CAST(valor AS DECIMAL(10,2))) as media_diaria
FROM leitura_sensor 
WHERE sensor_id = 1 
    AND data_hora >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(data_hora)
ORDER BY dia;
```

---

## 🏢 Oracle - Catálogo de Produtos

### ✅ Por que Oracle?

**1. Robustez Enterprise**
- Catálogo de produtos requer alta confiabilidade
- Recursos avançados de backup e recovery
- Segurança enterprise-grade

**2. Performance em Consultas Complexas**
- Otimizador de consultas avançado
- Índices especializados
- Paralelização automática

**3. Recursos Analíticos**
- Window functions para análises avançadas
- Particionamento sofisticado
- Materialized views para performance

### 🎯 Casos de Uso Específicos

```sql
-- Consulta analítica complexa
SELECT 
    f.nome as fabricante,
    f.pais,
    COUNT(m.id) as total_modelos,
    AVG(TO_NUMBER(REGEXP_SUBSTR(m.preco_referencia, '\d+\.\d+'))) as preco_medio
FROM fabricante_sensor f
JOIN fabricante_modelo fm ON f.id = fm.fabricante_id
JOIN modelo_sensor m ON fm.modelo_id = m.id
GROUP BY f.nome, f.pais
HAVING COUNT(m.id) > 1
ORDER BY total_modelos DESC;
```

---

## 🚀 Benefícios da Arquitetura Poliglota

### 1. **Otimização por Caso de Uso**
- **MongoDB**: Documentos complexos e flexíveis
- **MySQL**: Time series e transações ACID
- **Oracle**: Análises complexas e confiabilidade enterprise

### 2. **Performance Especializada**
```
Operação                    | Banco Otimizado | Justificativa
----------------------------|-----------------|------------------
Busca de culturas          | MongoDB         | Queries em documentos aninhados
Séries temporais           | MySQL           | Índices temporais otimizados
Relatórios analíticos      | Oracle          | Window functions e paralelização
Inserção de leituras       | MySQL           | Transações ACID rápidas
Agregações de campo        | MongoDB         | Pipeline de agregação nativo
```

### 3. **Escalabilidade Diferenciada**
- **MongoDB**: Sharding horizontal para dados de domínio
- **MySQL**: Particionamento temporal para séries de dados
- **Oracle**: Clustering e paralelização para análises

### 4. **Manutenibilidade**
- Cada banco com responsabilidade específica
- Evolução independente dos schemas
- Backup e recovery especializados

---

## 🔧 Justificativas Técnicas

### Integração entre Bancos

```python
class DatabaseService:
    def __init__(self):
        self.mongo_db = MongoClient(MONGO_URI)
        self.mysql_db = create_engine(MYSQL_URI)
        self.oracle_db = create_engine(ORACLE_URI)
    
    def criar_campo_com_sensores(self, campo_data, sensores):
        # 1. Criar campo no MongoDB
        campo_id = self.mongo_db.campos.insert_one(campo_data)
        
        # 2. Criar sensores no MySQL
        for sensor in sensores:
            sensor_id = self.mysql_db.execute(
                "INSERT INTO sensor (...) VALUES (...)"
            )
            
            # 3. Associar posição
            self.mysql_db.execute(
                "INSERT INTO posicao_sensor (sensor_id, campo_id) VALUES (?, ?)",
                (sensor_id, str(campo_id))
            )
```

## 🎨 Padrões de Design Utilizados

### 1. **Service Layer**
```python
class AnaliseService:
    def __init__(self, cultura_repo, sensor_repo, catalogo_repo):
        self.cultura_repo = cultura_repo
        self.sensor_repo = sensor_repo
        self.catalogo_repo = catalogo_repo
    
    def gerar_recomendacao(self, campo_id):
        # Combina dados dos 3 bancos
        pass
```
---

## 📈 Métricas de Performance

### Comparativo de Performance por Operação (Dados Ilustrativos)

| Operação | MongoDB | MySQL | Oracle | Banco Escolhido | Motivo |
|----------|---------|-------|--------|-----------------|--------|
| Inserir cultura | **50ms** | 120ms | 200ms | MongoDB | Schema flexível |
| Query temporal | 300ms | **20ms** | 80ms | MySQL | Índices temporais |
| Análise complexa | 500ms | 400ms | **100ms** | Oracle | Otimizador avançado |
| Busca por localização | **80ms** | 250ms | 180ms | MongoDB | Queries geoespaciais |

### Escalabilidade (Dados Ilustrativos)

```
Cenário: 1M registros de leituras/dia

MongoDB (Culturas):
- 10K documentos
- Crescimento: Linear
- Sharding: Geográfico

MySQL (Sensores):
- 1M+ registros/dia
- Crescimento: Exponencial
- Particionamento: Por data

Oracle (Catálogo):
- 1K produtos
- Crescimento: Mínimo
- Otimização: Índices especializados
```

---

## 🎯 Conclusão

A arquitetura poliglota do FarmTech Solutions oferece:

### ✅ **Vantagens Principais**
1. **Performance Otimizada**: Cada banco na sua especialidade
2. **Escalabilidade Adequada**: Estratégias específicas por tipo de dado
3. **Flexibilidade**: Evolução independente dos componentes
4. **Manutenibilidade**: Responsabilidades bem definidas
5. **Robustez**: Falha em um banco não afeta os outros

### 🔄 **Trade-offs Aceitos**
1. **Complexidade**: Múltiplos bancos para gerenciar
2. **Consistência**: Eventual consistency em alguns cenários
3. **Latência**: Possíveis delays em operações cross-database
4. **Curva de Aprendizado**: Expertise em múltiplas tecnologias

### 🚀 **Resultado Final**
Uma solução robusta, escalável e performática que atende às necessidades específicas da agricultura de precisão, aproveitando o melhor de cada tecnologia de banco de dados.

---

**Desenvolvido por**: Equipe FarmTech Solutions  
**Data**: Janeiro 2025  
**Versão**: 1.0