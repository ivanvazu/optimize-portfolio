from pydantic import BaseModel, Field

class PortfolioOptimizationParams(BaseModel):
    # Este modelo podría ser usado internamente por la lógica de negocio
    # o como DTO (Data Transfer Object) si los parámetros vinieran de un JSON body.
    # Como viene de Form, Pydantic lo valida automáticamente sin necesidad de instanciarlo.
    risk_level: float = Field(..., ge=0, description="Nivel máximo de volatilidad aceptable para el portafolio.")
    max_weight: float = Field(..., gt=0, le=1, description="Peso máximo que un solo activo puede tener en el portafolio.")
