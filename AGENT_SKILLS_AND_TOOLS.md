# Agent Skills and LangChain Tools Guide

## Overview
This guide provides comprehensive documentation for using and extending the agent skills and LangChain tools system, following the official LangChain guidelines.

## System Architecture

### Skills System
- **Python-based skills**: Traditional class-based skills that execute self-contained functionality
  - Managed separately from tools
  - Can be used programmatically in custom workflows

- **Deep Agent skills**: Directory-based skills with SKILL.md metadata following the Deep Agents specification
  - Loaded directly by create_deep_agent from the skills directory
  - Used for specialized workflows and domain knowledge

### LangChain Tools System
The tools system uses LangChain's official tool decorator approach, allowing agents to interact with external services and utilities through well-defined functions.

### Integration with create_deep_agent
- **tools parameter**: Receives only LangChain tools (callable functions with @tool decorator)
- **skills parameter**: Receives a list of directories containing Deep Agent skills


## Key Components

### Tools
- **@tool decorator**: LangChain's official tool decorator for creating tools
- **tool_registry**: Manages registration and lookup of LangChain tools

### Skills
- **Skill**: Base class for Python-based skills
- **SkillRegistry**: Manages registration and lookup of Python-based skills
  - Provides method to wrap skills as LangChain tools
  - Provides method to get the skills directory for Deep Agent skills

### Package Structure
```
skills/
├── __init__.py           # Package imports
├── base.py               # Base classes and interfaces
├── registry.py           # Registry implementation
├── example_skill.py      # Example Python-based skill
└── example_deep_skill/    # Example directory-based Deep Agent skill
    └── SKILL.md          # Skill metadata and instructions

tools/
├── __init__.py           # Package imports
├── base.py               # Base classes and utilities
├── registry.py           # Registry implementation
└── example_tool.py       # Example LangChain tool
```

## Usage Examples

### Using Skills

#### Recommended: Package Level Import
```python
from app.skills import skill_registry

# Get a skill
skill_class = skill_registry.get_skill("example_skill")
skill = skill_class()

# Execute the skill
result = skill.execute(a=5, b=3, operation="add")
print(f"Result: {result}")  # Output: 8
```

#### Direct Import
```python
from app.skills.registry import skill_registry
from app.skills.base import Skill

# Get and execute skill
skill = skill_registry.get_skill("example_skill")()
result = skill.execute(a=5, b=3, operation="multiply")
```

### Using LangChain Tools

#### Recommended: Package Level Import
```python
from app.tools import tool_registry

# Get a tool
tool = tool_registry.get_tool("example_tool")

# Call the tool
result = tool(endpoint="/api/data", method="GET", param1="value1")
print(f"Result: {result}")
```

#### Direct Import
```python
from app.tools.registry import tool_registry
from app.tools.base import tool

# Get and call tool
tool = tool_registry.get_tool("example_tool")
result = tool(endpoint="/api/data", method="POST", data={"key": "value"})
```

## Creating New Skills

### Step 1: Create Skill Class
Create a new file in `backend/app/skills/`:

```python
from app.skills.base import Skill
from typing import Any

class MyCustomSkill(Skill):
    """My custom agent skill"""
    
    name = "my_custom_skill"
    description = "This skill performs a custom operation"
    
    def execute(self, **kwargs) -> Any:
        """Execute the skill with given parameters
        
        Args:
            param1: First parameter for the skill
            param2: Second parameter for the skill
            
        Returns:
            Result of the skill execution
        """
        # Implementation here
        param1 = kwargs.get('param1', 0)
        param2 = kwargs.get('param2', 0)
        result = param1 * param2
        return result
```

### Step 2: Register Skill
The skill will be automatically registered when the module is imported. The registry scans the skills directory and registers all Skill subclasses.

