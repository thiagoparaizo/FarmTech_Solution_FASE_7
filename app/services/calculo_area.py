class CalculoArea:
    @staticmethod
    def calcular_area_retangular(comprimento, largura):
        """
        Calcula a área de um campo retangular
        
        Args:
            comprimento (float): Comprimento do campo em metros
            largura (float): Largura do campo em metros
            
        Returns:
            dict: Dicionário com área em m² e hectares
        """
        area_m2 = comprimento * largura
        area_hectare = area_m2 / 10000
        
        return {
            'area_m2': area_m2,
            'area_hectare': area_hectare
        }
    
    @staticmethod
    def calcular_area_triangular(base, altura):
        """
        Calcula a área de um campo triangular
        
        Args:
            base (float): Base do triângulo em metros
            altura (float): Altura do triângulo em metros
            
        Returns:
            dict: Dicionário com área em m² e hectares
        """
        area_m2 = (base * altura) / 2
        area_hectare = area_m2 / 10000
        
        return {
            'area_m2': area_m2,
            'area_hectare': area_hectare
        }
    
    @staticmethod
    def calcular_area_circular(raio):
        """
        Calcula a área de um campo circular
        
        Args:
            raio (float): Raio do círculo em metros
            
        Returns:
            dict: Dicionário com área em m² e hectares
        """
        area_m2 = 3.14159 * (raio ** 2)
        area_hectare = area_m2 / 10000
        
        return {
            'area_m2': area_m2,
            'area_hectare': area_hectare
        }
    
    @staticmethod
    def calcular_area_trapezoidal(base_maior, base_menor, altura):
        """
        Calcula a área de um campo trapezoidal
        
        Args:
            base_maior (float): Base maior do trapézio em metros
            base_menor (float): Base menor do trapézio em metros
            altura (float): Altura do trapézio em metros
            
        Returns:
            dict: Dicionário com área em m² e hectares
        """
        area_m2 = ((base_maior + base_menor) * altura) / 2
        area_hectare = area_m2 / 10000
        
        return {
            'area_m2': area_m2,
            'area_hectare': area_hectare
        }
    
    @staticmethod
    def calcular_quantidade_plantas(area_hectare, densidade_plantas_por_hectare):
        """
        Calcula a quantidade de plantas com base na área e densidade
        
        Args:
            area_hectare (float): Área em hectares
            densidade_plantas_por_hectare (int): Quantidade de plantas por hectare
            
        Returns:
            int: Quantidade total de plantas
        """
        return int(area_hectare * densidade_plantas_por_hectare)