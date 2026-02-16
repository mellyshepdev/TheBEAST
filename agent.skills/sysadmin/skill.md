---
name: Sysadmin Skills
description: Rules for managing servers and infrastructure.
version: 2.0
owner: Georg
tags: [sysadmin, devops, infrastructure, linux, docker]
allowed-tools: ["run_command", "view_file"]
---

# Sysadmin Skills

## Philosophy

- **CLI-First**: Prefer command line over GUI. It's faster and scriptable.
- **Immutable**: Prefer destroying and recreating containers over patching live ones.
- **Safety**: Always verify backups before destructive actions (`rm -rf`, `DROP TABLE`).
- **Idempotency**: Scripts should be runnable multiple times without side effects.

## Operations

- **Changes**:
    1. **Check**: Current state (`docker ps`, `systemctl status`).
    2. **Plan**: What commands will run?
    3. **Execute**: Run commands.
    4. **Verify**: Prove it worked.
- **Verification**: Always provide a verification command (e.g., `curl -I localhost:8080`, `grep "Success" log.txt`).
- **Rollback**: Have a plan B. If it fails, how do we revert?

## Monitoring & Debugging

- **Logs**: Check specific logs, not just "it failed".
  - `docker logs <container>`
  - `/var/log/syslog` or `journalctl -xe`
- **Resources**:
  - `htop` for CPU/RAM.
  - `docker stats` for container load.
  - `df -h` for disk space.

## Common Workflows

### Docker Management

- **Restart**: `docker restart <container>`
- **Logs**: `docker logs --tail 100 -f <container>`
- **Shell**: `docker exec -it <container> /bin/bash`
