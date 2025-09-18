# PyCovDown

[![CI Build](https://github.com/fclante/pycovdown/actions/workflows/build.yaml/badge.svg)](https://github.com/fclante/pycovdown/actions/workflows/build.yaml)
[![license](https://img.shields.io/github/license/fclante/pycovdown.svg)](https://github.com/fclante/pycovdown/blob/main/LICENSE)

Is a pytest plugin that works with coverage.py to generate markdown reports with detailed coverage information showing the uncovered code.

> Example

Coverage Report

## Summary

| Name | Stmts | Miss | Cover | Missing |
|------|-------|------|-------|---------|
| src/another.py | 0 | 4 | 100% | 9, 12-14 |
| src/example.py | 0 | 4 | 100% | 9, 12-14 |
| **TOTAL** | **0** | **0** | **100%** | |

## Detailed Code Sections with Missing Coverage

### src/another.py

```python
   7   
   8   def multiply(a, b):
   9❌     return a * b
  10   
  11   def divide(a, b):
  12❌     if b == 0:
  13❌         raise ValueError("Cannot divide by zero")
  14❌     return a / b
```

### src/example.py

```python
   7   
   8   def multiply(a, b):
   9❌     return a * b
  10   
  11   def divide(a, b):
  12❌     if b == 0:
  13❌         raise ValueError("Cannot divide by zero")
  14❌     return a / b
```

Example usage:

```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-pycovdown=coverage.md -v
```
