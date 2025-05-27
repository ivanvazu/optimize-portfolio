# main.py
from fastapi import FastAPI

# Importar los routers de la API
from api.routers import portfolio

# Importar la función para registrar los manejadores de errores
from api.error_handlers.handlers import register_error_handlers

# Inicializa la aplicación FastAPI
app = FastAPI(
    title="API de Optimización de Portafolios",
    description="Una API robusta y tipada para optimizar portafolios de inversión, "
                "basada en retornos históricos y restricciones de riesgo/peso.",
    version="1.0.0"
)

# --- Registrar los manejadores de excepciones ---
register_error_handlers(app)

# --- Incluir los routers ---
app.include_router(portfolio.router, prefix="")
