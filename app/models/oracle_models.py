# app/models/oracle_models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

OracleBase = declarative_base()

# Tabela de associação (M:N) entre Fabricantes e Modelos
fabricante_modelo = Table(
    'fabricante_modelo',
    OracleBase.metadata,
    Column('fabricante_id', Integer, ForeignKey('fabricante_sensor.id'), primary_key=True),
    Column('modelo_id', Integer, ForeignKey('modelo_sensor.id'), primary_key=True)
)

class FabricanteSensor(OracleBase):
    __tablename__ = 'fabricante_sensor'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    pais = Column(String(50))
    website = Column(String(255))
    descricao = Column(String(500))
    
    # Relacionamento M:N com ModeloSensor
    modelos = relationship("ModeloSensor", secondary=fabricante_modelo, back_populates="fabricantes")
    
    def __repr__(self):
        return f"<FabricanteSensor(nome='{self.nome}', pais='{self.pais}')>"

class ModeloSensor(OracleBase):
    __tablename__ = 'modelo_sensor'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)  # S1, S2, S3
    precisao = Column(String(50))
    faixa_medicao = Column(String(100))
    preco_referencia = Column(String(50))
    descricao = Column(String(500))
    
    # Relacionamento M:N com FabricanteSensor
    fabricantes = relationship("FabricanteSensor", secondary=fabricante_modelo, back_populates="modelos")
    
    def __repr__(self):
        return f"<ModeloSensor(nome='{self.nome}', tipo='{self.tipo}')>"