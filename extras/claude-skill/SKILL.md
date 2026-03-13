---
name: read-aloud
description: Read Claude's latest response aloud using text-to-speech. Use when the user says "read that aloud", "read it to me", "speak that", or "/read-aloud".
argument-hint: "[speed, e.g. +30%]"
allowed-tools: Bash
---

## Read Latest Response Aloud

1. Find the current session JSONL:
   ```bash
   SESSION_DIR="$HOME/.claude/projects/$(echo "$PWD" | sed 's|/|-|g; s|^-||')"
   JSONL=$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1)
   ```

2. Extract the last assistant text (skip tool-use-only messages), save to temp file:
   ```bash
   tac "$JSONL" | python3 -c "
   import sys, json
   for line in sys.stdin:
       obj = json.loads(line.strip())
       if obj.get('type') == 'assistant':
           texts = [b['text'] for b in obj['message'].get('content', []) if isinstance(b, dict) and b.get('type') == 'text']
           if texts:
               print('\n'.join(texts))
               break
   " > /tmp/claude-read-aloud.txt
   ```

3. Play it: `aloud ${ARGUMENTS:+-s "$ARGUMENTS"} /tmp/claude-read-aloud.txt`

4. If no text found, tell the user.
