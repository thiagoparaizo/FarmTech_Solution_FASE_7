# app/routes/sensor_routes.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app.services.sql_db_service import SQLDatabaseService
from app.services.db_service import DatabaseService
from datetime import datetime, timedelta
sensor_bp = Blueprint('sensores', __name__)

# Obter instâncias de serviço
def get_sql_db():
    return SQLDatabaseService(current_app.config['SQL_DATABASE_URI'])

def get_mongo_db():
    return DatabaseService(current_app.config['MONGO_URI'])

# Rotas web para sensores
@sensor_bp.route('/')
def index():
    """Página principal de sensores"""
    sql_db = get_sql_db()
    mongo_db = get_mongo_db()
    
    # Obter todos os sensores ativos
    sensores = []
    session = sql_db.get_session()
    try:
        from app.models.sensor_models import Sensor
        from sqlalchemy.orm import joinedload
        #sensores = session.query(Sensor).filter_by(ativo=True).all()
        sensores = session.query(Sensor).options(joinedload(Sensor.posicao)).filter_by(ativo=True).all()
    finally:
        session.close()
    
    # Obter todos os campos para referenciar
    campos = mongo_db.obter_todos_campos()
    
    return render_template('sensores/index.html', 
                          sensores=sensores, 
                          campos=campos, 
                          total_sensores=len(sensores))

@sensor_bp.route('/sensor/<int:sensor_id>')
def detalhe_sensor(sensor_id):
    """Página de detalhes de um sensor"""
    sql_db = get_sql_db()
    
    # Obter sensor e sua posição
    sensor = sql_db.obter_sensor(sensor_id)
    if not sensor:
        flash('Sensor não encontrado', 'danger')
        return redirect(url_for('sensores.index'))
    
    # Obter as últimas leituras
    leituras = sql_db.obter_leituras_por_sensor(sensor_id, limite=50)
    
    # Calcular estatísticas dos últimos 7 dias
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=7)
    estatisticas = sql_db.calcular_estatisticas_leituras(sensor_id, data_inicio, data_fim)
    
    # Obter alertas ativos
    session = sql_db.get_session()
    alertas = []
    try:
        from app.models.sensor_models import AlertaSensor
        alertas = session.query(AlertaSensor).filter_by(
            sensor_id=sensor_id, 
            resolvido=False
        ).order_by(AlertaSensor.data_hora.desc()).all()
    finally:
        session.close()
    
    # Se for um sensor instalado em um campo, obter informações do campo
    campo = None
    if hasattr(sensor, 'posicao') and sensor.posicao and sensor.posicao.campo_id:
        mongo_db = get_mongo_db()
        campo = mongo_db.obter_campo_por_id(sensor.posicao.campo_id)
    
    return render_template('sensores/detalhe_sensor.html', 
                          sensor=sensor, 
                          leituras=leituras, 
                          estatisticas=estatisticas,
                          alertas=alertas,
                          campo=campo)

@sensor_bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_sensor():
    """Adicionar um novo sensor"""
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        modelo = request.form.get('modelo')
        campo_id = request.form.get('campo_id')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        profundidade = request.form.get('profundidade')
        
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
            profundidade = float(profundidade) if profundidade else None
            
            sql_db = get_sql_db()
            
            # Adicionar sensor
            sensor_id = sql_db.adicionar_sensor(tipo, modelo)
            
            # Se tiver campo_id, adicionar posição
            if campo_id:
                sql_db.adicionar_posicao_sensor(
                    sensor_id, 
                    campo_id, 
                    latitude, 
                    longitude, 
                    profundidade
                )
            
            flash('Sensor adicionado com sucesso!', 'success')
            return redirect(url_for('sensores.detalhe_sensor', sensor_id=sensor_id))
        except Exception as e:
            flash(f'Erro ao adicionar sensor: {str(e)}', 'danger')
    
    # GET: mostrar formulário
    mongo_db = get_mongo_db()
    campos = mongo_db.obter_todos_campos()
    
    return render_template('sensores/sensor_form.html', campos=campos)

@sensor_bp.route('/campo/<campo_id>')
def sensores_por_campo(campo_id):
    """Lista de sensores em um campo específico"""
    sql_db = get_sql_db()
    mongo_db = get_mongo_db()
    
    # Obter campo
    campo = mongo_db.obter_campo_por_id(campo_id)
    if not campo:
        flash('Campo não encontrado', 'danger')
        return redirect(url_for('sensores.index'))
    
    # Obter sensores do campo
    sensores = sql_db.obter_sensores_por_campo(campo_id)
    
    return render_template('sensores/sensores_campo.html', 
                          sensores=sensores, 
                          campo=campo)

