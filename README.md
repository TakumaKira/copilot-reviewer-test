# Test Plan: GitHub Copilot Reviewer Behavior

## Context

We want to systematically verify two things about GitHub Copilot's code review feature:
1. **When** does Copilot read `.github/copilot-instructions.md`? (PR branch only vs. merged into default branch)
2. Does Copilot follow **Agent Skills** (`.github/skills/`) and sub-skills during code review?

The repository is fresh and empty (`https://github.com/TakumaKira/copilot-reviewer-test.git`, branch `master`).

**Key research finding:** Documentation does NOT clarify whether Copilot reads instructions from the PR's head branch or the base/default branch. Community reports suggest inconsistent behavior. This is exactly what we're testing.

**Important caveat:** Agent Skills officially support "Copilot coding agent, CLI, and VS Code agent mode" — code review support for Skills is **not confirmed** in docs. Test 2 will verify this empirically.

---

## Prerequisites

- Copilot code review access (free tier allows manual review requests)
- **Optional:** Copilot Pro/Pro+ plan (required for auto-review in Tests 1B, 1D — skip these if not on Pro)
- Enable Copilot code review in repo settings (Settings → Copilot → Code review → enable custom instructions)

---

## Test 1: When does Copilot read `copilot-instructions.md`?

Each PR will include a simple Python file with an intentional issue (to give Copilot something to review). The instruction file will contain a unique marker phrase that Copilot MUST output if it reads the file.

### Test 1A — Instructions in PR branch only, manual review request

**Branch:** `test/1a-instructions-pr-branch-manual`

**Files to create:**

1. `.github/copilot-instructions.md`:
```markdown
IMPORTANT: You MUST begin every single review comment with the exact phrase "[MARKER-1A-READ]".
This is a mandatory requirement. Every comment you leave must start with [MARKER-1A-READ].
```

2. `app.py`:
```python
import os
import sys

def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    average = total / len(numbers)  # potential ZeroDivisionError
    return average

result = calculate_average([])
print(result)
```

**Steps:**
1. Create branch from `master`, add both files, push
2. Open PR targeting `master`
3. Manually request review from "Copilot" via the PR reviewers sidebar
4. **Observe:** Does Copilot's review include `[MARKER-1A-READ]`?

### Test 1B — Instructions in PR branch only, auto-requested review *(Pro plan required — skip if not available)*

**Branch:** `test/1b-instructions-pr-branch-auto`

**Before creating the PR**, set up auto-review:
- Repo Settings → Rules → Rulesets → New branch ruleset
- Name: "Copilot auto review"
- Enforcement: Active
- Target: default branch
- Enable: "Automatically request Copilot code review"
- Enable: "Review new pushes"

**Files to create:**

1. `.github/copilot-instructions.md` (same content but with marker `[MARKER-1B-READ]`)
2. `utils.py`:
```python
def find_max(items):
    max_val = items[0]  # potential IndexError on empty list
    for item in items:
        if item > max_val:
            max_val = item
    return max_val

passwords = {"admin": "password123", "user": "qwerty"}  # hardcoded credentials
```

**Steps:**
1. Create branch from `master`, add both files, push
2. Open PR targeting `master`
3. **Do NOT manually request review** — wait for auto-review
4. **Observe:** Does Copilot's review include `[MARKER-1B-READ]`?

### Test 1C — Instructions merged into default branch, manual review request

**Branch for merge:** `test/1c-setup-instructions`
**Branch for PR:** `test/1c-instructions-default-branch-manual`

**Steps:**
1. Create branch `test/1c-setup-instructions` from `master`
2. Add `.github/copilot-instructions.md` with marker `[MARKER-1C-READ]`
3. Open PR, merge into `master` (this puts instructions in default branch)
4. Create new branch `test/1c-instructions-default-branch-manual` from updated `master`
5. Add `helpers.py`:
```python
def parse_user_input(data):
    return eval(data)  # dangerous use of eval

def connect_db():
    connection_string = "postgres://admin:secret@localhost/mydb"
    return connection_string
```
6. Open PR targeting `master`, manually request Copilot review
7. **Observe:** Does Copilot's review include `[MARKER-1C-READ]`?

