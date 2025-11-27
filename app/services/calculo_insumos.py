class CalculoInsumos:
    @staticmethod
    def calcular_quantidade_fertilizante(area_hectare, npk_por_hectare):
        """
        Calcula a quantidade de fertilizante NPK necessária
        
        Args:
            area_hectare (float): Área em hectares
            npk_por_hectare (dict): Quantidade de N, P2O5 e K2O por hectare
            
        Returns:
            dict: Quantidade de cada elemento NPK
        """
        return {
            'N': npk_por_hectare.get('N', 0) * area_hectare,
            'P2O5': npk_por_hectare.get('P2O5', 0) * area_hectare,
            'K2O': npk_por_hectare.get('K2O', 0) * area_hectare,
            'total_kg': (
                npk_por_hectare.get('N', 0) + 
                npk_por_hectare.get('P2O5', 0) + 
                npk_por_hectare.get('K2O', 0)
            ) * area_hectare
        }
    
    @staticmethod
    def calcular_quantidade_metro_linear(quantidade_total_kg, numero_linhas, comprimento_linha):
        """
        Calcula a quantidade de fertilizante por metro linear
        
        Args:
            quantidade_total_kg (float): Quantidade total de fertilizante em kg
            numero_linhas (int): Número total de linhas
            comprimento_linha (float): Comprimento de cada linha em metros
            
        Returns:
            float: Quantidade por metro linear em kg
        """
        if numero_linhas > 0 and comprimento_linha > 0:
            return quantidade_total_kg / (numero_linhas * comprimento_linha)
        return 0
    
    @staticmethod
    def calcular_volume_irrigacao(volume_por_metro, quantidade_ruas, comprimento_rua):
        """
        Calcula o volume total de irrigação
        
        Args:
            volume_por_metro (float): Volume de água por metro linear em litros
            quantidade_ruas (int): Número total de ruas/linhas
            comprimento_rua (float): Comprimento de cada rua em metros
            
        Returns:
            float: Volume total em litros
        """
        return volume_por_metro * quantidade_ruas * comprimento_rua
    
    @staticmethod
    def calcular_numero_linhas(comprimento_campo, espacamento_entre_linhas):
        """
        Calcula o número de linhas com base no espaçamento
        
        Args:
            comprimento_campo (float): Comprimento do campo em metros
            espacamento_entre_linhas (float): Espaçamento entre linhas em metros
            
        Returns:
            int: Número de linhas
        """
        if espacamento_entre_linhas > 0:
            return int(comprimento_campo / espacamento_entre_linhas)
        return 0
    
    @staticmethod
    def calcular_irrigacao_total(campo, cultura):
        """
        Calcula os dados de irrigação com base no campo e cultura
        
        Args:
            campo (dict): Dados do campo
            cultura (dict): Dados da cultura
            
        Returns:
            dict: Dados de irrigação calculados
        """
        # Extrair dados necessários
        area_m2 = campo.get('area_total_m2', 0)
        tipo_geometria = campo.get('tipo_geometria', '')
        comprimento = campo.get('comprimento_m', 0)
        largura = campo.get('largura_m', 0)
        
        # Obter dados da cultura
        densidade_plantio = cultura.get('dados_agronomicos', {}).get('densidade_plantio', {})
        espacamento_entre_linhas = densidade_plantio.get('espacamento_m', {}).get('entre_linhas', 0)
        
        # Calcular número de linhas
        numero_linhas = CalculoInsumos.calcular_numero_linhas(comprimento, espacamento_entre_linhas)
        
        # Configurações de irrigação
        volume_por_metro = 0.5  # Litros por metro
        
        # Calcular volume total
        volume_total = CalculoInsumos.calcular_volume_irrigacao(
            volume_por_metro, numero_linhas, largura
        )
        
        return {
            'metodo': 'aspersão',
            'volume_litros_por_metro': volume_por_metro,
            'quantidade_ruas': numero_linhas,
            'quantidade_total_litros': volume_total
        }
    
    @staticmethod
    def calcular_insumos_completo(campo, cultura):
        """
        Realiza todos os cálculos de insumos para um campo e cultura
        
        Args:
            campo (dict): Dados do campo
            cultura (dict): Dados da cultura
            
        Returns:
            dict: Dados completos de insumos calculados
        """
        # Extrair área em hectares
        area_hectare = campo.get('area_total_hectare', 0)
        
        # Calcular fertilizantes
        npk_por_hectare = cultura.get('fertilizantes_insumos', {}).get('adubacao_NPK_por_hectare_kg', {})
        fertilizante = CalculoInsumos.calcular_quantidade_fertilizante(area_hectare, npk_por_hectare)
        
        # Calcular número de linhas para distribuição
        espacamento_entre_linhas = cultura.get('dados_agronomicos', {}).get('densidade_plantio', {}).get('espacamento_m', {}).get('entre_linhas', 0)
        comprimento = campo.get('comprimento_m', 0)
        numero_linhas = CalculoInsumos.calcular_numero_linhas(comprimento, espacamento_entre_linhas)
        
        # Calcular quantidade por metro linear
        quantidade_por_metro = CalculoInsumos.calcular_quantidade_metro_linear(
            fertilizante['total_kg'], numero_linhas, campo.get('largura_m', 0)
        )
        
        # Calcular dados de irrigação
        irrigacao = CalculoInsumos.calcular_irrigacao_total(campo, cultura)
        
        # Retornar todos os dados calculados
        return {
            'fertilizante_utilizado': "NPK Misto",
            'quantidades_kg': fertilizante,
            'quantidade_por_metro_linear_kg': quantidade_por_metro,
            'irrigacao': irrigacao
        }