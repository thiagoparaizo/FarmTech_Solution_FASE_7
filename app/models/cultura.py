from bson import ObjectId

class Cultura:
    def __init__(self, nome_cultura, nome_cientifico, descricao, dados_agronomicos, 
                 clima_solo, fertilizantes_insumos, _id=None):
        self._id = _id if _id else str(ObjectId())
        self.nome_cultura = nome_cultura
        self.nome_cientifico = nome_cientifico
        self.descricao = descricao
        self.dados_agronomicos = dados_agronomicos
        self.clima_solo = clima_solo
        self.fertilizantes_insumos = fertilizantes_insumos
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância de Cultura a partir de um dicionário"""
        return cls(
            nome_cultura=data.get('nome_cultura'),
            nome_cientifico=data.get('nome_cientifico'),
            descricao=data.get('descricao'),
            dados_agronomicos=data.get('dados_agronomicos'),
            clima_solo=data.get('clima_solo'),
            fertilizantes_insumos=data.get('fertilizantes_insumos'),
            _id=data.get('_id')
        )
    
    def to_dict(self):
        """Converte a instância para dicionário"""
        return {
            '_id': self._id,
            'nome_cultura': self.nome_cultura,
            'nome_cientifico': self.nome_cientifico,
            'descricao': self.descricao,
            'dados_agronomicos': self.dados_agronomicos,
            'clima_solo': self.clima_solo,
            'fertilizantes_insumos': self.fertilizantes_insumos
        }
    
    @staticmethod
    def get_mandioca_default():
        """Retorna dados padrão para a cultura de mandioca"""
        return {
            "nome_cultura": "Mandioca",
            "nome_cientifico": "Manihot esculenta",
            "descricao": "Mandioca (Macaxeira), variedade para mesa ou indústria, adaptada ao litoral cearense.",
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
                "adubacao_organica_recomendada": "esterco bovino ou composto orgânico (5-10 litros por cova)",
                "correcao_solo": {
                    "calagem": "calcário dolomítico, 1.5 a 2 ton/ha",
                    "gessagem": "não essencial, recomendável em solos pobres em Ca e S"
                },
                "frequencia_adubacao": "Plantio e cobertura aos 3-4 meses"
            }
        }
    
    @staticmethod
    def get_feijao_caupi_default():
        """Retorna dados padrão para a cultura de feijão-caupi"""
        return {
            "nome_cultura": "Feijão-Caupi",
            "nome_cientifico": "Vigna unguiculata",
            "descricao": "Feijão-de-corda adaptado ao semiárido cearense, utilizado tanto verde quanto seco.",
            "dados_agronomicos": {
                "densidade_plantio": {
                    "espacamento_m": {
                        "entre_linhas": 0.8,
                        "entre_plantas": 0.25
                    },
                    "plantas_por_hectare": 50000
                },
                "ciclo_producao_dias": {
                    "minimo": 60,
                    "maximo": 90
                }
            },
            "clima_solo": {
                "temperatura_ideal_c": {
                    "minima": 20,
                    "maxima": 34
                },
                "precipitacao_minima_mm": 350,
                "precipitacao_maxima_mm": 600,
                "tipo_solo_ideal": "franco-arenoso bem drenado",
                "ph_ideal": {
                    "minimo": 5.5,
                    "maximo": 6.5
                },
                "tolerancia_salinidade": "baixa",
                "estrategias_climaticas": [
                    "plantio em camalhões",
                    "plantio escalonado"
                ]
            },
            "fertilizantes_insumos": {
                "adubacao_NPK_por_hectare_kg": {
                    "N": 20,
                    "P2O5": 50,
                    "K2O": 40
                },
                "adubacao_organica_recomendada": "esterco bovino (2 litros por metro linear)",
                "correcao_solo": {
                    "calagem": "calcário dolomítico, 1 a 2 ton/ha",
                    "gessagem": "opcional, recomendado se faltar cálcio e enxofre"
                },
                "frequencia_adubacao": "Na semeadura e eventualmente cobertura nitrogenada após 20 dias"
            }
        }