---
name: test-pipeline
description: Run the full Notomai test suite and pipeline validation. Use when user says "run tests", "test pipeline", "check tests", "pytest", or "validate pipeline".
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

# Test Pipeline - Notomai

Run the complete Notomai test pipeline and report results clearly.

## Steps

1. **Run pytest** on the full test suite:
   ```bash
   cd $PROJECT_ROOT
   python -m pytest tests/ -v --tb=short 2>&1
   ```

2. **Run the reliability test** (if pytest passes):
   ```bash
   python execution/test_fiabilite.py 2>&1
   ```

3. **Check template conformity** for all 4 templates:
   - vente_lots_copropriete.md (target: >=80%)
   - promesse_vente_lots_copropriete.md (target: >=88%)
   - reglement_copropriete_edd.md (target: >=85%)
   - modificatif_edd.md (target: >=91%)

4. **Report summary** in this format:
   ```
   ## Test Results
   - pytest: X passed, Y failed, Z errors
   - Reliability: PASS/FAIL
   - Template conformity:
     - Vente: XX% (target 80%) OK/FAIL
     - Promesse: XX% (target 88%) OK/FAIL
     - Reglement: XX% (target 85%) OK/FAIL
     - Modificatif: XX% (target 91%) OK/FAIL

   ## Failures (if any)
   [Details of each failure with file:line reference]

   ## Recommended Actions
   [What to fix first, ordered by priority]
   ```

## Important
- If pytest fails, still report all results (don't stop early)
- Include file paths and line numbers for every failure
- Suggest fixes based on error patterns (self-anneal principle)
- NEVER modify test files or source code - only report
