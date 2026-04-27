---
description: Update all documentation for the current repository — README, docs/INDEX.md, and CLAUDE.md. Run with no arguments.
---

# Update Documentation

Update all documentation for the repository rooted at the current working directory.

Do not ask for a target — use the entire repository as the scope.

Follow the full workflow defined in the `doc-updater` subagent:
1. Analyze the repository structure and entry points
2. Update `README.md`
3. Update `docs/INDEX.md`
4. Validate and update any other files in `docs/`
5. Update `CLAUDE.md` if present

Run the quality checklist before finishing.
