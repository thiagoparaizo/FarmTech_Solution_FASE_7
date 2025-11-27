import os
import sys
import json
from pymongo import MongoClient
from bson import ObjectId, json_util

# Adicionar o diretório raiz ao sys.path para importar os módulos da aplicação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.cultura import Cultura
from app.models.campo import Campo
from app.services.calculo_area import CalculoArea
from app.services.calculo_insumos import CalculoInsumos
from app.services.db_service import DatabaseService

# Configuração do banco de dados
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/farmtech')
db_service = DatabaseService(MONGO_URI)

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_menu():
    """Exibe o menu principal"""
    limpar_tela()
    print("\n===== FarmTech Solutions - Modo Terminal =====")
    print("1. Gerenciar Culturas")
    print("2. Gerenciar Campos")
    print("3. Calculadora de Área")
    print("4. Calculadora de Insumos")
    print("5. Exportar Dados")
    print("6. Sair do programa")
    print("============================================")
    return input("Escolha uma opção: ")

def menu_culturas():
    """Menu para gerenciamento de culturas"""
    while True:
        limpar_tela()
        print("\n===== Gerenciamento de Culturas =====")
        print("1. Listar todas as culturas")
        print("2. Visualizar detalhes de uma cultura")
        print("3. Adicionar nova cultura")
        print("4. Atualizar cultura existente")
        print("5. Remover cultura")
        print("6. Voltar ao menu principal")
        print("=====================================")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            listar_culturas()
        elif opcao == '2':
            visualizar_cultura()
        elif opcao == '3':
            adicionar_cultura()
        elif opcao == '4':
            atualizar_cultura()
        elif opcao == '5':
            remover_cultura()
        elif opcao == '6':
            break
        else:
            input("Opção inválida. Pressione Enter para continuar...")

def listar_culturas():
    """Lista todas as culturas cadastradas"""
    limpar_tela()
    print("\n===== Lista de Culturas Cadastradas =====")
    
    culturas = db_service.obter_todas_culturas()
    
    if not culturas:
        print("Nenhuma cultura cadastrada.")
    else:
        for i, cultura in enumerate(culturas, 1):
            print(f"{i}. {cultura['nome_cultura']} ({cultura['nome_cientifico']})")
    
    input("\nPressione Enter para continuar...")

