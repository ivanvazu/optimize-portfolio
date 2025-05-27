from typing import TypeVar, Generic, Union, Any

S = TypeVar('S') # Success type
E = TypeVar('E') # Error type

class Result(Generic[S, E]):
    """
    Un tipo de dato que representa un resultado que puede ser éxito (Ok) o error (Err).
    Modelado a partir de los tipos Result en Rust o Either en otros lenguajes funcionales.
    """
    def __init__(self, value: Union[S, E], is_ok: bool):
        self._value = value
        self._is_ok = is_ok

    def is_ok(self) -> bool:
        return self._is_ok

    def is_err(self) -> bool:
        return not self._is_ok

    def ok(self) -> Union[S, None]:
        return self._value if self._is_ok else None

    def err(self) -> Union[E, None]:
        return self._value if not self._is_ok else None

    def unwrap(self) -> S:
        if self._is_ok:
            return self._value
        raise RuntimeError(f"Tried to unwrap an Err value: {self._value}")

    def unwrap_err(self) -> E:
        if not self._is_ok:
            return self._value
        raise RuntimeError(f"Tried to unwrap an Ok value: {self._value}")

    def __repr__(self) -> str:
        if self._is_ok:
            return f"Ok({self._value!r})"
        return f"Err({self._value!r})"

def Ok(value: S) -> Result[S, Any]:
    return Result(value, True)

def Err(error: E) -> Result[Any, E]:
    return Result(error, False)
