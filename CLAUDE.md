## Project brief introduction
- A Lightweight Tool for Prompt Optimization

## Project Rule
- This is a project with Python as the primary programming language
- This project environment is handled by 'uv'. Use 'uv add' or 'uv pip install' commands to manage dependencies.

## Technology Stack
- Collect langgraph as the agent framework
- pytest for testing framework with asyncio, mock, and coverage support

## Environment Configuration
- DEEPSEEK_BASE_URL and DEEPSEEK_API_KEY have been set in .env file, feel free to use them in any openai compatible clients.
- Python 3.11 environment initialized with `uv init -p 3.11`

## Project Structure
- The main source code are located in 'src/promptuner' directory
- The main test code are located in 'tests'

## Development Methodology
- Adopt the test-driven development approach
- Run tests with `pytest` or `uv run pytest`
- Generate coverage reports with `pytest --cov=src/promptuner`