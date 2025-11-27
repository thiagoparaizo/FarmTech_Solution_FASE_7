# app/routes/catalogo_routes.py
from flask import Blueprint, render_template, current_app
from app.services.oracle_db_service import OracleDatabaseService

catalogo_bp = Blueprint('catalogo', __name__)

# Obter instância de serviço
def get_oracle_db():
    from app import oracle_db_service
    return oracle_db_service

@catalogo_bp.route('/')
def index():
    """Página principal do catálogo de sensores"""
    oracle_db = get_oracle_db()
    
    # Obter todos os fabricantes e modelos
    fabricantes = oracle_db.obter_todos_fabricantes()
    modelos = oracle_db.obter_todos_modelos()
    
    # Separar modelos por tipo
    modelos_umidade = [m for m in modelos if m.tipo == 'S1']
    modelos_ph = [m for m in modelos if m.tipo == 'S2']
    modelos_nutrientes = [m for m in modelos if m.tipo == 'S3']
    
    return render_template('catalogo/index.html',
                          fabricantes=fabricantes,
                          modelos=modelos,
                          modelos_umidade=modelos_umidade,
                          modelos_ph=modelos_ph,
                          modelos_nutrientes=modelos_nutrientes)

@catalogo_bp.route('/fabricantes/<int:fabricante_id>')
def detalhe_fabricante(fabricante_id):
    """Página de detalhes de um fabricante"""
    oracle_db = get_oracle_db()
    
    # Obter fabricante
    fabricante = oracle_db.obter_fabricante_por_id(fabricante_id)
    if not fabricante:
        return render_template('errors/404.html'), 404
    
    return render_template('catalogo/detalhe_fabricante.html',
                          fabricante=fabricante)

@catalogo_bp.route('/modelos/<int:modelo_id>')
def detalhe_modelo(modelo_id):
    """Página de detalhes de um modelo"""
    oracle_db = get_oracle_db()
    
    # Obter modelo
    modelo = oracle_db.obter_modelo_por_id(modelo_id)
    if not modelo:
        return render_template('errors/404.html'), 404
    
    return render_template('catalogo/detalhe_modelo.html',
                          modelo=modelo)

@catalogo_bp.route('/tipo/<tipo>')
def modelos_por_tipo(tipo):
    """Página de modelos por tipo"""
    oracle_db = get_oracle_db()
    
    # Obter modelos do tipo especificado
    modelos = oracle_db.obter_modelos_por_tipo(tipo)
    
    # Definir título com base no tipo
    titulo = "Sensores de Umidade"
    if tipo == 'S2':
        titulo = "Sensores de pH"
    elif tipo == 'S3':
        titulo = "Sensores de Nutrientes"
    
    return render_template('catalogo/modelos_por_tipo.html',
                          modelos=modelos,
                          tipo=tipo,
                          titulo=titulo)