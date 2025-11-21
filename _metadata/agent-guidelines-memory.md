# Agent Script Guidelines (Memory)

Rule: In all further scripts, always implement graceful Ctrl+C handling (KeyboardInterrupt) to exit cleanly. Otherwise, avoid additional error handling; keep demos minimal and educational.

Context: Applied Option B in `demos/02-agent-service/02-knowledge-tools/agent-knowledge-tools-py/agents-function-calling.py` by removing extra env var validation and broad try/except blocks, retaining only improved prompt and Ctrl+C handling.

Last Updated: 2025-11-21
