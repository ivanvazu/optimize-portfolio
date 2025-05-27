import pandas as pd
from io import StringIO
from typing import Any, Tuple

from shared.utils.result import Result, Ok, Err # Importar Result desde el nuevo location

async def validate_and_parse_csv(file_content: bytes, filename: str) -> Result[pd.DataFrame, str]:
    """
    Valida el contenido binario de un archivo CSV y lo parsea en un DataFrame de pandas.
    Retorna un Ok(DataFrame) si es exitoso, o un Err(mensaje de error) si falla.
    """
    
    if not filename:
        return Err("Nombre de archivo vacío. Por favor, suba un archivo.")
        
    if not filename.endswith('.csv'):
        return Err(f"Tipo de archivo no soportado. Se esperaba '.csv', pero se recibió '{filename.split('.')[-1]}'.")

    try:
        csv_data = StringIO(file_content.decode("utf-8"))
        returns_df = pd.read_csv(csv_data, index_col=0) 
        
        if returns_df.empty:
            return Err("El archivo CSV está vacío o no contiene datos válidos después de la lectura.")
        
        if not all(pd.api.types.is_numeric_dtype(returns_df[col]) for col in returns_df.columns):
            non_numeric_cols = [col for col in returns_df.columns if not pd.api.types.is_numeric_dtype(returns_df[col])]
            return Err(f"Todas las columnas de retornos en el CSV deben ser numéricas. "
                       f"Columnas no numéricas encontradas: {', '.join(non_numeric_cols)}.")
            
        initial_rows = len(returns_df)
        returns_df = returns_df.dropna()
        if len(returns_df) < initial_rows:
            print(f"Advertencia: Se eliminaron {initial_rows - len(returns_df)} filas debido a valores faltantes.")
        
        if returns_df.empty:
            return Err("El archivo CSV no contiene datos numéricos válidos después de procesar valores faltantes.")
        
        return Ok(returns_df)
        
    except pd.errors.EmptyDataError:
        return Err("El archivo CSV está vacío o solo contiene encabezados.")
    except pd.errors.ParserError:
        return Err("Error al parsear el archivo CSV. Verifique que el formato sea correcto (ej. delimitadores, comillas).")
    except UnicodeDecodeError:
        return Err("Error de codificación del archivo. Asegúrese de que el CSV esté codificado en UTF-8.")
    except Exception as e:
        return Err(f"Error inesperado al procesar el archivo CSV: {str(e)}")
    