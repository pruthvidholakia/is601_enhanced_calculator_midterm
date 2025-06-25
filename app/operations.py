
from decimal import Decimal
from app.exceptions import ValidationError, OperationError


# ──────────────────────────── Base Class ────────────────────────────
class Operation:
    """Abstract base class – every concrete operation implements `apply`."""

    def apply(self, a: Decimal, b: Decimal | None = None) -> Decimal:  # pragma: no cover
        raise NotImplementedError("Each operation must override `apply`")

    # shared numeric validator
    @staticmethod
    def _num(val):
        if not isinstance(val, (int, float, Decimal)):
            raise ValidationError(f"Value {val!r} is not numeric")
        return Decimal(val)


# ───────────────────────── Concrete Operations ──────────────────────
class Add(Operation):
    def apply(self, a, b):  # type: ignore[override]
        return self._num(a) + self._num(b)


class Subtract(Operation):
    def apply(self, a, b):  # type: ignore[override]
        return self._num(a) - self._num(b)


class Multiply(Operation):
    def apply(self, a, b):  # type: ignore[override]
        return self._num(a) * self._num(b)


class Divide(Operation):
    def apply(self, a, b):  # type: ignore[override]
        divisor = self._num(b)
        if divisor == 0:
            raise ValidationError("Division by zero is not allowed")
        return self._num(a) / divisor


class Power(Operation):
    def apply(self, a, b):  # type: ignore[override]
        return self._num(a) ** self._num(b)


class Root(Operation):
    def apply(self, a, b):  # type: ignore[override]
        degree = self._num(b)
        if degree == 0:
            raise ValidationError("Root degree cannot be zero")
        return self._num(a) ** (Decimal(1) / degree)


class Modulus(Operation):
    def apply(self, a, b):  # type: ignore[override]
        return self._num(a) % self._num(b)


class IntDivide(Operation):
    def apply(self, a, b):  # type: ignore[override]
        divisor = self._num(b)
        if divisor == 0:
            raise ValidationError("Division by zero is not allowed")
        return self._num(a) // divisor


class Percent(Operation):
    def apply(self, a, b):  # type: ignore[override]
        return (self._num(a) / self._num(b)) * 100


class AbsDiff(Operation):
    def apply(self, a, b):  # type: ignore[override]
        return abs(self._num(a) - self._num(b))


# ───────────────────────────── Factory ──────────────────────────────
_OPERATION_MAP: dict[str, type[Operation]] = {
    "add": Add,
    "subtract": Subtract,
    "multiply": Multiply,
    "divide": Divide,
    "power": Power,
    "root": Root,
    "modulus": Modulus,
    "int_divide": IntDivide,
    "percent": Percent,
    "abs_diff": AbsDiff,
}


def get_operation(name: str) -> Operation:
    """
    Return an `Operation` instance for *name*.

    Raises
    ------
    OperationError
        If *name* is not registered in `_OPERATION_MAP`.
    """
    cls = _OPERATION_MAP.get(name.lower())
    if cls is None:
        raise OperationError(
            f"Unknown operation '{name}'. "
            f"Available: {', '.join(sorted(_OPERATION_MAP))}"
        )
    return cls()
