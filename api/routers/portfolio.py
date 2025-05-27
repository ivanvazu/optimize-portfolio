from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Annotated, Dict
import pandas as pd

# Importar la lógica de optimización
from core.services.portfolio_optimizer import optimize_portfolio

# Importar los modelos necesarios para la respuesta
from shared.models.common import OptimalPortfolioResponse # Asumiendo que OptimalPortfolioResponse se mantiene en models.py

# Importar la dependencia del CSV
from api.dependencies.common import get_validated_returns_df_dependency

# Crear un APIRouter
router = APIRouter()

@router.post(
    "/optimize-portfolio", 
    response_model=OptimalPortfolioResponse,
    summary="Optimiza un portafolio de inversión",
    description="Sube un archivo CSV con retornos de activos para obtener pesos óptimos del portafolio, "
                "minimizando el riesgo dado un nivel de riesgo máximo y un peso máximo por activo."
)
async def optimize_portfolio_endpoint(
    returns_df: Annotated[pd.DataFrame, Depends(get_validated_returns_df_dependency)],
    risk_level: float = Form(..., ge=0, description="Nivel máximo de volatilidad (desviación estándar) aceptable para el portafolio."),
    max_weight: float = Form(..., gt=0, le=1, description="Peso máximo que un solo activo puede tener en el portafolio (entre 0 y 1).")
):
    """
    **Optimiza un portafolio de inversión:**
    
    Este endpoint permite a los usuarios subir un archivo CSV con retornos de activos
    y recibir los pesos óptimos del portafolio que minimizan el riesgo,
    considerando un nivel de riesgo máximo aceptable y un peso máximo para cualquier activo individual.
    
    **Parámetros de Entrada:**
    - `file`: **Archivo CSV** con los retornos de los activos (gestionado por la dependencia).
              La primera columna debe ser el índice (ej. fechas) y las demás columnas
              deben ser los tickers/nombres de los activos con sus retornos numéricos.
    - `risk_level`: **Nivel máximo de volatilidad (desviación estándar)** que estás dispuesto a aceptar en tu portafolio.
                    Debe ser un número flotante no negativo.
    - `max_weight`: **Peso máximo** que cualquier activo individual puede tener en el portafolio.
                    Debe ser un número flotante entre 0 (exclusivo) y 1 (inclusivo).
    
    **Respuesta Exitosa (200 OK):**
    - `optimal_portfolio`: Un diccionario donde las claves son los nombres de los activos
                           y los valores son sus pesos óptimos en el portafolio (redondeados a 6 decimales).
    
    **Respuestas de Error:**
    - `400 Bad Request`: Errores relacionados con el archivo CSV, formato o contenido.
    - `422 Unprocessable Entity`: Errores de validación de los parámetros del formulario (`risk_level`, `max_weight`).
    - `500 Internal Server Error`: Errores inesperados durante la optimización del portafolio.
    
    Todas las respuestas de error siguen el estándar **RFC 7807 (Problem Details for HTTP APIs)**.
    """
    
    optimal_portfolio_result: Dict[str, Any] = optimize_portfolio(returns_df, risk_level, max_weight)
    
    if "error" in optimal_portfolio_result:
        raise HTTPException(
            status_code=500, 
            detail=optimal_portfolio_result["error"]
        )
    else:
        return OptimalPortfolioResponse(optimal_portfolio=optimal_portfolio_result)
