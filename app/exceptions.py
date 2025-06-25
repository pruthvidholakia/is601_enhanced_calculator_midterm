# app/exceptions.py

class CalculatorError(Exception):
    """Base exception for calculator errors."""
    pass

class ValidationError(CalculatorError):
    """Raised when input validation fails."""
    pass

class OperationError(CalculatorError):
    """Raised when an unknown or invalid operation is requested."""
    pass
