from bson import ObjectId
from datetime import datetime

class Campo:
    def __init__(self, nome_produtor, localizacao, campo, _id=None):
        self._id = _id if _id else str(ObjectId())
        self.nome_produtor = nome_produtor
        self.localizacao = localizacao
        self.campo = campo
        
        # Garantir que a data de plantio seja string no formato correto
        if isinstance(self.campo['data_plantio'], datetime):
            self.campo['data_plantio'] = self.campo['data_plantio'].strftime('%Y-%m-%d')
        
        # Calcular a área automaticamente se não estiver definida
        if 'area_total_m2' not in self.campo or not self.campo['area_total_m2']:
            self.calcular_area()
        
        # Calcular área em hectares
        if 'area_total_hectare' not in self.campo or not self.campo['area_total_hectare']:
            self.campo['area_total_hectare'] = self.campo['area_total_m2'] / 10000
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância de Campo a partir de um dicionário"""
        return cls(
            nome_produtor=data.get('nome_produtor'),
            localizacao=data.get('localizacao'),
            campo=data.get('campo'),
            _id=data.get('_id')
        )
    
    def to_dict(self):
        """Converte a instância para dicionário"""
        return {
            '_id': self._id,
            'nome_produtor': self.nome_produtor,
            'localizacao': self.localizacao,
            'campo': self.campo
        }
    
    def calcular_area(self):
        """Calcula a área com base no tipo de geometria"""
        tipo_geometria = self.campo.get('tipo_geometria', '').lower()
        
        if tipo_geometria == 'retangular':
            comprimento = self.campo.get('comprimento_m', 0)
            largura = self.campo.get('largura_m', 0)
            self.campo['area_total_m2'] = comprimento * largura
        
        elif tipo_geometria == 'triangular':
            base = self.campo.get('base_m', 0)
            altura = self.campo.get('altura_m', 0)
            self.campo['area_total_m2'] = (base * altura) / 2
        
        elif tipo_geometria == 'circular':
            raio = self.campo.get('raio_m', 0)
            self.campo['area_total_m2'] = 3.14159 * (raio ** 2)
        
        elif tipo_geometria == 'trapezoidal':
            base_maior = self.campo.get('base_maior_m', 0)
            base_menor = self.campo.get('base_menor_m', 0)
            altura = self.campo.get('altura_m', 0)
            self.campo['area_total_m2'] = ((base_maior + base_menor) * altura) / 2
        
        else:
            # Tipo de geometria não reconhecido
            self.campo['area_total_m2'] = 0
        
        return self.campo['area_total_m2']
    
    def calcular_quantidade_insumos(self, cultura):
        """Calcula a quantidade de insumos necessários com base na cultura e área"""
        area_hectare = self.campo['area_total_hectare']
        
        # Verificar se temos dados de insumos já configurados
        if 'dados_insumos' not in self.campo:
            self.campo['dados_insumos'] = {}
        
        # Calcular fertilizantes com base na cultura
        if cultura and 'fertilizantes_insumos' in cultura:
            npk = cultura['fertilizantes_insumos'].get('adubacao_NPK_por_hectare_kg', {})
            
            self.campo['dados_insumos']['fertilizante_recomendado'] = {
                'N': npk.get('N', 0) * area_hectare,
                'P2O5': npk.get('P2O5', 0) * area_hectare,
                'K2O': npk.get('K2O', 0) * area_hectare
            }
            
            # Calcular quantidade total assumindo um NPK comum (por exemplo, NPK 10-10-10)
            self.campo['dados_insumos']['quantidade_total_kg'] = sum(
                self.campo['dados_insumos']['fertilizante_recomendado'].values()
            )
            
            # Cálculo por metro linear (adaptado para diferentes geometrias)
        if 'espacamento_m' in cultura.get('dados_agronomicos', {}).get('densidade_plantio', {}):
            entre_linhas = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
            tipo_geometria = self.campo.get('tipo_geometria', '').lower()
            
            numero_linhas = 0
            metros_lineares_total = 0
            comprimento_medio = 0
            
            # Calcular número de linhas e metros lineares com base no tipo de geometria
            if tipo_geometria == 'retangular':
                comprimento = self.campo.get('comprimento_m', 0)
                largura = self.campo.get('largura_m', 0)
                numero_linhas = int(largura / entre_linhas) if entre_linhas > 0 else 0
                metros_lineares_total = numero_linhas * comprimento
                comprimento_medio = comprimento
                
            elif tipo_geometria == 'triangular':
                base = self.campo.get('base_m', 0)
                altura = self.campo.get('altura_m', 0)
                numero_linhas = int(altura / entre_linhas) if entre_linhas > 0 else 0
                # Para cada linha, o comprimento diminui linearmente do topo à base
                comprimento_medio = base / 2  # média do comprimento das linhas
                metros_lineares_total = numero_linhas * comprimento_medio
                
            elif tipo_geometria == 'circular':
                raio = self.campo.get('raio_m', 0)
                diametro = 2 * raio
                numero_linhas = int(diametro / entre_linhas) if entre_linhas > 0 else 0
                # Para um círculo, o comprimento médio das linhas é aproximadamente (2/π) * diâmetro
                comprimento_medio = 2 * raio * 0.6366  # aproximação de 2/π = 0.6366
                metros_lineares_total = numero_linhas * comprimento_medio
                
            elif tipo_geometria == 'trapezoidal':
                base_maior = self.campo.get('base_maior_m', 0)
                base_menor = self.campo.get('base_menor_m', 0)
                altura = self.campo.get('altura_m', 0)
                numero_linhas = int(altura / entre_linhas) if entre_linhas > 0 else 0
                comprimento_medio = (base_maior + base_menor) / 2  # média das bases
                metros_lineares_total = numero_linhas * comprimento_medio
            
            else:
                # Para tipos desconhecidos, calculamos baseado na área total
                area_m2 = self.campo['area_total_m2']
                # Estimativa de lado para um quadrado equivalente
                lado_estimado = area_m2 ** 0.5
                numero_linhas = int(lado_estimado / entre_linhas) if entre_linhas > 0 else 0
                metros_lineares_total = (area_m2 / entre_linhas) if entre_linhas > 0 else 0
                comprimento_medio = metros_lineares_total / numero_linhas if numero_linhas > 0 else 0
            
            # Atualizar dados de insumos
            if numero_linhas > 0 and metros_lineares_total > 0:
                self.campo['dados_insumos']['quantidade_por_metro_linear_kg'] = (
                    self.campo['dados_insumos']['quantidade_total_kg'] / metros_lineares_total
                )
                
                # Calcular dados para irrigação
                if 'irrigacao' not in self.campo['dados_insumos']:
                    self.campo['dados_insumos']['irrigacao'] = {}
                
                self.campo['dados_insumos']['irrigacao']['metodo'] = 'gotejamento'
                self.campo['dados_insumos']['irrigacao']['espacamento_entre_linhas'] = entre_linhas
                self.campo['dados_insumos']['irrigacao']['volume_litros_por_metro'] = 0.5
                self.campo['dados_insumos']['irrigacao']['quantidade_ruas'] = int(numero_linhas)
                self.campo['dados_insumos']['irrigacao']['comprimento_medio'] = comprimento_medio
                self.campo['dados_insumos']['irrigacao']['quantidade_total_litros'] = (
                    self.campo['dados_insumos']['irrigacao']['volume_litros_por_metro'] * 
                    metros_lineares_total
                )
        
        return self.campo['dados_insumos']