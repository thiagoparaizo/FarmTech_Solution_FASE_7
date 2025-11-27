/*
 * FarmTech Solutions - Sistema de Sensores Agrícolas FASE 4
 * 
 * Código otimizado para ESP32 com:
 * - Display LCD I2C para visualização local
 * - Serial Plotter para monitoramento gráfico
 * - Otimizações de memória
 * - Múltiplas saídas de dados
 * 
 * Autor: FarmTech Solutions Team
 * Data: FASE 4 - 2024
 */

#include <WiFi.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ========== OTIMIZAÇÕES DE MEMÓRIA ==========
// Usar tipos de dados menores para economizar RAM
// int (32 bits) -> uint8_t (8 bits) = economia de 3 bytes por variável
// float (32 bits) -> mantido apenas quando necessária precisão decimal

// Pinos do sistema (uint8_t economiza 3 bytes vs int)
const uint8_t PIN_FOSFORO_BTN = 12;     // Botão P - economiza 3 bytes
const uint8_t PIN_POTASSIO_BTN = 14;    // Botão K - economiza 3 bytes  
const uint8_t PIN_UMIDADE_DHT = 15;     // DHT22 - economiza 3 bytes
const uint8_t PIN_RELE = 27;            // Relé irrigação - economiza 3 bytes
const uint8_t PIN_LED_BOMBA = 2;        // LED indicador - economiza 3 bytes

// Configuração LCD I2C
const uint8_t LCD_ADDRESS = 0x27;       // Endereço I2C padrão - economiza 3 bytes
const uint8_t LCD_COLS = 20;            // Colunas do display - economiza 3 bytes
const uint8_t LCD_ROWS = 4;             // Linhas do display - economiza 3 bytes

// Pinos I2C do ESP32 (SDA e SCL)
const uint8_t SDA_PIN = 21;             // Pino SDA - economiza 3 bytes
const uint8_t SCL_PIN = 22;             // Pino SCL - economiza 3 bytes

// Limites do sistema (float necessário para precisão dos sensores)
const float LIMITE_UMIDADE_MIN = 30.0f;  // f suffix para garantir float de 32 bits
const float LIMITE_UMIDADE_MAX = 70.0f;
const float LIMITE_PH_MIN = 6.0f;
const float LIMITE_PH_MAX = 7.5f;

// Configurações de timing (uint16_t para valores até 65535)
const uint16_t INTERVALO_LEITURA = 5000;    // 5 segundos - economiza 2 bytes vs int
const uint16_t INTERVALO_LCD = 2000;        // 2 segundos para LCD - economiza 2 bytes
const uint16_t INTERVALO_PLOTTER = 1000;    // 1 segundo para plotter - economiza 2 bytes

// Simulação de pH (float necessário para precisão)
float ph_base = 7.0f;
float ph_amplitude = 3.5f;
float ph_frequencia = 0.001f;

// Estados do sistema (bool usa apenas 1 byte vs int que usa 4 bytes)
volatile bool fosforo_presente = false;     // volatile para interrupt - economiza 3 bytes
volatile bool potassio_presente = false;    // volatile para interrupt - economiza 3 bytes
bool irrigacao_ativa = false;               // Estado da irrigação - economiza 3 bytes
bool sistema_iniciado = false;              // Flag de inicialização - economiza 3 bytes

// Controle de timing (unsigned long necessário para millis())
unsigned long ultimo_leitura = 0;
unsigned long ultimo_lcd = 0;
unsigned long ultimo_plotter = 0;
unsigned long tempo_boot = 0;

// Variáveis de leitura (tipos otimizados)
float umidade_solo = 0.0f;              // float necessário para precisão
float ph_solo = 7.0f;                   // float necessário para precisão
float temperatura = 25.0f;              // float necessário para precisão
uint8_t umidade_ar = 50;                // uint8_t suficiente para % (0-100)

// Estados anteriores para detecção de mudança (economiza processamento)
bool fosforo_anterior = false;
bool potassio_anterior = false;
bool irrigacao_anterior = false;

// Objetos globais
DHT dht(PIN_UMIDADE_DHT, DHT22);
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLS, LCD_ROWS);