@sensor_bp.route('/registrar-leitura', methods=['POST'])
def registrar_leitura():
    """Registra uma nova leitura de sensor (via formulário ou API)"""
    if request.content_type == 'application/json':
        data = request.json
    else:
        data = request.form
    
    sensor_id = data.get('sensor_id')
    valor = data.get('valor')
    unidade = data.get('unidade')
    
    if not all([sensor_id, valor, unidade]):
        if request.content_type == 'application/json':
            return jsonify({"erro": "Dados incompletos"}), 400
        else:
            flash('Dados incompletos', 'danger')
            return redirect(url_for('sensores.index'))
    
    try:
        sql_db = get_sql_db()
        sql_db.adicionar_leitura(
            int(sensor_id), 
            float(valor), 
            unidade
        )
        
        if request.content_type == 'application/json':
            return jsonify({"mensagem": "Leitura registrada com sucesso"}), 201
        else:
            flash('Leitura registrada com sucesso!', 'success')
            return redirect(url_for('sensores.detalhe_sensor', sensor_id=sensor_id))
    except Exception as e:
        if request.content_type == 'application/json':
            return jsonify({"erro": str(e)}), 500
        else:
            flash(f'Erro ao registrar leitura: {str(e)}', 'danger')
            return redirect(url_for('sensores.detalhe_sensor', sensor_id=sensor_id))

