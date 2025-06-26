# Advanced Python Calculator – Midterm Project

## Overview

This project is an advanced calculator application developed in Python. It supports various mathematical operations and includes features such as command history management, dynamic plugin architecture, and data analysis capabilities using the Pandas library. The application provides a user-friendly REPL (Read-Eval-Print Loop) interface for interactive calculations.

## Features
Basic Operations: Perform addition, subtraction, multiplication, and division.
Statistical Functions: Calculate mean, median, and standard deviation.
History Management: Track and display the history of executed commands.
Dynamic Plugins: Utilize an extensible architecture for adding new commands seamlessly.
Data Handling: Leverage the Pandas library for effective command history management and analysis.
Comprehensive Testing: Implement unit tests to ensure functionality and reliability.

---

## Features

-  **Basic Operations**: add, subtract, multiply, divide  
-  **Advanced Operations**: power, root, modulus, int divide, percent, abs diff  
-  **Undo/Redo Functionality** using Memento pattern  
-  **Auto-Save** to CSV using pandas  
-  **Real-time Logging** to log file  
-  **Environment-based configuration** via `.env`  
-  **Command-line Interface (REPL)**  
-  **CI/CD pipeline** with test coverage enforcement  
-  **Custom error handling** and input validation  

---


## 🔧 Installation

1. **Clone the repository**

    ```bash
    git clone https://github.com/your-username/is601_enhanced_calculator_midterm.git
    cd is601_enhanced_calculator_midterm
    ```


2. **Create virtual environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```


3. **Install dependencies**

pip install -r requirements.txt


4. **Running Tests**

pytest
pytest --cov=app --cov-report=term-missing