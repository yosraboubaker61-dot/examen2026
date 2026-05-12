# Image légère Python
FROM python:3.10-slim

# Dossier de travail
WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Exposer le port Flask
EXPOSE 5000

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Lancer Flask
CMD ["python3", "app.py"]