# API para recomendações
@sensor_bp.route('/api/analisar-campo/<campo_id>', methods=['GET'])
def analisar_campo(campo_id):
    """Analisa os dados dos sensores de um campo e gera recomendações"""
    sql_db = get_sql_db()
    mongo_db = get_mongo_db()
    
    # Verificar se o campo existe
    campo = mongo_db.obter_campo_por_id(campo_id)
    if not campo:
        return jsonify({"erro": "Campo não encontrado"}), 404
    
    # Obter todos os sensores do campo
    sensores = sql_db.obter_sensores_por_campo(campo_id)
    if not sensores:
        return jsonify({"erro": "Nenhum sensor encontrado no campo"}), 404
    
    # Analisar dados de cada tipo de sensor
    resultado = {"campo_id": campo_id, "recomendacoes": []}
    
    # 1. Sensor de umidade (S1)
    sensores_umidade = [s for s in sensores if s.tipo == 'S1']
    if sensores_umidade:
        for sensor in sensores_umidade:
            # Obter últimas leituras
            leituras = sql_db.obter_leituras_por_sensor(sensor.id, limite=10)
            if leituras:
                # Calcular média das últimas leituras
                media_umidade = sum(l.valor for l in leituras) / len(leituras)
                
                # Verificar se precisa de irrigação
                if media_umidade < 30:  # Valor exemplo, ajustar conforme necessidade
                    # Calcular quantidade de água recomendada
                    area_hectare = campo.get('campo', {}).get('area_total_hectare', 0)
                    agua_recomendada = (30 - media_umidade) * area_hectare * 1000  # Litros
                    
                    recomendacao_id = sql_db.adicionar_recomendacao(
                        campo_id,
                        "água",
                        agua_recomendada,
                        "L",
                        f"Média de umidade: {media_umidade}% - Abaixo do ideal (30%)"
                    )
                    
                    resultado["recomendacoes"].append({
                        "id": recomendacao_id,
                        "tipo": "irrigação",
                        "quantidade": agua_recomendada,
                        "unidade": "L",
                        "motivo": f"Umidade média de {media_umidade:.1f}% está abaixo do ideal"
                    })
    
   # 2. Sensor de pH (S2)
    sensores_ph = [s for s in sensores if s.tipo == 'S2']
    if sensores_ph:
        for sensor in sensores_ph:
            # Obter últimas leituras
            leituras = sql_db.obter_leituras_por_sensor(sensor.id, limite=10)
            if leituras:
                # Calcular média das últimas leituras
                media_ph = sum(l.valor for l in leituras) / len(leituras)
                
                # Obter os valores ideais de pH da cultura plantada
                cultura_nome = campo.get('campo', {}).get('cultura_plantada', '')
                cultura = mongo_db.obter_cultura_por_nome(cultura_nome) if cultura_nome else None
                
                if cultura:
                    ph_min = cultura.get('clima_solo', {}).get('ph_ideal', {}).get('minimo', 0)
                    ph_max = cultura.get('clima_solo', {}).get('ph_ideal', {}).get('maximo', 0)
                    
                    # Verificar se o pH está fora do ideal
                    if media_ph < ph_min:
                        # Recomendar calagem (aumentar pH)
                        area_hectare = campo.get('campo', {}).get('area_total_hectare', 0)
                        calagem_recomendada = (ph_min - media_ph) * area_hectare * 500  # kg de calcário por hectare
                        
                        recomendacao_id = sql_db.adicionar_recomendacao(
                            campo_id,
                            "calcário",
                            calagem_recomendada,
                            "kg",
                            f"pH médio: {media_ph} - Abaixo do ideal ({ph_min}-{ph_max})"
                        )
                        
                        resultado["recomendacoes"].append({
                            "id": recomendacao_id,
                            "tipo": "calagem",
                            "quantidade": calagem_recomendada,
                            "unidade": "kg",
                            "motivo": f"pH médio de {media_ph:.1f} está abaixo do ideal ({ph_min:.1f}-{ph_max:.1f})"
                        })
                    elif media_ph > ph_max:
                        # Recomendar aplicação de enxofre (diminuir pH)
                        area_hectare = campo.get('campo', {}).get('area_total_hectare', 0)
                        enxofre_recomendado = (media_ph - ph_max) * area_hectare * 300  # kg de enxofre por hectare
                        
                        recomendacao_id = sql_db.adicionar_recomendacao(
                            campo_id,
                            "enxofre",
                            enxofre_recomendado,
                            "kg",
                            f"pH médio: {media_ph} - Acima do ideal ({ph_min}-{ph_max})"
                        )
                        
                        resultado["recomendacoes"].append({
                            "id": recomendacao_id,
                            "tipo": "aplicação de enxofre",
                            "quantidade": enxofre_recomendado,
                            "unidade": "kg",
                            "motivo": f"pH médio de {media_ph:.1f} está acima do ideal ({ph_min:.1f}-{ph_max:.1f})"
                        })
    
    # 3. Sensor de nutrientes (S3)
    sensores_nutrientes = [s for s in sensores if s.tipo == 'S3']
    if sensores_nutrientes:
        for sensor in sensores_nutrientes:
            # Obter últimas leituras - assumindo que são enviadas como JSON
            # Exemplo: {"P": 12.5, "K": 8.3}
            leituras = sql_db.obter_leituras_por_sensor(sensor.id, limite=10)
            if leituras:
                # Extrair os valores de P e K das leituras
                valores_p = []
                valores_k = []
                
                for leitura in leituras:
                    try:
                        import json
                        # Verificar se o valor é um JSON válido
                        nutrientes = json.loads(leitura.valor) if isinstance(leitura.valor, str) else leitura.valor
                        if isinstance(nutrientes, dict):
                            if 'P' in nutrientes:
                                valores_p.append(float(nutrientes['P']))
                            if 'K' in nutrientes:
                                valores_k.append(float(nutrientes['K']))
                    except (json.JSONDecodeError, ValueError):
                        # Se não for JSON, tentar interpretar como valor único
                        if leitura.unidade == 'P_ppm':
                            valores_p.append(leitura.valor)
                        elif leitura.unidade == 'K_ppm':
                            valores_k.append(leitura.valor)
                
                # Calcular médias (se houver valores)
                media_p = sum(valores_p) / len(valores_p) if valores_p else 0
                media_k = sum(valores_k) / len(valores_k) if valores_k else 0
                
                # Obter níveis ideais da cultura plantada
                cultura_nome = campo.get('campo', {}).get('cultura_plantada', '')
                cultura = mongo_db.obter_cultura_por_nome(cultura_nome) if cultura_nome else None
                
                if cultura:
                    # Obter valores de referência de P e K da cultura
                    p_ideal = cultura.get('fertilizantes_insumos', {}).get('adubacao_NPK_por_hectare_kg', {}).get('P2O5', 0)
                    k_ideal = cultura.get('fertilizantes_insumos', {}).get('adubacao_NPK_por_hectare_kg', {}).get('K2O', 0)
                    
                    # Converter de ppm para kg/ha (aproximação simplificada)
                    p_atual_kg_ha = media_p * 2.29 / 10  # Conversão aproximada de ppm P para kg/ha P2O5
                    k_atual_kg_ha = media_k * 1.2 / 10   # Conversão aproximada de ppm K para kg/ha K2O
                    
                    area_hectare = campo.get('campo', {}).get('area_total_hectare', 0)
                    
                    # Verificar deficiência de P
                    if p_atual_kg_ha < p_ideal * 0.7:  # 70% do ideal
                        p_deficit = (p_ideal * 0.7 - p_atual_kg_ha) * area_hectare
                        
                        recomendacao_id = sql_db.adicionar_recomendacao(
                            campo_id,
                            "fertilizante P2O5",
                            p_deficit,
                            "kg",
                            f"Nível de P: {media_p} ppm - Abaixo do ideal"
                        )
                        
                        resultado["recomendacoes"].append({
                            "id": recomendacao_id,
                            "tipo": "fertilização com fósforo",
                            "quantidade": p_deficit,
                            "unidade": "kg",
                            "motivo": f"Nível de fósforo está abaixo do ideal"
                        })
                    
                    # Verificar deficiência de K
                    if k_atual_kg_ha < k_ideal * 0.7:  # 70% do ideal
                        k_deficit = (k_ideal * 0.7 - k_atual_kg_ha) * area_hectare
                        
                        recomendacao_id = sql_db.adicionar_recomendacao(
                            campo_id,
                            "fertilizante K2O",
                            k_deficit,
                            "kg",
                            f"Nível de K: {media_k} ppm - Abaixo do ideal"
                        )
                        
                        resultado["recomendacoes"].append({
                            "id": recomendacao_id,
                            "tipo": "fertilização com potássio",
                            "quantidade": k_deficit,
                            "unidade": "kg",
                            "motivo": f"Nível de potássio está abaixo do ideal"
                        })
    
    return jsonify(resultado)

