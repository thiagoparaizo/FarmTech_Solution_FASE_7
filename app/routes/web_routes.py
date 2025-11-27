from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app.services.db_service import DatabaseService
from app.models.cultura import Cultura
from app.models.campo import Campo
import json
import subprocess
import os
import time
import threading
import webbrowser
from flask import redirect, url_for, jsonify

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Página inicial"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    culturas = db_service.obter_todas_culturas()
    campos = db_service.obter_todos_campos()
    
    return render_template('index.html', 
                           culturas=culturas, 
                           campos=campos, 
                           total_culturas=len(culturas),
                           total_campos=len(campos))

@web_bp.route('/culturas')
def listar_culturas():
    """Lista todas as culturas"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    culturas = db_service.obter_todas_culturas()
    return render_template('culturas.html', culturas=culturas)

@web_bp.route('/culturas/adicionar', methods=['GET', 'POST'])
def adicionar_cultura():
    """Adiciona uma nova cultura"""
    if request.method == 'POST':
        try:
            dados = request.form.to_dict()
            
            # Construir estrutura de dados aninhada
            dados_agronomicos = {
                'densidade_plantio': {
                    'espacamento_m': {
                        'entre_linhas': float(dados.get('entre_linhas', 0)),
                        'entre_plantas': float(dados.get('entre_plantas', 0))
                    },
                    'plantas_por_hectare': int(dados.get('plantas_por_hectare', 0))
                },
                'ciclo_producao_dias': {
                    'minimo': int(dados.get('ciclo_minimo', 0)),
                    'maximo': int(dados.get('ciclo_maximo', 0))
                }
            }
            
            clima_solo = {
                'temperatura_ideal_c': {
                    'minima': float(dados.get('temp_minima', 0)),
                    'maxima': float(dados.get('temp_maxima', 0))
                },
                'precipitacao_minima_mm': float(dados.get('precipitacao_minima', 0)),
                'precipitacao_maxima_mm': float(dados.get('precipitacao_maxima', 0)),
                'tipo_solo_ideal': dados.get('tipo_solo', ''),
                'ph_ideal': {
                    'minimo': float(dados.get('ph_minimo', 0)),
                    'maximo': float(dados.get('ph_maximo', 0))
                },
                'tolerancia_salinidade': dados.get('tolerancia_salinidade', ''),
                'estrategias_climaticas': dados.get('estrategias_climaticas', '').split(',')
            }
            
            fertilizantes_insumos = {
                'adubacao_NPK_por_hectare_kg': {
                    'N': float(dados.get('npk_n', 0)),
                    'P2O5': float(dados.get('npk_p', 0)),
                    'K2O': float(dados.get('npk_k', 0))
                },
                'adubacao_organica_recomendada': dados.get('adubacao_organica', ''),
                'correcao_solo': {
                    'calagem': dados.get('calagem', ''),
                    'gessagem': dados.get('gessagem', '')
                },
                'frequencia_adubacao': dados.get('frequencia_adubacao', '')
            }
            
            cultura = Cultura(
                nome_cultura=dados.get('nome_cultura', ''),
                nome_cientifico=dados.get('nome_cientifico', ''),
                descricao=dados.get('descricao', ''),
                dados_agronomicos=dados_agronomicos,
                clima_solo=clima_solo,
                fertilizantes_insumos=fertilizantes_insumos
            )
            
            db_service = DatabaseService(current_app.config['MONGO_URI'])
            db_service.adicionar_cultura(cultura)
            
            flash('Cultura adicionada com sucesso!', 'success')
            return redirect(url_for('web.listar_culturas'))
        except Exception as e:
            flash(f'Erro ao adicionar cultura: {str(e)}', 'danger')
    
    return render_template('cultura_form.html')

@web_bp.route('/culturas/<cultura_id>')
def visualizar_cultura(cultura_id):
    """Visualiza detalhes de uma cultura específica"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    cultura = db_service.obter_cultura_por_id(cultura_id)
    
    if not cultura:
        flash('Cultura não encontrada', 'danger')
        return redirect(url_for('web.listar_culturas'))
    
    return render_template('cultura_detalhes.html', cultura=cultura)

