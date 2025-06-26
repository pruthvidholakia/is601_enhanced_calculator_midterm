from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP, getcontext
from datetime import datetime
from pathlib import Path
from typing import List, Protocol

from app.operations import get_operation
from app.calculator_config import CONFIG
from app.exceptions import CalculatorError
from app.calculator_memento import (
    CalculatorMemento,
    CalculatorCaretaker,
    HistoryItem,
)

# ---------------------------------------------------------------------------
# 1.  Global numeric precision
# ---------------------------------------------------------------------------
getcontext().prec = max(CONFIG.precision + 2, 28)

# ---------------------------------------------------------------------------
# 2.  --- Observer infrastructure ---
# ---------------------------------------------------------------------------
class Observer(Protocol):
    """Simple Observer interface."""

    def update(self, calculator: "Calculator", item: HistoryItem) -> None: ...


class LoggingObserver:
    """
    Logs every new calculation in human-readable form.

    Log destination/path is taken from CONFIG.log_file by default but can be
    overridden when the observer is instantiated.
    """

    def __init__(self, log_file: Path | str | None = None) -> None:
        log_path = Path(log_file or CONFIG.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger("calculator")
        if not self._logger.handlers:  # configure once
            self._logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path, encoding=CONFIG.default_encoding)
            handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
            self._logger.addHandler(handler)

    # ------------------------------------------------------------------ #
    def update(self, _calculator: "Calculator", item: HistoryItem) -> None:
        op, a, b, res, _ts = item
        self._logger.info("%s(%s, %s) = %s", op, a, b, res)


class AutoSaveObserver:
    """
    Dumps the entire calculation history to CSV every time a new
    calculation is recorded.
    """

    def __init__(self, csv_file: Path | str | None = None) -> None:
        self._csv_file = Path(csv_file or CONFIG.history_file)
        self._csv_file.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    def update(self, calculator: "Calculator", _item: HistoryItem) -> None:
        calculator.save_history(self._csv_file)


# ---------------------------------------------------------------------------
# 3.  --- Core Calculator class with Observer + Memento support ---
# ---------------------------------------------------------------------------
class Calculator:
    """
    Core calculator with:
      • Memento-based undo/redo
      • Observer notifications (logging + auto-save)
    """

    # ---------------- constructor & helpers ----------------
    def __init__(self) -> None:
        self._history: List[HistoryItem] = []
        self._caretaker = CalculatorCaretaker()
        self._observers: list[Observer] = []

        # Register default observers on creation
        self.add_observer(LoggingObserver())
        if CONFIG.auto_save:
            self.add_observer(AutoSaveObserver())

    def _snapshot(self) -> CalculatorMemento:
        # Immutable copy so later mutations don’t change saved state
        return CalculatorMemento(tuple(self._history))

    def _restore(self, memento: CalculatorMemento) -> None:
        self._history = list(memento.get_state())

    @staticmethod
    def _round(val: Decimal) -> Decimal:
        q = Decimal(10) ** -CONFIG.precision
        return val.quantize(q, rounding=ROUND_HALF_UP)
    
    @staticmethod
    def _round(val: Decimal) -> Decimal:
        q = Decimal(10) ** -CONFIG.precision
        return val.quantize(q, rounding=ROUND_HALF_UP)

    # clean string for CSV so it looks like the REPL output
    @staticmethod
    def _display(val: Decimal) -> str:
        q = Decimal("1") if val == val.to_integral() else Decimal(10) ** -CONFIG.precision
        return str(val.quantize(q, rounding=ROUND_HALF_UP))

    # ---------------- observer API -------------------------
    def add_observer(self, obs: Observer) -> None:
        if obs not in self._observers:
            self._observers.append(obs)

    def remove_observer(self, obs: Observer) -> None:
        try:
            self._observers.remove(obs)
        except ValueError:
            pass  # silent if not registered

    def _notify(self, item: HistoryItem) -> None:
        for obs in list(self._observers):  # iterate on copy in case observers mutate list
            try:
                obs.update(self, item)
            except Exception:  # never break core flow because of an observer
                logging.exception("Observer %s raised an error", obs)

    # ---------------- public calculator API ----------------
    def calculate(self, op_name: str, a: Decimal, b: Decimal) -> Decimal:
        op = get_operation(op_name)
        result = self._round(op.apply(a, b))

        # Store undo snapshot *before* mutating history
        self._caretaker.push_undo(self._snapshot())

        item: HistoryItem = (op_name, a, b, result, datetime.now())
        self._history.append(item)

        # Trim history if oversized
        if len(self._history) > CONFIG.max_history_size:
            self._history.pop(0)

        # Notify observers
        self._notify(item)
        return result

    # --- history views
    @property
    def history(self) -> List[HistoryItem]:
        return list(self._history)  # copy for read-only access

    # --- persistence helpers (used by AutoSaveObserver & CLI)
    def save_history(self, path: Path | str | None = None) -> None:
        """
        Persist history to CSV using pandas, formatting numbers
        without unnecessary trailing zeros.
        """
        import pandas as pd

        target = Path(path or CONFIG.history_file)

        rows = [
            {
                "operation": op,
                "a": self._display(a),
                "b": self._display(b),
                "result": self._display(res),
                "timestamp": ts,
            }
            for op, a, b, res, ts in self._history
        ]

        df = pd.DataFrame(rows, columns=["operation", "a", "b", "result", "timestamp"])
        df.to_csv(target, index=False, encoding=CONFIG.default_encoding)


    def load_history(self, path: Path | str | None = None) -> None:
        """Load history from a CSV file created by `save_history`."""
        import pandas as pd

        target = Path(path or CONFIG.history_file)
        if not target.exists():
            return

        df = pd.read_csv(target, parse_dates=["timestamp"])
        # Convert numeric columns back to Decimal for full precision
        self._history = [
            (
                row["operation"],
                Decimal(str(row["a"])),
                Decimal(str(row["b"])),
                Decimal(str(row["result"])),
                row["timestamp"].to_pydatetime(),
            )
            for _, row in df.iterrows()
        ]

    # --- clear / undo / redo
    def clear(self) -> None:
        if self._history:
            self._caretaker.push_undo(self._snapshot())
        self._history.clear()

    def undo(self) -> bool:
        m = self._caretaker.pop_undo()
        if m is None:
            return False
        self._caretaker.push_redo(self._snapshot())
        self._restore(m)
        # No notify: external state didn’t change (optional)
        return True

    def redo(self) -> bool:
        m = self._caretaker.pop_redo()
        if m is None:
            return False
        self._caretaker.push_undo(self._snapshot())
        self._restore(m)
        # No notify: external state didn’t change (optional)
        return True