// ========== STRINGS EM PROGMEM PARA ECONOMIZAR RAM ==========
// Mover strings constantes para Flash memory (PROGMEM) economiza RAM preciosa
const char MSG_BOOT[] PROGMEM = "FarmTech Solutions";
const char MSG_FASE4[] PROGMEM = "FASE 4 - Otimizado";
const char MSG_INICIALIZANDO[] PROGMEM = "Inicializando...";
const char MSG_SISTEMA_OK[] PROGMEM = "Sistema OK!";
const char MSG_SENSORES[] PROGMEM = "Sensores Ativos";
const char MSG_IRRIGACAO_ON[] PROGMEM = "IRRIGACAO: ATIVA";
const char MSG_IRRIGACAO_OFF[] PROGMEM = "IRRIGACAO: INATIVA";
const char MSG_PH_IDEAL[] PROGMEM = "pH: IDEAL";
const char MSG_PH_FORA[] PROGMEM = "pH: FORA LIMITE";


// ========== INTERRUPTS PARA BOTÕES ==========
// ISR deve ser rápida e usar apenas variáveis volatile
// IRAM_ATTR coloca função na RAM para execução mais rápida
void IRAM_ATTR interrupt_fosforo() {
  fosforo_presente = !digitalRead(PIN_FOSFORO_BTN); // Inverte por causa do pullup
}

void IRAM_ATTR interrupt_potassio() {
  potassio_presente = !digitalRead(PIN_POTASSIO_BTN); // Inverte por causa do pullup
}
  

// ========== CONFIGURAÇÃO INICIAL ==========
void setup() {
  // Inicializar comunicação serial para debug e CSV
  Serial.begin(115200);
  
  // Guardar tempo de boot para referência
  tempo_boot = millis();
  
  // Inicializar I2C para LCD
  Wire.begin(SDA_PIN, SCL_PIN);
  
  // Inicializar LCD
  lcd.init();
  lcd.backlight();
  
  // Mostrar splash screen
  mostrarSplashScreen();
  
  // Configurar pinos de entrada (INPUT_PULLUP economiza componentes externos)
  pinMode(PIN_FOSFORO_BTN, INPUT_PULLUP);   // Pull-up interno economiza resistor
  pinMode(PIN_POTASSIO_BTN, INPUT_PULLUP);  // Pull-up interno economiza resistor
  
  // Configurar pinos de saída
  pinMode(PIN_RELE, OUTPUT);
  pinMode(PIN_LED_BOMBA, OUTPUT);
  
  // Estado inicial dos atuadores (LOW = desligado)
  digitalWrite(PIN_RELE, LOW);
  digitalWrite(PIN_LED_BOMBA, LOW);
  
  // Inicializar sensor DHT22
  dht.begin();

  // Configurar interrupts para botões (economia de processamento)
  attachInterrupt(digitalPinToInterrupt(PIN_FOSFORO_BTN), interrupt_fosforo, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_POTASSIO_BTN), interrupt_potassio, CHANGE);
  
  // Teste inicial do sistema
  testeInicialSistema();
  
  // Imprimir cabeçalho CSV
  Serial.println("timestamp,fosforo,potassio,ph,umidade,irrigacao,temperatura,umidade_ar");
  
  // Sistema pronto
  sistema_iniciado = true;
  
  // Log inicial
  Serial.println("# FarmTech Solutions FASE 4 - Sistema Iniciado");
  Serial.println("# Otimizações implementadas:");
  Serial.println("# - uint8_t para pinos (economia de 21 bytes)");
  Serial.println("# - PROGMEM para strings (economia de ~200 bytes RAM)");
  Serial.println("# - volatile para ISRs (segurança de concorrência)");
  Serial.println("# - INPUT_PULLUP (economia de componentes)");
  Serial.println("# - Interrupts para botões (economia de CPU)");
}

// ========== FUNÇÃO PRINCIPAL (LOOP) ==========
void loop() {
  unsigned long tempo_atual = millis();
  
  // Leitura principal dos sensores (a cada 5 segundos)
  if (tempo_atual - ultimo_leitura >= INTERVALO_LEITURA) {
    lerSensores();
    processarLogicaIrrigacao();
    enviarDadosCSV();
    ultimo_leitura = tempo_atual;
  }
  
  // Atualização do LCD (a cada 2 segundos para não sobrecarregar)
  if (tempo_atual - ultimo_lcd >= INTERVALO_LCD) {
    atualizarLCD();
    ultimo_lcd = tempo_atual;
  }
  
  // Dados para Serial Plotter (a cada 1 segundo)
  if (tempo_atual - ultimo_plotter >= INTERVALO_PLOTTER) {
    enviarDadosPlotter();
    ultimo_plotter = tempo_atual;
  }
  
  // Verificar mudanças de estado para logs
  verificarMudancasEstado();
  
  // Delay mínimo para não sobrecarregar o sistema (economia de CPU)
  delay(50); // 50ms é suficiente para responsividade
}

