# tests/test_operations.py

from decimal import Decimal
import pytest

from app.operations import get_operation
from app.exceptions import ValidationError, OperationError


@pytest.mark.parametrize(
    "name,a,b,expected",
    [
        # basic
        ("add", 10, 5, Decimal(15)),
        ("subtract", 10, 5, Decimal(5)),
        ("multiply", 6, 7, Decimal(42)),
        ("divide", 10, 4, Decimal(2.5)),
        ("power", 2, 3, Decimal(8)),
        ("root", 16, 2, Decimal(4)),
        ("modulus", 10, 3, Decimal(1)),
        ("int_divide", 10, 3, Decimal(3)),
        ("percent", 50, 200, Decimal(25)),
        ("abs_diff", 10, 4, Decimal(6)),
    ],
)
def test_operations(name, a, b, expected):
    op = get_operation(name)
    assert op.apply(a, b) == expected


def test_unknown_operation():
    with pytest.raises(OperationError):
        get_operation("not_a_real_op")


def test_divide_by_zero():
    op = get_operation("divide")
    with pytest.raises(ValidationError):
        op.apply(5, 0)


def test_int_divide_by_zero():
    op = get_operation("int_divide")
    with pytest.raises(ValidationError):
        op.apply(5, 0)


def test_root_degree_zero():
    op = get_operation("root")
    with pytest.raises(ValidationError):
        op.apply(9, 0)


def test_non_numeric_input():
    op = get_operation("add")
    with pytest.raises(ValidationError):
        op.apply("hello", 3)