### Step 3: Use Skill
```python
from app.skills import skill_registry

skill = skill_registry.get_skill("my_custom_skill")()
result = skill.execute(param1=10, param2=5)
print(f"Result: {result}")  # Output: 50
```

## Creating New LangChain Tools

### Step 1: Create Tool Function
Create a new file in `backend/app/tools/`:

```python
from app.tools import tool
from typing import Any

@tool
async def my_custom_tool(endpoint: str, method: str = "GET", data: dict = None) -> str:
    """Interacts with an external service.
    
    Args:
        endpoint: API endpoint to call
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Data to send with the request
        
    Returns:
        String description of the tool's response
    """
    # Implementation here
    data = data or {}
    
    # Simulate API call
    return f"Called {method} {endpoint} with data: {data}"

@tool("calculator")
def calculate(expression: str) -> str:
    """Performs arithmetic calculations.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        Result of the calculation
    """
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Step 2: Register Tool
The tool will be automatically registered when the module is imported. The registry scans the tools directory and registers all functions decorated with @tool.

### Step 3: Use Tool
```python
from app.tools import tool_registry

# Get the tool
tool = tool_registry.get_tool("my_custom_tool")

# Call the tool
result = await tool(endpoint="/api/users", method="POST", data={"name": "John", "email": "john@example.com"})
print(f"Result: {result}")

# Use calculator tool
calc_tool = tool_registry.get_tool("calculator")
result = calc_tool(expression="2 + 2 * 3")
print(f"Calculation result: {result}")
```

## Creating Deep Agent Skills

Deep Agent skills follow the directory-based format specified in the Deep Agents documentation. These skills use a SKILL.md file with frontmatter metadata.

### Step 1: Create Skill Directory
Create a new directory in `backend/app/skills/`:

```
skills/
└── my_deep_skill/
    └── SKILL.md
```

### Step 2: Create SKILL.md File
```markdown
---
name: my_deep_skill
description: This skill provides specialized functionality for a specific domain
license: MIT
compatibility: Requires internet access
metadata:
  author: Your Name
  version: "1.0"
allowed-tools: fetch_url
---

# My Deep Skill

## Overview

This skill provides specialized functionality for handling specific types of requests.

## Instructions

### 1. Analyze the Request

Analyze the user's request to determine if this skill is applicable.

### 2. Gather Information

Use the fetch_url tool to gather any necessary information.

### 3. Provide a Response

Based on the gathered information, provide a comprehensive response to the user's request.
```

### Step 3: Register Skill
The skill will be automatically registered when the module is imported. The registry scans the skills directory and registers all directories containing a SKILL.md file.

### Step 4: Use Skill
Deep Agent skills are automatically included in the agent's skills list and will be used when appropriate.

## Key Concepts

### 1. Registry Pattern
- **Dynamic Discovery**: Skills and tools are automatically discovered and loaded
- **Centralized Management**: Single point of access for all skills and tools
- **Decoupled Design**: Skills and tools can be developed independently

### 2. LangChain Tool Decorator
- **Simple Syntax**: Use @tool decorator to create tools
- **Automatic Schema**: Type hints generate tool input schemas
- **Flexible**: Support for both sync and async functions

### 3. Deep Agent Skills Format
- **Directory-based**: Skills are organized as directories with SKILL.md files
- **Frontmatter Metadata**: Skills include metadata in YAML frontmatter
- **Progressive Disclosure**: Agent only reviews skill information when needed

### 4. Minimal __init__.py Files
- **Only Re-exports**: __init__.py files only contain import statements
- **No Complex Logic**: All implementation is in separate modules
- **Clean Structure**: Clear separation of concerns

## Best Practices

### 1. Skill Development
- **Single Responsibility**: Each skill should do one thing well
- **Clear Documentation**: Document parameters and return values
- **Error Handling**: Implement proper error handling in execute() method
- **Testability**: Write unit tests for each skill

### 2. Tool Development
- **Idempotent**: Tool calls should be idempotent when possible
- **Error Handling**: Implement proper error handling in call() method
- **Logging**: Add logging for debugging and monitoring
- **Rate Limiting**: Consider adding rate limiting for external services

### 3. Registry Management
- **Unique Names**: Ensure skill and tool names are unique
- **Descriptive Descriptions**: Provide clear descriptions for each skill and tool
- **Versioning**: Consider adding version information for future compatibility

## Troubleshooting

### Skill Not Found
- Ensure the skill class inherits from Skill
- Check that the skill has name and description attributes
- Verify the skill file is in the skills directory
- Confirm the skill module is being imported

### Tool Not Found
- Ensure the tool class inherits from MCPTool
- Check that the tool has name and description attributes
- Verify the tool file is in the tools directory
- Confirm the tool module is being imported

### Import Errors
- Check that all required dependencies are installed
- Verify the import paths are correct
- Ensure the package structure is properly set up

## Future Enhancements

- **Skill Dependencies**: Add support for skill dependencies and conflict resolution
- **Tool Caching**: Implement tool result caching for performance
- **Skill Marketplace**: Add skill and tool marketplace functionality
- **Remote Discovery**: Support for remote skill/tool discovery and loading
- **Web Interface**: Add web interface for managing skills and tools

## Integration with create_deep_agent

You can directly integrate skills and tools into the `create_deep_agent` call. The system automatically loads all registered tools and passes the skills directory for Deep Agent skills.

### Usage Example

```python
from deepagents import create_deep_agent
from app.skills import skill_registry
from app.tools import tool_registry

