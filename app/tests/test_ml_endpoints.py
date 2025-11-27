# test_ml_endpoints.py

"""
Script para testar os endpoints de ML do FarmTech
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_status_endpoint():
    """Testa endpoint /api/ml/status"""
    print("🔍 Testando /api/ml/status...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ml/status")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resposta recebida:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se que o Flask está rodando em localhost:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_predict_endpoint():
    """Testa endpoint /api/ml/predict"""
    print("\n🔍 Testando /api/ml/predict...")
    
    payload = {
        "umidade": 25.5,
        "ph": 6.8,
        "fosforo": 1,
        "potassio": 0,
        "temperature": 28.5,
        "humidity_air": 75
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ml/predict",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predição recebida:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_train_endpoint():
    """Testa endpoint /api/ml/train"""
    print("\n🔍 Testando /api/ml/train...")
    
    payload = {
        "sensor_id": 1,
        "days_back": 30,
        "min_samples": 20,
        "location": "-3.763081,-38.524465"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ml/train",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Treinamento iniciado:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_flask_routes():
    """Testa se o Flask está respondendo"""
    print("🔍 Testando se Flask está ativo...")
    
    try:
        # Testar rota principal
        response = requests.get(f"{BASE_URL}/")
        print(f"Rota principal (/): {response.status_code}")
        
        # Testar rota de API conhecida
        response = requests.get(f"{BASE_URL}/api/culturas")
        print(f"API culturas: {response.status_code}")
        
        # Listar todas as rotas registradas
        print("\n📋 Testando se rota ML existe...")
        response = requests.get(f"{BASE_URL}/api/ml/status")
        if response.status_code == 404:
            print("❌ Rota /api/ml/status não encontrada!")
            print("   Verifique se o blueprint ml_bp está registrado")
        else:
            print(f"✅ Rota ML encontrada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    print("🚀 FarmTech ML Endpoints - Teste Completo")
    print("=" * 50)
    
    # 1. Testar conectividade básica
    test_flask_routes()
    
    # 2. Testar status do modelo
    test_status_endpoint()
    
    # 3. Testar predição
    test_predict_endpoint()
    
    # 4. Testar treinamento (opcional)
    print("\n❓ Deseja testar treinamento? (pode demorar) [y/N]: ", end="")
    if input().lower().startswith('y'):
        test_train_endpoint()
    
    print("\n🏁 Testes concluídos!")

if __name__ == "__main__":
    main()
    

## python app/tests/test_ml_endpoints.py