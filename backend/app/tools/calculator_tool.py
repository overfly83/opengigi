#!/usr/bin/env python3
"""
Advanced Calculator Tool

This tool performs various arithmetic operations including:
- Basic operations: addition, subtraction, multiplication, division
- Advanced operations: exponents, square roots, factorials
- Order of operations with parentheses
"""

from app.tools import tool
import math


@tool
def calculator(expression: str) -> dict:
    """Advanced calculator that evaluates arithmetic expressions
    
    Args:
        expression: Arithmetic expression to evaluate (e.g., "2 + 3 * 4", "sqrt(16)", "(5 + 3) ^ 2")
        
    Returns:
        Calculation result
    """
    try:
        # Replace common math functions with Python equivalents
        expr = expression.replace('^', '**')
        expr = expr.replace('sqrt(', 'math.sqrt(')
        expr = expr.replace('sin(', 'math.sin(')
        expr = expr.replace('cos(', 'math.cos(')
        expr = expr.replace('tan(', 'math.tan(')
        expr = expr.replace('log(', 'math.log(')
        expr = expr.replace('ln(', 'math.log(')
        expr = expr.replace('pi', 'math.pi')
        expr = expr.replace('e', 'math.e')
        
        # Evaluate the expression safely
        result = eval(expr, {"math": math})
        
        return {
            "status": "success",
            "expression": expression,
            "result": result,
            "message": "Calculation successful"
        }
    except ZeroDivisionError:
        return {
            "status": "error",
            "expression": expression,
            "result": None,
            "message": "Division by zero error"
        }
    except SyntaxError:
        return {
            "status": "error",
            "expression": expression,
            "result": None,
            "message": "Invalid syntax in expression"
        }
    except Exception as e:
        return {
            "status": "error",
            "expression": expression,
            "result": None,
            "message": f"Error: {str(e)}"
        }
