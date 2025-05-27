from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from shared.models.common import ProblemDetails # Importa el modelo ProblemDetails desde su nueva ubicación

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Captura HTTPExceptions y las formatea como ProblemDetails (RFC 7807).
    """
    problem_details = ProblemDetails(
        type=f"/errors/{exc.status_code}",
        title=exc.detail if exc.status_code < 500 else "Internal Server Error",
        status=exc.status_code,
        detail=exc.detail
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_details.model_dump(exclude_none=True)
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Captura RequestValidationErrors (de Pydantic) y las formatea como ProblemDetails (RFC 7807).
    """
    problem_details = ProblemDetails(
        type="/errors/validation",
        title="Validation Error",
        status=422,
        detail="One or more validation errors occurred.",
        errors=exc.errors() # Incluye los errores detallados de Pydantic
    )
    return JSONResponse(
        status_code=422,
        content=problem_details.model_dump(exclude_none=True)
    )

def register_error_handlers(app):
    """
    Función para registrar los manejadores de excepciones en la aplicación FastAPI.
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
