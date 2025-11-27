# app/services/sql_db_service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database
from app.models.sensor_models import Base, Sensor, PosicaoSensor, LeituraSensor, AplicacaoRecurso, RecomendacaoAutomatica, AlertaSensor, HistoricoSensor
from datetime import datetime, timedelta
import statistics

class SQLDatabaseService:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        
        # Criar banco de dados se não existir
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        
        # Criar tabelas
        Base.metadata.create_all(self.engine)
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
    
    def get_session(self):
        return self.Session()
    
    # Métodos para Sensores
    def adicionar_sensor(self, tipo, modelo=None, data_instalacao=None):
        """Adiciona um novo sensor ao banco de dados"""
        session = self.get_session()
        try:
            novo_sensor = Sensor(
                tipo=tipo,
                modelo=modelo,
                data_instalacao=data_instalacao or datetime.now().date(),
                ativo=True,
                ultima_manutencao=datetime.now()
            )
            session.add(novo_sensor)
            session.commit()
            return novo_sensor.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def obter_sensor(self, sensor_id):
        """Obtém um sensor pelo ID"""
        from sqlalchemy.orm import joinedload
        session = self.get_session()
        try:
            #return session.query(Sensor).filter_by(id=sensor_id).first()
            return session.query(Sensor).options(joinedload(Sensor.posicao)).filter_by(id=sensor_id).first()
        finally:
            session.close()
    
    def obter_sensores_por_tipo(self, tipo):
        """Obtém todos os sensores de um determinado tipo"""
        session = self.get_session()
        try:
            return session.query(Sensor).filter_by(tipo=tipo, ativo=True).all()
        finally:
            session.close()
    
    def obter_sensores_por_campo(self, campo_id):
        """Obtém todos os sensores instalados em um determinado campo"""
        session = self.get_session()
        try:
            posicoes = session.query(PosicaoSensor).filter_by(campo_id=campo_id).all()
            return [posicao.sensor for posicao in posicoes if posicao.sensor.ativo]
        finally:
            session.close()
    
    def atualizar_sensor(self, sensor_id, **kwargs):
        """Atualiza as propriedades de um sensor"""
        session = self.get_session()
        try:
            sensor = session.query(Sensor).filter_by(id=sensor_id).first()
            if not sensor:
                return False
            
            for key, value in kwargs.items():
                if hasattr(sensor, key):
                    setattr(sensor, key, value)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Métodos para Posição do Sensor
    def adicionar_posicao_sensor(self, sensor_id, campo_id, latitude=None, longitude=None, profundidade=None):
        """Adiciona uma nova posição para um sensor"""
        session = self.get_session()
        try:
            nova_posicao = PosicaoSensor(
                sensor_id=sensor_id,
                campo_id=campo_id,
                latitude=latitude,
                longitude=longitude,
                profundidade=profundidade
            )
            session.add(nova_posicao)
            session.commit()
            return nova_posicao.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Métodos para Leituras de Sensores
    # def adicionar_leitura(self, sensor_id, valor, unidade, data_hora=None, valido=True):
    #     """Adiciona uma nova leitura de sensor"""
    #     session = self.get_session()
    #     try:
    #         nova_leitura = LeituraSensor(
    #             sensor_id=sensor_id,
    #             data_hora=data_hora or datetime.now(),
    #             valor=valor,
    #             unidade=unidade,
    #             valido=valido
    #         )
    #         session.add(nova_leitura)
    #         session.commit()
    #         return nova_leitura.id
    #     except Exception as e:
    #         session.rollback()
    #         raise e
    #     finally:
    #         session.close()
    
    def adicionar_leitura(self, sensor_id, valor, unidade, data_hora=None, valido=True):
        """Adiciona uma nova leitura de sensor"""
        session = self.get_session()
        try:
            # Obter o tipo de sensor
            sensor = session.query(Sensor).filter_by(id=sensor_id).first()
            
            if not sensor:
                raise ValueError(f"Sensor com ID {sensor_id} não encontrado")
                
            # Para sensores de nutrientes (S3), extrair valores do JSON
            if sensor.tipo == 'S3' and isinstance(valor, str) and (valor.startswith('{') or unidade == 'ppm'):
                try:
                    import json
                    nutrientes = json.loads(valor)
                    
                    # Armazenar as leituras separadamente
                    if 'P' in nutrientes:
                        nova_leitura_p = LeituraSensor(
                            sensor_id=sensor_id,
                            data_hora=data_hora or datetime.now(),
                            valor=float(nutrientes['P']),
                            unidade='P_ppm',
                            valido=valido
                        )
                        session.add(nova_leitura_p)
                    
                    if 'K' in nutrientes:
                        nova_leitura_k = LeituraSensor(
                            sensor_id=sensor_id,
                            data_hora=data_hora or datetime.now(),
                            valor=float(nutrientes['K']),
                            unidade='K_ppm',
                            valido=valido
                        )
                        session.add(nova_leitura_k)
                    
                    session.commit()
                    return True
                    
                except (json.JSONDecodeError, ValueError) as e:
                    session.rollback()
                    raise ValueError(f"Erro ao processar dados JSON: {str(e)}")
            
            # Para outros sensores, armazenar o valor diretamente
            else:
                # Converter para float se for string
                if isinstance(valor, str):
                    try:
                        valor = float(valor)
                    except ValueError:
                        raise ValueError(f"Valor inválido para o sensor: {valor}")
                
                nova_leitura = LeituraSensor(
                    sensor_id=sensor_id,
                    data_hora=data_hora or datetime.now(),
                    valor=valor,
                    unidade=unidade,
                    valido=valido
                )
                session.add(nova_leitura)
                session.commit()
                return nova_leitura.id
        
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def obter_leituras_por_sensor(self, sensor_id, inicio=None, fim=None, limite=100):
        """Obtém leituras de um sensor em um período"""
        session = self.get_session()
        try:
            query = session.query(LeituraSensor).filter_by(sensor_id=sensor_id, valido=True)
            
            if inicio:
                query = query.filter(LeituraSensor.data_hora >= inicio)
            if fim:
                query = query.filter(LeituraSensor.data_hora <= fim)
            
            return query.order_by(LeituraSensor.data_hora.desc()).limit(limite).all()
        finally:
            session.close()
    
    def calcular_estatisticas_leituras(self, sensor_id, inicio, fim):
        """Calcula estatísticas para as leituras de um sensor em um período"""
        session = self.get_session()
        try:
            leituras = session.query(LeituraSensor).filter_by(
                sensor_id=sensor_id, 
                valido=True
            ).filter(
                LeituraSensor.data_hora >= inicio,
                LeituraSensor.data_hora <= fim
            ).all()
            
            if not leituras:
                return None
            
            # Converter valores de texto para float quando possível
            valores = []
            for leitura in leituras:
                try:
                    # Verificar se o valor é um JSON
                    if leitura.valor.startswith('{') and leitura.valor.endswith('}'):
                        import json
                        # Para valores JSON (sensores de nutrientes), usar a média dos valores
                        dados_json = json.loads(leitura.valor)
                        valores_numericos = [float(v) for v in dados_json.values()]
                        # Adicionar a média dos valores no JSON
                        valores.append(sum(valores_numericos) / len(valores_numericos))
                    else:
                        # Para valores simples, converter para float
                        valores.append(float(leitura.valor))
                except (ValueError, json.JSONDecodeError, TypeError, AttributeError):
                    # Se não for possível converter, ignorar este valor
                    continue
            
            if not valores:
                return {
                    'media': 0,
                    'mediana': 0,
                    'min': 0,
                    'max': 0,
                    'desvio_padrao': 0,
                    'contagem': 0
                }
            
            import statistics
            
            return {
                'media': statistics.mean(valores),
                'mediana': statistics.median(valores) if len(valores) > 0 else 0,
                'min': min(valores) if valores else 0,
                'max': max(valores) if valores else 0,
                'desvio_padrao': statistics.stdev(valores) if len(valores) > 1 else 0,
                'contagem': len(valores)
            }
        finally:
            session.close()
    
    # Métodos para Aplicação de Recursos
    def adicionar_aplicacao_recurso(self, campo_id, tipo_recurso, quantidade, unidade, metodo_aplicacao=None, data_hora=None):
        """Registra uma aplicação de recurso em um campo"""
        session = self.get_session()
        try:
            nova_aplicacao = AplicacaoRecurso(
                campo_id=campo_id,
                data_hora=data_hora or datetime.now(),
                tipo_recurso=tipo_recurso,
                quantidade=quantidade,
                unidade=unidade,
                metodo_aplicacao=metodo_aplicacao
            )
            session.add(nova_aplicacao)
            session.commit()
            return nova_aplicacao.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def obter_aplicacoes_recurso(self, campo_id, tipo_recurso=None, inicio=None, fim=None):
        """Obtém aplicações de recursos para um campo"""
        session = self.get_session()
        try:
            query = session.query(AplicacaoRecurso).filter_by(campo_id=campo_id)
            
            if tipo_recurso:
                query = query.filter_by(tipo_recurso=tipo_recurso)
            if inicio:
                query = query.filter(AplicacaoRecurso.data_hora >= inicio)
            if fim:
                query = query.filter(AplicacaoRecurso.data_hora <= fim)
            
            return query.order_by(AplicacaoRecurso.data_hora.desc()).all()
        finally:
            session.close()
    
    # Métodos para Recomendações Automáticas
    def adicionar_recomendacao(self, campo_id, tipo_recurso, quantidade_recomendada, unidade, baseado_em=None):
        """Adiciona uma nova recomendação automática"""
        session = self.get_session()
        try:
            nova_recomendacao = RecomendacaoAutomatica(
                campo_id=campo_id,
                data_hora=datetime.now(),
                tipo_recurso=tipo_recurso,
                quantidade_recomendada=quantidade_recomendada,
                unidade=unidade,
                baseado_em=baseado_em,
                aplicada=False
            )
            session.add(nova_recomendacao)
            session.commit()
            return nova_recomendacao.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def marcar_recomendacao_aplicada(self, recomendacao_id):
        """Marca uma recomendação como aplicada"""
        session = self.get_session()
        try:
            recomendacao = session.query(RecomendacaoAutomatica).filter_by(id=recomendacao_id).first()
            if not recomendacao:
                return False
            
            recomendacao.aplicada = True
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Métodos para Alertas
    def registrar_alerta(self, sensor_id, tipo, mensagem, severidade='média'):
        """Registra um novo alerta para um sensor"""
        session = self.get_session()
        try:
            novo_alerta = AlertaSensor(
                sensor_id=sensor_id,
                data_hora=datetime.now(),
                tipo=tipo,
                mensagem=mensagem,
                severidade=severidade,
                resolvido=False
            )
            session.add(novo_alerta)
            session.commit()
            return novo_alerta.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def resolver_alerta(self, alerta_id):
        """Marca um alerta como resolvido"""
        session = self.get_session()
        try:
            alerta = session.query(AlertaSensor).filter_by(id=alerta_id).first()
            if not alerta:
                return False
            
            alerta.resolvido = True
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Métodos para Histórico
    def gerar_historico(self, sensor_id, data_inicio, data_fim):
        """Gera um registro histórico para um período"""
        estatisticas = self.calcular_estatisticas_leituras(sensor_id, data_inicio, data_fim)
        
        if not estatisticas:
            return None
        
        session = self.get_session()
        try:
            novo_historico = HistoricoSensor(
                sensor_id=sensor_id,
                data_inicio=data_inicio.date() if isinstance(data_inicio, datetime) else data_inicio,
                data_fim=data_fim.date() if isinstance(data_fim, datetime) else data_fim,
                media_leituras=estatisticas['media'],
                min_leitura=estatisticas['min'],
                max_leitura=estatisticas['max'],
                desvio_padrao=estatisticas['desvio_padrao']
            )
            session.add(novo_historico)
            session.commit()
            return novo_historico.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
