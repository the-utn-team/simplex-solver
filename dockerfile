FROM python:3.12-slim-bookworm

# 1. Variables de entorno
ENV TZ=America/Argentina/Mendoza
ENV FLASK_CONTEXT=production
ENV PYTHONUNBUFFERED=1
ENV PATH=$PATH:/home/flaskapp/.local/bin

# 2. Crear usuario
RUN useradd --create-home --home-dir /home/flaskapp flaskapp

# 3. Workdir antes de cambiar de usuario
WORKDIR /home/flaskapp

# 4. Instalar dependencias como root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# 5. Copiar aplicación COMPLETA como root
COPY . .

# 6. Crear carpeta outputs dentro del contenedor y asignar permisos y dueño
RUN mkdir -p /home/flaskapp/outputs && \
    chown -R flaskapp:flaskapp /home/flaskapp && \
    chmod -R 775 /home/flaskapp/outputs

# 7. Recién ahora cambiar a usuario flaskapp
USER flaskapp

# 8. Exponer puerto
EXPOSE 5000

# 9. Ejecutar con Gunicorn
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "web_app:app"]
