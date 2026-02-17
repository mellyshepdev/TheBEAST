---
name: QA & Review (Ops)
description: Standards for verifying work and reviewing outputs.
version: 2.0
owner: Georg
tags: [ops, qa, review, testing, safety]
allowed-tools: ["run_command", "view_file"]
---

# QA & Review Standards

## Technical QA Checklist

1. **Syntax Check**: Does the code look valid? Are brackets closed?
2. **Platform Check**: Are commands compatible with the target environment (Cloud/Linux)?
    - *Example*: Use `vercel cli` or `flyctl` instead of local SSH if possible.
3. **Safety Check**:
    - **Destructive Commands**: `rm -rf`, `DROP TABLE`, `pkill`. Are they necessary? Are they scoped correctly?
    - **Backup**: Is there a backup step before the destructive command?

## Content QA Checklist

1. **Voice Alignment**: Does this sound like **The Beast**?
    - Practical? Yes.
    - Slightly Edgy? Yes.
    - Fluff? No.
2. **Formatting**:
    - Clean Markdown.
    - Proper hierarchy (H1 -> H2 -> H3).
3. **Accuracy**:
    - Are facts checked?
    - Are citations real?

## Risk Assessment

- **High Risk**: Touching production database, editing firewall, system updates. -> **Require User Approval**.
- **Medium Risk**: Installing new packages, code refactoring. -> **Notify User**.
- **Low Risk**: Reading files, generating text. -> **Auto-Proceed**.
