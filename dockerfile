FROM python:3.12-slim-bookworm

# 2. Variables de Entorno 
ENV TZ=America/Argentina/Mendoza
ENV FLASK_CONTEXT=production
ENV PYTHONUNBUFFERED=1
ENV PATH=$PATH:/home/flaskapp/.local/bin

# 3. Usuario no-root
RUN useradd --create-home --home-dir /home/flaskapp flaskapp
WORKDIR /home/flaskapp
USER flaskapp

# 4. Dependencias (Optimizando la caché)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --user

# 5. Copiar TODA la aplicación
COPY . .

# 6. Exponer el puerto
EXPOSE 5000

# 7.Le decimos a Gunicorn que busque la variable 'app'
# en el archivo 'web_app.py'.
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "web_app:app"]