def adicionar_leitura(self, sensor_id, valor, unidade, data_hora=None, valido=True):
    """Adiciona uma nova leitura de sensor"""
    session = self.get_session()
    try:
        # Obter o tipo de sensor
        sensor = session.query(Sensor).filter_by(id=sensor_id).first()
        
        if not sensor:
            raise ValueError(f"Sensor com ID {sensor_id} não encontrado")
        
        # Garantir que o valor seja convertido adequadamente
        if isinstance(valor, dict):
            # Se for um dicionário, converter para JSON string
            import json
            valor_str = json.dumps(valor)
        elif isinstance(valor, (int, float)):
            # Se for numérico, converter para string
            valor_str = str(valor)
        else:
            # Se já for string, usar diretamente
            valor_str = str(valor)
        
        # Para sensores de nutrientes (S3), processar valores JSON
        if sensor.tipo == 'S3' and isinstance(valor, str) and valor.startswith('{'):
            try:
                import json
                nutrientes = json.loads(valor)
                
                # Armazenar as leituras separadamente
                if 'P' in nutrientes and nutrientes['P'] > 0:
                    nova_leitura_p = LeituraSensor(
                        sensor_id=sensor_id,
                        data_hora=data_hora or datetime.now(),
                        valor=str(nutrientes['P']),
                        unidade='P_ppm',
                        valido=valido
                    )
                    session.add(nova_leitura_p)
                
                if 'K' in nutrientes and nutrientes['K'] > 0:
                    nova_leitura_k = LeituraSensor(
                        sensor_id=sensor_id,
                        data_hora=data_hora or datetime.now(),
                        valor=str(nutrientes['K']),
                        unidade='K_ppm',
                        valido=valido
                    )
                    session.add(nova_leitura_k)
                
                session.commit()
                return True
                
            except (json.JSONDecodeError, ValueError) as e:
                session.rollback()
                raise ValueError(f"Erro ao processar dados JSON: {str(e)}")
        
        # Para outros sensores, armazenar o valor diretamente
        else:
            nova_leitura = LeituraSensor(
                sensor_id=sensor_id,
                data_hora=data_hora or datetime.now(),
                valor=valor_str,
                unidade=unidade,
                valido=valido
            )
            session.add(nova_leitura)
            session.commit()
            return nova_leitura.id
    
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()