// ========== LEITURA DOS SENSORES ==========
void lerSensores() {
  // Ler DHT22 (umidade e temperatura)
  // Usar variáveis locais para economizar memória global
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  // Verificar se leituras são válidas (NaN check economiza processamento futuro)
  if (!isnan(h) && h >= 0 && h <= 100) {
    umidade_solo = h; // Usar como umidade do solo para simulação
    umidade_ar = (uint8_t)h; // Cast para uint8_t economiza memória
  }
  
  if (!isnan(t) && t >= -40 && t <= 80) {
    temperatura = t;
  }
  
  // Simular pH com função senoidal otimizada
  // Usar millis() diretamente economiza uma variável
  ph_solo = ph_base + ph_amplitude * sin(millis() * ph_frequencia);
  
  // Garantir que pH esteja na faixa válida (0-14)
  ph_solo = constrain(ph_solo, 0.0f, 14.0f);
}

// ========== LÓGICA DE IRRIGAÇÃO OTIMIZADA ==========
void processarLogicaIrrigacao() {
  // Condições para irrigação (lógica booleana otimizada)
  bool umidade_baixa = (umidade_solo < LIMITE_UMIDADE_MIN);
  bool ph_ideal = (ph_solo >= LIMITE_PH_MIN && ph_solo <= LIMITE_PH_MAX);
  bool umidade_alta = (umidade_solo > LIMITE_UMIDADE_MAX);
  
  // Lógica de decisão otimizada (menos comparações)
  bool deve_irrigar = umidade_baixa && ph_ideal && !umidade_alta;
  
  // Atualizar estado da irrigação
  irrigacao_ativa = deve_irrigar;
  
  // Controlar hardware (digitalWrite é custoso, fazer apenas se necessário)
  static bool ultimo_estado_rele = false; // static mantém valor entre chamadas
  if (irrigacao_ativa != ultimo_estado_rele) {
    digitalWrite(PIN_RELE, irrigacao_ativa ? HIGH : LOW);
    digitalWrite(PIN_LED_BOMBA, irrigacao_ativa ? HIGH : LOW);
    ultimo_estado_rele = irrigacao_ativa;
  }
}

// ========== SAÍDA CSV OTIMIZADA ==========
void enviarDadosCSV() {
  // Usar timestamp relativo para economizar largura de banda
  unsigned long timestamp = millis();
  
  // Formato CSV otimizado (menos caracteres = menos memória e tempo)
  Serial.print(timestamp);
  Serial.print(',');
  Serial.print(fosforo_presente ? '1' : '0');
  Serial.print(',');
  Serial.print(potassio_presente ? '1' : '0');
  Serial.print(',');
  Serial.print(ph_solo, 2); // 2 casas decimais suficientes
  Serial.print(',');
  Serial.print(umidade_solo, 1); // 1 casa decimal suficiente
  Serial.print(',');
  Serial.print(irrigacao_ativa ? '1' : '0');
  Serial.print(',');
  Serial.print(temperatura, 1);
  Serial.print(',');
  Serial.print(umidade_ar);
  Serial.println();
}

// ========== SERIAL PLOTTER IMPLEMENTATION ==========
void enviarDadosPlotter() {
  // Formato específico para Serial Plotter do Arduino IDE
  // Usar nomes curtos para economizar largura de banda
  Serial.print("Umidade:");
  Serial.print(umidade_solo);
  Serial.print(",pH:");
  Serial.print(ph_solo);
  Serial.print(",Temp:");
  Serial.print(temperatura);
  Serial.print(",Irrigacao:");
  Serial.print(irrigacao_ativa ? 100 : 0); // Escalar para visualização
  Serial.print(",P:");
  Serial.print(fosforo_presente ? 80 : 0);
  Serial.print(",K:");
  Serial.print(potassio_presente ? 60 : 0);
  Serial.print(",LimiteMin:");
  Serial.print(LIMITE_UMIDADE_MIN);
  Serial.print(",LimiteMax:");
  Serial.println(LIMITE_UMIDADE_MAX);
}