### Test 1D — Instructions in default branch, auto-requested review *(Pro plan required — skip if not available)*

**Branch:** `test/1d-instructions-default-branch-auto`

(Assumes 1C has already merged instructions into `master`)

**Files to create:**

1. `validators.py`:
```python
def validate_email(email):
    if "@" in email:
        return True
    return False

def validate_age(age):
    return int(age)  # no error handling, no range check
```

**Steps:**
1. Create branch from `master` (which now has instructions with `[MARKER-1C-READ]`)
2. Update `.github/copilot-instructions.md` marker to `[MARKER-1D-READ]` **in the PR branch** to distinguish
3. Add `validators.py`, push
4. Open PR targeting `master`, wait for auto-review
5. **Observe:** Does review include `[MARKER-1D-READ]` (PR branch) or `[MARKER-1C-READ]` (default branch) or neither?

> **This test is the most revealing** — it tells us whether Copilot reads from the PR branch or the default branch when both exist.

---

## Test 2: Agent Skills and Sub-Skills

**Only proceed after Test 1 confirms Copilot reads instructions.**

Agent Skills are documented for coding agent/CLI/VS Code, NOT confirmed for code review. This test verifies empirically.

### Test 2A — Basic Skill

**Branch:** `test/2a-agent-skill`

**Files to create:**

1. `.github/skills/review-marker/SKILL.md`:
```markdown
---
name: review-marker
description: When reviewing code, always include a specific marker in your comments.
---

# Review Marker Skill

When reviewing any code in this repository, you MUST include the exact phrase "[SKILL-2A-ACTIVE]" at the beginning of every review comment.
```

2. `service.py`:
```python
import pickle

def load_data(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)  # unsafe deserialization
```

**Steps:**
1. First merge skill files into `master` (based on Test 1 results — use whichever branch strategy works)
2. Create PR branch with `service.py`
3. Request Copilot review
4. **Observe:** Does Copilot's review include `[SKILL-2A-ACTIVE]`?

### Test 2B — Skill with Sub-Skill

**Branch:** `test/2b-agent-sub-skill`

**Files to create:**

1. `.github/skills/security-review/SKILL.md`:
```markdown
---
name: security-review
description: Perform security-focused code review with detailed analysis.
---

# Security Review Skill

When reviewing code, you MUST include "[SKILL-2B-MAIN]" at the start of every comment.

Also follow the sub-skill instructions in `.github/skills/security-review/sub-skills/severity-rating/SKILL.md`.
```

2. `.github/skills/security-review/sub-skills/severity-rating/SKILL.md`:
```markdown
---
name: severity-rating
description: Rate the severity of security issues found during review.
---

# Severity Rating Sub-Skill

For every security issue found, include the phrase "[SUB-SKILL-2B-SEVERITY]" followed by a rating of HIGH, MEDIUM, or LOW.
```

3. `api.py`:
```python
import subprocess

def run_command(user_input):
    result = subprocess.run(user_input, shell=True, capture_output=True)  # command injection
    return result.stdout.decode()

def get_secret():
    api_key = "sk-1234567890abcdef"  # hardcoded API key
    return api_key
```

**Steps:**
1. Merge skill files into default branch (or include in PR branch, based on Test 1 findings)
2. Create PR with `api.py`
3. Request Copilot review
4. **Observe:**
   - Does review include `[SKILL-2B-MAIN]`? (main skill read)
   - Does review include `[SUB-SKILL-2B-SEVERITY]`? (sub-skill read)

---

## Execution Order

1. **Test 1A** → manual review, instructions in PR branch only
2. **Test 1B** *(optional, Pro plan)* → set up auto-review ruleset, then auto review with instructions in PR branch
3. **Test 1C** → merge instructions into default branch, then manual review of new PR
4. **Test 1D** *(optional, Pro plan)* → auto review with instructions in default branch (+ different marker in PR branch)
5. **Test 2A** → basic skill (use branch strategy that worked in Test 1)
6. **Test 2B** → skill + nested sub-skill

## Verification Checklist

For each test, record:
- [ ] Did Copilot leave any review comments?
- [ ] Did the marker phrase appear in the comments?
- [ ] Which marker appeared (if Test 1D)?
- [ ] How long did auto-review take (if applicable)?
