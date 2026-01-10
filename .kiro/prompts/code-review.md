---
description: Technical code review for quality and bugs
---

# Code Review

Perform technical code review on recently changed files.

## What to Review

Run these commands:
```bash
git status
git diff HEAD
git diff --stat HEAD
```

Check new files:
```bash
git ls-files --others --exclude-standard
```

Read each changed/new file in its entirety.

## Review Criteria

For each file, analyze for:

1. **Logic Errors**
   - Off-by-one errors
   - Incorrect conditionals
   - Missing error handling

2. **Security Issues**
   - Exposed secrets or API keys
   - Insecure data handling

3. **Performance Problems**
   - Inefficient algorithms
   - Unnecessary computations

4. **Code Quality**
   - DRY violations
   - Poor naming
   - Missing type hints

5. **Pattern Adherence**
   - Follows project conventions
   - Consistent with existing code

## Output Format

Save to `.kiro/code-reviews/[date]-review.md`

**For each issue:**
```
severity: critical|high|medium|low
file: path/to/file.py
line: 42
issue: [description]
suggestion: [how to fix]
```

If no issues: "Code review passed. No issues detected."
