#!/usr/bin/env python3
"""
Skills Module

This module contains utilities for Python-based skills and skill management.
"""

from typing import Dict, List, Type, Any, Optional

class Skill:
    """Base class for Python-based skills"""
    
    name: str
    description: str
    
    def __init__(self):
        self.name = self.__class__.name
        self.description = self.__class__.description
    
    def execute(self, **kwargs) -> Any:
        """Execute the skill with given parameters"""
        raise NotImplementedError("Skill must implement execute method")

class SkillRegistry:
    """Registry for managing Python-based skills"""
    
    def __init__(self):
        self.skills: Dict[str, Type[Skill]] = {}
    
    def register_skill(self, skill_class: Type[Skill]) -> None:
        """Register a new Python-based skill"""
        if skill_class.name in self.skills:
            raise ValueError(f"Skill {skill_class.name} already registered")
        self.skills[skill_class.name] = skill_class
    
    def get_skill(self, name: str) -> Optional[Type[Skill]]:
        """Get a registered Python-based skill by name"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict[str, str]]:
        """List all registered skills"""
        return [
            {"name": name, "description": skill.description, "type": "python"}
            for name, skill in self.skills.items()
        ]
    
    def get_skills_directory(self) -> str:
        """Get the directory containing skills"""
        import os
        return os.path.dirname(os.path.abspath(__file__))
