from flask import Blueprint, jsonify, request, current_app
from app.models.cultura import Cultura
from app.models.campo import Campo
from app.services.db_service import DatabaseService
from app.services.calculo_area import CalculoArea
from app.services.calculo_insumos import CalculoInsumos
from bson import json_util, ObjectId
import json

api_bp = Blueprint('api', __name__)

# Função auxiliar para converter BSON para JSON
def parse_json(data):
    return json.loads(json_util.dumps(data))

# Rotas para culturas
@api_bp.route('/culturas', methods=['GET'])
def obter_culturas():
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    culturas = db_service.obter_todas_culturas()
    return jsonify(parse_json(culturas))

@api_bp.route('/culturas/<cultura_id>', methods=['GET'])
def obter_cultura(cultura_id):
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    cultura = db_service.obter_cultura_por_id(cultura_id)
    if not cultura:
        return jsonify({"erro": "Cultura não encontrada"}), 404
    return jsonify(parse_json(cultura))

@api_bp.route('/culturas', methods=['POST'])
def adicionar_cultura():
    dados = request.json
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        cultura = Cultura.from_dict(dados)
        cultura_id = db_service.adicionar_cultura(cultura)
        return jsonify({"mensagem": "Cultura adicionada com sucesso", "id": str(cultura_id)}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@api_bp.route('/culturas/<cultura_id>', methods=['PUT'])
def atualizar_cultura(cultura_id):
    dados = request.json
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        resultado = db_service.atualizar_cultura(cultura_id, dados)
        if resultado:
            return jsonify({"mensagem": "Cultura atualizada com sucesso"})
        return jsonify({"erro": "Cultura não encontrada"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@api_bp.route('/culturas/<cultura_id>', methods=['DELETE'])
def remover_cultura(cultura_id):
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        resultado = db_service.remover_cultura(cultura_id)
        if resultado:
            return jsonify({"mensagem": "Cultura removida com sucesso"})
        return jsonify({"erro": "Cultura não encontrada"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Rotas para campos
@api_bp.route('/campos', methods=['GET'])
def obter_campos():
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    campos = db_service.obter_todos_campos()
    return jsonify(parse_json(campos))

@api_bp.route('/campos/<campo_id>', methods=['GET'])
def obter_campo(campo_id):
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    campo = db_service.obter_campo_por_id(campo_id)
    if not campo:
        return jsonify({"erro": "Campo não encontrado"}), 404
    return jsonify(parse_json(campo))

@api_bp.route('/campos', methods=['POST'])
def adicionar_campo():
    dados = request.json
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        # Verificar se a cultura existe
        cultura_nome = dados.get('campo', {}).get('cultura_plantada')
        if cultura_nome:
            cultura = db_service.obter_cultura_por_nome(cultura_nome)
            if not cultura:
                return jsonify({"erro": f"Cultura '{cultura_nome}' não encontrada"}), 404
            
            # Criar instância do campo e calcular área
            campo = Campo.from_dict(dados)
            campo.calcular_area()
            
            # Calcular insumos com base na cultura
            campo.calcular_quantidade_insumos(cultura)
            
            # Salvar no banco de dados
            campo_id = db_service.adicionar_campo(campo)
            return jsonify({
                "mensagem": "Campo adicionado com sucesso", 
                "id": str(campo_id),
                "dados": parse_json(campo.to_dict())
            }), 201
        else:
            return jsonify({"erro": "Cultura plantada não especificada"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@api_bp.route('/campos/<campo_id>', methods=['PUT'])
def atualizar_campo(campo_id):
    dados = request.json
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        resultado = db_service.atualizar_campo(campo_id, dados)
        if resultado:
            return jsonify({"mensagem": "Campo atualizado com sucesso"})
        return jsonify({"erro": "Campo não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@api_bp.route('/campos/<campo_id>', methods=['DELETE'])
def remover_campo(campo_id):
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        resultado = db_service.remover_campo(campo_id)
        if resultado:
            return jsonify({"mensagem": "Campo removido com sucesso"})
        return jsonify({"erro": "Campo não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Rotas para cálculos
@api_bp.route('/calculos/area', methods=['POST'])
def calcular_area():
    dados = request.json
    tipo_geometria = dados.get('tipo_geometria', '').lower()
    
    try:
        resultado = {}
        
        if tipo_geometria == 'retangular':
            comprimento = float(dados.get('comprimento_m', 0))
            largura = float(dados.get('largura_m', 0))
            resultado = CalculoArea.calcular_area_retangular(comprimento, largura)
        
        elif tipo_geometria == 'triangular':
            base = float(dados.get('base_m', 0))
            altura = float(dados.get('altura_m', 0))
            resultado = CalculoArea.calcular_area_triangular(base, altura)
        
        elif tipo_geometria == 'circular':
            raio = float(dados.get('raio_m', 0))
            resultado = CalculoArea.calcular_area_circular(raio)
        
        elif tipo_geometria == 'trapezoidal':
            base_maior = float(dados.get('base_maior_m', 0))
            base_menor = float(dados.get('base_menor_m', 0))
            altura = float(dados.get('altura_m', 0))
            resultado = CalculoArea.calcular_area_trapezoidal(base_maior, base_menor, altura)
        
        else:
            return jsonify({"erro": "Tipo de geometria não suportado"}), 400
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@api_bp.route('/calculos/insumos', methods=['POST'])
def calcular_insumos():
    dados = request.json
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        # Obter dados do campo
        campo = dados.get('campo', {})
        
        # Verificar se a cultura existe
        cultura_nome = campo.get('cultura_plantada')
        if not cultura_nome:
            return jsonify({"erro": "Cultura plantada não especificada"}), 400
        
        cultura = db_service.obter_cultura_por_nome(cultura_nome)
        if not cultura:
            return jsonify({"erro": f"Cultura '{cultura_nome}' não encontrada"}), 404
        
        # Calcular insumos
        resultado = CalculoInsumos.calcular_insumos_completo(campo, cultura)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@api_bp.route('/calculos/plantas', methods=['POST'])
def calcular_plantas():
    dados = request.json
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        area_hectare = float(dados.get('area_hectare', 0))
        cultura_nome = dados.get('cultura')
        
        if not cultura_nome:
            return jsonify({"erro": "Cultura não especificada"}), 400
        
        cultura = db_service.obter_cultura_por_nome(cultura_nome)
        if not cultura:
            return jsonify({"erro": f"Cultura '{cultura_nome}' não encontrada"}), 404
        
        # Obter densidade de plantas por hectare
        densidade = cultura.get('dados_agronomicos', {}).get('densidade_plantio', {}).get('plantas_por_hectare', 0)
        
        # Calcular quantidade de plantas
        quantidade_plantas = CalculoArea.calcular_quantidade_plantas(area_hectare, densidade)
        
        return jsonify({
            'area_hectare': area_hectare,
            'cultura': cultura_nome,
            'densidade_plantas_por_hectare': densidade,
            'quantidade_total_plantas': quantidade_plantas
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 400