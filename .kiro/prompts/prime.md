# Prime: Load Project Context

## Objective
Build comprehensive understanding of the codebase by analyzing structure, documentation, and key files.

## Process

### 1. Analyze Project Structure
If this is a git repository, list tracked files:
```bash
git ls-files
```

Show directory structure:
```bash
tree -L 3 -I 'node_modules|__pycache__|.git|dist|build|.venv|venv'
```
(or use `ls -la` and explore key directories if tree is not available)

### 2. Read Core Documentation
- Read README.md at project root
- Read DEVLOG.md for development context
- Review steering documents in .kiro/steering/
- Check pyproject.toml for dependencies

### 3. Identify Key Files
Based on the structure, identify and read:
- Main entry points (src/main.py, cli/main.py)
- Core configuration (src/config.py)
- Agent definitions (src/agents/)
- API routes (src/api/)
- Service integrations (src/services/)

### 4. Understand Current State (if git repository)
Check recent activity:
```bash
git log -10 --oneline
```

Check current branch and status:
```bash
git status
```

## Output Report
Provide a concise summary covering:

### Project Overview
- Purpose: Smart notification bridge for digital detox
- Primary technologies: Python, FastAPI, CrewAI, Typer

### Architecture
- Agent-based design with CrewAI
- FastAPI backend + Typer CLI
- Gmail API + Twilio integrations

### Current State
- Active branch
- Recent changes
- Any immediate observations

**Make this summary easy to scan - use bullet points and clear headers.**
