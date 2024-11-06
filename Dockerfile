# Usa uma imagem Python base
FROM python:3.10-slim

ENV PYTHONPATH="${PYTHONPATH}:/app"

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências e instala as dependências
COPY functions/ofp_api/requirements.txt ./requirements_ofp_api.txt
RUN pip install --no-cache-dir -r requirements_ofp_api.txt

COPY layers/sqlalchemy/requirements.txt ./requirements_sqlalchemy.txt
RUN pip install --no-cache-dir -r requirements_sqlalchemy.txt

# Instala o Uvicorn diretamente
RUN pip install uvicorn

# Copia o código da aplicação para o contêiner
COPY . .

# Expõe a porta 8000 para a aplicação
EXPOSE 8000

# Define o comando de inicialização do FastAPI
CMD ["uvicorn", "functions.ofp_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