@sensor_bp.route('/api/aplicar-recomendacao/<int:recomendacao_id>', methods=['POST'])
def aplicar_recomendacao(recomendacao_id):
    """Registra a aplicação de uma recomendação"""
    sql_db = get_sql_db()
    
    # Obter a recomendação
    session = sql_db.get_session()
    recomendacao = None
    try:
        from app.models.sensor_models import RecomendacaoAutomatica
        recomendacao = session.query(RecomendacaoAutomatica).filter_by(id=recomendacao_id).first()
    finally:
        session.close()
    
    if not recomendacao:
        return jsonify({"erro": "Recomendação não encontrada"}), 404
    
    # Registrar a aplicação
    metodo_aplicacao = request.json.get('metodo_aplicacao', '') if request.is_json else request.form.get('metodo_aplicacao', '')
    
    try:
        # Registrar a aplicação do recurso
        aplicacao_id = sql_db.adicionar_aplicacao_recurso(
            recomendacao.campo_id,
            recomendacao.tipo_recurso,
            recomendacao.quantidade_recomendada,
            recomendacao.unidade,
            metodo_aplicacao
        )
        
        # Marcar a recomendação como aplicada
        sql_db.marcar_recomendacao_aplicada(recomendacao_id)
        
        return jsonify({
            "mensagem": "Recomendação aplicada com sucesso",
            "aplicacao_id": aplicacao_id
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@sensor_bp.route('/relatorios')
def relatorios():
    """Página de relatórios de sensores"""
    return render_template('sensores/relatorios.html')

@sensor_bp.route('/api/relatorio/sensor/<int:sensor_id>', methods=['GET'])
def relatorio_sensor(sensor_id):
    """Gera um relatório para um sensor específico"""
    sql_db = get_sql_db()
    
    # Obter sensor
    sensor = sql_db.obter_sensor(sensor_id)
    if not sensor:
        return jsonify({"erro": "Sensor não encontrado"}), 404
    
    # Parâmetros de período
    dias = request.args.get('dias', '30')
    try:
        dias = int(dias)
    except ValueError:
        dias = 30
    
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=dias)
    
    # Obter leituras do período
    leituras = sql_db.obter_leituras_por_sensor(sensor_id, data_inicio, data_fim)
    
    # Calcular estatísticas
    estatisticas = sql_db.calcular_estatisticas_leituras(sensor_id, data_inicio, data_fim)
    
    # Gerar histórico (se ainda não existir)
    sql_db.gerar_historico(sensor_id, data_inicio, data_fim)
    
    # Formatar dados para o relatório
    dados_leituras = []
    for leitura in leituras:
        dados_leituras.append({
            "id": leitura.id,
            "data_hora": leitura.data_hora.isoformat(),
            "valor": leitura.valor,
            "unidade": leitura.unidade
        })
    
    return jsonify({
        "sensor": {
            "id": sensor.id,
            "tipo": sensor.tipo,
            "modelo": sensor.modelo
        },
        "periodo": {
            "inicio": data_inicio.isoformat(),
            "fim": data_fim.isoformat(),
            "dias": dias
        },
        "estatisticas": estatisticas,
        "leituras": dados_leituras
    })

@sensor_bp.route('/api/relatorio/campo/<campo_id>', methods=['GET'])
def relatorio_campo(campo_id):
    """Gera um relatório para um campo específico"""
    sql_db = get_sql_db()
    mongo_db = get_mongo_db()
    
    # Obter campo
    campo = mongo_db.obter_campo_por_id(campo_id)
    if not campo:
        return jsonify({"erro": "Campo não encontrado"}), 404
    
    # Parâmetros de período
    dias = request.args.get('dias', '30')
    try:
        dias = int(dias)
    except ValueError:
        dias = 30
    
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=dias)
    
    # Obter sensores do campo
    sensores = sql_db.obter_sensores_por_campo(campo_id)
    
    # Obter aplicações de recursos no período
    aplicacoes = sql_db.obter_aplicacoes_recurso(campo_id, inicio=data_inicio, fim=data_fim)
    
    # Formatar dados para o relatório
    dados_sensores = []
    for sensor in sensores:
        estatisticas = sql_db.calcular_estatisticas_leituras(sensor.id, data_inicio, data_fim)
        dados_sensores.append({
            "id": sensor.id,
            "tipo": sensor.tipo,
            "estatisticas": estatisticas
        })
    
    dados_aplicacoes = []
    for aplicacao in aplicacoes:
        dados_aplicacoes.append({
            "id": aplicacao.id,
            "data_hora": aplicacao.data_hora.isoformat(),
            "tipo_recurso": aplicacao.tipo_recurso,
            "quantidade": aplicacao.quantidade,
            "unidade": aplicacao.unidade
        })
    
    return jsonify({
        "campo": {
            "id": campo_id,
            "nome_produtor": campo.get('nome_produtor', ''),
            "cultura_plantada": campo.get('campo', {}).get('cultura_plantada', ''),
            "area_hectare": campo.get('campo', {}).get('area_total_hectare', 0)
        },
        "periodo": {
            "inicio": data_inicio.isoformat(),
            "fim": data_fim.isoformat(),
            "dias": dias
        },
        "sensores": dados_sensores,
        "aplicacoes": dados_aplicacoes
    })

