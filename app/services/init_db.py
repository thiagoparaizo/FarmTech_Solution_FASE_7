from app.models.cultura import Cultura
from app.models.campo import Campo
from pymongo import MongoClient
from app.models.sensor_models import Base
from sqlalchemy import create_engine
from datetime import datetime

def inicializar_banco_dados(mongo_uri):
    """
    Inicializa o banco de dados MongoDB com dados de exemplo quando a aplicação é executada pela primeira vez
    
    Args:
        mongo_uri (str): URI de conexão com o MongoDB
    """
    client = MongoClient(mongo_uri)
    db = client.get_database()
    
    # Verificar se já existem dados no banco de dados
    if db.culturas.count_documents({}) > 0 and db.campos.count_documents({}) > 0:
        print("Banco de dados MongoDB já inicializado.")
        return
    
    print("Inicializando banco de dados MongoDB com dados de exemplo...")
    
    # Limpar coleções existentes (garantir que não há dados duplicados)
    db.culturas.delete_many({})
    db.campos.delete_many({})
    
    # Adicionar culturas padrão
    mandioca = Cultura.from_dict(Cultura.get_mandioca_default())
    feijao = Cultura.from_dict(Cultura.get_feijao_caupi_default())
    
    db.culturas.insert_one(mandioca.to_dict())
    db.culturas.insert_one(feijao.to_dict())
    
    # Adicionar campos de exemplo
    campo_mandioca = Campo(
        nome_produtor="João Silva",
        localizacao={
            "municipio": "Fortaleza",
            "regiao": "Litoral Cearense"
        },
        campo={
            "tipo_geometria": "retangular",
            "comprimento_m": 100,
            "largura_m": 50,
            "cultura_plantada": "Mandioca",
            "data_plantio": datetime.now().strftime('%Y-%m-%d')
        }
    )
    
    # Calcular área e insumos com base na cultura
    campo_mandioca.calcular_area()
    campo_mandioca.calcular_quantidade_insumos(mandioca.to_dict())
    
    db.campos.insert_one(campo_mandioca.to_dict())
    
    campo_feijao = Campo(
        nome_produtor="Maria Oliveira",
        localizacao={
            "municipio": "Quixadá",
            "regiao": "Sertão Central"
        },
        campo={
            "tipo_geometria": "triangular",
            "base_m": 80,
            "altura_m": 120,
            "cultura_plantada": "Feijão-Caupi",
            "data_plantio": datetime.now().strftime('%Y-%m-%d')
        }
    )
    
    # Calcular área e insumos com base na cultura
    campo_feijao.calcular_area()
    campo_feijao.calcular_quantidade_insumos(feijao.to_dict())
    
    db.campos.insert_one(campo_feijao.to_dict())
    
    # Adicionar mais um exemplo com geometria diferente
    campo_mandioca_circular = Campo(
        nome_produtor="Pedro Santos",
        localizacao={
            "municipio": "Sobral",
            "regiao": "Norte"
        },
        campo={
            "tipo_geometria": "circular",
            "raio_m": 40,
            "cultura_plantada": "Mandioca",
            "data_plantio": datetime.now().strftime('%Y-%m-%d')
        }
    )
    
    # Calcular área e insumos com base na cultura
    campo_mandioca_circular.calcular_area()
    campo_mandioca_circular.calcular_quantidade_insumos(mandioca.to_dict())
    
    db.campos.insert_one(campo_mandioca_circular.to_dict())
    
    print("Inicialização do banco de dados MongoDB concluída.")

def inicializar_banco_dados_relacional(sql_database_uri):
    """
    Inicializa o banco de dados relacional criando as tabelas necessárias
    
    Args:
        sql_database_uri (str): URI de conexão com o banco de dados SQL
    """
    print("Inicializando banco de dados relacional...")
    
    # Criar engine com a URI fornecida
    engine = create_engine(sql_database_uri)
    
    # Criar todas as tabelas definidas no Base
    Base.metadata.create_all(engine)
    
    print("Tabelas do banco de dados relacional criadas com sucesso!")