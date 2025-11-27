# Modelagem de Entidade-Relacionamento (MER)

## Entidades Principais

### 1. Sensor

- `ID` (PK, INT): Identificador único do sensor  
- `Tipo` (VARCHAR): Tipo do sensor (`S1-umidade`, `S2-pH`, `S3-nutrientes`)  
- `Modelo` (VARCHAR): Modelo/fabricante do sensor  
- `DataInstalacao` (DATE): Data em que o sensor foi instalado  
- `Ativo` (BOOLEAN): Indica se o sensor está ativo  
- `UltimaManutencao` (DATETIME): Data e hora da última manutenção  

---

### 2. PosicaoSensor

- `ID` (PK, INT): Identificador único da posição  
- `SensorID` (FK, INT): Referência ao sensor  
- `CampoID` (VARCHAR): Referência ao campo (do MongoDB)  
- `Latitude` (DOUBLE): Coordenada de latitude  
- `Longitude` (DOUBLE): Coordenada de longitude  
- `Profundidade` (DOUBLE): Profundidade do sensor em cm (relevante para sensores de solo)  

---

### 3. LeituraSensor

- `ID` (PK, INT): Identificador único da leitura  
- `SensorID` (FK, INT): Referência ao sensor que fez a leitura  
- `DataHora` (DATETIME): Data e hora da leitura  
- `Valor` (DOUBLE): Valor registrado  
- `Unidade` (VARCHAR): Unidade de medida (`%`, `pH`, `ppm`)  
- `Valido` (BOOLEAN): Indica se a leitura é válida  

---

### 4. AplicacaoRecurso

- `ID` (PK, INT): Identificador único da aplicação  
- `CampoID` (VARCHAR): Referência ao campo (do MongoDB)  
- `DataHora` (DATETIME): Data e hora da aplicação  
- `TipoRecurso` (VARCHAR): Tipo do recurso (`água`, `fertilizante`, `corretivo`)  
- `Quantidade` (DOUBLE): Quantidade aplicada  
- `Unidade` (VARCHAR): Unidade de medida (`L`, `kg`, `g`)  
- `MetodoAplicacao` (VARCHAR): Método utilizado (`irrigação`, `pulverização`, etc)  

---

### 5. RecomendacaoAutomatica

- `ID` (PK, INT): Identificador único da recomendação  
- `CampoID` (VARCHAR): Referência ao campo (do MongoDB)  
- `DataHora` (DATETIME): Data e hora da recomendação  
- `TipoRecurso` (VARCHAR): Tipo do recurso recomendado  
- `QuantidadeRecomendada` (DOUBLE): Quantidade recomendada  
- `Unidade` (VARCHAR): Unidade de medida  
- `BaseadoEm` (TEXT): Descrição dos dados que levaram à recomendação  
- `Aplicada` (BOOLEAN): Indica se a recomendação foi aplicada  

---

### 6. AlertaSensor

- `ID` (PK, INT): Identificador único do alerta  
- `SensorID` (FK, INT): Referência ao sensor  
- `DataHora` (DATETIME): Data e hora do alerta  
- `Tipo` (VARCHAR): Tipo do alerta (`valor anormal`, `falha técnica`)  
- `Mensagem` (TEXT): Descrição do alerta  
- `Severidade` (VARCHAR): Nível de severidade (`baixa`, `média`, `alta`)  
- `Resolvido` (BOOLEAN): Indica se o alerta foi resolvido  

---

### 7. HistoricoSensor

- `ID` (PK, INT): Identificador único do registro  
- `SensorID` (FK, INT): Referência ao sensor  
- `DataInicio` (DATE): Data de início do período  
- `DataFim` (DATE): Data de fim do período  
- `MediaLeituras` (DOUBLE): Média das leituras no período  
- `MinLeitura` (DOUBLE): Valor mínimo registrado  
- `MaxLeitura` (DOUBLE): Valor máximo registrado  
- `DesvioPadrao` (DOUBLE): Desvio padrão das leituras  

---

## Relacionamentos

- **Sensor → PosicaoSensor**: Um sensor pode estar em uma posição (1:1)  
- **Sensor → LeituraSensor**: Um sensor pode ter várias leituras (1:N)  
- **Sensor → AlertaSensor**: Um sensor pode gerar vários alertas (1:N)  
- **Sensor → HistoricoSensor**: Um sensor pode ter vários registros históricos (1:N)  
- **CampoID**: Conexão com o MongoDB através do ID do campo  

---

## Cardinalidade

- **Sensor → PosicaoSensor**: (1:1) Um sensor está em uma posição específica  
- **Sensor → LeituraSensor**: (1:N) Um sensor faz múltiplas leituras  
- **CampoID → PosicaoSensor**: (1:N) Um campo pode ter múltiplos sensores  
- **CampoID → AplicacaoRecurso**: (1:N) Um campo pode receber múltiplas aplicações  
- **CampoID → RecomendacaoAutomatica**: (1:N) Um campo pode receber múltiplas recomendações  