# API para simulação de sensores (para testes/desenvolvimento)
@sensor_bp.route('/api/simular-leituras', methods=['POST'])
def simular_leituras():
    """Endpoint para simular leituras de sensores (para desenvolvimento)"""
    if not current_app.config['DEBUG']:
        return jsonify({"erro": "Simulação disponível apenas em ambiente de desenvolvimento"}), 403
    
    sql_db = get_sql_db()
    
    # Parâmetros
    campo_id = request.json.get('campo_id')
    if not campo_id:
        return jsonify({"erro": "Campo ID é obrigatório"}), 400
    
    # Verificar se o campo existe
    mongo_db = get_mongo_db()
    campo = mongo_db.obter_campo_por_id(campo_id)
    if not campo:
        return jsonify({"erro": "Campo não encontrado"}), 404
    
    # Verificar se já existem sensores neste campo
    sensores = sql_db.obter_sensores_por_campo(campo_id)
    
    # Se não existirem sensores, criar alguns
    if not sensores:
        # Criar 3 sensores, um de cada tipo
        sensor_ids = []
        for tipo in ['S1', 'S2', 'S3']:
            sensor_id = sql_db.adicionar_sensor(tipo, f"Sensor {tipo} Simulado")
            sql_db.adicionar_posicao_sensor(sensor_id, campo_id)
            sensor_ids.append(sensor_id)
        
        # Obter os sensores novamente
        sensores = sql_db.obter_sensores_por_campo(campo_id)
    
    # Simular leituras para cada sensor
    import random
    resultados = []
    
    for sensor in sensores:
        if sensor.tipo == 'S1':  # Sensor de umidade
            # Simular umidade do solo (15% a 70%)
            valor = random.uniform(15.0, 70.0)
            unidade = '%'
            
        elif sensor.tipo == 'S2':  # Sensor de pH
            # Simular pH do solo (4.5 a 8.0)
            valor = random.uniform(4.5, 8.0)
            unidade = 'pH'
            
        elif sensor.tipo == 'S3':  # Sensor de nutrientes
            # Simular valores de P e K
            valor_p = random.uniform(5.0, 50.0)  # ppm de P
            valor_k = random.uniform(10.0, 100.0)  # ppm de K
            valor = f'{{"P": {valor_p:.1f}, "K": {valor_k:.1f}}}'
            unidade = 'ppm'
        
        # Registrar a leitura
        leitura_id = sql_db.adicionar_leitura(sensor.id, valor, unidade)
        
        resultados.append({
            "sensor_id": sensor.id,
            "tipo": sensor.tipo,
            "leitura_id": leitura_id,
            "valor": valor,
            "unidade": unidade
        })
    
    # Gerar uma recomendação aleatória
    if random.random() < 0.3:  # 30% de chance de gerar uma recomendação
        tipo_recurso = random.choice(['água', 'fertilizante N', 'fertilizante P2O5', 'fertilizante K2O', 'calcário'])
        quantidade = random.uniform(10.0, 100.0)
        unidade = 'L' if tipo_recurso == 'água' else 'kg'
        
        recomendacao_id = sql_db.adicionar_recomendacao(
            campo_id,
            tipo_recurso,
            quantidade,
            unidade,
            "Recomendação gerada por simulação"
        )
        
        resultados.append({
            "recomendacao_id": recomendacao_id,
            "tipo_recurso": tipo_recurso,
            "quantidade": quantidade,
            "unidade": unidade
        })
    
    return jsonify({
        "mensagem": "Simulação concluída com sucesso",
        "resultados": resultados
    })
    
    # Adicione essas rotas ao arquivo sensor_routes.py

@sensor_bp.route('/api/sensores', methods=['GET'])
def listar_sensores_api():
    """API para listar todos os sensores ativos"""
    sql_db = get_sql_db()
    
    try:
        from app.models.sensor_models import Sensor
        session = sql_db.get_session()
        sensores = session.query(Sensor).filter_by(ativo=True).all()
        
        sensores_json = []
        for sensor in sensores:
            sensores_json.append({
                'id': sensor.id,
                'tipo': sensor.tipo,
                'modelo': sensor.modelo
            })
        
        return jsonify(sensores_json)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()
        

