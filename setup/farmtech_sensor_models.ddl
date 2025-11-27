-- Tabela de Sensores
CREATE TABLE Sensor (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Tipo VARCHAR(50) NOT NULL,  -- S1, S2, S3
    Modelo VARCHAR(100),
    DataInstalacao DATE,
    Ativo BOOLEAN DEFAULT TRUE,
    UltimaManutencao DATETIME
);

-- Tabela de Posição dos Sensores
CREATE TABLE PosicaoSensor (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    SensorID INT,
    CampoID VARCHAR(50) NOT NULL,  -- ID do MongoDB
    Latitude DOUBLE,
    Longitude DOUBLE,
    Profundidade DOUBLE,
    FOREIGN KEY (SensorID) REFERENCES Sensor(ID)
);

-- Tabela de Leituras dos Sensores
CREATE TABLE LeituraSensor (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    SensorID INT,
    DataHora DATETIME NOT NULL,
    Valor DOUBLE NOT NULL,
    Unidade VARCHAR(20) NOT NULL,
    Valido BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (SensorID) REFERENCES Sensor(ID)
);

-- Tabela de Aplicação de Recursos
CREATE TABLE AplicacaoRecurso (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    CampoID VARCHAR(50) NOT NULL,  -- ID do MongoDB
    DataHora DATETIME NOT NULL,
    TipoRecurso VARCHAR(50) NOT NULL,
    Quantidade DOUBLE NOT NULL,
    Unidade VARCHAR(20) NOT NULL,
    MetodoAplicacao VARCHAR(100)
);

-- Tabela de Recomendações Automáticas
CREATE TABLE RecomendacaoAutomatica (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    CampoID VARCHAR(50) NOT NULL,  -- ID do MongoDB
    DataHora DATETIME NOT NULL,
    TipoRecurso VARCHAR(50) NOT NULL,
    QuantidadeRecomendada DOUBLE NOT NULL,
    Unidade VARCHAR(20) NOT NULL,
    BaseadoEm TEXT,
    Aplicada BOOLEAN DEFAULT FALSE
);

-- Tabela de Alertas dos Sensores
CREATE TABLE AlertaSensor (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    SensorID INT,
    DataHora DATETIME NOT NULL,
    Tipo VARCHAR(50) NOT NULL,
    Mensagem TEXT,
    Severidade VARCHAR(20) DEFAULT 'média',
    Resolvido BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (SensorID) REFERENCES Sensor(ID)
);

-- Tabela de Histórico dos Sensores (agregações)
CREATE TABLE HistoricoSensor (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    SensorID INT,
    DataInicio DATE NOT NULL,
    DataFim DATE NOT NULL,
    MediaLeituras DOUBLE,
    MinLeitura DOUBLE,
    MaxLeitura DOUBLE,
    DesvioPadrao DOUBLE,
    FOREIGN KEY (SensorID) REFERENCES Sensor(ID)
);