# Imagen base liviana con Python
FROM python:3.11-slim


# (Opcional) Crear usuario no-root
RUN useradd -m appuser

# Actualiza pip (más rápido/seguro)
RUN python -m pip install --upgrade pip

# Workdir
WORKDIR /app

# Instalar dependencias primero para cachear capas
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY src ./src

# Exponer el puerto de la API
EXPOSE 8000

# Cambiar a usuario no-root
USER appuser

# Arranque con Gunicorn (módulo:objeto_app)
# - 2 workers + 4 threads es un default razonable
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000","--access-logfile", "-"]