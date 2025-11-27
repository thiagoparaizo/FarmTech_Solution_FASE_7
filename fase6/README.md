# FIAP - Faculdade de Informática e Administração Paulista
<p align="center">
<a href= "https://www.fiap.com.br/"><img src="https://avatars.githubusercontent.com/u/70102670?s=200&v=4" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

# Projeto Fase 6 - Visão Computacional com YOLOv5
## EasyAgro - FarmTechSolutions

## 👨‍🎓 Integrante: 
- <a href="https://www.linkedin.com/in/thiagoparaizo/?originalSubdomain=br">Thiago Paraizo - RM566159</a>

## 👩‍🏫 Professores:
### Tutor
- <a href="https://www.linkedin.com/company/inova-fusca">Leonardo Ruiz Orabona</a>
### Coordenador
- <a href="https://www.linkedin.com/company/inova-fusca">Andre Godoy Chiovato</a>

## 📜 Descrição

Sistema de visão computacional desenvolvido com **YOLOv5** para detecção e classificação de **bicicletas** e **carros**. O projeto demonstra a aplicabilidade de redes neurais convolucionais em cenários de monitoramento e segurança patrimonial.

### Objetivos
- Treinar modelo YOLOv5 customizado com dataset próprio
- Comparar performance entre diferentes configurações de treinamento (15 vs 40 épocas)
- Validar acurácia e tempo de inferência do modelo
- Aplicar em casos de uso da FarmTech Solutions

## 🎯 Resultados

### Performance Final (40 épocas)
- **mAP@0.5:** 99.5%
- **mAP@0.5:0.95:** 74.9%
- **Precision:** 98.3%
- **Recall:** 99.1%
- **Taxa de detecção no teste:** 87.5% (7/8 objetos)

### Comparação 15 vs 40 Épocas
| Métrica | 15 Épocas | 40 Épocas | Melhoria |
|---------|-----------|-----------|----------|
| mAP@0.5 | 92.0% | 99.5% | +8.2% |
| mAP@0.5:0.95 | 57.6% | 74.9% | +30.1% |
| Precision | 88.0% | 98.3% | +11.7% |
| Recall | 87.5% | 99.1% | +13.2% |

## 📁 Estrutura do Projeto
```
.
├── ThiagoParaizo_rm566159_pbl_Fase6.ipynb    # Notebook principal
├── dataset/                                   # Dataset organizado
│   ├── train/
│   │   ├── images/                           # 64 imagens (32 bikes + 32 carros)
│   │   └── labels/                           # Arquivos de rotulação .txt
│   ├── valid/
│   │   ├── images/                           # 8 imagens (4 bikes + 4 carros)
│   │   └── labels/
│   └── test/
│       └── images/                           # 8 imagens (4 bikes + 4 carros)
└── README.md
```

## 🚀 Como Executar

### 1. Abrir o Notebook
- Acesse o [Google Colab](https://colab.research.google.com/)
- Faça upload do arquivo `ThiagoParaizo_rm566159_pbl_Fase6.ipynb`
- Configure Runtime para **GPU (T4)**

### 2. Preparar Dataset
- Faça upload da pasta `dataset/` para o seu Google Drive
- Ajuste o caminho `base_path` no notebook para apontar para sua pasta

### 3. Executar
- Execute todas as células sequencialmente
- Tempo estimado total: ~2 horas (15 + 40 épocas de treinamento)

## 📊 Documentação Técnica

### Dataset
- **Total:** 80 imagens (40 bicicletas + 40 carros)
- **Divisão:** 64 treino / 8 validação / 8 teste
- **Formato:** BMP 640x480
- **Rotulação:** Make Sense IA (formato YOLO)
- **Classes:** 0 (bicicleta), 1 (carro)

### Modelo
- **Arquitetura:** YOLOv5s
- **Tamanho de entrada:** 640x640
- **Batch size:** 16
- **Otimizador:** SGD
- **Data augmentation:** Padrão YOLOv5

### Ambiente
- Python 3.12
- PyTorch 2.8.0
- CUDA 12.6
- Google Colab (GPU T4)

## 📈 Resultados Detalhados

### 📊 Análise dos Resultados de Teste

**Performance no conjunto de teste (8 imagens):**

**Taxa de Detecção Geral:** 7/8 objetos detectados (87.5%)

**Por Classe:**
- **Bicicletas:** 4/4 detectadas (100%) ✅
  - Todas as bicicletas foram corretamente identificadas
  - Confiança média alta (~0.7-0.8)
  
- **Carros:** 3/4 detectados (75%) ⚠️
  - 1 falha: carsgraz_039.bmp não foi detectado
  - Possível causa: ângulo, oclusão ou baixo contraste

**Observações:**
1. O modelo teve excelente performance em bicicletas (100%)
2. Carros tiveram 1 falso negativo (25% erro)
3. Não houve falsos positivos
4. Confiança das detecções: alta (>0.6)

**Casos de Sucesso:**
- Bicicletas detectadas corretamente mesmo com diferentes ângulos
- Carros identificados em cenários urbanos

**Limitações Identificadas:**
- 1 carro não detectado (investigar características da imagem)
- Dataset de teste pequeno (apenas 8 imagens)

**Conclusão:**
O modelo demonstrou boa generalização com 87.5% de acerto no teste, 
validando os resultados de treinamento (mAP@0.5 de 99.5%).


## 🔗 Links Úteis

- [Notebook no Colab](https://colab.research.google.com/drive/1zILKs7XvlW1pvsfWcpcXCyjvJA4RBL6M#scrollTo=bdgc5BXHeeYu)
- [YOLOv5 Repository](https://github.com/ultralytics/yolov5)
- [Make Sense IA](https://www.makesense.ai/)
- [Kaggle Dataset](https://www.kaggle.com/datasets/pavansanagapati/images-dataset/data/code)

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>