from fastapi import UploadFile, File, HTTPException
import pandas as pd
from typing import Annotated

from shared.utils.result import Result # Importar Result desde el nuevo location
from shared.utils.csv_parser import validate_and_parse_csv # Importar la función desde el nuevo location

async def get_validated_returns_df_dependency(
    file: UploadFile = File(..., description="Archivo CSV con los retornos diarios/mensuales de los activos.")
) -> pd.DataFrame:
    """
    Dependencia de FastAPI que utiliza la función de validación de CSV basada en Result.
    Si la validación falla, lanza una HTTPException formateada según RFC 7807.
    """
    file_content = await file.read()
    
    validation_result: Result[pd.DataFrame, str] = await validate_and_parse_csv(file_content, file.filename)
    
    if validation_result.is_ok():
        return validation_result.unwrap()
    else:
        raise HTTPException(
            status_code=400, 
            detail=validation_result.unwrap_err()
        )
