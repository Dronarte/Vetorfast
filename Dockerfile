# Usa imagem do Python
FROM python:3.10-slim

# Instala dependência do sistema para potrace
RUN apt-get update && apt-get install -y libpotrace-dev build-essential && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Flask
EXPOSE 5000

# Comando para rodar o app
CMD ["python", "app.py"]
