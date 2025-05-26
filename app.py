from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from io import StringIO
from pydantic import BaseModel, Field
from pydantic import ValidationError # Importar ValidationError para un manejo específico
from typing import Dict, Any, Tuple, Union # Importar Union para compatibilidad con Python 3.9

app = Flask(__name__)

# Modelos de datos para validación con Pydantic
class PortfolioOptimizationParams(BaseModel):
    risk_level: float = Field(..., ge=0, description="Nivel máximo de volatilidad aceptable para el portafolio.")
    max_weight: float = Field(..., gt=0, le=1, description="Peso máximo que un solo activo puede tener en el portafolio.")

def portfolio_volatility(weights: np.ndarray, returns: pd.DataFrame) -> float:
    """Calcula la volatilidad del portafolio."""
    covariance_matrix = returns.cov()
    return np.sqrt(np.transpose(weights) @ covariance_matrix @ weights)

def neg_sharpe_ratio(weights: np.ndarray, returns: pd.DataFrame, risk_free_rate: float = 0) -> float:
    """Calcula el negativo del Sharpe Ratio (para minimización)."""
    portfolio_return = np.sum(returns.mean() * weights)
    portfolio_vol = portfolio_volatility(weights, returns)
    # Evitar división por cero si la volatilidad es cero
    if portfolio_vol == 0:
        return -np.inf if portfolio_return > risk_free_rate else np.inf
    return -(portfolio_return - risk_free_rate) / portfolio_vol

def optimize_portfolio(returns: pd.DataFrame, risk_level: float, max_weight: float) -> Union[Dict[str, float], Dict[str, str]]:
    """Optimiza el portafolio para minimizar el riesgo dado un nivel de riesgo máximo y pesos máximos por activo."""
    num_assets = len(returns.columns)
    
    if num_assets == 0:
        return {"error": "No hay activos en los datos de retorno proporcionados."}

    args = (returns,)
    
    # Restricciones
    constraints = [
        # Restricción de riesgo: la volatilidad del portafolio debe ser menor o igual al risk_level
        {'type': 'ineq', 'fun': lambda weights: risk_level - portfolio_volatility(weights, returns)},
        # La suma de los pesos debe ser 1
        {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}
    ]
    
    # Límites para los pesos de cada activo (entre 0 y max_weight)
    bounds = tuple((0, max_weight) for _ in range(num_assets))
    
    # Pesos iniciales: distribución equitativa
    initial_weights = np.array([1/num_assets] * num_assets)
    
    # Asegurarse de que los pesos iniciales cumplan con los límites
    initial_weights = np.clip(initial_weights, 0, max_weight)
    if np.sum(initial_weights) == 0: # Si clipping resulta en suma cero, ajustar
        initial_weights = np.array([max_weight / num_assets] * num_assets)
        initial_weights = initial_weights / np.sum(initial_weights) # Normalizar

    try:
        # Minimizar el negativo del Sharpe Ratio para encontrar un portafolio eficiente
        optimized_results = minimize(
            fun=neg_sharpe_ratio, 
            x0=initial_weights, 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints, 
            args=args
        )

        if optimized_results.success:
            optimal_weights = optimized_results.x
            # Normalizar los pesos para asegurar que sumen 1, corrigiendo posibles errores de precisión
            optimal_weights = optimal_weights / np.sum(optimal_weights)
            optimal_portfolio = dict(zip(returns.columns, optimal_weights))
            return {asset: round(weight, 6) for asset, weight in optimal_portfolio.items()}
        else:
            return {"error": f"No se encontró una solución óptima: {optimized_results.message}"}
    except Exception as e:
        return {"error": f"Error durante la optimización: {str(e)}"}


def validate_and_parse_csv(file) -> Tuple[Union[pd.DataFrame, None], Union[str, None]]:
    """Valida el archivo CSV y lo parsea en un DataFrame de pandas."""
    if not file:
        return None, "No se proporcionó el archivo CSV."
    
    if file.filename == '':
        return None, "Nombre de archivo vacío."
        
    if not file.filename.endswith('.csv'):
        return None, "El archivo debe ser un CSV."

    try:
        csv_data = StringIO(file.stream.read().decode("utf-8"))
        returns_df = pd.read_csv(csv_data, index_col=0) 
        
        if returns_df.empty:
            return None, "El archivo CSV está vacío o no contiene datos válidos."
        if not all(pd.api.types.is_numeric_dtype(returns_df[col]) for col in returns_df.columns):
            return None, "Todas las columnas de retornos en el CSV deben ser numéricas."
            
        returns_df = returns_df.dropna() # Eliminar filas con valores NaN después de la validación inicial
        return returns_df, None
    except pd.errors.EmptyDataError:
        return None, "El archivo CSV está vacío."
    except pd.errors.ParserError:
        return None, "Error al parsear el archivo CSV. Verifique el formato."
    except Exception as e:
        return None, f"Error inesperado al procesar el archivo CSV: {str(e)}"

def validate_and_get_params(form_data) -> Tuple[Union[PortfolioOptimizationParams, None], Union[str, None]]:
    """Valida y obtiene los parámetros de optimización del formulario."""
    try:
        params = PortfolioOptimizationParams(
            risk_level=float(form_data.get('risk_level')),
            max_weight=float(form_data.get('max_weight'))
        )
        return params, None
    except ValidationError as e:
        # Pydantic ValidationError proporciona detalles más específicos
        return None, f"Error de validación de parámetros: {e.errors()}"
    except (ValueError, TypeError):
        return None, "Parámetros 'risk_level' y/o 'max_weight' no proporcionados o inválidos. Deben ser números flotantes."

@app.route('/optimize-portfolio', methods=['POST'])
def optimize_portfolio_endpoint():
    """Endpoint para optimizar el portafolio."""
    
    # 1. Validación y parseo del archivo CSV
    returns_df, error = validate_and_parse_csv(request.files.get('file'))
    if error:
        return jsonify({"error": error}), 400

    # 2. Validación y obtención de parámetros
    params, error = validate_and_get_params(request.form)
    if error:
        return jsonify({"error": error}), 400

    # 3. Llamada a la lógica de optimización
    optimal_portfolio = optimize_portfolio(returns_df, params.risk_level, params.max_weight)
    
    # 4. Manejo de resultados
    if "error" in optimal_portfolio:
        return jsonify(optimal_portfolio), 500
    else:
        return jsonify({"optimal_portfolio": optimal_portfolio})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
