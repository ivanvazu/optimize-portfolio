# Servicio de Optimización de Portafolios (Modelo de Markowitz)

Este servicio en Python, construido con FastAPI, permite a los usuarios estimar la composición óptima de un portafolio de activos financieros basándose en sus retornos históricos diarios y ciertas restricciones de riesgo.

## Funcionalidad

El servicio expone un único endpoint a través de una API REST:

* **Método HTTP:** `POST`
* **Endpoint:** `/optimize-portfolio`

Al enviar una solicitud `POST` a este endpoint, proporcionando un archivo CSV con los retornos de los activos y los parámetros de riesgo deseados, el servicio calcula y devuelve la asignación de pesos óptima para cada activo en formato JSON.

**Parámetros de Entrada:**

La solicitud `POST` espera los siguientes parámetros en formato `multipart/form-data`:

* `file`: Un archivo CSV que contiene los retornos diarios de los activos. El formato del archivo debe ser:
    * La primera fila (header) contiene los tickers de los activos.
    * La primera columna contiene las fechas.
    * Las celdas restantes contienen los retornos diarios para cada activo en la fecha correspondiente.
    * Ejemplo:
        ```csv
        Date,AAPL,MSFT,GOOG
        2023-01-02,0.01,0.005,0.008
        2023-01-03,-0.005,-0.002,0.001
        ...
        ```
* `risk_level` (float): El nivel máximo de riesgo total que el inversor está dispuesto a aceptar para el portafolio. La métrica de riesgo utilizada en este modelo es la **volatilidad anualizada** del portafolio (desviación estándar de los retornos).
* `max_weight` (float): El peso máximo que se puede asignar a cualquier activo individual en el portafolio. Este valor debe estar entre 0 y 1 (ej. 0.15 significa un máximo del 15% de inversión en un solo activo).

**Respuesta Esperada (Formato JSON):**

```json
{
  "optimal_portfolio": {
    "ticker_1": weight_1,
    "ticker_2": weight_2,
    "...": "..."
  }
}
```

## Método de Optimización

Se utilizó el modelo de optimización de portafolios de **Markowitz**, centrándonos en la **minimización de la volatilidad (riesgo)** del portafolio.

**¿Por qué se eligió?** Para principiantes, la volatilidad es una medida de riesgo intuitiva. El modelo de Markowitz es un concepto fundamental y ampliamente estudiado, que además favorece la diversificación, un principio clave para gestionar el riesgo. Es un excelente punto de partida para entender la optimización de portafolios.