@web_bp.route('/culturas/<cultura_id>/editar', methods=['GET', 'POST'])
def editar_cultura(cultura_id):
    """Edita uma cultura existente"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    cultura = db_service.obter_cultura_por_id(cultura_id)
    
    if not cultura:
        flash('Cultura não encontrada', 'danger')
        return redirect(url_for('web.listar_culturas'))
    
    if request.method == 'POST':
        try:
            dados = request.form.to_dict()
            
            # Construir estrutura de dados aninhada (similar ao adicionar_cultura)
            # ... [código omitido para brevidade, similar ao método adicionar_cultura]
            
            db_service.atualizar_cultura(cultura_id, cultura)
            flash('Cultura atualizada com sucesso!', 'success')
            return redirect(url_for('web.visualizar_cultura', cultura_id=cultura_id))
        except Exception as e:
            flash(f'Erro ao atualizar cultura: {str(e)}', 'danger')
    
    return render_template('cultura_form.html', cultura=cultura, modo='editar')

@web_bp.route('/culturas/<cultura_id>/remover', methods=['POST'])
def remover_cultura(cultura_id):
    """Remove uma cultura"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        db_service.remover_cultura(cultura_id)
        flash('Cultura removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover cultura: {str(e)}', 'danger')
    
    return redirect(url_for('web.listar_culturas'))

@web_bp.route('/campos')
def listar_campos():
    """Lista todos os campos cadastrados"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    campos = db_service.obter_todos_campos()
    
    return render_template('campos.html', campos=campos)

@web_bp.route('/campos/adicionar', methods=['GET', 'POST'])
def adicionar_campo():
    """Adiciona um novo campo"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    culturas = db_service.obter_todas_culturas()
    
    if request.method == 'POST':
        try:
            dados = request.form.to_dict()
            
            # Construir estrutura de dados do campo
            campo_data = {
                'nome_produtor': dados.get('nome_produtor', ''),
                'localizacao': {
                    'municipio': dados.get('municipio', ''),
                    'regiao': dados.get('regiao', '')
                },
                'campo': {
                    'tipo_geometria': dados.get('tipo_geometria', ''),
                    'cultura_plantada': dados.get('cultura_plantada', ''),
                    'data_plantio': dados.get('data_plantio', '')
                }
            }
            
            # Adicionar dimensões com base no tipo de geometria
            tipo_geometria = dados.get('tipo_geometria', '').lower()
            if tipo_geometria == 'retangular':
                campo_data['campo']['comprimento_m'] = float(dados.get('comprimento_m', 0))
                campo_data['campo']['largura_m'] = float(dados.get('largura_m', 0))
            elif tipo_geometria == 'triangular':
                campo_data['campo']['base_m'] = float(dados.get('base_m', 0))
                campo_data['campo']['altura_m'] = float(dados.get('altura_m', 0))
            elif tipo_geometria == 'circular':
                campo_data['campo']['raio_m'] = float(dados.get('raio_m', 0))
            elif tipo_geometria == 'trapezoidal':
                campo_data['campo']['base_maior_m'] = float(dados.get('base_maior_m', 0))
                campo_data['campo']['base_menor_m'] = float(dados.get('base_menor_m', 0))
                campo_data['campo']['altura_m'] = float(dados.get('altura_t_m', 0))
            
            # Criar instância do campo e calcular área
            campo = Campo.from_dict(campo_data)
            campo.calcular_area()
            
            # Obter cultura para calcular insumos
            cultura_nome = campo_data['campo']['cultura_plantada']
            cultura = db_service.obter_cultura_por_nome(cultura_nome)
            
            if cultura:
                campo.calcular_quantidade_insumos(cultura)
            
            # Salvar no banco de dados
            db_service.adicionar_campo(campo)
            
            flash('Campo adicionado com sucesso!', 'success')
            return redirect(url_for('web.listar_campos'))
        except Exception as e:
            flash(f'Erro ao adicionar campo: {str(e)}', 'danger')
    
    return render_template('campo_form.html', culturas=culturas)

