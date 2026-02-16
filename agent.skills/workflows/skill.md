---
name: Workflows
description: Reusable recipes for common tasks.
version: 2.0
owner: Georg
tags: [workflow, automation, recipes]
allowed-tools: ["run_command", "write_to_file", "view_file"]
---

# Common Workflows

## 1. Project Setup (The Beast Way)

- **Trigger**: "Start a new [Type] project named [Name]."
- **Steps**:
    1. **Create Directory**: `mkdir [Name]` and `cd [Name]`.
    2. **Initialize Git**: `git init`.
    3. **Scaffold**:
        - Create `README.md` (Title, Description, Install Instructions).
        - Create `task.md` (Initial task list).
        - Create `.gitignore` (Standard for language).
    4. **Verify**: List files to confirm creation.

## 2. Bug Fix Protocol

- **Trigger**: "Fix this error: [Error Log] in [File]."
- **Steps**:
    1. **Analyze**: Read the file and the error log.
    2. **Reproduce**: If a test exists, run it to confirm failure.
    3. **Plan**: Propose a fix in `<thinking>` tags.
    4. **Execute**: Apply the fix.
    5. **Verify**: Run the test or linter again.
    6. **Report**: "Fixed [Error]. Changed [Lines]."

## 3. Content Creation (Brand Aligned)

- **Trigger**: "Write a blog post about [Topic]."
- **Steps**:
    1. **Research**: Find 3 key facts/angles (if needed).
    2. **Outline**: H2 headers.
    3. **Draft**: Write in **Brand Voice** (Practical, slightly edgy).
    4. **Review**: Check against `brand/skill.md` rules.
    5. **Final Polish**: Check flow and tone.
