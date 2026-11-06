FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Variáveis de ambiente com valores padrão
ENV SECRET_KEY=dev-secret-key-change-in-production
# Caminho relativo ao instance_path (Flask-SQLAlchemy): /app/instance/edenred.db
ENV DATABASE_URI=sqlite:///edenred.db
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Expõe a porta do Flask
EXPOSE 5000

# Comando para iniciar a aplicação com gunicorn
# 1 worker com threads: SocketIO (chat em tempo real) exige processo único
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--worker-class", "gthread", "wsgi:app"]
