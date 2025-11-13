# Força Python 3.12, que ainda tem audioop
FROM python:3.12-slim

# Diretório de trabalho
WORKDIR /app

# Copia o projeto
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pelo Flask
EXPOSE 8080

# Executa o bot
CMD ["python", "main.py"]
