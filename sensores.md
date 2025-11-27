# Sistema de Sensores - FarmTech Solutions

Esta parte do projeto FarmTech Solutions implementa a integração com sensores físicos para monitoramento de solo e controle de irrigação.

## Descrição do Sistema

O sistema utiliza sensores simulados no ambiente Wokwi.com com um ESP32 para coletar dados de:

- **Sensor de Fósforo (P)**: Simula a presença ou ausência de fósforo no solo
- **Sensor de Potássio (K)**: Simula a presença ou ausência de potássio no solo
- **Sensor de pH**: Mede o nível de acidez ou alcalinidade do solo
- **Sensor de Umidade do Solo**: Mede a porcentagem de umidade presente no solo

Estes dados são coletados pelo ESP32 e enviados para nosso sistema backend, que processa as informações e fornece análises e recomendações para o gerenciamento da irrigação.

## Circuito ESP32

![Circuito ESP32 no Wokwi](https://exemplo.com/imagem-do-circuito.png)

### Componentes utilizados:
- ESP32 DevKit V1
- Botões para simular sensores de nutrientes (P e K)
- LDR (Light Dependent Resistor) para simular sensor de pH
- Sensor DHT22 para simular sensor de umidade do solo
- LED e relé para controle de irrigação

## Lógica de Controle da Irrigação

O sistema ativa a irrigação automaticamente quando:
1. A umidade do solo está abaixo de 30%, E
2. O pH do solo está dentro dos limites aceitáveis (entre 6.0 e 7.5)

A irrigação é desativada quando:
1. A umidade do solo ultrapassa 70%, OU
2. O pH do solo está fora dos limites aceitáveis

Além disso, o sistema considera dados climáticos obtidos via API para evitar irrigação desnecessária quando há previsão de chuva.

## Integração com o Sistema Backend

Os dados dos sensores são enviados ao sistema backend através de:

1. **API REST**: O ESP32 pode enviar dados diretamente via HTTP POST
2. **Importação Manual**: Um script Python permite importar dados CSV do monitor serial

### Fluxo de Dados

1. ESP32 coleta leituras dos sensores
2. Os dados são enviados para o servidor ou salvos em CSV
3. O sistema processa os dados e armazena no banco de dados SQL
4. Os dados são analisados para gerar recomendações de irrigação
5. A interface web exibe as informações e permite o controle manual

## Integração com API de Clima

O sistema utiliza a API OpenWeather para obter dados meteorológicos em tempo real, auxiliando nas decisões de irrigação ao considerar:

- Temperatura atual
- Umidade do ar
- Condições climáticas (chuva, sol, nublado)
- Previsão de chuva nas próximas horas

## Dashboard de Visualização

Uma dashboard interativa construída com Streamlit permite visualizar:

- Gráficos históricos de umidade do solo
- Gráficos históricos de pH
- Monitoramento de nutrientes (P e K)
- Estatísticas sobre o estado atual do solo
- Recomendações de irrigação baseadas nos dados coletados

## Banco de Dados e Operações CRUD

Os dados dos sensores são armazenados em um banco SQL com as seguintes tabelas principais:

- `sensor`: Armazena informações sobre os sensores instalados
- `posicao_sensor`: Registra a localização física dos sensores nos campos
- `leitura_sensor`: Armazena as leituras periódicas dos sensores
- `aplicacao_recurso`: Registra irrigações e aplicações de fertilizantes
- `recomendacao_automatica`: Armazena recomendações geradas pelo sistema

O sistema implementa operações CRUD completas para todas as entidades, permitindo:
- **Create**: Adicionar novos sensores e registrar leituras
- **Read**: Consultar leituras e histórico de sensores
- **Update**: Atualizar posição e estado dos sensores
- **Delete**: Remover leituras inválidas e sensores desativados

## Como Utilizar

### 1. Configuração do ESP32
- Carregue o código para o ESP32 usando a plataforma Wokwi ou Arduino IDE
- Conecte os sensores conforme o diagrama do circuito

### 2. Importação Manual de Dados
```bash
python scripts/importar_dados_esp32.py caminho/para/arquivo.csv id_do_sensor
```	

### 3 Monitoramento via Dashboard
```bash
cd scripts
streamlit run dashboard.py
```	
### 4 Configuração da API de Clima
- Acesse https://openweathermap.org/api para obter uma chave de API
- Configure a chave na variável `OPENWEATHER_API_KEY` no arquivo `.env`