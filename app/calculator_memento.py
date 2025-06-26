from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
from decimal import Decimal
from datetime import datetime


HistoryItem = Tuple[str, Decimal, Decimal, Decimal, datetime]
#  (operation, a, b, result, timestamp)


@dataclass(frozen=True, slots=True)
class CalculatorMemento:
    """Immutable snapshot of the calculator’s history state."""
    _history: Tuple[HistoryItem, ...]

    def get_state(self) -> Tuple[HistoryItem, ...]:
        return self._history


class CalculatorCaretaker:
    """
    Stores undo / redo stacks of mementos.
    Each stack holds *snapshots*, not live objects, so state can be restored safely.
    """

    def __init__(self) -> None:
        self._undo: list[CalculatorMemento] = []
        self._redo: list[CalculatorMemento] = []

    # --- push helpers -------------------------------------------------
    def push_undo(self, m: CalculatorMemento) -> None:
        self._undo.append(m)
        self._redo.clear()          # new action invalidates redo history

    def push_redo(self, m: CalculatorMemento) -> None:
        self._redo.append(m)

    # --- pop helpers --------------------------------------------------
    def pop_undo(self) -> CalculatorMemento | None:
        return self._undo.pop() if self._undo else None

    def pop_redo(self) -> CalculatorMemento | None:
        return self._redo.pop() if self._redo else None

    # --- public inspection (optional) --------------------------------
    def can_undo(self) -> bool: return bool(self._undo)
    def can_redo(self) -> bool: return bool(self._redo)
