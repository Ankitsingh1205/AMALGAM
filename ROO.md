# AMALGAM Development Rules

You are an implementation engineer for AMALGAM.

Rules:

1. Never break architecture.
2. Never remove existing functionality.
3. Always run pytest after modifications.
4. If tests fail, fix them until all pass.
5. Modify the minimum number of files necessary.
6. Explain every changed file.
7. Never invent APIs.
8. Prefer extending existing modules.
9. Follow the execution pipeline:

Brain
→ Intent
→ Planner
→ Dispatcher
→ Tool/Service
→ Result

10. If uncertain, stop and ask.

Current Goal:
Build → Integrate → Test → Freeze → Next Mission
