# app/models/sensor_models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensor'
    
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)  # S1, S2, S3
    modelo = Column(String(100))
    data_instalacao = Column(Date)
    ativo = Column(Boolean, default=True)
    ultima_manutencao = Column(DateTime)
    
    posicao = relationship("PosicaoSensor", back_populates="sensor", uselist=False)
    leituras = relationship("LeituraSensor", back_populates="sensor")
    alertas = relationship("AlertaSensor", back_populates="sensor")
    historicos = relationship("HistoricoSensor", back_populates="sensor")
    
    def __repr__(self):
        return f"<Sensor(id={self.id}, tipo='{self.tipo}', ativo={self.ativo})>"

class PosicaoSensor(Base):
    __tablename__ = 'posicao_sensor'
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    campo_id = Column(String(50), nullable=False)  # ID do MongoDB
    latitude = Column(Float)
    longitude = Column(Float)
    profundidade = Column(Float)
    
    sensor = relationship("Sensor", back_populates="posicao")
    
    def __repr__(self):
        return f"<PosicaoSensor(id={self.id}, campo_id='{self.campo_id}')>"

class LeituraSensor(Base):
    __tablename__ = 'leitura_sensor'
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    data_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    valor = Column(Text, nullable=False)
    unidade = Column(String(20), nullable=False)
    valido = Column(Boolean, default=True)
    
    sensor = relationship("Sensor", back_populates="leituras")
    
    def __repr__(self):
        return f"<LeituraSensor(id={self.id}, valor={self.valor}, data_hora='{self.data_hora}')>"

class AplicacaoRecurso(Base):
    __tablename__ = 'aplicacao_recurso'
    
    id = Column(Integer, primary_key=True)
    campo_id = Column(String(50), nullable=False)
    data_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    tipo_recurso = Column(String(50), nullable=False)
    quantidade = Column(Float, nullable=False)
    unidade = Column(String(20), nullable=False)
    metodo_aplicacao = Column(String(100))
    
    def __repr__(self):
        return f"<AplicacaoRecurso(id={self.id}, tipo='{self.tipo_recurso}', quantidade={self.quantidade})>"

class RecomendacaoAutomatica(Base):
    __tablename__ = 'recomendacao_automatica'
    
    id = Column(Integer, primary_key=True)
    campo_id = Column(String(50), nullable=False)
    data_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    tipo_recurso = Column(String(50), nullable=False)
    quantidade_recomendada = Column(Float, nullable=False)
    unidade = Column(String(20), nullable=False)
    baseado_em = Column(Text)
    aplicada = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<RecomendacaoAutomatica(id={self.id}, tipo='{self.tipo_recurso}', aplicada={self.aplicada})>"

class AlertaSensor(Base):
    __tablename__ = 'alerta_sensor'
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    data_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    tipo = Column(String(50), nullable=False)
    mensagem = Column(Text)
    severidade = Column(String(20), default='média')
    resolvido = Column(Boolean, default=False)
    
    sensor = relationship("Sensor", back_populates="alertas")
    
    def __repr__(self):
        return f"<AlertaSensor(id={self.id}, tipo='{self.tipo}', resolvido={self.resolvido})>"

class HistoricoSensor(Base):
    __tablename__ = 'historico_sensor'
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    media_leituras = Column(Float)
    min_leitura = Column(Float)
    max_leitura = Column(Float)
    desvio_padrao = Column(Float)
    
    sensor = relationship("Sensor", back_populates="historicos")
    
    def __repr__(self):
        return f"<HistoricoSensor(id={self.id}, data_inicio='{self.data_inicio}', data_fim='{self.data_fim}')>"