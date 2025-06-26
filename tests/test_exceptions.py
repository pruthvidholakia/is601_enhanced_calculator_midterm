from app.exceptions import CalculatorError, ValidationError, OperationError

def test_exception_str_and_message():
    err = ValidationError("bad input")
    assert str(err) == "bad input"
    assert isinstance(err, CalculatorError)
    err2 = OperationError()             # no message
    assert str(err2) == "OperationError"
