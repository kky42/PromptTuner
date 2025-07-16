# CLAUDE CODE

## UNIVERSAL RULE
- Don't remove or update `UNIVERSAL RULE`, `PRJECT`, `DEVELOPMENT` section unless user requests
- Read `docs\NOTE.md` file before starting work. Create it if it doesn't exist.

## PROJECT

### INTRODUCTION

A Lightweight Tool for Prompt Optimization.

### TECH STACK
- python 3.11
- openai sdk
- pytest

## DEVELOPMENT

### STYLE
- Start Simple: Always begin with the simplest working implementation. Avoid premature abstraction or over-engineering.
- Minimize Wrapping: Do not wrap logic into functions or classes unless: It will be reused, It improves clarity significantly, It reduces duplication or isolates side effects.
- Avoid Over-Generalization: Prefer writing specific solutions for current needs. Generalize only when a pattern clearly emerges.
- One Layer at a Time: Delay introducing decorators, wrappers, base classes, or factories until functionality demands them.
- Readable > Clever: Favor code that’s easy to read and modify over “smart” or overly compact tricks.
- Use Pythonic Conventions: Follow PEP8 for formatting. Use black or ruff for consistency, but don’t let tooling override clarity.

### CODE STRUCTURE
- The main source code are located in 'src/promptuner' directory
- The main test code are located in 'tests'

### ENVIRONMENT VARIABLES
- `.env` file is used to store environment variables, such as API keys and base URLs
- `.env.example` file is provided to show the format of the `.env` file, keep `.env.example` up-to-date when `.env` changes
- Don't commit the `.env` file, don't fill in the actual values in `.env.example`

### DEPENDENCY MANAGEMENT
- Install dependencies with `uv add` or `uv pip install`
- Run modules with `uv run -m [module_name]`, e.g. `uv run -m src.promptuner.main`
- Uninstall dependencies with `uv remove` or `uv pip uninstall` when it's no longer needed
- load_dotenv() is used to load environment variables from .env file, make sure to call it before testing or running the entrypoint

### TEST
- Run tests with `pytest` command
- Don't test all modules with `pytest` command, use `pytest [file_name]` instead
- Write tests in `tests` directory, name the test file as `test_[module_name].py`

## NOTE