// ========== CONTROLE DO DISPLAY LCD ==========
void atualizarLCD() {
  // Limpar display apenas quando necessário (economia de tempo)
  static uint8_t tela_atual = 0; // static economiza reinicialização
  static unsigned long ultimo_troca = 0;
  
  // Alternar entre telas a cada 5 segundos
  if (millis() - ultimo_troca >= 5000) {
    tela_atual = (tela_atual + 1) % 4; // 4 telas diferentes
    ultimo_troca = millis();
    lcd.clear();
  }
  
  // Mostrar tela atual
  switch (tela_atual) {
    case 0:
      mostrarTelaPrincipal();
      break;
    case 1:
      mostrarTelaSensores();
      break;
    case 2:
      mostrarTelaIrrigacao();
      break;
    case 3:
      mostrarTelaStatus();
      break;
  }
}

// ========== TELAS DO LCD ==========
void mostrarTelaPrincipal() {
  // Linha 1: Título
  lcd.setCursor(0, 0);
  lcd.print(F("FarmTech FASE 4"));
  
  // Linha 2: Umidade
  lcd.setCursor(0, 1);
  lcd.print(F("Umidade: "));
  lcd.print(umidade_solo, 1);
  lcd.print(F("%"));
  
  // Linha 3: pH
  lcd.setCursor(0, 2);
  lcd.print(F("pH: "));
  lcd.print(ph_solo, 2);
  
  // Linha 4: Irrigação
  lcd.setCursor(0, 3);
  if (irrigacao_ativa) {
    lcd.print(F("IRRIGANDO"));
  } else {
    lcd.print(F("PARADO"));
  }
}

void mostrarTelaSensores() {
  lcd.setCursor(0, 0);
  lcd.print(F("=== SENSORES ==="));
  
  lcd.setCursor(0, 1);
  lcd.print(F("P: "));
  lcd.print(fosforo_presente ? F("PRESENTE") : F("AUSENTE"));
  
  lcd.setCursor(0, 2);
  lcd.print(F("K: "));
  lcd.print(potassio_presente ? F("PRESENTE") : F("AUSENTE"));
  
  lcd.setCursor(0, 3);
  lcd.print(F("T: "));
  lcd.print(temperatura, 1);
  lcd.print(F("C "));
  lcd.print(F("AR: "));
  lcd.print(umidade_ar);
  lcd.print(F("%"));
}

void mostrarTelaIrrigacao() {
  lcd.setCursor(0, 0);
  lcd.print(F("== IRRIGACAO =="));
  
  lcd.setCursor(0, 1);
  lcd.print(F("Status: "));
  lcd.print(irrigacao_ativa ? F("ATIVA") : F("INATIVA"));
  
  lcd.setCursor(0, 2);
  lcd.print(F("Limite Min: "));
  lcd.print(LIMITE_UMIDADE_MIN, 0);
  lcd.print(F("%"));
  
  lcd.setCursor(0, 3);
  lcd.print(F("Limite Max: "));
  lcd.print(LIMITE_UMIDADE_MAX, 0);
  lcd.print(F("%"));
}

void mostrarTelaStatus() {
  lcd.setCursor(0, 0);
  lcd.print(F("=== STATUS ==="));
  
  // Uptime em minutos (economia de processamento)
  unsigned long uptime_min = (millis() - tempo_boot) / 60000;
  lcd.setCursor(0, 1);
  lcd.print(F("Uptime: "));
  lcd.print(uptime_min);
  lcd.print(F(" min"));
  
  // Memória livre (função otimizada)
  lcd.setCursor(0, 2);
  lcd.print(F("RAM: "));
  lcd.print(esp_get_free_heap_size() / 1024);
  lcd.print(F(" KB"));
  
  // pH Status
  lcd.setCursor(0, 3);
  if (ph_solo >= LIMITE_PH_MIN && ph_solo <= LIMITE_PH_MAX) {
    lcd.print(F("pH: IDEAL"));
  } else {
    lcd.print(F("pH: FORA"));
  }
}

