from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP, getcontext
from datetime import datetime
from pathlib import Path
from typing import List, Protocol

from app.operations import get_operation
from app.calculator_config import CONFIG
from app.calculator_memento import (
    CalculatorMemento,
    CalculatorCaretaker,
    HistoryItem,
)

# --------------------------------------------------  Global precision
getcontext().prec = max(CONFIG.precision + 2, 28)

# --------------------------------------------------  Observer infra
class Observer(Protocol):
    def update(self, calculator: "Calculator", item: HistoryItem) -> None: ...


class LoggingObserver:
    """Write each calculation to a log file (one handler per path)."""

    def __init__(self, log_file: Path | str | None = None) -> None:
        log_path = Path(log_file or CONFIG.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger("calculator")
        self._logger.setLevel(logging.INFO)

        existing = {getattr(h, "baseFilename", None) for h in self._logger.handlers}
        if str(log_path) not in existing:
            handler = logging.FileHandler(log_path, encoding=CONFIG.default_encoding, delay=True)
            handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
            self._logger.addHandler(handler)

    def update(self, _calc: "Calculator", item: HistoryItem) -> None:
        op, a, b, res, _ts = item
        self._logger.info("%s(%s, %s) = %s", op, a, b, res)


class AutoSaveObserver:
    """Save history to CSV after every calculation."""

    def __init__(self, csv_file: Path | str | None = None) -> None:
        self._csv = Path(csv_file or CONFIG.history_file)
        self._csv.parent.mkdir(parents=True, exist_ok=True)

    def update(self, calc: "Calculator", _item: HistoryItem) -> None:
        calc.save_history(self._csv)

# --------------------------------------------------  Core calculator
class Calculator:
    """Factory-based operations, Memento undo/redo, Observer hooks."""

    def __init__(self) -> None:
        self._history: List[HistoryItem] = []
        self._caretaker = CalculatorCaretaker()
        self._observers: list[Observer] = []
        self.add_observer(LoggingObserver())
        if CONFIG.auto_save:
            self.add_observer(AutoSaveObserver())

    # ---------- helpers
    def _snapshot(self) -> CalculatorMemento:  # for undo
        return CalculatorMemento(tuple(self._history))

    def _restore(self, m: CalculatorMemento) -> None:  # for redo
        self._history = list(m.get_state())

    @staticmethod
    def _round(val: Decimal) -> Decimal:
        q = Decimal(10) ** -CONFIG.precision
        return val.quantize(q, rounding=ROUND_HALF_UP)

    @staticmethod
    def _display(val: Decimal) -> str:
        q = Decimal("1") if val == val.to_integral() else Decimal(10) ** -CONFIG.precision
        return str(val.quantize(q, rounding=ROUND_HALF_UP))

    # ---------- observer API
    def add_observer(self, obs: Observer) -> None:
        if obs not in self._observers:
            self._observers.append(obs)

    def remove_observer(self, obs: Observer) -> None:
        if obs in self._observers: # pragma: no cover
            self._observers.remove(obs) 

    def _notify(self, item: HistoryItem) -> None:
        for obs in tuple(self._observers):
            try:
                obs.update(self, item)
            except Exception: # pragma: no cover
                logging.exception("Observer %s failed", obs) 

    # ---------- public API
    def calculate(self, op_name: str, a: Decimal, b: Decimal) -> Decimal:
        res = self._round(get_operation(op_name).apply(a, b))
        self._caretaker.push_undo(self._snapshot())
        item: HistoryItem = (op_name, a, b, res, datetime.now())
        self._history.append(item)
        if len(self._history) > CONFIG.max_history_size:
            self._history.pop(0) # pragma: no cover
        self._notify(item)
        return res

    @property
    def history(self) -> List[HistoryItem]:
        return list(self._history)

    # ---------- persistence
    def save_history(self, path: Path | str | None = None) -> None:
        import pandas as pd
        rows = [
            {"operation": op, "a": self._display(a), "b": self._display(b),
             "result": self._display(res), "timestamp": ts}
            for op, a, b, res, ts in self._history
        ]
        pd.DataFrame(rows).to_csv(Path(path or CONFIG.history_file), index=False,
                                  encoding=CONFIG.default_encoding)

    def load_history(self, path: Path | str | None = None) -> None:
        import pandas as pd
        target = Path(path or CONFIG.history_file)
        if not target.exists():
            return # pragma: no cover
        df = pd.read_csv(target, parse_dates=["timestamp"])
        self._history = [
            (row.operation,
             Decimal(str(row.a)),
             Decimal(str(row.b)),
             Decimal(str(row.result)),
             row.timestamp.to_pydatetime())
            for row in df.itertuples()
        ]

    # ---------- clear / undo / redo
    def clear(self) -> None:
        if self._history:
            self._caretaker.push_undo(self._snapshot())
        self._history.clear()  # no observer notify (avoids CSV overwrite)

    def undo(self) -> bool:
        m = self._caretaker.pop_undo()
        if not m:
            return False # pragma: no cover
        self._caretaker.push_redo(self._snapshot())
        self._restore(m)
        return True

    def redo(self) -> bool:
        m = self._caretaker.pop_redo()
        if not m:
            return False
        # push current state onto undo *without* destroying remaining redos
        self._caretaker.push_undo_preserve_redo(self._snapshot())
        self._restore(m)
        return True
