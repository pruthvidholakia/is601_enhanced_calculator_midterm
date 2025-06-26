from __future__ import annotations

from decimal import Decimal
from operator import add, sub, mul, mod, floordiv, pow as _pow

from app.exceptions import ValidationError, OperationError


# ───────────────────────────── Base Class ─────────────────────────────
class Operation:
    """Abstract product for the Factory"""
    def apply(self, a: Decimal, b: Decimal | None = None) -> Decimal:  # pragma: no cover
        raise NotImplementedError


# ──────────────────────── Helper: runtime product ─────────────────────
class _BinaryOperation(Operation):
    """
    Wrap a simple 2-arg callable so we don’t need a separate
    subclass for every arithmetic operator.
    """

    __slots__ = ("_fn", "_name")

    def __init__(self, fn, name: str):
        self._fn = fn
        self._name = name

    @staticmethod
    def _num(x):
        if not isinstance(x, (int, float, Decimal)):
            raise ValidationError(f"Non-numeric input: {x!r}")
        return Decimal(x)

    def apply(self, a, b):  # type: ignore[override]
        return self._fn(self._num(a), self._num(b))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self._name}>"


# ─────────────────────────── Implementations ──────────────────────────
def _safe_div(a: Decimal, b: Decimal) -> Decimal:
    if b == 0:
        raise ValidationError("Division by zero")
    return a / b


def _safe_floor_div(a: Decimal, b: Decimal) -> Decimal:
    if b == 0:
        raise ValidationError("Division by zero")
    return a // b


def _root(a: Decimal, n: Decimal) -> Decimal:
    if n == 0:
        raise ValidationError("Root degree cannot be zero")
    return a ** (Decimal(1) / n)


def _percent(a: Decimal, b: Decimal) -> Decimal:
    return (a / b) * 100


def _abs_diff(a: Decimal, b: Decimal) -> Decimal:
    return abs(a - b)


# ───────────────────────────── Operation Map ──────────────────────────
_OP_FUNCS: dict[str, callable] = {
    "add": add,
    "subtract": sub,
    "multiply": mul,
    "divide": _safe_div,
    "power": _pow,
    "root": _root,
    "modulus": mod,
    "int_divide": _safe_floor_div,
    "percent": _percent,
    "abs_diff": _abs_diff,
}


# ───────────────────────────── Factory ────────────────────────────────
def get_operation(name: str) -> Operation:
    try:
        return _BinaryOperation(_OP_FUNCS[name.lower()], name)
    except KeyError:
        raise OperationError(f"Unknown operation '{name}'")
