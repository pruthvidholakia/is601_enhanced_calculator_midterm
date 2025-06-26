"""
Comprehensive functional + edge-case tests for the Enhanced Calculator.
"""

from decimal import Decimal
from pathlib import Path
import logging
import pandas as pd
import pytest

from app.calculator import Calculator, Observer, LoggingObserver, AutoSaveObserver
from app.exceptions import ValidationError, OperationError


# ──────────────────────────────────────────────────────────────────────
# 1️⃣  Parametrized happy-path for every operation
# ──────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "op,a,b,expect",
    [
        ("add",        2, 3,   "5.0000"),
        ("subtract",   5, 3,   "2.0000"),
        ("multiply",   4, 6,   "24.0000"),
        ("divide",     8, 4,   "2.0000"),
        ("power",      2, 3,   "8.0000"),
        ("root",       27, 3,  "3.0000"),
        ("modulus",    10, 3,  "1.0000"),
        ("int_divide", 9, 2,   "4.0000"),
        ("percent",    25, 100,"25.0000"),
        ("abs_diff",   3, 10,  "7.0000"),
    ],
)
def test_all_operations(op, a, b, expect):
    calc = Calculator()
    res = calc.calculate(op, Decimal(a), Decimal(b))
    assert str(res) == expect
    assert len(calc.history) == 1
    assert calc.history[0][0] == op


# ──────────────────────────────────────────────────────────────────────
# 2️⃣  Error / edge-case conditions
# ──────────────────────────────────────────────────────────────────────
def test_division_by_zero():
    with pytest.raises(ValidationError):
        Calculator().calculate("divide", Decimal(5), Decimal(0))


def test_root_zero_degree():
    with pytest.raises(ValidationError):
        Calculator().calculate("root", Decimal(16), Decimal(0))


def test_unknown_operation():
    with pytest.raises(OperationError):
        Calculator().calculate("does_not_exist", Decimal(1), Decimal(1))


# ──────────────────────────────────────────────────────────────────────
# 3️⃣  Multi-step undo / redo
# ──────────────────────────────────────────────────────────────────────
def test_multi_step_undo_redo():
    c = Calculator()
    for n in range(5):
        c.calculate("add", Decimal(n), Decimal(1))

    assert len(c.history) == 5

    # Undo all five operations
    for _ in range(5):
        assert c.undo()
    assert c.history == []

    # Redo until the stack is exhausted
    redo_count = 0
    while c.redo():
        redo_count += 1

    assert redo_count == 5          # we restored every operation
    assert len(c.history) == 5
    assert c.history[0][0] == "add"


# ──────────────────────────────────────────────────────────────────────
# 4️⃣  Clear + undo restore
# ──────────────────────────────────────────────────────────────────────
def test_clear_and_restore():
    c = Calculator()
    c.calculate("subtract", Decimal(10), Decimal(3))
    c.clear()
    assert c.history == []
    c.undo()
    assert len(c.history) == 1
    assert c.history[0][0] == "subtract"


# ──────────────────────────────────────────────────────────────────────
# 5️⃣  Observer: custom log & CSV paths, plus load_history round-trip
# ──────────────────────────────────────────────────────────────────────
def test_logging_and_autosave(tmp_path: Path):
    log_file = tmp_path / "calc.log"
    csv_file = tmp_path / "history.csv"

    # ensure global logger starts clean
    logging.getLogger("calculator").handlers.clear()

    calc = Calculator()
    calc._observers.clear()  # remove defaults
    calc.add_observer(LoggingObserver(log_file))
    calc.add_observer(AutoSaveObserver(csv_file))

    res = calc.calculate("add", Decimal(2), Decimal(3))
    assert str(res) == "5.0000"

    # files created?
    assert log_file.exists()
    assert csv_file.exists()

    # CSV contents valid
    df = pd.read_csv(csv_file)
    assert len(df) == 1 and str(df.loc[0, "result"]) == "5"

    # load back into fresh calculator
    calc2 = Calculator()
    calc2._observers.clear()
    calc2.load_history(csv_file)
    assert len(calc2.history) == 1
    assert calc2.history[0][0] == "add"
    
def test_load_history_when_file_missing(tmp_path):
    calc = Calculator()
    csv_file = tmp_path / "does_not_exist.csv"
    # No exception should be raised
    calc.load_history(csv_file)
    assert calc.history == []           # still empty


def test_observer_exception_does_not_break_flow(monkeypatch):
    """Trigger the except branch inside _notify()."""

    class BadObserver(Observer):        # type: ignore[misc]
        def update(self, _c, _i):
            raise RuntimeError("boom")

    calc = Calculator()
    calc.add_observer(BadObserver())    # attach faulty observer

    # Must not raise, history still updated
    calc.calculate("add", Decimal(1), Decimal(1))
    assert len(calc.history) == 1
