#!/usr/bin/env python3
"""
Example Skill

This is a template for creating new agent skills.
"""

from app.skills.base import Skill

class ExampleSkill(Skill):
    """Example skill that demonstrates the skill interface"""
    
    name = "example_skill"
    description = "An example skill that performs a simple calculation"
    
    def execute(self, a: int, b: int, operation: str = "add") -> int:
        """Execute the example skill
        
        Args:
            a: First number
            b: Second number
            operation: Operation to perform (add, subtract, multiply, divide)
            
        Returns:
            Result of the operation
        """
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a // b
        else:
            raise ValueError(f"Unknown operation: {operation}")