@sensor_bp.route('/api/receber-dados-esp32', methods=['POST'])
def receber_dados_esp32():
    """Recebe dados do ESP32 via API"""
    try:
        # Verificar se os dados estão em formato CSV ou JSON
        if request.content_type == 'application/json':
            dados = request.json
            timestamp = dados.get('timestamp')
            fosforo = dados.get('fosforo') == 1 or dados.get('fosforo') == '1'
            potassio = dados.get('potassio') == 1 or dados.get('potassio') == '1'
            ph = float(dados.get('ph', 0))
            umidade = float(dados.get('umidade', 0))
            irrigacao = dados.get('irrigacao') == 1 or dados.get('irrigacao') == '1'
        else:
            # Formato CSV: timestamp,fosforo,potassio,ph,umidade,irrigacao
            csv_data = request.data.decode('utf-8').strip()
            partes = csv_data.split(',')
            if len(partes) != 6:
                return jsonify({"erro": "Formato CSV inválido"}), 400
                
            timestamp = int(partes[0])
            fosforo = partes[1] == '1'
            potassio = partes[2] == '1'
            ph = float(partes[3])
            umidade = float(partes[4])
            irrigacao = partes[5] == '1'

        # Obter ID do sensor associado (pode ser parametrizado)
        sensor_id = request.args.get('sensor_id')
        if not sensor_id:
            return jsonify({"erro": "ID do sensor não especificado"}), 400
            
        # Registrar leituras no banco
        sql_db = get_sql_db()

        # Registrar leitura de umidade
        sql_db.adicionar_leitura(sensor_id, umidade, '%')
        
        # Registrar leitura de pH
        sql_db.adicionar_leitura(sensor_id, ph, 'pH')
        
        # Registrar leituras de nutrientes
        dados_nutrientes = {
            'P': 1 if fosforo else 0,
            'K': 1 if potassio else 0
        }
        sql_db.adicionar_leitura(sensor_id, str(dados_nutrientes), 'ppm')
        
        # Registrar estado de irrigação
        # Isso poderia atualizar um campo na tabela Sensor ou ser salvo em uma tabela específica
        
        return jsonify({
            "mensagem": "Dados recebidos com sucesso",
            "timestamp": timestamp
        }), 201
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

# Adicionar às rotas existentes
@sensor_bp.route('/api/verificar-irrigacao-clima/<campo_id>', methods=['GET'])
def verificar_irrigacao_clima(campo_id):
    """Verifica a necessidade de irrigação com base no clima"""
    from app.services.weather_service import WeatherService
    
    # Obter cidade
    cidade = request.args.get('cidade', 'Fortaleza')
    
    # Criar instância do serviço de clima
    weather_service = WeatherService(current_app.config['OPENWEATHER_API_KEY'])
    
    # Obter serviços de banco de dados
    sql_db = get_sql_db()
    mongo_db = get_mongo_db()
    
    # Verificar necessidade de irrigação
    resultado = weather_service.verificar_necessidade_irrigacao(
        campo_id,
        cidade,
        sql_db,
        mongo_db
    )
    
    return jsonify(resultado)


