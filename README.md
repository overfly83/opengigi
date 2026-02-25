# OpenGigi

OpenGigi is an autonomous agent system built on LangChain Deep Agents, featuring both streaming and non-streaming modes, custom logging, and a flexible plugin architecture for skills and tools.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Streaming Implementation](#streaming-implementation)
- [Tools and Skills](#tools-and-skills)
  - [Creating Tools](#creating-tools)
  - [Creating Skills](#creating-skills)
  - [Registering Components](#registering-components)
- [API Documentation](#api-documentation)
- [Frontend Usage](#frontend-usage)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Features

- **Dual Mode Execution**: Both streaming and non-streaming modes
- **Human Typing Effect**: Real-time streaming with typing animation
- **Custom Logging**: Color-coded logs with source identification
- **Plugin Architecture**: Extensible system for tools and skills
- **Web Search Integration**: Built-in web search capability
- **Stream Tracking**: Subagent progress, LLM tokens, and tool calls
- **Server-Sent Events**: Real-time frontend updates

## Installation

### Prerequisites

- Python 3.10+
- Node.js 14+
- npm 6+

### Quick Installation

Run the provided installation script:

```bash
# Windows
install.bat

# macOS/Linux
chmod +x install.sh && ./install.sh
```

### Manual Installation

#### Backend

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the backend directory:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your-openai-api-key
   BASE_URL=https://api.openai.com/v1
   MODEL_NAME=gpt-4
   MODEL_TEMPERATURE=0.7

   # Tavily Search (for websearch tool)
   TAVILY_API_KEY=your-tavily-api-key
   ```

#### Frontend

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

## Getting Started

### Starting Both Servers

Run the provided start script:

```bash
# Windows
start-all.bat

# macOS/Linux
chmod +x start-all.sh && ./start-all.sh
```

### Starting Servers Individually

#### Backend

```bash
# Windows
cd backend
venv\Scripts\activate
python -m uvicorn app.api.api:app --reload

# macOS/Linux
cd backend
source venv/bin/activate
uvicorn app.api.api:app --reload
```

#### Frontend

```bash
cd frontend
npm run dev
```

### Accessing the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000

## Project Structure

```
opengigi/
├── backend/                 # Python backend
│   ├── app/
│   │   ├── agent/           # Agent implementation
│   │   ├── api/             # FastAPI endpoints
│   │   ├── middleware/      # Middleware components
│   │   ├── models/          # Pydantic models
│   │   ├── skills/          # Agent skills
│   │   ├── tools/           # LangChain tools
│   │   └── utils/           # Utility functions
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/                # Vue.js frontend
│   ├── src/
│   │   ├── App.vue          # Main application
│   │   └── main.js          # Entry point
│   ├── index.html           # HTML template
│   └── package.json         # npm dependencies
├── .gitignore               # Git ignore file
├── AGENT_SKILLS_AND_TOOLS.md # Detailed documentation
├── README.md                # This file
├── STREAMING_IMPLEMENTATION.md # Streaming details
├── install.bat              # Installation script
├── main.py                  # Main entry point
└── start-all.bat            # Start script
```

## Streaming Implementation

OpenGigi supports three streaming modes:

1. **updates**: Node-level updates from the agent graph
2. **messages**: LLM token streaming
3. **custom**: Custom event streaming

For detailed implementation, see [STREAMING_IMPLEMENTATION.md](STREAMING_IMPLEMENTATION.md).

## Tools and Skills

OpenGigi has a flexible plugin architecture for tools and skills:

### Creating Tools

Tools are LangChain-compatible functions that the agent can use. To create a new tool:

1. **Create a new file** in `backend/app/tools/` (e.g., `my_tool.py`)
2. **Use the @tool decorator** to define your tool:

```python
from langchain.tools import tool

@tool
def my_tool(param1: str, param2: int = 1) -> dict:
    """Description of what the tool does
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Result of the tool execution
    """
    # Tool implementation
    return {"result": f"Processed {param1} with {param2}"}
```

### Creating Skills

Skills are Deep Agent-compatible components. There are two ways to create skills:

#### Python-based Skills

1. **Create a new file** in `backend/app/skills/` (e.g., `my_skill.py`)
2. **Extend the Skill base class**:

```python
from app.skills.base import Skill

class MySkill(Skill):
    name = "my_skill"
    description = "Description of what the skill does"
    
    def execute(self, **kwargs):
        """Execute the skill
        
        Args:
            **kwargs: Skill parameters
            
        Returns:
            Result of the skill execution
        """
        # Skill implementation
        return {"result": "Skill executed successfully"}
```

#### Directory-based Skills

1. **Create a new directory** in `backend/app/skills/` (e.g., `my_directory_skill/`)
2. **Add a SKILL.md file** with skill metadata
3. **Add implementation files** as needed

### Registering Components

#### Tools

Tools are automatically discovered and registered at startup. No manual registration is required.

#### Skills

Python-based skills are automatically discovered and registered at startup. Directory-based skills are loaded from the skills directory.

### Using Tools and Skills

Tools and skills are automatically available to the agent. The agent will use them as needed based on the task requirements.

For detailed documentation, see [AGENT_SKILLS_AND_TOOLS.md](AGENT_SKILLS_AND_TOOLS.md).

## API Documentation

### Backend Endpoints

#### POST /run-agent

Run the agent in non-streaming mode.

**Request Body**:
```json
{
  "goal": "What is the capital of France?",
  "mode": "non-streaming"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "phase": "reflect",
    "result": "The capital of France is Paris.",
    "is_completed": true,
    "todos": []
  }
}
```

#### GET /run-agent-stream

Run the agent in streaming mode.

**Query Parameters**:
- `goal`: The task for the agent to complete
- `stream_mode`: Streaming mode (`updates`, `messages`, `custom`)

**Response**:
Server-Sent Events (SSE) with streaming updates.

## Frontend Usage

### Basic Usage

1. **Enter a goal** in the input field
2. **Select execution mode** (streaming or non-streaming)
3. **Click "Start Execution"**
4. **View results** in the output area

### Streaming Mode

In streaming mode, you'll see:
- Real-time token generation with typing effect
- Subagent events and tool calls
- Color-coded log messages

### Non-Streaming Mode

In non-streaming mode, you'll see:
- Complete results after execution finishes
- Structured response data

## Environment Variables

### Required Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `MODEL_NAME`: The OpenAI model to use (e.g., `gpt-4`)

### Optional Variables

- `BASE_URL`: Custom OpenAI API base URL
- `MODEL_TEMPERATURE`: Temperature for model responses (0-1)
- `TAVILY_API_KEY`: API key for Tavily Search (required for websearch tool)

## Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check that Python dependencies are installed
   - Verify environment variables are set correctly
   - Ensure port 8000 is not in use

2. **Frontend not connecting**
   - Check that npm dependencies are installed
   - Ensure backend is running on port 8000
   - Verify CORS settings in backend

3. **Websearch tool not working**
   - Ensure TAVILY_API_KEY is set in environment variables
   - Check network connectivity

4. **Streaming not working**
   - Verify that server-sent events are supported by your browser
   - Check backend logs for streaming errors

### Debugging

- **Backend logs**: Check the terminal where uvicorn is running
- **Frontend logs**: Open browser developer tools and check the console
- **API requests**: Use tools like Postman or curl to test API endpoints directly

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines

1. **Follow existing code style**
2. **Add documentation** for new features
3. **Write tests** for critical functionality
4. **Update README.md** if needed

## License

This project is licensed under the MIT License.
