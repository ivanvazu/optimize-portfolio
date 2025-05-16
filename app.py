from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from io import StringIO

app = Flask(__name__)

def portfolio_volatility(weights, returns):
    """Calcula la volatilidad del portafolio."""
    covariance_matrix = returns.cov()
    return np.sqrt(np.transpose(weights) @ covariance_matrix @ weights)

def neg_sharpe_ratio(weights, returns, risk_free_rate=0):
    """Calcula el negativo del Sharpe Ratio (para minimización)."""
    portfolio_return = np.sum(returns.mean() * weights)
    portfolio_vol = portfolio_volatility(weights, returns)
    return -(portfolio_return - risk_free_rate) / portfolio_vol

def optimize_portfolio(returns, risk_level, max_weight):
    """Optimiza el portafolio para minimizar la volatilidad dado un nivel de riesgo máximo."""
    num_assets = len(returns.columns)
    args = (returns,)
    constraints = ({'type': 'ineq', 'fun': lambda weights: risk_level - portfolio_volatility(weights, returns)}, # Restricción de riesgo
                   {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}) # La suma de los pesos debe ser 1
    bounds = tuple((0, max_weight) for _ in range(num_assets)) # Pesos máximos por activo
    initial_weights = np.array([1/num_assets] * num_assets)

    # Minimizar el negativo del Sharpe Ratio (proxy para eficiencia riesgo-retorno)
    optimized_results = minimize(neg_sharpe_ratio, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints, args=args)

    if optimized_results.success:
        optimal_weights = optimized_results.x
        optimal_portfolio = dict(zip(returns.columns, optimal_weights))
        return optimal_portfolio
    else:
        return {"error": "No se encontró una solución óptima bajo las restricciones dadas."}

@app.route('/optimize-portfolio', methods=['POST'])
def optimize_portfolio_endpoint():
    """Endpoint para optimizar el portafolio."""
    if 'file' not in request.files:
        return jsonify({"error": "No se proporcionó el archivo CSV."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío."}), 400
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "El archivo debe ser un CSV."}), 400

    try:
        csv_data = StringIO(file.stream.read().decode("utf-8"))
        returns_df = pd.read_csv(csv_data, index_col=0) # La primera columna es la fecha
        returns_df = returns_df.dropna() # Eliminar filas con valores NaN

        try:
            risk_level = float(request.form.get('risk_level'))
            max_weight = float(request.form.get('max_weight'))
            if not (0 <= risk_level) or not (0 < max_weight <= 1):
                return jsonify({"error": "Los valores de risk_level y max_weight no son válidos."}), 400
        except (ValueError, KeyError):
            return jsonify({"error": "Parámetros risk_level y/o max_weight no proporcionados o inválidos."}), 400

        optimal_portfolio = optimize_portfolio(returns_df, risk_level, max_weight)
        return jsonify({"optimal_portfolio": optimal_portfolio})

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo o realizar la optimización: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)