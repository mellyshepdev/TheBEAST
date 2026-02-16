---
name: Planning (Ops)
description: Rules for analyzing and planning complex tasks.
version: 2.0
owner: Georg
tags: [ops, planning, strategy]
allowed-tools: ["task_boundary", "write_to_file"]
---

# Ops Planning Standards

## Objective

To turn vague goals into structured, actionable, and winning plans.

## The Planning Loop (A-P-E-R)

1. **Analyze (A)**:
    - What is the *real* goal?
    - What are the constraints (budget, time, tech)?
    - What are the risks?
2. **Plan (P)**:
    - Breakdown: Milestones -> Tasks -> Sub-tasks.
    - Dependencies: What must happen first?
    - Resources: What tools/skills are needed?
3. **Execute (E)**:
    - Run the steps.
    - Adapt if blocked.
4. **Review (R)**:
    - Did it work?
    - Does it meet the standards?

## Output Format

When creating an `implementation_plan.md`:

```markdown
# [Goal Name]

## Objective
One sentence summary.

## Proposed Changes
- [ ] Task 1
- [ ] Task 2

## Verification Plan
- How will we prove it works?
```

## Complexity Thresholds

- **Low (1-3 steps)**: Just do it. No plan needed.
- **Medium (3-10 steps)**: Quick bulleted plan in chat.
- **High (>10 steps or critical system)**: Proper `implementation_plan.md` artifact required.
