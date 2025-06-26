# 🧮 Advanced Python Calculator – Midterm Project

## 📘 Overview

This project is a modular, extensible, and fully testable **command-line calculator** written in Python. It supports multiple arithmetic operations, complete **undo/redo history management**, **logging**, **auto-saving**, and integrates **Factory**, **Memento**, and **Observer** design patterns. The application includes **CI/CD pipeline via GitHub Actions** and achieves **>95% test coverage** with `pytest`.

---

## Features

- ✅ **Basic Operations**: add, subtract, multiply, divide  
- ✅ **Advanced Operations**: power, root, modulus, int divide, percent, abs diff  
- ✅ **Undo/Redo Functionality** using Memento pattern  
- ✅ **Auto-Save** to CSV using pandas  
- ✅ **Real-time Logging** to log file  
- ✅ **Environment-based configuration** via `.env`  
- ✅ **Command-line Interface (REPL)**  
- ✅ **CI/CD pipeline** with test coverage enforcement  
- ✅ **Custom error handling** and input validation  

---

## 🏗️ Directory Structure

project_root/
├── app/
│ ├── calculator.py
│ ├── calculator_config.py
│ ├── calculator_memento.py
│ ├── exceptions.py
│ ├── operations.py
│ ├── init.py
├── tests/
│ ├── test_calculator.py
│ ├── test_operations.py
│ ├── test_calculator_config.py
│ └── init.py
├── main.py
├── .env
├── requirements.txt
├── README.md
└── .github/workflows/python-app.yml

## 🔧 Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-username/advanced-calculator.git
cd advanced-calculator


2. **Create virtual environment**

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


3. **Install dependencies**

pip install -r requirements.txt


4. **Running Tests**

pytest
pytest --cov=app --cov-report=term-missing