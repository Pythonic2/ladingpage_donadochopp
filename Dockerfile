# Use uma imagem base do Python
FROM python:3.13

# Configura o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para o contêiner
COPY . .

# Comando para iniciar o servidor Django
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8008"]
CMD exec python manage.py runserver 0.0.0.0:$PORT
#RUN pip install gunicorn

#CMD ["sh", "-c", "gunicorn core.wsgi:application --bind 0.0.0.0:$PORT"]





