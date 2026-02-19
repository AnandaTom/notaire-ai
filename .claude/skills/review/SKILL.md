---
name: review
description: MANDATORY after writing or modifying any code (Python, TypeScript, React, or any language). Reviews code with fresh eyes for correctness and effectiveness (2-pass). Must be called before /document and before committing. Auto-invoke after any code creation or modification — do not wait for user to ask.
argument-hint: "[file-path (optional)]"
---

You are being asked to review code that was just written or modified.

## Instructions

1. **Identify what to review.** If the user passed `$ARGUMENTS`, review those files. Otherwise, check git for uncommitted changes:
   ```bash
   git diff --name-only
   git diff --cached --name-only
   ```
   Cover ALL file types: `.py`, `.ts`, `.tsx`, `.js`, templates (`.md` Jinja2), schemas (`.json`).
   If nothing shows up, look at recent conversation context for what was just worked on.

2. **Read every changed file completely.** Do not skim. Understand the intent before judging the code.

3. **Spawn the reviewer subagent** using the Task tool:
   ```
   subagent_type: "superpowers:code-reviewer"
   ```
   Pass it:
   - The full file contents
   - A clear description of what the code is supposed to do
   - The language/framework context (Python backend, Next.js/React frontend, Jinja2 template, etc.)
   The reviewer agent prompt lives at `~/.claude/agents/reviewer.md` — it performs a 2-pass review (correctness then effectiveness).

4. **Act on findings:**
   - **CRITICAL** issues → fix immediately, then re-spawn the reviewer to confirm the fix
   - **MODERATE** issues → fix them, briefly explain what changed
   - **MINOR** only → list them for the user, ask if they want them addressed
   - **No issues** → report that the review passed clean

5. **Report to the user** with a short summary:
   - What was reviewed (files + line counts)
   - What was found (count by severity)
   - What was fixed
   - What remains (if anything deferred)

## Key Behavior

- Do NOT ask the user what to review if git shows obvious recent changes — just review them
- Do NOT skip the subagent and review it yourself — the whole point is fresh, unbiased eyes
- Do NOT limit scope to Python — frontend (`.tsx/.ts`) changes are equally critical
- Be fast. Read → spawn → fix → report. No preamble.