@sensor_bp.route('/api/ativar-irrigacao/<campo_id>', methods=['POST'])
def ativar_irrigacao(campo_id):
    """Ativa a irrigação para um campo específico"""
    try:
        # Obter serviços
        sql_db = get_sql_db()
        mongo_db = get_mongo_db()
        
        # Verificar se o campo existe
        campo = mongo_db.obter_campo_por_id(campo_id)
        if not campo:
            return jsonify({"erro": "Campo não encontrado"}), 404
        
        # Registrar aplicação de recurso (água)
        # Calcular quantidade baseada na área
        area_hectare = campo.get('campo', {}).get('area_total_hectare', 0)
        volume_agua = area_hectare * 10000  # 10.000 litros por hectare (exemplo)
        
        # Registrar aplicação
        aplicacao_id = sql_db.adicionar_aplicacao_recurso(
            campo_id=campo_id,
            tipo_recurso="água",
            quantidade=volume_agua,
            unidade="L",
            metodo_aplicacao="Sistema de Irrigação"
        )
        
        return jsonify({
            "mensagem": f"Irrigação ativada com {volume_agua:.0f} litros de água",
            "aplicacao_id": aplicacao_id
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
import csv
import tempfile
from werkzeug.utils import secure_filename
from flask import request, flash, redirect

# Adicionar estas rotas ao arquivo sensor_routes.py

@sensor_bp.route('/upload-csv')
def upload_csv_form():
    """Página para upload de arquivo CSV"""
    # Obter lista de sensores para associar os dados
    sql_db = get_sql_db()
    session = sql_db.get_session()
    try:
        from app.models.sensor_models import Sensor
        sensores = session.query(Sensor).filter_by(ativo=True).all()
    finally:
        session.close()
    
    # Obter lista de campos para associar sensores
    mongo_db = get_mongo_db()
    campos = mongo_db.obter_todos_campos()
    
    return render_template('sensores/upload_csv.html', sensores=sensores, campos=campos)

@sensor_bp.route('/processar-upload-csv', methods=['POST'])
def processar_upload_csv():
    """Processa o upload do arquivo CSV e importa os dados"""
    temp_file_path = None
    try:
        # Verificar se foi enviado um arquivo
        if 'arquivo_csv' not in request.files:
            flash('Nenhum arquivo foi selecionado', 'danger')
            return redirect(url_for('sensores.upload_csv_form'))
        
        arquivo = request.files['arquivo_csv']
        if arquivo.filename == '':
            flash('Nenhum arquivo foi selecionado', 'danger')
            return redirect(url_for('sensores.upload_csv_form'))
        
        # Verificar se é um arquivo CSV
        if not arquivo.filename.lower().endswith('.csv'):
            flash('Por favor, selecione um arquivo CSV válido', 'danger')
            return redirect(url_for('sensores.upload_csv_form'))
        
        # Obter parâmetros do formulário
        sensor_id = request.form.get('sensor_id')
        campo_id = request.form.get('campo_id')
        separador = request.form.get('separador', ';')
        criar_sensor_automatico = request.form.get('criar_sensor_automatico') == 'on'
        
        if not sensor_id and not criar_sensor_automatico:
            flash('Selecione um sensor existente ou marque a opção para criar automaticamente', 'danger')
            return redirect(url_for('sensores.upload_csv_form'))
        
        # Salvar arquivo temporariamente com correção
        filename = secure_filename(arquivo.filename)
        
        # Criar arquivo temporário sem deletar automaticamente
        import tempfile
        temp_fd, temp_file_path = tempfile.mkstemp(suffix='.csv', text=True)
        
        # Fechar o file descriptor antes de usar o arquivo
        os.close(temp_fd)
        
        # Salvar o conteúdo do arquivo
        arquivo.save(temp_file_path)
        
        # Processar o arquivo CSV
        sql_db = get_sql_db()
        mongo_db = get_mongo_db()
        
        resultado = processar_arquivo_csv(
            temp_file_path, 
            sensor_id, 
            campo_id,
            separador,
            criar_sensor_automatico,
            sql_db, 
            mongo_db
        )
        
        if resultado['sucesso']:
            periodo_info = resultado.get('periodo_simulado', {})
            mensagem_principal = f'Arquivo processado com sucesso! {resultado["registros_importados"]} registros importados.'
            
            if periodo_info:
                mensagem_periodo = f' Período simulado: {periodo_info["inicio"]} até {periodo_info["fim"]} (intervalos de {periodo_info["intervalo"]}).'
                flash(mensagem_principal + mensagem_periodo, 'success')
            else:
                flash(mensagem_principal, 'success')
            
            if resultado.get('registros_erro', 0) > 0:
                flash(f'Atenção: {resultado["registros_erro"]} registros tiveram erro e foram ignorados.', 'warning')
            if resultado.get('sensor_criado'):
                flash(f'Sensor criado automaticamente com ID: {resultado["sensor_id"]}', 'info')
        else:
            flash(f'Erro ao processar arquivo: {resultado["erro"]}', 'danger')
        
        return redirect(url_for('sensores.upload_csv_form'))
        
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'danger')
        return redirect(url_for('sensores.upload_csv_form'))
    finally:
        # Remover arquivo temporário de forma segura
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Aviso: Não foi possível remover arquivo temporário: {e}")

def processar_arquivo_csv(caminho_arquivo, sensor_id, campo_id, separador, criar_sensor_automatico, sql_db, mongo_db):
    """Função para processar o arquivo CSV e importar os dados"""
    try:
        # Ler o arquivo CSV
        dados = []
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            # Detectar se tem cabeçalho
            primeira_linha = arquivo.readline().strip()
            arquivo.seek(0)
            
            # Se a primeira linha contém "timestamp" é um cabeçalho
            tem_cabecalho = 'timestamp' in primeira_linha.lower()
            
            if separador == 'auto':
                # Detectar separador automaticamente
                if ';' in primeira_linha:
                    separador = ';'
                elif ',' in primeira_linha:
                    separador = ','
                else:
                    separador = ';'  # padrão
            
            leitor = csv.reader(arquivo, delimiter=separador)
            
            if tem_cabecalho:
                next(leitor)  # Pular cabeçalho
            
            for linha in leitor:
                if len(linha) >= 6:  # Garantir que tem todas as colunas
                    dados.append(linha)
        
        if not dados:
            return {'sucesso': False, 'erro': 'Arquivo CSV vazio ou formato inválido'}
        
        # Verificar/criar sensor
        sensor_criado = False
        if not sensor_id or sensor_id == '':
            if criar_sensor_automatico:
                # Criar sensor automaticamente
                tipo_sensor = 'S1'  # Padrão para multi-sensor
                modelo_sensor = 'Multi-Sensor ESP32'
                sensor_id = sql_db.adicionar_sensor(tipo_sensor, modelo_sensor)
                
                # Se temos um campo, associar o sensor ao campo
                if campo_id:
                    sql_db.adicionar_posicao_sensor(sensor_id, campo_id)
                
                sensor_criado = True
            else:
                return {'sucesso': False, 'erro': 'Sensor não especificado'}
        else:
            sensor_id = int(sensor_id)
            # Verificar se o sensor existe
            sensor = sql_db.obter_sensor(sensor_id)
            if not sensor:
                return {'sucesso': False, 'erro': f'Sensor com ID {sensor_id} não encontrado'}
        
        # Importar dados com timestamps simulados
        registros_importados = 0
        registros_erro = 0
        
        # Calcular timestamps simulados
        # Começar da data/hora atual e retroceder 5 minutos por registro
        data_fim = datetime.now()
        total_registros = len(dados)
        
        print(f"Gerando timestamps simulados para {total_registros} registros")
        print(f"Data final (mais recente): {data_fim}")
        
        # Calcular a data de início (total_registros * 5 minutos antes da data atual)
        minutos_total = total_registros * 5
        data_inicio = data_fim - timedelta(minutes=minutos_total)
        print(f"Data inicial (mais antiga): {data_inicio}")
        
        for i, linha in enumerate(dados):
            try:
                if len(linha) < 6:
                    registros_erro += 1
                    continue
                
                # Parsing dos dados: timestamp;fosforo;potassio;ph;umidade;irrigacao
                timestamp_original = linha[0]  # Manter para debug, mas não usar
                fosforo = linha[1] == '1'
                potassio = linha[2] == '1'
                ph = float(linha[3])
                umidade = float(linha[4])
                irrigacao = linha[5] == '1'
                
                # Gerar timestamp simulado
                # Começar da data mais antiga e adicionar 5 minutos por cada registro
                data_hora_simulada = data_inicio + timedelta(minutes=i * 5)
                
                # Debug para os primeiros registros
                if i < 3:
                    print(f"Registro {i}: timestamp original={timestamp_original}, simulado={data_hora_simulada}")
                
                # Adicionar leitura de umidade
                sql_db.adicionar_leitura(
                    sensor_id=sensor_id,
                    valor=umidade,
                    unidade='%',
                    data_hora=data_hora_simulada
                )
                
                # Adicionar leitura de pH
                sql_db.adicionar_leitura(
                    sensor_id=sensor_id,
                    valor=ph,
                    unidade='pH',
                    data_hora=data_hora_simulada
                )
                
                # Adicionar leituras separadas para P e K (apenas se presentes)
                if fosforo:
                    sql_db.adicionar_leitura(
                        sensor_id=sensor_id,
                        valor=1,
                        unidade='P_ppm',
                        data_hora=data_hora_simulada
                    )
                
                if potassio:
                    sql_db.adicionar_leitura(
                        sensor_id=sensor_id,
                        valor=1,
                        unidade='K_ppm',
                        data_hora=data_hora_simulada
                    )
                
                # Registrar estado de irrigação se necessário
                if irrigacao and campo_id:
                    try:
                        # Calcular quantidade de água baseada na área do campo
                        mongo_db = get_mongo_db()
                        campo = mongo_db.obter_campo_por_id(campo_id)
                        area_hectare = campo.get('campo', {}).get('area_total_hectare', 1) if campo else 1
                        quantidade_agua = area_hectare * 150  # 150L por hectare
                        
                        sql_db.adicionar_aplicacao_recurso(
                            campo_id=campo_id,
                            tipo_recurso="água",
                            quantidade=quantidade_agua,
                            unidade="L",
                            metodo_aplicacao="Sistema ESP32 Simulado",
                            data_hora=data_hora_simulada
                        )
                    except Exception as e:
                        print(f"Erro ao registrar irrigação: {e}")
                        # Não falhar por causa da irrigação
                
                registros_importados += 1
                
            except Exception as e:
                print(f"Erro ao processar linha {linha}: {str(e)}")
                registros_erro += 1
                continue
        
        print(f"Importação concluída: {registros_importados} registros importados")
        
        resultado = {
            'sucesso': True,
            'registros_importados': registros_importados,
            'registros_erro': registros_erro,
            'sensor_id': sensor_id,
            'periodo_simulado': {
                'inicio': data_inicio.strftime('%d/%m/%Y %H:%M'),
                'fim': data_fim.strftime('%d/%m/%Y %H:%M'),
                'intervalo': '5 minutos'
            }
        }
        
        if sensor_criado:
            resultado['sensor_criado'] = True
        
        return resultado
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


# @sensor_bp.route('/notebook-results')
# def notebook_results():
#     """Converte e exibe o notebook PBL como HTML"""
#     try:
#         # Caminho para o notebook
#         notebook_path = os.path.join(current_app.root_path, '..', 'fase6', 'pbl.ipynb')
        
#         if not os.path.exists(notebook_path):
#             return f"Notebook não encontrado em: {notebook_path}", 404
            
#         # Ler o notebook
#         with open(notebook_path, 'r', encoding='utf-8') as f:
#             notebook_content = nbformat.read(f, as_version=4)
            
#         # Configurar o exportador HTML
#         html_exporter = HTMLExporter()
#         html_exporter.template_name = 'classic' # ou 'lab'
        
#         # Converter para HTML
#         (body, resources) = html_exporter.from_notebook_node(notebook_content)
        
#         return body
#     except Exception as e:
#         return f"Erro ao processar o notebook: {str(e)}", 500

@sensor_bp.route('/analise-notebook')
def analise_notebook():
    """Página de análise com Jupyter Notebook"""
    return render_template('sensores/analise_notebook.html')