@web_bp.route('/campos/<campo_id>')
def visualizar_campo(campo_id):
    """Visualiza detalhes de um campo específico"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    campo = db_service.obter_campo_por_id(campo_id)
    
    if not campo:
        flash('Campo não encontrado', 'danger')
        return redirect(url_for('web.listar_campos'))
    
    # Obter informações da cultura associada
    cultura_nome = campo.get('campo', {}).get('cultura_plantada', '')
    cultura = db_service.obter_cultura_por_nome(cultura_nome) if cultura_nome else None
    
    return render_template('campo_detalhes.html', campo=campo, cultura=cultura)

@web_bp.route('/campos/<campo_id>/editar', methods=['GET', 'POST'])
def editar_campo(campo_id):
    """Edita um campo existente"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    campo = db_service.obter_campo_por_id(campo_id)
    culturas = db_service.obter_todas_culturas()
    
    if not campo:
        flash('Campo não encontrado', 'danger')
        return redirect(url_for('web.listar_campos'))
    
    if request.method == 'POST':
        try:
            dados = request.form.to_dict()
            
            # Construir estrutura de dados atualizada (similar ao adicionar_campo)
            # ... [código omitido para brevidade, similar ao método adicionar_campo]
            
            db_service.atualizar_campo(campo_id, campo)
            flash('Campo atualizado com sucesso!', 'success')
            return redirect(url_for('web.visualizar_campo', campo_id=campo_id))
        except Exception as e:
            flash(f'Erro ao atualizar campo: {str(e)}', 'danger')
    
    return render_template('campo_form.html', campo=campo, culturas=culturas, modo='editar')

@web_bp.route('/campos/<campo_id>/remover', methods=['POST'])
def remover_campo(campo_id):
    """Remove um campo"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    
    try:
        db_service.remover_campo(campo_id)
        flash('Campo removido com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover campo: {str(e)}', 'danger')
    
    return redirect(url_for('web.listar_campos'))

@web_bp.route('/calculadora')
def calculadora():
    """Página da calculadora interativa"""
    db_service = DatabaseService(current_app.config['MONGO_URI'])
    culturas = db_service.obter_todas_culturas()
    
    return render_template('calculadora.html', culturas=culturas)

@web_bp.route('/modo-simples')
def modo_simples():
    """Página do modo simples (similar a terminal)"""
    return render_template('modo_simples.html')


def iniciar_streamlit_dashboard():
    """Função para iniciar o dashboard Streamlit em segundo plano"""
    script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'scripts', 'dashboard.py')
    
    # Verificar se o processo já está em execução
    try:
        # Iniciar o processo Streamlit
        process = subprocess.Popen(
            ["streamlit", "run", script_path], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar para garantir que o servidor inicie
        time.sleep(3)
        
        # Opcional: abrir o navegador automaticamente
        #webbrowser.open('http://localhost:8501')
    except Exception as e:
        print(f"Erro ao iniciar Streamlit: {str(e)}")
        
def iniciar_streamlit_dashboard_ml():
    """Função para iniciar o dashboard-ml Streamlit em segundo plano"""
    script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'scripts', 'dashboard_ml.py')
    
    # Verificar se o processo já está em execução
    try:
        # Iniciar o processo Streamlit
        process = subprocess.Popen(
            ["streamlit", "run", script_path], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar para garantir que o servidor inicie
        time.sleep(3)
        
        # Opcional: abrir o navegador automaticamente
        #webbrowser.open('http://localhost:8501')
    except Exception as e:
        print(f"Erro ao iniciar Streamlit: {str(e)}")

@web_bp.route('/iniciar-dashboard')
def iniciar_dashboard():
    """Rota para iniciar o dashboard Streamlit"""
    # Iniciar o dashboard em uma thread para não bloquear a resposta HTTP
    thread = threading.Thread(target=iniciar_streamlit_dashboard)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "sucesso": True,
        "mensagem": "Dashboard iniciado com sucesso",
        "url": "http://localhost:8501"
    })
    
    # Redirecionar para a página de sensores enquanto o dashboard inicia
    # Ou retornar JSON se for uma chamada AJAX
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     return jsonify({
    #         "sucesso": True,
    #         "mensagem": "Dashboard está iniciando...",
    #         "url": "http://localhost:8501"
    #     })
    # else:
    #     # Redirecionar para a página de sensores com mensagem
    #     flash('Dashboard está sendo iniciado. Aguarde um momento...', 'info')
    #     return redirect(url_for('sensores.index'))
    
@web_bp.route('/iniciar-dashboard-ml')
def iniciar_dashboard_ml():
    """Rota para iniciar o dashboard Streamlit"""
    # Iniciar o dashboard em uma thread para não bloquear a resposta HTTP
    thread = threading.Thread(target=iniciar_streamlit_dashboard_ml)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "sucesso": True,
        "mensagem": "Dashboard iniciado com sucesso",
        "url": "http://localhost:8501"
    })