from decimal import Decimal
from app.calculator_config import CONFIG
from app.operations import get_operation
from app.exceptions import CalculatorError, OperationError, ValidationError
import sys

history = []
undone = []

def _fmt(val: Decimal) -> str:
    # Show as integer if whole, else round to 3 decimals
    return str(val.quantize(Decimal("1"))) if val == val.to_integral() else str(val.quantize(Decimal("0.001")))

def print_menu():
    print("\nAvailable commands:")
    print("  add, subtract, multiply, divide, power, root - Perform calculations")
    print("  history - Show calculation history")
    print("  clear - Clear calculation history")
    print("  undo - Undo the last calculation")
    print("  redo - Redo the last undone calculation")
    print("  save - Save calculation history to file")
    print("  load - Load calculation history from file")
    print("  exit - Exit the calculator\n")

def input_number(prompt):
    while True:
        user_input = input(prompt)
        if user_input.lower() == "cancel":
            return None
        try:
            num = Decimal(user_input)
            if abs(num) > CONFIG.max_input_value:
                print(f"Input exceeds allowed limit ({CONFIG.max_input_value})")
            else:
                return num
        except:
            print("Please enter a valid number or type 'cancel' to abort.")

def perform_operation(op_name):
    print("\nEnter numbers (or 'cancel' to abort):")
    a = input_number("First number: ")
    if a is None:
        print("Operation canceled.")
        return
    b = input_number("Second number: ")
    if b is None:
        print("Operation canceled.")
        return

    try:
        op = get_operation(op_name)
        result = op.apply(a, b)
        print(f"\nResult: {_fmt(result)}")
        history.append((op_name, a, b, result))
        undone.clear()
    except CalculatorError as e:
        print(f"Error: {e}")

def show_history():
    if not history:
        print("No history available.")
    else:
        for i, (op, a, b, res) in enumerate(history, 1):
            print(f"[{i}] {op}({a}, {b}) = {_fmt(res)}")

def undo():
    if history:
        undone.append(history.pop())
        print("Last operation undone.")
    else:
        print("Nothing to undo.")

def redo():
    if undone:
        history.append(undone.pop())
        print("Redo successful.")
    else:
        print("Nothing to redo.")

def main():
    print("Welcome to the Enhanced Calculator!")
    print_menu()

    while True:
        command = input("Enter command: ").strip().lower()

        if command in {"add", "subtract", "multiply", "divide", "power", "root"}:
            perform_operation(command)
        elif command == "history":
            show_history()
        elif command == "clear":
            history.clear()
            undone.clear()
            print("History cleared.")
        elif command == "undo":
            undo()
        elif command == "redo":
            redo()
        elif command == "save":
            print("Saving history to file is not yet implemented.")  # Placeholder
        elif command == "load":
            print("Loading history from file is not yet implemented.")  # Placeholder
        elif command == "exit":
            print("Goodbye!")
            break
        else:
            print("Unknown command. Type from the listed options.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
