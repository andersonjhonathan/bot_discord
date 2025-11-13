# Usa Python 3.11.9 para evitar erro do audioop
FROM python:3.11.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o conteúdo do projeto
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Flask
EXPOSE 8080

# Comando de execução
CMD ["python", "main.py"]
