# Imagem base
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos
COPY . /app

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Porta
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "app.py"]