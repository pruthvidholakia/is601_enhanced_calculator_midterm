# app/exceptions.py
class CalculatorError(Exception):
    """Base exception for any calculator failure."""

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message            # keeps mypy / IDE happy

    def __str__(self) -> str:             # nice display in REPL / logs
        return self.message or self.__class__.__name__


class ValidationError(CalculatorError):
    """Raised when input validation fails."""


class OperationError(CalculatorError):
    """Raised when an unknown or invalid operation is requested."""
