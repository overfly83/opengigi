#!/usr/bin/env python3
"""
Skills Registry

This module manages the registration and discovery of Python-based skills.
"""

import importlib
import os
from typing import Dict, List, Type, Any
from app.skills.base import Skill, SkillRegistry

# Global skill registry
skill_registry = SkillRegistry()

def load_skills() -> None:
    """Load all Python-based skills from the skills directory"""
    skills_dir = os.path.dirname(__file__)
    
    # Load Python-based skills
    for filename in os.listdir(skills_dir):
        if filename.endswith('.py') and filename not in ['__init__.py', 'base.py', 'registry.py']:
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f'app.skills.{module_name}')
                
                # Find all Skill subclasses in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    try:
                        if isinstance(attr, type) and issubclass(attr, Skill) and attr != Skill:
                            skill_registry.register_skill(attr)
                    except TypeError:
                        continue
            except Exception as e:
                print(f"Failed to load skill module {module_name}: {e}")

# Load skills on module import
load_skills()