FROM python:3.11-slim

# Instalar dependências do Instant Client
RUN apt-get update && apt-get install -y libaio1 wget unzip

# Baixar e instalar o Oracle Instant Client
RUN mkdir -p /opt/oracle && \
    wget https://download.oracle.com/otn_software/linux/instantclient/211000/instantclient-basic-linux.x64-21.1.0.0.0.zip -O /opt/oracle/instantclient.zip && \
    unzip /opt/oracle/instantclient.zip -d /opt/oracle && \
    rm /opt/oracle/instantclient.zip && \
    ln -s /opt/oracle/instantclient_21_1 /opt/oracle/instantclient && \
    echo /opt/oracle/instantclient > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

# Configurar variáveis de ambiente para cx_Oracle
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient
ENV ORACLE_HOME=/opt/oracle/instantclient
ENV PATH=$PATH:$ORACLE_HOME

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]