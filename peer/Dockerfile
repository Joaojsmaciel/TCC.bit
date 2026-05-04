FROM python:3.9-slim

WORKDIR /app

COPY network.py .
COPY file_manager.py .
COPY heartbeat.py .
COPY replication.py .
COPY ui.py .
COPY peer.py .
COPY web_gateway.py .

# Criar diretório para arquivos
RUN mkdir -p /app/files

EXPOSE 6000-6100

CMD ["python", "peer.py"]
