---
description: Execute an implementation plan
argument-hint: [path-to-plan]
---

# Execute: Implement from Plan

## Plan to Execute

Read plan file: `$ARGUMENTS`

## Execution Instructions

### 1. Read and Understand
- Read the ENTIRE plan carefully
- Understand all tasks and dependencies
- Note validation commands to run
- Review testing strategy

### 2. Execute Tasks in Order

For EACH task:
- Identify file and action required
- Implement following specifications exactly
- Maintain consistency with existing patterns
- Include type hints and documentation

### 3. Verify as You Go
- After each file change, check syntax
- Ensure imports are correct
- Verify types are properly defined

### 4. Run Validation Commands

Execute ALL validation commands from the plan:
```bash
# Run each command exactly as specified
```

If any command fails:
- Fix the issue
- Re-run the command
- Continue only when it passes

### 5. Final Verification

Before completing:
- ✅ All tasks completed
- ✅ All tests passing
- ✅ All validation commands pass
- ✅ Code follows conventions

## Output Report

Provide summary:
- Completed tasks
- Files created/modified
- Test results
- Validation results

## IMPORTANT: Update DEVLOG

After completing the feature, you MUST update DEVLOG.md with:
- What was built
- Files created/modified
- Time spent (estimate)
- Any decisions or challenges
- Kiro CLI usage notes