# Get all registered tools
def get_tool_instances():
    """获取所有注册的工具实例"""
    instances = []
    
    # 添加工具实例（LangChain tools are already callable functions）
    for tool_name in tool_registry.tools:
        tool_func = tool_registry.tools[tool_name]
        instances.append(tool_func)
    
    return instances

# 准备工具列表
tools = get_tool_instances()

# 获取技能目录（用于Deep Agent技能）
skills_directory = skill_registry.get_skills_directory()

# 创建深度代理
agent = create_deep_agent(
    name="agent_name",
    system_prompt="You are a helpful assistant",
    model=llm,
    tools=tools,  # 只传递LangChain工具
    skills=[skills_directory],  # 传递技能目录列表
    response_format=AgentResponse,
    middleware=[log_tool_calls]
)
```

### How It Works

1. **Automatic Discovery**: The system automatically discovers all registered tools
2. **Tool Collection**: Collects all LangChain tools (callable functions with @tool decorator)
3. **Skills Directory**: Gets the directory containing skills for Deep Agent skills
4. **Integration**: Passes the tool functions and skills directory to the `create_deep_agent` function
5. **Ready to Use**: The agent can now use all the tools and Deep Agent skills

## Conclusion

The agent skills and LangChain tools system provides a flexible, extensible framework for enhancing agent capabilities, following the official LangChain guidelines. By following this guide, you can:

1. **Use existing skills and tools** to extend agent functionality
2. **Create new Python-based skills** to implement custom functionality
3. **Develop new LangChain tools** using the @tool decorator
4. **Create Deep Agent skills** following the directory-based format
5. **Extend the system** to meet your specific needs
6. **Integrate directly** with create_deep_agent for seamless usage

The decoupled design and dynamic loading capabilities make it easy to add new functionality without modifying core code, ensuring the system remains maintainable and scalable as it grows.

## Final Notes

- **LangChain Compatibility**: The tools system now fully follows LangChain's tool guidelines
- **Deep Agents Support**: The skills system supports both Python-based skills and directory-based Deep Agent skills
- **Automatic Registration**: Skills and tools are automatically discovered and registered
- **Seamless Integration**: Direct integration with create_deep_agent using the tools and skills parameters

This implementation provides a robust foundation for building and extending agent capabilities using industry-standard practices and conventions.

---

*Last updated: 2026-02-22*