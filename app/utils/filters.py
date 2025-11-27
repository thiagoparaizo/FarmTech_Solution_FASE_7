def configure_template_filters(app):
    """Configuração de filtros personalizados para templates"""
    
    @app.template_filter('format_br')
    def format_number_br(value, decimal_places=2):
        """
        Formata um número para o padrão brasileiro 
        (ponto como separador de milhares e vírgula como separador decimal)
        
        Args:
            value: O valor a ser formatado
            decimal_places: Número de casas decimais (padrão: 2)
            
        Returns:
            String formatada no padrão brasileiro (ex: 1.234,56)
        """
        if value is None:
            return "-"
        
        try:
            # Tenta converter para float caso não seja um número
            value = float(value)
            
            # Formata o número com as casas decimais especificadas
            format_str = "{:,.%df}" % decimal_places
            formatted = format_str.format(value)
            
            # No formato padrão (1,234.56), substituímos:
            # 1. Primeiro, vírgulas por pontos (1.234.56)
            # 2. Depois, pontos decimais por vírgulas (1.234,56)
            parts = formatted.split('.')
            if len(parts) > 1:
                # Temos uma parte decimal
                integer_part = parts[0].replace(',', '.')
                decimal_part = parts[1]
                formatted = f"{integer_part},{decimal_part}"
            else:
                # Não temos parte decimal
                formatted = formatted.replace(',', '.')
            
            return formatted
        except (ValueError, TypeError):
            # Se não conseguir converter para float, retorna o valor original
            return value

    @app.template_filter('format_int_br')
    def format_integer_br(value):
        """
        Formata um número inteiro para o padrão brasileiro (com pontos como separadores de milhares)
        
        Args:
            value: O valor inteiro a ser formatado
            
        Returns:
            String formatada no padrão brasileiro (ex: 1.234)
        """
        if value is None:
            return "0"
        
        try:
            # Converte para inteiro
            value = int(value)
            # Formata o número
            formatted = "{:,}".format(value)
            # Substitui vírgulas por pontos
            formatted = formatted.replace(',', '.')
            
            return formatted
        except (ValueError, TypeError):
            # Se não conseguir converter para inteiro, retorna o valor original
            return value