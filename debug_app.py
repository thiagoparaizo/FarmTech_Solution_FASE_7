# debug_app.py

"""
Script para debuggar o registro do blueprint ML
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_blueprint_import():
    """Testa import individual dos blueprints"""
    print("🔍 Testando imports individuais...")
    
    try:
        from app.routes.web_routes import web_bp
        print("✅ web_bp importado")
    except Exception as e:
        print(f"❌ web_bp erro: {e}")
    
    try:
        from app.routes.api_routes import api_bp
        print("✅ api_bp importado")
    except Exception as e:
        print(f"❌ api_bp erro: {e}")
    
    try:
        from app.routes.sensor_routes import sensor_bp
        print("✅ sensor_bp importado")
    except Exception as e:
        print(f"❌ sensor_bp erro: {e}")
    
    try:
        from app.routes.catalogo_routes import catalogo_bp
        print("✅ catalogo_bp importado")
    except Exception as e:
        print(f"❌ catalogo_bp erro: {e}")
    
    try:
        from app.routes.ml_routes import ml_bp
        print("✅ ml_bp importado")
        print(f"   Blueprint name: {ml_bp.name}")
        print(f"   URL prefix: {ml_bp.url_prefix}")
        
        # Testar rotas do blueprint
        print("   Rotas registradas no blueprint:")
        for rule in ml_bp.deferred_functions:
            print(f"     {rule}")
            
    except Exception as e:
        print(f"❌ ml_bp erro: {e}")
        import traceback
        traceback.print_exc()

def test_app_creation():
    """Testa criação da aplicação passo a passo"""
    print("\n🔍 Testando criação da aplicação...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        print("✅ Flask app criada")
        
        # Testar registro manual do ml_bp
        from app.routes.ml_routes import ml_bp
        print("✅ ml_bp importado para registro")
        
        app.register_blueprint(ml_bp, url_prefix='/api/ml')
        print("✅ ml_bp registrado manualmente")
        
        # Verificar rotas
        print("Rotas registradas:")
        for rule in app.url_map.iter_rules():
            if '/api/ml' in rule.rule:
                print(f"  {rule.methods} {rule.rule}")
        
        return app
        
    except Exception as e:
        print(f"❌ Erro na criação: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dependencies():
    """Testa dependências do ml_routes"""
    print("\n🔍 Testando dependências do ml_routes...")
    
    try:
        from app.services.sql_db_service import SQLDatabaseService
        print("✅ SQLDatabaseService importado")
    except Exception as e:
        print(f"❌ SQLDatabaseService erro: {e}")
    
    try:
        from app.ml.irrigation_predictor import IrrigationPredictor
        print("✅ IrrigationPredictor importado")
    except Exception as e:
        print(f"❌ IrrigationPredictor erro: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from app.ml.model_trainer import ModelTrainer
        print("✅ ModelTrainer importado")
    except Exception as e:
        print(f"❌ ModelTrainer erro: {e}")
    
    try:
        from app.services.climate_service import ClimateDataService
        print("✅ ClimateDataService importado")
    except Exception as e:
        print(f"❌ ClimateDataService erro: {e}")

def test_predictor_methods():
    """Testa métodos específicos do IrrigationPredictor"""
    print("\n🔍 Testando métodos do IrrigationPredictor...")
    
    try:
        from app.ml.irrigation_predictor import IrrigationPredictor
        predictor = IrrigationPredictor()
        print("✅ IrrigationPredictor instanciado")
        
        # Testar método load_models
        result = predictor.load_models()
        print(f"✅ load_models(): {result}")
        
        # Testar método get_feature_importance
        importance = predictor.get_feature_importance()
        print(f"✅ get_feature_importance(): {type(importance)}")
        
    except Exception as e:
        print(f"❌ Erro nos métodos: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🚀 Debug Blueprint ML Registration")
    print("=" * 50)
    
    # 1. Testar imports
    test_blueprint_import()
    
    # 2. Testar dependências
    test_dependencies()
    
    # 3. Testar métodos específicos
    test_predictor_methods()
    
    # 4. Testar criação manual da app
    app = test_app_creation()
    
    if app:
        print("\n✅ Aplicação criada com sucesso!")
        print("🔍 Testando rota manual...")
        
        with app.test_client() as client:
            response = client.get('/api/ml/status')
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.get_json()}")
            else:
                print(f"Error: {response.data}")

if __name__ == "__main__":
    main()