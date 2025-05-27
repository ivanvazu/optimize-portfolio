from pydantic import BaseModel, Field
from typing import Dict, Any

class OptimalPortfolioResponse(BaseModel): # <-- Ensure this model is here
    optimal_portfolio: Dict[str, float] = Field(..., description="Pesos óptimos para cada activo en el portafolio.")

class ProblemDetails(BaseModel):
    """
    Representa un objeto Problem Details según RFC 7807 para respuestas de error estandarizadas.
    """
    type: str = Field(
        default="about:blank",
        description="URI de referencia de tipo que identifica el tipo de problema."
    )
    title: str = Field(
        ...,
        description="Título corto y legible por humanos para el tipo de problema. "
                    "No debe cambiar para diferentes ocurrencias del mismo tipo de problema."
    )
    status: int = Field(
        ...,
        description="El código de estado HTTP generado por el servidor para esta ocurrencia de problema."
    )
    detail: str = Field(
        None,
        description="Una explicación legible por humanos específica de esta ocurrencia del problema."
    )
    instance: str = Field(
        None,
        description="URI de referencia que identifica la ocurrencia específica del problema."
    )
    errors: Any = Field(
        None,
        description="Detalles adicionales sobre los errores, como errores de validación de Pydantic."
    )