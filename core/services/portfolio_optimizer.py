import pandas as pd
import numpy as np
from scipy.optimize import minimize
from typing import Dict, Union

def portfolio_volatility(weights: np.ndarray, returns: pd.DataFrame) -> float:
    """Calcula la volatilidad del portafolio."""
    covariance_matrix = returns.cov()
    return np.sqrt(np.transpose(weights) @ covariance_matrix @ weights)

def neg_sharpe_ratio(weights: np.ndarray, returns: pd.DataFrame, risk_free_rate: float = 0) -> float:
    """Calcula el negativo del Sharpe Ratio (para minimización)."""
    portfolio_return = np.sum(returns.mean() * weights)
    portfolio_vol = portfolio_volatility(weights, returns)
    if portfolio_vol == 0:
        return -np.inf if portfolio_return > risk_free_rate else np.inf
    return -(portfolio_return - risk_free_rate) / portfolio_vol

def optimize_portfolio(returns: pd.DataFrame, risk_level: float, max_weight: float) -> Union[Dict[str, float], Dict[str, str]]:
    """
    Optimiza el portafolio para minimizar el riesgo dado un nivel de riesgo máximo y pesos máximos por activo.
    
    Args:
        returns (pd.DataFrame): DataFrame con los retornos de los activos.
                                La primera columna es el índice (ej. fecha) y las demás los activos.
        risk_level (float): Nivel máximo de volatilidad aceptable para el portafolio.
        max_weight (float): Peso máximo que un solo activo puede tener en el portafolio.

    Returns:
        Union[Dict[str, float], Dict[str, str]]: Un diccionario con los pesos óptimos de cada activo
                                                  o un diccionario con un mensaje de error.
    """
    num_assets = len(returns.columns)
    
    if num_assets == 0:
        return {"error": "No hay activos en los datos de retorno proporcionados para la optimización."}

    args = (returns,)
    
    constraints = [
        {'type': 'ineq', 'fun': lambda weights: risk_level - portfolio_volatility(weights, returns)},
        {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}
    ]
    
    bounds = tuple((0, max_weight) for _ in range(num_assets))
    
    initial_weights = np.array([1/num_assets] * num_assets)
    initial_weights = np.clip(initial_weights, 0, max_weight)
    if np.sum(initial_weights) == 0:
        initial_weights = np.array([max_weight / num_assets] * num_assets)
        initial_weights = initial_weights / np.sum(initial_weights)

    try:
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
            optimal_weights = optimal_weights / np.sum(optimal_weights)
            optimal_portfolio = dict(zip(returns.columns, optimal_weights))
            return {asset: round(weight, 6) for asset, weight in optimal_portfolio.items()}
        else:
            return {"error": f"No se encontró una solución óptima para el portafolio: {optimized_results.message}"}
    except Exception as e:
        return {"error": f"Error inesperado durante la optimización del portafolio: {str(e)}"}
