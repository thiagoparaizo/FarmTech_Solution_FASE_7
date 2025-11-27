#import pymysql
#pymysql.install_as_MySQLdb()
from flask import Flask, render_template
from pymongo import MongoClient
from app.services.db_service import DatabaseService
from app.services.oracle_db_service import OracleDatabaseService
from app.services.sql_db_service import SQLDatabaseService
from app.routes.web_routes import web_bp
from app.routes.api_routes import api_bp
from app.routes.ml_routes import ml_bp
from app.routes.catalogo_routes import catalogo_bp
from app.routes.sensor_routes import sensor_bp  # Nova rota para sensores
from app.utils.filters import configure_template_filters
from app.services.init_db import inicializar_banco_dados, inicializar_banco_dados_relacional
import os

db_service = None
sql_db_service = None
oracle_db_service = None

def create_app(config_object='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Iniciar conexão com MongoDB
    global db_service
    db_service = DatabaseService(app.config['MONGO_URI'])
    
    # Iniciar conexão com banco relacional
    global sql_db_service
    sql_db_service = SQLDatabaseService(app.config['SQL_DATABASE_URI'])
    
    # Iniciar conexão com Oracle
    global oracle_db_service
    oracle_db_service = OracleDatabaseService(app.config['ORACLE_DATABASE_URI'])
    
    # Inicializar banco de dados com dados de exemplo (se necessário)
    with app.app_context():
        # Inicializar MongoDB
        inicializar_banco_dados(app.config['MONGO_URI'])
        
        # Inicializar banco de dados relacional
        inicializar_banco_dados_relacional(app.config['SQL_DATABASE_URI'])
        
        try:
            # Oracle - dados de exemplo # TODO comentar caso não tenha o Oracle configurado
            oracle_db_service.inicializar_dados_exemplo()
        except Exception as e:
            print(f"Erro ao inicializar banco de dados Oracle: {e}")
            app.flash(f"Erro ao inicializar banco de dados Oracle: {e}", "danger")
            pass
    
    # Registrar blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(sensor_bp, url_prefix='/sensores')
    app.register_blueprint(catalogo_bp, url_prefix='/catalogo')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    
    
    
    # Configurar filtros de template
    configure_template_filters(app)
    
    # Adicionar variáveis globais ao contexto do template
    @app.context_processor
    def inject_debug():
        return dict(is_debug=app.config['DEBUG'])
    
    # Configurar tratamento de erros
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    @app.template_filter('number_format')
    def number_format_filter(number):
        """Formata um número com separadores de milhar."""
        return format(int(number), ',').replace(',', '.')
    
    return app