def visualizar_cultura():
    """Exibe detalhes de uma cultura específica"""
    limpar_tela()
    print("\n===== Detalhes da Cultura =====")
    
    culturas = db_service.obter_todas_culturas()
    
    if not culturas:
        print("Nenhuma cultura cadastrada.")
        input("\nPressione Enter para continuar...")
        return
    
    print("Culturas disponíveis:")
    for i, cultura in enumerate(culturas, 1):
        print(f"{i}. {cultura['nome_cultura']}")
    
    try:
        indice = int(input("\nEscolha o número da cultura: ")) - 1
        
        if indice < 0 or indice >= len(culturas):
            print("Índice inválido.")
            input("\nPressione Enter para continuar...")
            return
        
        cultura = culturas[indice]
        
        print(f"\nNome: {cultura['nome_cultura']}")
        print(f"Nome Científico: {cultura['nome_cientifico']}")
        print(f"Descrição: {cultura['descricao']}")
        
        print("\nDados Agronômicos:")
        densidade = cultura['dados_agronomicos']['densidade_plantio']
        print(f"  Espaçamento: {densidade['espacamento_m']['entre_linhas']}m x {densidade['espacamento_m']['entre_plantas']}m")
        print(f"  Plantas por Hectare: {densidade['plantas_por_hectare']}")
        print(f"  Ciclo de Produção: {cultura['dados_agronomicos']['ciclo_producao_dias']['minimo']}-{cultura['dados_agronomicos']['ciclo_producao_dias']['maximo']} dias")
        
        print("\nClima e Solo:")
        clima = cultura['clima_solo']
        print(f"  Temperatura Ideal: {clima['temperatura_ideal_c']['minima']}-{clima['temperatura_ideal_c']['maxima']}°C")
        print(f"  Precipitação: {clima['precipitacao_minima_mm']}-{clima['precipitacao_maxima_mm']} mm")
        print(f"  Tipo de Solo Ideal: {clima['tipo_solo_ideal']}")
        print(f"  pH Ideal: {clima['ph_ideal']['minimo']}-{clima['ph_ideal']['maximo']}")
        
        print("\nFertilizantes e Insumos:")
        fert = cultura['fertilizantes_insumos']
        print(f"  NPK por Hectare: N={fert['adubacao_NPK_por_hectare_kg']['N']}kg, P2O5={fert['adubacao_NPK_por_hectare_kg']['P2O5']}kg, K2O={fert['adubacao_NPK_por_hectare_kg']['K2O']}kg")
        print(f"  Adubação Orgânica: {fert['adubacao_organica_recomendada']}")
        
    except (ValueError, IndexError) as e:
        print(f"Erro: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def adicionar_cultura():
    """Adiciona uma nova cultura"""
    limpar_tela()
    print("\n===== Adicionar Nova Cultura =====")
    
    try:
        nome_cultura = input("Nome da Cultura: ")
        nome_cientifico = input("Nome Científico: ")
        descricao = input("Descrição: ")
        
        print("\nDados Agronômicos:")
        entre_linhas = float(input("Espaçamento entre Linhas (m): "))
        entre_plantas = float(input("Espaçamento entre Plantas (m): "))
        plantas_por_hectare = int(input("Plantas por Hectare: "))
        ciclo_minimo = int(input("Ciclo Mínimo (dias): "))
        ciclo_maximo = int(input("Ciclo Máximo (dias): "))
        
        print("\nClima e Solo:")
        temp_minima = float(input("Temperatura Mínima (°C): "))
        temp_maxima = float(input("Temperatura Máxima (°C): "))
        precipitacao_minima = float(input("Precipitação Mínima (mm): "))
        precipitacao_maxima = float(input("Precipitação Máxima (mm): "))
        tipo_solo = input("Tipo de Solo Ideal: ")
        ph_minimo = float(input("pH Mínimo: "))
        ph_maximo = float(input("pH Máximo: "))
        tolerancia_salinidade = input("Tolerância à Salinidade: ")
        estrategias_climaticas = input("Estratégias Climáticas (separadas por vírgula): ").split(',')
        
        print("\nFertilizantes e Insumos:")
        npk_n = float(input("Quantidade de N por Hectare (kg): "))
        npk_p = float(input("Quantidade de P2O5 por Hectare (kg): "))
        npk_k = float(input("Quantidade de K2O por Hectare (kg): "))
        adubacao_organica = input("Adubação Orgânica Recomendada: ")
        calagem = input("Calagem: ")
        gessagem = input("Gessagem: ")
        frequencia_adubacao = input("Frequência de Adubação: ")
        
        # Construir estrutura de dados aninhada
        dados_agronomicos = {
            'densidade_plantio': {
                'espacamento_m': {
                    'entre_linhas': entre_linhas,
                    'entre_plantas': entre_plantas
                },
                'plantas_por_hectare': plantas_por_hectare
            },
            'ciclo_producao_dias': {
                'minimo': ciclo_minimo,
                'maximo': ciclo_maximo
            }
        }
        
        clima_solo = {
            'temperatura_ideal_c': {
                'minima': temp_minima,
                'maxima': temp_maxima
            },
            'precipitacao_minima_mm': precipitacao_minima,
            'precipitacao_maxima_mm': precipitacao_maxima,
            'tipo_solo_ideal': tipo_solo,
            'ph_ideal': {
                'minimo': ph_minimo,
                'maximo': ph_maximo
            },
            'tolerancia_salinidade': tolerancia_salinidade,
            'estrategias_climaticas': estrategias_climaticas
        }
        
        fertilizantes_insumos = {
            'adubacao_NPK_por_hectare_kg': {
                'N': npk_n,
                'P2O5': npk_p,
                'K2O': npk_k
            },
            'adubacao_organica_recomendada': adubacao_organica,
            'correcao_solo': {
                'calagem': calagem,
                'gessagem': gessagem
            },
            'frequencia_adubacao': frequencia_adubacao
        }
        
        cultura = Cultura(
            nome_cultura=nome_cultura,
            nome_cientifico=nome_cientifico,
            descricao=descricao,
            dados_agronomicos=dados_agronomicos,
            clima_solo=clima_solo,
            fertilizantes_insumos=fertilizantes_insumos
        )
        
        db_service.adicionar_cultura(cultura)
        print("\nCultura adicionada com sucesso!")
        
    except Exception as e:
        print(f"\nErro ao adicionar cultura: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def atualizar_cultura():
    """Atualiza uma cultura existente"""
    limpar_tela()
    print("\n===== Atualizar Cultura Existente =====")
    
    culturas = db_service.obter_todas_culturas()
    
    if not culturas:
        print("Nenhuma cultura cadastrada.")
        input("\nPressione Enter para continuar...")
        return
    
    print("Culturas disponíveis:")
    for i, cultura in enumerate(culturas, 1):
        print(f"{i}. {cultura['nome_cultura']}")
    
    try:
        indice = int(input("\nEscolha o número da cultura: ")) - 1
        
        if indice < 0 or indice >= len(culturas):
            print("Índice inválido.")
            input("\nPressione Enter para continuar...")
            return
        
        cultura = culturas[indice]
        cultura_id = cultura['_id']
        
        print("\nDigite os novos valores (ou pressione Enter para manter os atuais):")

        dados_atualizados = {}

        # Campos simples
        nome = input(f"Nome da Cultura [{cultura['nome_cultura']}]: ") or cultura['nome_cultura']
        nome_cientifico = input(f"Nome Científico [{cultura['nome_cientifico']}]: ") or cultura['nome_cientifico']
        descricao = input(f"Descrição [{cultura['descricao']}]: ") or cultura['descricao']

        dados_atualizados.update({
            "nome_cultura": nome,
            "nome_cientifico": nome_cientifico,
            "descricao": descricao
        })

        # ======= Dados Agronômicos =======
        if input("\nDeseja atualizar Dados Agronômicos? (s/n): ").lower() == 's':
            dados_agronomicos = cultura.get('dados_agronomicos', {})

            espacamento_linhas = input(f"Espaçamento entre linhas (m) [{dados_agronomicos.get('densidade_plantio', {}).get('espacamento_m', {}).get('entre_linhas', '')}]: ")
            espacamento_plantas = input(f"Espaçamento entre plantas (m) [{dados_agronomicos.get('densidade_plantio', {}).get('espacamento_m', {}).get('entre_plantas', '')}]: ")
            plantas_por_ha = input(f"Plantas por hectare [{dados_agronomicos.get('densidade_plantio', {}).get('plantas_por_hectare', '')}]: ")
            ciclo_min = input(f"Ciclo de produção mínimo (dias) [{dados_agronomicos.get('ciclo_producao_dias', {}).get('minimo', '')}]: ")
            ciclo_max = input(f"Ciclo de produção máximo (dias) [{dados_agronomicos.get('ciclo_producao_dias', {}).get('maximo', '')}]: ")

            dados_atualizados['dados_agronomicos'] = {
                "densidade_plantio": {
                    "espacamento_m": {
                        "entre_linhas": float(espacamento_linhas) if espacamento_linhas else dados_agronomicos.get('densidade_plantio', {}).get('espacamento_m', {}).get('entre_linhas'),
                        "entre_plantas": float(espacamento_plantas) if espacamento_plantas else dados_agronomicos.get('densidade_plantio', {}).get('espacamento_m', {}).get('entre_plantas')
                    },
                    "plantas_por_hectare": int(plantas_por_ha) if plantas_por_ha else dados_agronomicos.get('densidade_plantio', {}).get('plantas_por_hectare')
                },
                "ciclo_producao_dias": {
                    "minimo": int(ciclo_min) if ciclo_min else dados_agronomicos.get('ciclo_producao_dias', {}).get('minimo'),
                    "maximo": int(ciclo_max) if ciclo_max else dados_agronomicos.get('ciclo_producao_dias', {}).get('maximo')
                }
            }

        # ======= Clima e Solo =======
        if input("\nDeseja atualizar Dados de Clima e Solo? (s/n): ").lower() == 's':
            clima_solo = cultura.get('clima_solo', {})

            temp_min = input(f"Temperatura mínima ideal (°C) [{clima_solo.get('temperatura_ideal_c', {}).get('minima', '')}]: ")
            temp_max = input(f"Temperatura máxima ideal (°C) [{clima_solo.get('temperatura_ideal_c', {}).get('maxima', '')}]: ")
            precipitacao_min = input(f"Precipitação mínima (mm) [{clima_solo.get('precipitacao_minima_mm', '')}]: ")
            precipitacao_max = input(f"Precipitação máxima (mm) [{clima_solo.get('precipitacao_maxima_mm', '')}]: ")
            tipo_solo = input(f"Tipo de solo ideal [{clima_solo.get('tipo_solo_ideal', '')}]: ") or clima_solo.get('tipo_solo_ideal', '')
            ph_min = input(f"pH mínimo [{clima_solo.get('ph_ideal', {}).get('minimo', '')}]: ")
            ph_max = input(f"pH máximo [{clima_solo.get('ph_ideal', {}).get('maximo', '')}]: ")
            tolerancia = input(f"Tolerância à salinidade [{clima_solo.get('tolerancia_salinidade', '')}]: ") or clima_solo.get('tolerancia_salinidade', '')
            estrategias = input(f"Estratégias climáticas (separadas por vírgula) [{', '.join(clima_solo.get('estrategias_climaticas', []))}]: ")

            estrategias_list = [e.strip() for e in estrategias.split(',')] if estrategias else clima_solo.get('estrategias_climaticas', [])

            dados_atualizados['clima_solo'] = {
                "temperatura_ideal_c": {
                    "minima": float(temp_min) if temp_min else clima_solo.get('temperatura_ideal_c', {}).get('minima'),
                    "maxima": float(temp_max) if temp_max else clima_solo.get('temperatura_ideal_c', {}).get('maxima')
                },
                "precipitacao_minima_mm": float(precipitacao_min) if precipitacao_min else clima_solo.get('precipitacao_minima_mm'),
                "precipitacao_maxima_mm": float(precipitacao_max) if precipitacao_max else clima_solo.get('precipitacao_maxima_mm'),
                "tipo_solo_ideal": tipo_solo,
                "ph_ideal": {
                    "minimo": float(ph_min) if ph_min else clima_solo.get('ph_ideal', {}).get('minimo'),
                    "maximo": float(ph_max) if ph_max else clima_solo.get('ph_ideal', {}).get('maximo')
                },
                "tolerancia_salinidade": tolerancia,
                "estrategias_climaticas": estrategias_list
            }

        # ======= Fertilizantes e Insumos =======
        if input("\nDeseja atualizar Fertilizantes e Insumos? (s/n): ").lower() == 's':
            fertilizantes = cultura.get('fertilizantes_insumos', {})

            N = input(f"N (kg/ha) [{fertilizantes.get('adubacao_NPK_por_hectare_kg', {}).get('N', '')}]: ")
            P = input(f"P2O5 (kg/ha) [{fertilizantes.get('adubacao_NPK_por_hectare_kg', {}).get('P2O5', '')}]: ")
            K = input(f"K2O (kg/ha) [{fertilizantes.get('adubacao_NPK_por_hectare_kg', {}).get('K2O', '')}]: ")
            adubacao_organica = input(f"Adubação orgânica recomendada [{fertilizantes.get('adubacao_organica_recomendada', '')}]: ") or fertilizantes.get('adubacao_organica_recomendada', '')
            calagem = input(f"Calagem [{fertilizantes.get('correcao_solo', {}).get('calagem', '')}]: ") or fertilizantes.get('correcao_solo', {}).get('calagem', '')
            gessagem = input(f"Gessagem [{fertilizantes.get('correcao_solo', {}).get('gessagem', '')}]: ") or fertilizantes.get('correcao_solo', {}).get('gessagem', '')
            frequencia = input(f"Frequência de adubação [{fertilizantes.get('frequencia_adubacao', '')}]: ") or fertilizantes.get('frequencia_adubacao', '')

            dados_atualizados['fertilizantes_insumos'] = {
                "adubacao_NPK_por_hectare_kg": {
                    "N": float(N) if N else fertilizantes.get('adubacao_NPK_por_hectare_kg', {}).get('N'),
                    "P2O5": float(P) if P else fertilizantes.get('adubacao_NPK_por_hectare_kg', {}).get('P2O5'),
                    "K2O": float(K) if K else fertilizantes.get('adubacao_NPK_por_hectare_kg', {}).get('K2O')
                },
                "adubacao_organica_recomendada": adubacao_organica,
                "correcao_solo": {
                    "calagem": calagem,
                    "gessagem": gessagem
                },
                "frequencia_adubacao": frequencia
            }

        # Atualizar no banco de dados
        db_service.atualizar_cultura(cultura_id, dados_atualizados)

        print("\nCultura atualizada com sucesso!")

    except Exception as e:
        print(f"\nErro ao atualizar cultura: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def remover_cultura():
    """Remove uma cultura"""
    limpar_tela()
    print("\n===== Remover Cultura =====")
    
    culturas = db_service.obter_todas_culturas()
    
    if not culturas:
        print("Nenhuma cultura cadastrada.")
        input("\nPressione Enter para continuar...")
        return
    
    print("Culturas disponíveis:")
    for i, cultura in enumerate(culturas, 1):
        print(f"{i}. {cultura['nome_cultura']}")
    
    try:
        indice = int(input("\nEscolha o número da cultura a ser removida: ")) - 1
        
        if indice < 0 or indice >= len(culturas):
            print("Índice inválido.")
            input("\nPressione Enter para continuar...")
            return
        
        cultura = culturas[indice]
        confirmacao = input(f"Tem certeza que deseja remover '{cultura['nome_cultura']}'? (S/N): ")
        
        if confirmacao.upper() == 'S':
            db_service.remover_cultura(cultura['_id'])
            print(f"\nCultura '{cultura['nome_cultura']}' removida com sucesso!")
        else:
            print("\nOperação cancelada.")
        
    except Exception as e:
        print(f"\nErro ao remover cultura: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def menu_campos():
    """Menu para gerenciamento de campos"""
    while True:
        limpar_tela()
        print("\n===== Gerenciamento de Campos =====")
        print("1. Listar todos os campos")
        print("2. Visualizar detalhes de um campo")
        print("3. Adicionar novo campo")
        print("4. Atualizar campo existente")
        print("5. Remover campo")
        print("6. Voltar ao menu principal")
        print("=====================================")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            listar_campos()
        elif opcao == '2':
            visualizar_campo()
        elif opcao == '3':
            adicionar_campo()
        elif opcao == '4':
            atualizar_campo()
        elif opcao == '5':
            remover_campo()
        elif opcao == '6':
            break
        else:
            input("Opção inválida. Pressione Enter para continuar...")

def listar_campos():
    """Lista todos os campos cadastrados"""
    limpar_tela()
    print("\n===== Lista de Campos Cadastrados =====")
    
    campos = db_service.obter_todos_campos()
    
    if not campos:
        print("Nenhum campo cadastrado.")
    else:
        for i, campo in enumerate(campos, 1):
            print(f"{i}. {campo['nome_produtor']} - {campo['campo']['cultura_plantada']} ({campo['campo']['area_total_hectare']:.2f} ha)")
    
    input("\nPressione Enter para continuar...")

def visualizar_campo():
    """Exibe detalhes de um campo específico"""
    limpar_tela()
    print("\n===== Detalhes do Campo =====")
    
    campos = db_service.obter_todos_campos()
    
    if not campos:
        print("Nenhum campo cadastrado.")
        input("\nPressione Enter para continuar...")
        return
    
    print("Campos disponíveis:")
    for i, campo in enumerate(campos, 1):
        print(f"{i}. {campo['nome_produtor']} - {campo['campo']['cultura_plantada']}")
    
    try:
        indice = int(input("\nEscolha o número do campo: ")) - 1
        
        if indice < 0 or indice >= len(campos):
            print("Índice inválido.")
            input("\nPressione Enter para continuar...")
            return
        
        campo = campos[indice]
        
        print(f"\nProdutor: {campo['nome_produtor']}")
        print(f"Localização: {campo['localizacao']['municipio']}, {campo['localizacao']['regiao']}")
        print(f"Cultura Plantada: {campo['campo']['cultura_plantada']}")
        print(f"Data de Plantio: {campo['campo']['data_plantio']}")
        print(f"Tipo de Geometria: {campo['campo']['tipo_geometria']}")
        
        # Exibir dimensões conforme o tipo de geometria
        if campo['campo']['tipo_geometria'] == 'retangular':
            print(f"Dimensões: {campo['campo']['comprimento_m']} x {campo['campo']['largura_m']} m")
        elif campo['campo']['tipo_geometria'] == 'triangular':
            print(f"Base: {campo['campo']['base_m']} m")
            print(f"Altura: {campo['campo']['altura_m']} m")
        elif campo['campo']['tipo_geometria'] == 'circular':
            print(f"Raio: {campo['campo']['raio_m']} m")
        elif campo['campo']['tipo_geometria'] == 'trapezoidal':
            print(f"Base Maior: {campo['campo']['base_maior_m']} m")
            print(f"Base Menor: {campo['campo']['base_menor_m']} m")
            print(f"Altura: {campo['campo']['altura_m']} m")
        
        print(f"\nÁrea Total: {campo['campo']['area_total_m2']:.2f} m² ({campo['campo']['area_total_hectare']:.2f} ha)")
        
        # Exibir dados de insumos, se disponíveis
        if 'dados_insumos' in campo['campo'] and campo['campo']['dados_insumos']:
            insumos = campo['campo']['dados_insumos']
            print("\nDados de Insumos:")
            print(f"  Fertilizante Utilizado: {insumos.get('fertilizante_utilizado', 'NPK Misto')}")
            print(f"  Quantidade Total: {insumos.get('quantidade_total_kg', 0):.2f} kg")
            print(f"  Quantidade por Metro Linear: {insumos.get('quantidade_por_metro_linear_kg', 0):.2f} kg/m")
            
            if 'irrigacao' in insumos:
                irrigacao = insumos['irrigacao']
                print("\nDados de Irrigação:")
                print(f"  Método: {irrigacao.get('metodo', 'aspersão')}")
                print(f"  Quantidade de Ruas: {irrigacao.get('quantidade_ruas', 0)}")
                print(f"  Volume por Metro: {irrigacao.get('volume_litros_por_metro', 0):.2f} L/m")
                print(f"  Volume Total: {irrigacao.get('quantidade_total_litros', 0):.2f} L")
        
    except (ValueError, IndexError) as e:
        print(f"Erro: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def adicionar_campo():
    """Adiciona um novo campo"""
    limpar_tela()
    print("\n===== Adicionar Novo Campo =====")
    
    # Obter lista de culturas disponíveis
    culturas = db_service.obter_todas_culturas()
    if not culturas:
        print("Não há culturas cadastradas. Cadastre uma cultura primeiro.")
        input("\nPressione Enter para continuar...")
        return
    
    try:
        nome_produtor = input("Nome do Produtor: ")
        
        print("\nLocalização:")
        municipio = input("Município: ")
        regiao = input("Região: ")
        
        print("\nCultura Plantada:")
        print("Culturas disponíveis:")
        for i, cultura in enumerate(culturas, 1):
            print(f"{i}. {cultura['nome_cultura']}")
        
        indice_cultura = int(input("\nEscolha o número da cultura: ")) - 1
        if indice_cultura < 0 or indice_cultura >= len(culturas):
            print("Índice inválido.")
            input("\nPressione Enter para continuar...")
            return
        
        cultura_plantada = culturas[indice_cultura]['nome_cultura']
        data_plantio = input("Data de Plantio (AAAA-MM-DD): ")
        
        print("\nTipo de Geometria:")
        print("1. Retangular")
        print("2. Triangular")
        print("3. Circular")
        print("4. Trapezoidal")
        tipo_opcao = input("Escolha o tipo de geometria (1-4): ")
        
        campo_data = {
            "tipo_geometria": "",
            "cultura_plantada": cultura_plantada,
            "data_plantio": data_plantio
        }
        
        if tipo_opcao == '1':
            campo_data["tipo_geometria"] = "retangular"
            campo_data["comprimento_m"] = float(input("Comprimento (m): "))
            campo_data["largura_m"] = float(input("Largura (m): "))
        elif tipo_opcao == '2':
            campo_data["tipo_geometria"] = "triangular"
            campo_data["base_m"] = float(input("Base (m): "))
            campo_data["altura_m"] = float(input("Altura (m): "))
        elif tipo_opcao == '3':
            campo_data["tipo_geometria"] = "circular"
            campo_data["raio_m"] = float(input("Raio (m): "))
        elif tipo_opcao == '4':
            campo_data["tipo_geometria"] = "trapezoidal"
            campo_data["base_maior_m"] = float(input("Base Maior (m): "))
            campo_data["base_menor_m"] = float(input("Base Menor (m): "))
            campo_data["altura_m"] = float(input("Altura (m): "))
        else:
            print("Opção inválida.")
            input("\nPressione Enter para continuar...")
            return
        
        # Criar instância do campo
        campo = Campo(
            nome_produtor=nome_produtor,
            localizacao={
                "municipio": municipio,
                "regiao": regiao
            },
            campo=campo_data
        )
        
        # Calcular área
        campo.calcular_area()
        
        # Calcular insumos com base na cultura
        cultura = db_service.obter_cultura_por_nome(cultura_plantada)
        if cultura:
            campo.calcular_quantidade_insumos(cultura)
            
            # Perguntar se deseja fazer cálculo detalhado da irrigação
            calcular_irrig_detalhado = input("\nDeseja fazer um cálculo detalhado da irrigação? (S/N): ").upper() == 'S'
            
            if calcular_irrig_detalhado:
                print("\n===== Cálculo Detalhado de Irrigação =====")
                
                # Para campos retangulares, podemos usar o comprimento e largura diretamente
                if campo_data["tipo_geometria"] == "retangular":
                    comprimento = campo_data["comprimento_m"]
                    largura = campo_data["largura_m"]
                    
                    # Perguntar o volume por metro
                    volume_por_metro = float(input("Volume de água por metro linear (L/m) [padrão 0.5]: ") or "0.5")
                    
                    # Calcular irrigação usando nossa função
                    espacamento = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
                    num_linhas = int(largura / espacamento)
                    volume_por_linha = volume_por_metro * comprimento
                    volume_total = volume_por_linha * num_linhas
                    
                    irrigacao = {
                        'metodo': 'gotejamento',
                        'espacamento_entre_linhas': espacamento,
                        'quantidade_ruas': num_linhas,
                        'volume_litros_por_metro': volume_por_metro,
                        'volume_litros_por_linha': volume_por_linha,
                        'quantidade_total_litros': volume_total
                    }
                    
                elif campo_data["tipo_geometria"] == "triangular":
                    # Solicitar como o produtor pretende fazer a irrigação
                    print("\nPara um campo triangular, como você pretende organizar as linhas de irrigação?")
                    print("1. Paralelas à base")
                    print("2. Paralelas à altura")
                    orientacao = input("Escolha uma opção (1-2) [padrão: 1]: ") or "1"
                    
                    base = campo_data["base_m"]
                    altura = campo_data["altura_m"]
                    
                    volume_por_metro = float(input("Volume de água por metro linear (L/m) [padrão 0.5]: ") or "0.5")
                    
                    # Ajustar o cálculo conforme a orientação escolhida
                    if orientacao == "1":
                        # Calcular com linhas paralelas à base
                        comprimento_medio = base / 2  # média do comprimento das linhas
                        num_linhas = int(altura / cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas'])
                        
                        irrigacao = {
                            'metodo': 'gotejamento',
                            'espacamento_entre_linhas': cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas'],
                            'quantidade_ruas': num_linhas,
                            'volume_litros_por_metro': volume_por_metro,
                            'volume_litros_por_linha': comprimento_medio * volume_por_metro,
                            'quantidade_total_litros': num_linhas * comprimento_medio * volume_por_metro
                        }
                    else:
                        # Calcular com linhas paralelas à altura
                        comprimento_medio = altura / 2  # média do comprimento das linhas
                        num_linhas = int(base / cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas'])
                        
                        irrigacao = {
                            'metodo': 'gotejamento',
                            'espacamento_entre_linhas': cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas'],
                            'quantidade_ruas': num_linhas,
                            'volume_litros_por_metro': volume_por_metro,
                            'volume_litros_por_linha': comprimento_medio * volume_por_metro,
                            'quantidade_total_litros': num_linhas * comprimento_medio * volume_por_metro
                        }
                        
                elif campo_data["tipo_geometria"] == "circular":
                    raio = campo_data["raio_m"]
                    
                    # Perguntar o método de irrigação
                    print("\nPara um campo circular, qual método de irrigação você pretende usar?")
                    print("1. Pivô central")
                    print("2. Linhas paralelas")
                    metodo = input("Escolha uma opção (1-2) [padrão: 1]: ") or "1"
                    
                    volume_por_metro = float(input("Volume de água por metro linear (L/m) [padrão 0.5]: ") or "0.5")
                    
                    if metodo == "1":
                        # Pivô central - cálculo simplificado
                        comprimento_total = 2 * 3.14159 * raio  # Circunferência
                        irrigacao = {
                            'metodo': 'pivô central',
                            'raio': raio,
                            'comprimento_perimetro': comprimento_total,
                            'volume_litros_por_metro': volume_por_metro,
                            'quantidade_total_litros': comprimento_total * volume_por_metro
                        }
                    else:
                        # Linhas paralelas
                        espacamento = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
                        num_linhas = int(2 * raio / espacamento)
                        comprimento_medio = 1.5708 * raio  # média aproximada (π/2 * raio)
                        
                        irrigacao = {
                            'metodo': 'gotejamento',
                            'espacamento_entre_linhas': espacamento,
                            'quantidade_ruas': num_linhas,
                            'volume_litros_por_metro': volume_por_metro,
                            'volume_litros_por_linha': comprimento_medio * volume_por_metro,
                            'quantidade_total_litros': num_linhas * comprimento_medio * volume_por_metro
                        }
                
                elif campo_data["tipo_geometria"] == "trapezoidal":
                    base_maior = campo_data["base_maior_m"]
                    base_menor = campo_data["base_menor_m"]
                    altura = campo_data["altura_m"]
                    
                    volume_por_metro = float(input("Volume de água por metro linear (L/m) [padrão 0.5]: ") or "0.5")
                    
                    # Calcular com linhas paralelas às bases
                    espacamento = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
                    num_linhas = int(altura / espacamento)
                    comprimento_medio = (base_maior + base_menor) / 2  # média do comprimento das linhas
                    
                    irrigacao = {
                        'metodo': 'gotejamento',
                        'espacamento_entre_linhas': espacamento,
                        'quantidade_ruas': num_linhas,
                        'volume_litros_por_metro': volume_por_metro,
                        'volume_litros_por_linha': comprimento_medio * volume_por_metro,
                        'quantidade_total_litros': num_linhas * comprimento_medio * volume_por_metro
                    }
                
                else:
                    # Para outros tipos de geometria desconhecidos, fazer um cálculo aproximado com base na área
                    area_hectare = campo.campo['area_total_hectare']
                    volume_por_metro = float(input("Volume de água por metro linear (L/m) [padrão 0.5]: ") or "0.5")
                    
                    # Cálculo manual em vez de usar um método que não existe
                    espacamento = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
                    metros_lineares = (area_hectare * 10000) / espacamento
                    lado = (area_hectare * 10000) ** 0.5  # Raiz quadrada da área em m²
                    num_linhas = int(lado / espacamento)
                    
                    # Comprimento médio de cada linha
                    comprimento_medio = metros_lineares / num_linhas if num_linhas > 0 else 0
                    
                    irrigacao = {
                        'metodo': 'gotejamento',
                        'espacamento_entre_linhas': espacamento,
                        'quantidade_ruas': num_linhas,
                        'volume_litros_por_metro': volume_por_metro,
                        'volume_litros_por_linha': comprimento_medio * volume_por_metro,
                        'quantidade_total_litros': metros_lineares * volume_por_metro
                    }
            
            else:
                # Cálculo automático simplificado para qualquer tipo de geometria
                print("\nRealizando cálculo automático de irrigação...")
                area_hectare = campo.campo['area_total_hectare']
                volume_por_metro = 0.5  # Valor padrão
                
                # Cálculo manual em vez de usar um método que não existe
                espacamento = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
                metros_lineares = (area_hectare * 10000) / espacamento
                
                # Para campos retangulares, podemos fazer um cálculo mais preciso
                if campo_data["tipo_geometria"] == "retangular":
                    comprimento = campo_data["comprimento_m"]
                    largura = campo_data["largura_m"]
                    num_linhas = int(largura / espacamento)
                    volume_total = comprimento * num_linhas * volume_por_metro
                else:
                    # Para outros tipos, usamos aproximação baseada em área
                    num_linhas = int((area_hectare * 10000) ** 0.5 / espacamento)
                    volume_total = metros_lineares * volume_por_metro
                
                irrigacao = {
                    'metodo': 'gotejamento',
                    'espacamento_entre_linhas': espacamento,
                    'quantidade_ruas': num_linhas,
                    'volume_litros_por_metro': volume_por_metro,
                    'quantidade_total_litros': volume_total
                }
            
            # Adicionar dados de irrigação ao campo (em ambos os casos)
            if 'dados_insumos' not in campo.campo:
                campo.campo['dados_insumos'] = {}
            
            campo.campo['dados_insumos']['irrigacao'] = irrigacao
                    
            print("\nDados de irrigação calculados com sucesso!")
            # Exibir resultados baseados no tipo de geometria e de cálculo
            if 'quantidade_ruas' in irrigacao:
                print(f"Número de linhas: {irrigacao['quantidade_ruas']}")
            if 'volume_litros_por_linha' in irrigacao:
                print(f"Volume por linha: {irrigacao.get('volume_litros_por_linha', 0):.2f} L")
            print(f"Volume total: {irrigacao['quantidade_total_litros']:.2f} L")
        
        # Salvar no banco de dados
        db_service.adicionar_campo(campo)
        
        print(f"\nCampo adicionado com sucesso!")
        print(f"Área calculada: {campo.campo['area_total_m2']:.2f} m² ({campo.campo['area_total_hectare']:.2f} ha)")
        
    except Exception as e:
        print(f"\nErro ao adicionar campo: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def atualizar_campo():
    """Atualiza um campo existente"""
    limpar_tela()
    print("\n===== Atualizar Campo Existente =====")
    
    campos = db_service.obter_todos_campos()
    
    if not campos:
        print("Nenhum campo cadastrado.")
        input("\nPressione Enter para continuar...")
        return
    
    print("Campos disponíveis:")
    for i, campo in enumerate(campos, 1):
        print(f"{i}. {campo['nome_produtor']} - {campo['campo']['cultura_plantada']}")
    
    try:
        indice = int(input("\nEscolha o número do campo: ")) - 1
        
        if indice < 0 or indice >= len(campos):
            print("Índice inválido.")
            input("\nPressione Enter para continuar...")
            return
        
        campo = campos[indice]
        campo_id = campo['_id']
        
        dados_atualizados = {}
        
        print("\nDigite os novos valores (ou pressione Enter para manter os atuais):")
        
        # ===== Nome do produtor =====
        nome_produtor = input(f"Nome do Produtor [{campo['nome_produtor']}]: ") or campo['nome_produtor']
        dados_atualizados['nome_produtor'] = nome_produtor

        # ===== Localização =====
        if input("\nDeseja atualizar a Localização? (s/n): ").lower() == 's':
            localizacao = campo.get('localizacao', {})
            municipio = input(f"Município [{localizacao.get('municipio', '')}]: ") or localizacao.get('municipio', '')
            regiao = input(f"Região [{localizacao.get('regiao', '')}]: ") or localizacao.get('regiao', '')
            dados_atualizados['localizacao'] = {
                "municipio": municipio,
                "regiao": regiao
            }

        # ===== Dados do Campo =====
        if input("\nDeseja atualizar os Dados do Campo? (s/n): ").lower() == 's':
            campo_info = campo.get('campo', {})

            cultura = input(f"Cultura plantada [{campo_info.get('cultura_plantada', '')}]: ") or campo_info.get('cultura_plantada', '')
            data_plantio = input(f"Data de Plantio [{campo_info.get('data_plantio', '')}]: ") or campo_info.get('data_plantio', '')

            tipo_geometria_atual = campo_info.get('tipo_geometria', '')
            print(f"Tipo de Geometria atual [{tipo_geometria_atual}]")
            print("Opções válidas: retangular, triangular, circular, trapezoidal")

            tipo_geometria = input(f"Tipo de Geometria [{tipo_geometria_atual}]: ") or tipo_geometria_atual

            while tipo_geometria.lower() not in ["retangular", "triangular", "circular", "trapezoidal"]:
                print("Tipo inválido. Escolha entre: retangular, triangular, circular ou trapezoidal.")
                tipo_geometria = input(f"Tipo de Geometria [{tipo_geometria_atual}]: ") or tipo_geometria_atual

            campo_atualizado = {
                "cultura_plantada": cultura,
                "data_plantio": data_plantio,
                "tipo_geometria": tipo_geometria.lower()
            }

            # Atualizar geometria específica
            if tipo_geometria == "retangular":
                comprimento = input(f"Comprimento (m) [{campo_info.get('comprimento_m', '')}]: ")
                largura = input(f"Largura (m) [{campo_info.get('largura_m', '')}]: ")
                campo_atualizado.update({
                    "comprimento_m": float(comprimento) if comprimento else campo_info.get('comprimento_m'),
                    "largura_m": float(largura) if largura else campo_info.get('largura_m')
                })

            elif tipo_geometria == "triangular":
                base = input(f"Base (m) [{campo_info.get('base_m', '')}]: ")
                altura = input(f"Altura (m) [{campo_info.get('altura_m', '')}]: ")
                campo_atualizado.update({
                    "base_m": float(base) if base else campo_info.get('base_m'),
                    "altura_m": float(altura) if altura else campo_info.get('altura_m')
                })

            elif tipo_geometria == "circular":
                raio = input(f"Raio (m) [{campo_info.get('raio_m', '')}]: ")
                campo_atualizado.update({
                    "raio_m": float(raio) if raio else campo_info.get('raio_m')
                })

            elif tipo_geometria == "trapezoidal":
                base_maior = input(f"Base Maior (m) [{campo_info.get('base_maior_m', '')}]: ")
                base_menor = input(f"Base Menor (m) [{campo_info.get('base_menor_m', '')}]: ")
                altura = input(f"Altura (m) [{campo_info.get('altura_m', '')}]: ")
                campo_atualizado.update({
                    "base_maior_m": float(base_maior) if base_maior else campo_info.get('base_maior_m'),
                    "base_menor_m": float(base_menor) if base_menor else campo_info.get('base_menor_m'),
                    "altura_m": float(altura) if altura else campo_info.get('altura_m')
                })

            # Área
            area_m2 = input(f"Área total (m²) [{campo_info.get('area_total_m2', '')}]: ")
            area_ha = input(f"Área total (hectare) [{campo_info.get('area_total_hectare', '')}]: ")

            campo_atualizado.update({
                "area_total_m2": float(area_m2) if area_m2 else campo_info.get('area_total_m2'),
                "area_total_hectare": float(area_ha) if area_ha else campo_info.get('area_total_hectare')
            })

            # ===== Dados de Insumos =====
            if input("\nDeseja atualizar os Dados de Insumos? (s/n): ").lower() == 's':
                insumos = campo_info.get('dados_insumos', {})

                N = input(f"N (kg) [{insumos.get('fertilizante_recomendado', {}).get('N', '')}]: ")
                P = input(f"P2O5 (kg) [{insumos.get('fertilizante_recomendado', {}).get('P2O5', '')}]: ")
                K = input(f"K2O (kg) [{insumos.get('fertilizante_recomendado', {}).get('K2O', '')}]: ")

                quantidade_total_kg = input(f"Quantidade total de fertilizante (kg) [{insumos.get('quantidade_total_kg', '')}]: ")
                quantidade_por_metro = input(f"Quantidade por metro linear (kg) [{insumos.get('quantidade_por_metro_linear_kg', '')}]: ")

                dados_insumos = {
                    "fertilizante_recomendado": {
                        "N": float(N) if N else insumos.get('fertilizante_recomendado', {}).get('N'),
                        "P2O5": float(P) if P else insumos.get('fertilizante_recomendado', {}).get('P2O5'),
                        "K2O": float(K) if K else insumos.get('fertilizante_recomendado', {}).get('K2O')
                    },
                    "quantidade_total_kg": float(quantidade_total_kg) if quantidade_total_kg else insumos.get('quantidade_total_kg'),
                    "quantidade_por_metro_linear_kg": float(quantidade_por_metro) if quantidade_por_metro else insumos.get('quantidade_por_metro_linear_kg')
                }

                # ===== Dados de Irrigação =====
                if 'irrigacao' in insumos and input("\nDeseja atualizar os Dados de Irrigação? (s/n): ").lower() == 's':
                    irrigacao = insumos.get('irrigacao', {})
                    metodo = input(f"Método de irrigação [{irrigacao.get('metodo', '')}]: ") or irrigacao.get('metodo', '')
                    volume_metro = input(f"Volume (L/m) [{irrigacao.get('volume_litros_por_metro', '')}]: ")
                    ruas = input(f"Quantidade de ruas [{irrigacao.get('quantidade_ruas', '')}]: ")
                    volume_total = input(f"Volume total (L) [{irrigacao.get('quantidade_total_litros', '')}]: ")

                    dados_insumos['irrigacao'] = {
                        "metodo": metodo,
                        "volume_litros_por_metro": float(volume_metro) if volume_metro else irrigacao.get('volume_litros_por_metro'),
                        "quantidade_ruas": int(ruas) if ruas else irrigacao.get('quantidade_ruas'),
                        "quantidade_total_litros": float(volume_total) if volume_total else irrigacao.get('quantidade_total_litros')
                    }
                else:
                    if 'irrigacao' in insumos:
                        dados_insumos['irrigacao'] = insumos['irrigacao']

                campo_atualizado['dados_insumos'] = dados_insumos
            else:
                campo_atualizado['dados_insumos'] = campo_info.get('dados_insumos', {})

            dados_atualizados['campo'] = campo_atualizado

        # ===== Atualizar no banco =====
        db_service.atualizar_campo(campo_id, dados_atualizados)

        print("\nCampo atualizado com sucesso!")

    except Exception as e:
        print(f"\nErro ao atualizar campo: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def remover_campo():
    """Remove um campo"""
    limpar_tela()
    print("\n===== Remover Campo =====")
    
    campos = db_service.obter_todos_campos()
    
    if not campos:
        print("Nenhum campo cadastrado.")
        input("\nPressione Enter para continuar...")
        return
    
    print("Campos disponíveis:")
    for i, campo in enumerate(campos, 1):
        print(f"{i}. {campo['nome_produtor']} - {campo['campo']['cultura_plantada']}")
    
    try:
        indice = int(input("\nEscolha o número do campo a ser removido: ")) - 1
        
        if indice < 0 or indice >= len(campos):
            print("Índice inválido.")
            input("\nPressione Enter para continuar...")
            return
        
        campo = campos[indice]
        confirmacao = input(f"Tem certeza que deseja remover o campo de {campo['campo']['cultura_plantada']} do produtor '{campo['nome_produtor']}'? (S/N): ")
        
        if confirmacao.upper() == 'S':
            db_service.remover_campo(campo['_id'])
            print(f"\nCampo removido com sucesso!")
        else:
            print("\nOperação cancelada.")
        
    except Exception as e:
        print(f"\nErro ao remover campo: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def menu_calculadora_area():
    """Menu para calculadora de área"""
    limpar_tela()
    print("\n===== Calculadora de Área =====")
    
    print("Tipos de geometria disponíveis:")
    print("1. Retangular")
    print("2. Triangular")
    print("3. Circular")
    print("4. Trapezoidal")
    
    tipo_opcao = input("\nEscolha o tipo de geometria (1-4): ")
    
    try:
        if tipo_opcao == '1':
            tipo_geometria = "retangular"
            comprimento = float(input("Comprimento (m): "))
            largura = float(input("Largura (m): "))
            
            area = CalculoArea.calcular_area_retangular(comprimento, largura)
            print(f"\nÁrea calculada: {area['area_m2']:.2f} m² ({area['area_hectare']:.2f} ha)")
            
        elif tipo_opcao == '2':
            tipo_geometria = "triangular"
            base = float(input("Base (m): "))
            altura = float(input("Altura (m): "))
            
            area = CalculoArea.calcular_area_triangular(base, altura)
            print(f"\nÁrea calculada: {area['area_m2']:.2f} m² ({area['area_hectare']:.2f} ha)")
            
        elif tipo_opcao == '3':
            tipo_geometria = "circular"
            raio = float(input("Raio (m): "))
            
            area = CalculoArea.calcular_area_circular(raio)
            print(f"\nÁrea calculada: {area['area_m2']:.2f} m² ({area['area_hectare']:.2f} ha)")
            
        elif tipo_opcao == '4':
            tipo_geometria = "trapezoidal"
            base_maior = float(input("Base Maior (m): "))
            base_menor = float(input("Base Menor (m): "))
            altura = float(input("Altura (m): "))
            
            area = CalculoArea.calcular_area_trapezoidal(base_maior, base_menor, altura)
            print(f"\nÁrea calculada: {area['area_m2']:.2f} m² ({area['area_hectare']:.2f} ha)")
            
        else:
            print("Opção inválida.")
    
    except Exception as e:
        print(f"Erro ao calcular área: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def calcular_irrigacao(cultura, comprimento, largura, volume_por_metro):
    """
    Calcula os dados de irrigação com base na cultura e dimensões do campo
    
    Args:
        cultura (dict): Dados da cultura
        comprimento (float): Comprimento do campo em metros
        largura (float): Largura do campo em metros
        volume_por_metro (float): Volume de água por metro linear (L/m)
        
    Returns:
        dict: Dicionário com os dados de irrigação calculados
    """
    try:
        # Obter o espaçamento entre linhas da cultura
        espacamento = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
        
        # Calcular número de linhas
        numero_linhas = int(largura / espacamento)
        
        # Calcular volume por linha
        volume_por_linha = volume_por_metro * comprimento
        
        # Calcular volume total
        volume_total = volume_por_linha * numero_linhas
        
        return {
            'metodo': 'gotejamento',
            'espacamento_entre_linhas': espacamento,
            'quantidade_ruas': numero_linhas,
            'volume_litros_por_metro': volume_por_metro,
            'volume_litros_por_linha': volume_por_linha,
            'quantidade_total_litros': volume_total
        }
    except Exception as e:
        print(f"Erro ao calcular irrigação: {str(e)}")
        return None

def menu_calculadora_insumos():
    """Menu para calculadora de insumos"""
    limpar_tela()
    print("\n===== Calculadora de Insumos =====")
    
    # Obter lista de culturas disponíveis
    culturas = db_service.obter_todas_culturas()
    if not culturas:
        print("Não há culturas cadastradas. Cadastre uma cultura primeiro.")
        input("\nPressione Enter para continuar...")
        return
    
    try:
        print("Culturas disponíveis:")
        for i, cultura in enumerate(culturas, 1):
            print(f"{i}. {cultura['nome_cultura']}")
        
        indice_cultura = int(input("\nEscolha o número da cultura: ")) - 1
        if indice_cultura < 0 or indice_cultura >= len(culturas):
            print("Índice inválido.")
            input("\nPressione Enter para continuar...")
            return
        
        cultura = culturas[indice_cultura]
        
        area_hectare = float(input("\nÁrea em hectares: "))
        
        # Calcular quantidade de insumos
        npk_por_hectare = cultura['fertilizantes_insumos']['adubacao_NPK_por_hectare_kg']
        insumos = CalculoInsumos.calcular_quantidade_fertilizante(area_hectare, npk_por_hectare)
        
        print("\n===== Resultado do Cálculo de Insumos =====")
        print(f"Cultura: {cultura['nome_cultura']}")
        print(f"Área: {area_hectare:.2f} hectares")
        print("\nQuantidade de Fertilizantes:")
        print(f"  Nitrogênio (N): {insumos['N']:.2f} kg")
        print(f"  Fósforo (P2O5): {insumos['P2O5']:.2f} kg")
        print(f"  Potássio (K2O): {insumos['K2O']:.2f} kg")
        print(f"  Total: {insumos['total_kg']:.2f} kg")
        
        # Calcular a quantidade de plantas
        plantas = CalculoArea.calcular_quantidade_plantas(area_hectare, cultura['dados_agronomicos']['densidade_plantio']['plantas_por_hectare'])
        print(f"\nQuantidade estimada de plantas: {plantas}")
        
        # Perguntar se deseja detalhar cálculo de irrigação
        calcular_irrig_detalhado = input("\nDeseja fazer um cálculo detalhado da irrigação? (S/N): ").upper() == 'S'
        
        if calcular_irrig_detalhado:
            print("\n===== Cálculo Detalhado de Irrigação =====")
            
            # Verificar se o usuário conhece as dimensões exatas do campo
            tem_dimensoes = input("Você conhece as dimensões exatas do campo? (S/N): ").upper() == 'S'
            
            if tem_dimensoes:
                # Para campo retangular
                comprimento = float(input("Comprimento do campo (m): "))
                largura = float(input("Largura do campo (m): "))
                volume_por_metro = float(input("Volume de água por metro linear (L/m) [padrão 0.5]: ") or "0.5")
                
                # Calcular irrigação com dimensões exatas
                irrigacao = calcular_irrigacao(cultura, comprimento, largura, volume_por_metro)
                
                print("\nResultados do Cálculo de Irrigação:")
                print(f"Espaçamento entre linhas: {irrigacao['espacamento_entre_linhas']:.2f} m")
                print(f"Número de linhas: {irrigacao['quantidade_ruas']}")
                print(f"Volume por linha: {irrigacao['volume_litros_por_linha']:.2f} L")
                print(f"Volume total: {irrigacao['quantidade_total_litros']:.2f} L")
            else:
                # Usar cálculo aproximado baseado na área
                volume_por_metro = float(input("Volume de água por metro linear (L/m) [padrão 0.5]: ") or "0.5")
                
                # Usar o método da classe CalculoInsumos
                irrigacao = CalculoInsumos.calcular_irrigacao(area_hectare, cultura, volume_por_metro)
                
                print("\nResultados do Cálculo de Irrigação (estimativa):")
                print(f"Espaçamento entre linhas: {irrigacao['espacamento_entre_linhas']:.2f} m")
                print(f"Número estimado de linhas: {irrigacao['quantidade_ruas']}")
                print(f"Comprimento médio das linhas: {irrigacao['comprimento_medio_linha']:.2f} m")
                print(f"Volume por metro linear: {irrigacao['volume_litros_por_metro']:.2f} L/m")
                print(f"Volume total estimado: {irrigacao['quantidade_total_litros']:.2f} L")
        else:
            # Cálculo simplificado (original do código)
            espacamento_entre_linhas = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
            metros_lineares = (area_hectare * 10000) / espacamento_entre_linhas
            
            volume_por_metro = 0.5  # Padrão: 0.5 L/m
            volume_total = metros_lineares * volume_por_metro
            
            print("\nDados de Irrigação (simplificado):")
            print(f"  Metros lineares estimados: {metros_lineares:.2f} m")
            print(f"  Volume por metro linear: {volume_por_metro} L/m")
            print(f"  Volume total estimado: {volume_total:.2f} L")
        
    except Exception as e:
        print(f"\nErro ao calcular insumos: {str(e)}")
    
    input("\nPressione Enter para continuar...")

@staticmethod
def calcular_irrigacao(area_hectare, cultura, volume_por_metro=0.5):
    """
    Calcula a irrigação necessária para uma área com base na cultura
    
    Args:
        area_hectare (float): Área em hectares
        cultura (dict): Dados da cultura
        volume_por_metro (float): Volume de água por metro linear (L/m)
        
    Returns:
        dict: Dicionário com os dados de irrigação calculados
    """
    try:
        # Obter o espaçamento entre linhas da cultura
        espacamento = cultura['dados_agronomicos']['densidade_plantio']['espacamento_m']['entre_linhas']
        
        # Calcular metros lineares totais
        metros_lineares = (area_hectare * 10000) / espacamento
        
        # Número de linhas (aproximado para uma área quadrada, ajustar conforme necessário)
        lado = (area_hectare * 10000) ** 0.5  # Raiz quadrada da área em m²
        numero_linhas = int(lado / espacamento)
        
        # Comprimento médio de cada linha
        comprimento_medio = metros_lineares / numero_linhas if numero_linhas > 0 else 0
        
        # Calcular volume por linha
        volume_por_linha = volume_por_metro * comprimento_medio
        
        # Calcular volume total
        volume_total = volume_por_metro * metros_lineares
        
        return {
            'metodo': 'gotejamento',
            'espacamento_entre_linhas': espacamento,
            'quantidade_ruas': numero_linhas,
            'comprimento_medio_linha': comprimento_medio,
            'volume_litros_por_metro': volume_por_metro,
            'volume_litros_por_linha': volume_por_linha,
            'quantidade_total_litros': volume_total
        }
    except Exception as e:
        print(f"Erro ao calcular irrigação: {str(e)}")
        return None

def exportar_dados():
    """Exporta dados para arquivos CSV para análise em R"""
    import datetime
    
    limpar_tela()
    print("\n===== Exportar Dados para Análise =====")
    
    # Obter data e hora atual para o nome do arquivo
    data_atual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Perguntar ao usuário se deseja usar um diretório personalizado
    usar_diretorio_personalizado = input("Deseja exportar para um diretório específico? (S/N): ").upper() == 'S'
    
    diretorio_exportacao = ""
    if usar_diretorio_personalizado:
        diretorio_exportacao = input("Digite o caminho completo do diretório: ")
        # Verificar se o diretório existe
        if not os.path.exists(diretorio_exportacao):
            try:
                os.makedirs(diretorio_exportacao)
                print(f"Diretório '{diretorio_exportacao}' criado com sucesso.")
            except Exception as e:
                print(f"Erro ao criar diretório: {str(e)}")
                diretorio_exportacao = ""
                input("\nUsando diretório atual. Pressione Enter para continuar...")
    
    # Preparar prefixo do nome do arquivo
    prefixo_arquivo = f"farmtech_export_{data_atual}"
    
    try:
        # Exportar culturas
        culturas = db_service.obter_todas_culturas()
        culturas_exportadas = False
        if culturas:
            # Construir caminho do arquivo
            arquivo_culturas = os.path.join(diretorio_exportacao, f"{prefixo_arquivo}_culturas.csv")
            
            with open(arquivo_culturas, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write("nome_cultura,nome_cientifico,ciclo_minimo,ciclo_maximo,temperatura_min,temperatura_max,precipitacao_min,precipitacao_max\n")
                
                # Dados
                for cultura in culturas:
                    f.write(f"{cultura['nome_cultura']},{cultura['nome_cientifico']}")
                    f.write(f",{cultura['dados_agronomicos']['ciclo_producao_dias']['minimo']}")
                    f.write(f",{cultura['dados_agronomicos']['ciclo_producao_dias']['maximo']}")
                    f.write(f",{cultura['clima_solo']['temperatura_ideal_c']['minima']}")
                    f.write(f",{cultura['clima_solo']['temperatura_ideal_c']['maxima']}")
                    f.write(f",{cultura['clima_solo']['precipitacao_minima_mm']}")
                    f.write(f",{cultura['clima_solo']['precipitacao_maxima_mm']}\n")
            
            print(f"Arquivo de culturas exportado: {arquivo_culturas}")
            culturas_exportadas = True
        
        # Exportar campos
        campos = db_service.obter_todos_campos()
        campos_exportados = False
        if campos:
            # Construir caminho do arquivo
            arquivo_campos = os.path.join(diretorio_exportacao, f"{prefixo_arquivo}_campos.csv")
            
            with open(arquivo_campos, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write("nome_produtor,municipio,regiao,cultura_plantada,tipo_geometria,area_m2,area_hectare\n")
                
                # Dados
                for campo in campos:
                    f.write(f"{campo['nome_produtor']},{campo['localizacao']['municipio']},{campo['localizacao']['regiao']}")
                    f.write(f",{campo['campo']['cultura_plantada']},{campo['campo']['tipo_geometria']}")
                    f.write(f",{campo['campo']['area_total_m2']},{campo['campo']['area_total_hectare']}\n")
            
            print(f"Arquivo de campos exportado: {arquivo_campos}")
            campos_exportados = True
        
        
        
        # Exportar insumos com informações detalhadas de irrigação
        insumos_exportados = False
        if campos:
            arquivo_insumos = os.path.join(diretorio_exportacao, f"{prefixo_arquivo}_insumos.csv")
            
            with open(arquivo_insumos, 'w', encoding='utf-8') as f:
                # Cabeçalho expandido com mais dados de irrigação
                f.write("nome_produtor,cultura_plantada,area_hectare,fertilizante_total_kg,")
                f.write("irrigacao_metodo,irrigacao_espacamento,irrigacao_linhas,")
                f.write("irrigacao_volume_por_metro,irrigacao_volume_total\n")
                
                # Dados
                registros_insumos = 0
                for campo in campos:
                    if 'dados_insumos' in campo['campo'] and campo['campo']['dados_insumos']:
                        insumos = campo['campo']['dados_insumos']
                        
                        # Informações básicas
                        f.write(f"{campo['nome_produtor']},{campo['campo']['cultura_plantada']}")
                        f.write(f",{campo['campo']['area_total_hectare']}")
                        f.write(f",{insumos.get('quantidade_total_kg', 0)}")
                        
                        # Dados de irrigação, se disponíveis
                        if 'irrigacao' in insumos:
                            irrigacao = insumos['irrigacao']
                            f.write(f",{irrigacao.get('metodo', 'gotejamento')}")
                            f.write(f",{irrigacao.get('espacamento_entre_linhas', 0)}")
                            f.write(f",{irrigacao.get('quantidade_ruas', 0)}")
                            f.write(f",{irrigacao.get('volume_litros_por_metro', 0)}")
                            f.write(f",{irrigacao.get('quantidade_total_litros', 0)}")
                        else:
                            # Se não há dados de irrigação, preencher com valores padrão
                            f.write(",N/A,0,0,0,0")
                        
                        f.write("\n")
                        registros_insumos += 1
            
            if registros_insumos > 0:
                print(f"Arquivo de insumos exportado: {arquivo_insumos}")
                insumos_exportados = True
            else:
                print("Nenhum registro de insumos para exportar.")
                os.remove(arquivo_insumos)  # Remove o arquivo vazio
        
        # Criar um arquivo de resumo
        arquivo_resumo = os.path.join(diretorio_exportacao, f"{prefixo_arquivo}_resumo.txt")
        with open(arquivo_resumo, 'w', encoding='utf-8') as f:
            f.write("===== RESUMO DE EXPORTAÇÃO FARMTECH =====\n")
            f.write(f"Data e hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            if culturas_exportadas:
                f.write(f"Culturas exportadas: {len(culturas)}\n")
            else:
                f.write("Nenhuma cultura exportada\n")
                
            if campos_exportados:
                f.write(f"Campos exportados: {len(campos)}\n")
            else:
                f.write("Nenhum campo exportado\n")
                
            if insumos_exportados:
                f.write(f"Registros de insumos exportados: {registros_insumos}\n")
            else:
                f.write("Nenhum registro de insumos exportado\n")
        
        print(f"Arquivo de resumo exportado: {arquivo_resumo}")
        
        if not culturas_exportadas and not campos_exportados and not insumos_exportados:
            print("Não há dados para exportar.")
    
    except Exception as e:
        print(f"\nErro ao exportar dados: {str(e)}")
    
    input("\nPressione Enter para continuar...")

def main():
    """Função principal"""
    while True:
        opcao = exibir_menu()
        
        if opcao == '1':
            menu_culturas()
        elif opcao == '2':
            menu_campos()
        elif opcao == '3':
            menu_calculadora_area()
        elif opcao == '4':
            menu_calculadora_insumos()
        elif opcao == '5':
            exportar_dados()
        elif opcao == '6':
            limpar_tela()
            print("\nObrigado por utilizar o FarmTech Solutions!")
            print("Saindo do programa...")
            break
        else:
            input("Opção inválida. Pressione Enter para continuar...")

if __name__ == "__main__":
    main()