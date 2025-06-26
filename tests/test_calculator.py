import pytest
from decimal import Decimal
from app.calculator import Calculator


def test_calculate_and_history():
    c = Calculator()
    result = c.calculate("add", Decimal(2), Decimal(3))
    assert result == Decimal("5")
    assert len(c.history) == 1
    assert c.history[0][0] == "add"

def test_undo_redo():
    c = Calculator()
    c.calculate("multiply", Decimal(3), Decimal(2))  # 6
    assert len(c.history) == 1
    assert c.undo() is True
    assert len(c.history) == 0
    assert c.redo() is True
    assert len(c.history) == 1

def test_clear_and_restore():
    c = Calculator()
    c.calculate("subtract", Decimal(10), Decimal(3))
    c.clear()
    assert c.history == []
    c.undo()
    assert len(c.history) == 1
    assert c.history[0][0] == "subtract"

def test_logging_and_autosave(tmp_path):
    calc = Calculator()

    # Override config paths
    CONFIG.log_file = tmp_path / "logfile.log"
    CONFIG.history_file = tmp_path / "history.csv"

    # Calculate something
    result = calc.calculate("mul", Decimal("2"), Decimal("3"))
    assert result == Decimal("6.00")

    # Check files
    assert CONFIG.log_file.exists(), "Log file missing"
    assert CONFIG.history_file.exists(), "History file missing"