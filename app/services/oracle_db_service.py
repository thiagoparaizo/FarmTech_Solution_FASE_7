# app/services/oracle_db_service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models.oracle_models import OracleBase, FabricanteSensor, ModeloSensor

class OracleDatabaseService:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        
        # Criar tabelas
        try:
            OracleBase.metadata.drop_all(self.engine)
        except Exception as e:
            print(f"Erro ao excluir tabelas: {e}")
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
    
    def get_session(self):
        return self.Session()
    
    def inicializar_dados_exemplo(self):
        """Inicializa o banco com dados de exemplo se não existirem"""
        session = self.get_session()
        try:
            # Verificar se já existem fabricantes
            if session.query(FabricanteSensor).count() > 0:
                return
            
            # Criar fabricantes
            fabricante1 = FabricanteSensor(
                nome="SensorTech",
                pais="Brasil",
                website="https://sensortech.com.br",
                descricao="Empresa brasileira especializada em sensores agrícolas"
            )
            
            fabricante2 = FabricanteSensor(
                nome="AgriSense",
                pais="EUA",
                website="https://agrisense.com",
                descricao="Líder mundial em sensores de precisão para agricultura"
            )
            
            fabricante3 = FabricanteSensor(
                nome="EcoMonitor",
                pais="Alemanha",
                website="https://ecomonitor.de",
                descricao="Sensores sustentáveis com tecnologia alemã"
            )
            
            # Criar modelos
            modelo1 = ModeloSensor(
                nome="HydroSense Pro",
                tipo="S1",  # Umidade
                precisao="±1%",
                faixa_medicao="0-100%",
                preco_referencia="R$ 450,00",
                descricao="Sensor de umidade do solo de alta precisão"
            )
            
            modelo2 = ModeloSensor(
                nome="pHMaster 2000",
                tipo="S2",  # pH
                precisao="±0.1 pH",
                faixa_medicao="0-14 pH",
                preco_referencia="R$ 680,00",
                descricao="Sensor de pH com leitura digital e compensação de temperatura"
            )
            
            modelo3 = ModeloSensor(
                nome="NutriScan",
                tipo="S3",  # Nutrientes
                precisao="±5 ppm",
                faixa_medicao="0-2000 ppm",
                preco_referencia="R$ 1.200,00",
                descricao="Sensor para análise de NPK com transmissão sem fio"
            )
            
            modelo4 = ModeloSensor(
                nome="SoilHydro Basic",
                tipo="S1",  # Umidade
                precisao="±2%",
                faixa_medicao="0-100%",
                preco_referencia="R$ 280,00",
                descricao="Sensor de umidade do solo econômico"
            )
            
            modelo5 = ModeloSensor(
                nome="NPK Tracker",
                tipo="S3",  # Nutrientes
                precisao="±10 ppm",
                faixa_medicao="0-1500 ppm",
                preco_referencia="R$ 890,00",
                descricao="Sensor compacto para monitoramento de nutrientes"
            )
            
            # Estabelecer relacionamentos
            fabricante1.modelos = [modelo1, modelo4]
            fabricante2.modelos = [modelo2, modelo3]
            fabricante3.modelos = [modelo1, modelo5]  # Mesmo modelo, fabricantes diferentes
            
            # Adicionar tudo ao banco
            session.add_all([fabricante1, fabricante2, fabricante3])
            session.add_all([modelo1, modelo2, modelo3, modelo4, modelo5])
            
            session.commit()
            
            print("Dados de exemplo para Oracle inicializados com sucesso.")
        except Exception as e:
            session.rollback()
            print(f"Erro ao inicializar dados de exemplo: {str(e)}")
        finally:
            session.close()
    
    def obter_todos_fabricantes(self):
        """Retorna todos os fabricantes cadastrados"""
        session = self.get_session()
        try:
            return session.query(FabricanteSensor).all()
        finally:
            session.close()
    
    def obter_todos_modelos(self):
        """Retorna todos os modelos de sensores cadastrados"""
        session = self.get_session()
        try:
            return session.query(ModeloSensor).all()
        finally:
            session.close()
    
    def obter_modelos_por_tipo(self, tipo):
        """Retorna modelos de sensores por tipo (S1, S2, S3)"""
        session = self.get_session()
        try:
            return session.query(ModeloSensor).filter_by(tipo=tipo).all()
        finally:
            session.close()
    
    def obter_fabricante_por_id(self, fabricante_id):
        """Retorna um fabricante pelo ID"""
        session = self.get_session()
        try:
            return session.query(FabricanteSensor).filter_by(id=fabricante_id).first()
        finally:
            session.close()
    
    def obter_modelo_por_id(self, modelo_id):
        """Retorna um modelo pelo ID"""
        session = self.get_session()
        try:
            return session.query(ModeloSensor).filter_by(id=modelo_id).first()
        finally:
            session.close()