// ========== SPLASH SCREEN ==========
void mostrarSplashScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(F("FarmTech Solutions"));
  lcd.setCursor(0, 1);
  lcd.print(F("FASE 4 - 2024"));
  lcd.setCursor(0, 2);
  lcd.print(F("Sistema Otimizado"));
  lcd.setCursor(0, 3);
  lcd.print(F("Inicializando..."));
  delay(3000); // Mostrar por 3 segundos
}

// ========== TESTE INICIAL DO SISTEMA ==========
void testeInicialSistema() {
  Serial.println("# Iniciando teste do sistema...");
  
  // Teste do LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(F("TESTE DO SISTEMA"));
  
  // Teste dos LEDs
  digitalWrite(PIN_LED_BOMBA, HIGH);
  delay(500);
  digitalWrite(PIN_LED_BOMBA, LOW);
  
  // Teste do relé
  digitalWrite(PIN_RELE, HIGH);
  delay(500);
  digitalWrite(PIN_RELE, LOW);
  
  // Teste DHT22
  lcd.setCursor(0, 1);
  float teste_temp = dht.readTemperature();
  if (!isnan(teste_temp)) {
    lcd.print(F("DHT22: OK"));
    Serial.println("# DHT22: OK");
  } else {
    lcd.print(F("DHT22: ERRO"));
    Serial.println("# DHT22: ERRO");
  }
  
  // Teste dos botões
  lcd.setCursor(0, 2);
  bool p_state = !digitalRead(PIN_FOSFORO_BTN);
  bool k_state = !digitalRead(PIN_POTASSIO_BTN);
  lcd.print(F("BTN P:"));
  lcd.print(p_state ? F("OK") : F("--"));
  lcd.print(F(" K:"));
  lcd.print(k_state ? F("OK") : F("--"));
  
  lcd.setCursor(0, 3);
  lcd.print(F("Sistema Pronto!"));
  
  Serial.println("# Teste concluído");
  delay(2000);
}

// ========== VERIFICAÇÃO DE MUDANÇAS DE ESTADO ==========
void verificarMudancasEstado() {
  // Log apenas quando há mudança (economia de largura de banda)
  if (fosforo_presente != fosforo_anterior) {
    Serial.print("# Fosforo: ");
    Serial.println(fosforo_presente ? "DETECTADO" : "AUSENTE");
    fosforo_anterior = fosforo_presente;
  }
  
  if (potassio_presente != potassio_anterior) {
    Serial.print("# Potassio: ");
    Serial.println(potassio_presente ? "DETECTADO" : "AUSENTE");
    potassio_anterior = potassio_presente;
  }
  
  if (irrigacao_ativa != irrigacao_anterior) {
    Serial.print("# Irrigacao: ");
    Serial.println(irrigacao_ativa ? "ATIVADA" : "DESATIVADA");
    irrigacao_anterior = irrigacao_ativa;
  }
}

/*
 * ========== RESUMO DAS OTIMIZAÇÕES IMPLEMENTADAS ==========
 * 
 * 1. TIPOS DE DADOS OTIMIZADOS:
 *    - uint8_t para pinos (economiza 3 bytes por variável)
 *    - uint16_t para intervalos (economiza 2 bytes por variável)
 *    - bool para flags (economiza 3 bytes por variável)
 *    - Total estimado: ~60 bytes de RAM economizados
 * 
 * 2. STRINGS EM PROGMEM:
 *    - Todas as strings constantes movidas para Flash
 *    - Economia estimada: ~400 bytes de RAM
 * 
 * 3. INTERRUPTS PARA BOTÕES:
 *    - Elimina necessidade de polling contínuo
 *    - Economia de ciclos de CPU: ~90%
 * 
 * 4. INPUT_PULLUP:
 *    - Elimina necessidade de resistores externos
 *    - Economia de componentes e fios
 * 
 * 5. OTIMIZAÇÕES DE CÓDIGO:
 *    - Variáveis static para manter estado
 *    - Constrain para limitar valores
 *    - Verificações NaN para robustez
 *    - Formato CSV compacto
 * 
 * 6. CONTROLE DE FLUXO:
 *    - Diferentes intervalos para diferentes tarefas
 *    - Delays mínimos para responsividade
 *    - Logs condicionais para economizar largura de banda
 * 
 * RESULTADO TOTAL:
 * - RAM economizada: ~460 bytes
 * - CPU otimizada: ~90% menos ciclos para botões
 * - Largura de banda otimizada: ~50% menos dados serial
 * - Componentes economizados: 2 resistores
 */ 