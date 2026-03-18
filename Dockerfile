# Dockerfile
FROM python:3.11-slim

# Prevenir Python de escrever arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevenir Python de fazer buffer de stdout e stderr
ENV PYTHONUNBUFFERED=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar projeto
COPY . /app/

# Criar diretórios necessários
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Expor porta
EXPOSE 8000

# Comando padrão
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

