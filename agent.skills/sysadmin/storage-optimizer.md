---
name: Storage Optimizer
description: Intelligence for managing disk space and automated offloading.
version: 1.0
owner: Georg
tags: [sysadmin, storage, optimization, automation]
allowed-tools: ["run_command", "view_file"]
---

# Storage Optimizer Skills

## Philosophy

- **Zero Downtime**: Never let the system crash due to disk fullness (Disk-Pressure Survival).
- **Least-Recently-Used (LRU)**: Prioritize moving files that haven't been accessed in a long time.
- **User Agency**: The Beast proposes; the User approves (unless set to AUTO_HEAL).

## Operations

### 1. Monitoring
- **Check**: Run `storage_manager.py` or `df -h` daily.
- **Alert**: If Usage > 85%, start planning. If Usage > 95%, enter CRITICAL phase.

### 2. Candidate Selection
- **Criteria**:
    1. **Size**: Large files (> 500MB) such as logs, VM images, old video renders.
    2. **Age**: Files not modified in > 30 days.
    3. **Type**: Downloads, Temp files, Archive folders.

### 3. Offloading Execution
- **Steps**:
    1. List candidates to user: "I can save 50GB by moving these 10 folders to OneDrive."
    2. Upon approval, invoke `cloud-storage` skill to upload.
    3. Verify.
    4. Delete local and replace with a `.placeholder` file or metadata link.

## Safety & Standards
- **Protected Paths**: Never offload `/etc`, `/bin`, `System32`, or active project source code.
- **Verification**: Byte-for-byte or SHA-256 verification preferred.
- **Rollback**: Keep a local backup of critical small metadata before deletion.
