from __future__ import annotations

import sys
from decimal import Decimal

from app.calculator import Calculator
from app.calculator_config import CONFIG
from app.exceptions import CalculatorError

# ────────────────────────── Helpers ──────────────────────────
def _fmt(val: Decimal) -> str:
    """
    Format a Decimal for display:
      • show as an int if it has no fractional part
      • otherwise respect CALCULATOR_PRECISION (default 4)
    """
    scale = Decimal(f"1.{'0' * CONFIG.precision}")
    q = Decimal("1") if val == val.to_integral() else scale
    return str(val.quantize(q))


def print_menu() -> None:
    print(
        """
Available commands
──────────────────
  add, subtract, multiply, divide,
  power, root, modulus, int_divide,
  percent, abs_diff        → perform calculation
  history                  → display history
  clear                    → clear history
  undo / redo              → undo or redo last change
  save / load              → manual save or load of history
  help                     → show this menu
  exit                     → quit the calculator
"""
    )


def input_number(prompt: str) -> Decimal | None:
    """
    Ask the user for a numeric value (Decimal).
    Type 'cancel' to abort the current operation.
    """
    while True:
        raw = input(prompt).strip().lower()
        if raw == "cancel":
            return None
        try:
            return Decimal(raw)
        except Exception:
            print("Please enter a valid number or 'cancel'.")


# ────────────────────── Core REPL utilities ──────────────────────
calc = Calculator()  # one shared instance for the session


def perform_operation(op_name: str) -> None:
    print("\nEnter numbers (or type 'cancel' to abort):")
    a = input_number("  first  : ")
    if a is None:
        print("Operation cancelled.")
        return
    b = input_number("  second : ")
    if b is None:
        print("Operation cancelled.")
        return

    try:
        result = calc.calculate(op_name, a, b)
        print(f"\n Result → {_fmt(result)}\n")
    except CalculatorError as exc:
        print(f"Error: {exc}")


def show_history() -> None:
    if not calc.history:
        print("No history yet.")
        return

    for idx, (op, a, b, res, ts) in enumerate(calc.history, 1):
        print(f"[{idx:>3}] {ts:%H:%M:%S}  {op}({a}, {b}) = {_fmt(res)}")


# ─────────────────────────── Main loop ───────────────────────────
def main() -> None:
    print("Welcome to the Enhanced Calculator!")
    print_menu()

    valid_ops: set[str] = {
        "add",
        "subtract",
        "multiply",
        "divide",
        "power",
        "root",
        "modulus",
        "int_divide",
        "percent",
        "abs_diff",
    }

    while True:
        command = input("» ").strip().lower()

        #  calculation commands
        if command in valid_ops:
            perform_operation(command)

        # history management
        elif command == "history":
            show_history()
        elif command == "clear":
            calc.clear()
            print("History cleared.")

        # undo / redo
        elif command == "undo":
            print("Undone." if calc.undo() else "Nothing to undo.")
        elif command == "redo":
            print("Redone." if calc.redo() else "Nothing to redo.")

        # manual save / load
        elif command == "save":
            calc.save_history()
            print(f"History saved")
        elif command == "load":
            calc.load_history()
            print("History loaded.")

        # misc
        elif command in {"help", "menu", "h", "?"}:
            print_menu()
        elif command in {"exit", "quit"}:
            print("Goodbye!")
            break
        else:
            print("Unknown command. Type 'help' for a list of commands.")


# ────────────────────────── Entrypoint ──────────────────────────
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Exiting…")
        sys.exit(0)
