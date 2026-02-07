# Test Plan: GitHub Copilot Reviewer Behavior

## Context

We want to systematically verify two things about GitHub Copilot's code review feature:
1. **When** does Copilot read `.github/copilot-instructions.md`? (PR branch only vs. merged into default branch)
2. Does Copilot follow **Agent Skills** (`.github/skills/`) and sub-skills during code review?

The repository is fresh and empty (`https://github.com/TakumaKira/copilot-reviewer-test.git`, branch `master`).

**Key research finding:** Documentation does NOT clarify whether Copilot reads instructions from the PR's head branch or the base/default branch. Community reports suggest inconsistent behavior. This is exactly what we're testing.

**Important caveat:** Agent Skills officially support "Copilot coding agent, CLI, and VS Code agent mode" — code review support for Skills is **not confirmed** in docs. Test 2 will verify this empirically.

---

## Results

### Summary of Findings

| Finding | Confidence | Evidence |
|---|---|---|
| `copilot-instructions.md` is read from **default branch only** | **Confirmed** | Tests 1A, 1B, 1C, 1D all returned `[MARKER-1C-READ]` (the default branch marker) |
| Agent Skills are read from **default branch** during code review | **Confirmed** | Tests 2A, 2B, 3B |
| Sub-skills work but may be **non-deterministic** | Likely | Worked in 2B, skipped in 3B |
| Skills in PR branch only are **not read** | **Confirmed** | Test 3A |
| PR modifying `.github/skills/` may **suppress** skill reading | Possible | Test 3A had no skill markers at all (even existing default-branch skills didn't trigger) |

### Detailed Results

| PR | Test | Markers in Review |
|---|---|---|
| #1 | 1A — Instructions in PR branch only (manual) | `[MARKER-1C-READ]` |
| #10 | 1B — Instructions in PR branch only (auto) | `[MARKER-1C-READ]` |
| #4 | 1C — Instructions in default branch (manual) | `[MARKER-1C-READ]` |
| #11 | 1D — Instructions in both branches (auto) | `[MARKER-1C-READ]` |
| #7 | 2A — Basic Agent Skill | `[MARKER-1C-READ]` `[SKILL-2A-ACTIVE]` |
| #9 | 2B — Skill with Sub-Skill | `[MARKER-1C-READ]` `[SKILL-2B-MAIN]` `[SUB-SKILL-2B-SEVERITY]` |
| #12 | 3A — Skill in PR branch only | `[MARKER-1C-READ]` only (no skill markers) |
| #13 | 3B — Skills consistency check (no skill changes) | `[MARKER-1C-READ]` `[SKILL-2A-ACTIVE]` `[SKILL-2B-MAIN]` |

### Key Conclusions

1. **Copilot always reads `copilot-instructions.md` from the default branch.** Even when the PR branch contains a different version of the file (Test 1D: PR had `[MARKER-1D-READ]`, default had `[MARKER-1C-READ]`), Copilot used the default branch version.

2. **Agent Skills work for code review** — this is undocumented. Skills in `.github/skills/` on the default branch are read and followed during code review, not just in coding agent/CLI/VS Code.

3. **Skills must be in the default branch.** A skill that exists only in the PR branch (Test 3A) was not read.

4. **Sub-skill reading is non-deterministic.** The `[SUB-SKILL-2B-SEVERITY]` marker appeared in Test 2B but not in Test 3B, even though the sub-skill file exists in the default branch for both.

5. **PRs that modify `.github/skills/` may suppress skill reading entirely.** In Test 3A, even existing default-branch skills (`[SKILL-2A-ACTIVE]`, `[SKILL-2B-MAIN]`) did not trigger, possibly because the PR itself added a new skill file.

### Prerequisites

- **Copilot Pro** plan or higher (code review is not available on the free tier)
- Auto-review requires a branch ruleset configured **before** the PR is created
- Enable Copilot code review in repo settings (Settings → Copilot → Code review → enable custom instructions)

---

## Test Details

### Test 1: When does Copilot read `copilot-instructions.md`?

Each PR includes a simple Python file with an intentional issue (to give Copilot something to review). The instruction file contains a unique marker phrase that Copilot MUST output if it reads the file.

#### Test 1A — Instructions in PR branch only, manual review request

**Branch:** `test/1a-instructions-pr-branch-manual` | **PR:** #1

**Setup:** `.github/copilot-instructions.md` with `[MARKER-1A-READ]` exists only in PR branch (not in master at time of branch creation). `copilot-instructions.md` with `[MARKER-1C-READ]` was later merged into master via Test 1C setup.

**Result:** `[MARKER-1C-READ]` — Copilot read from default branch, not PR branch.

#### Test 1B — Instructions in PR branch only, auto-requested review

**Branch:** `test/1b-instructions-pr-branch-auto` | **PR:** #10

**Setup:** Same as 1A but with `[MARKER-1B-READ]` marker and auto-review via ruleset.

**Note:** Auto-review required: (1) ruleset set to Active, (2) PR created after ruleset, (3) non-empty commits.

**Result:** `[MARKER-1C-READ]` — Copilot read from default branch.

#### Test 1C — Instructions merged into default branch, manual review request

**Branch:** `test/1c-instructions-default-branch-manual` | **PR:** #4

**Setup:** `copilot-instructions.md` with `[MARKER-1C-READ]` merged into master first (via PR #3). PR only adds `helpers.py`.

**Result:** `[MARKER-1C-READ]` — Copilot read from default branch (as expected).

#### Test 1D — Instructions in both branches, auto-requested review

**Branch:** `test/1d-instructions-default-branch-auto` | **PR:** #11

**Setup:** Default branch has `[MARKER-1C-READ]`, PR branch updates to `[MARKER-1D-READ]`. This is the most revealing test.

**Result:** `[MARKER-1C-READ]` — **Copilot reads from default branch even when the PR branch has a different version.**

### Test 2: Agent Skills and Sub-Skills

#### Test 2A — Basic Skill

**Branch:** `test/2a-agent-skill` | **PR:** #7

**Setup:** `.github/skills/review-marker/SKILL.md` with `[SKILL-2A-ACTIVE]` merged into master (via PR #6). PR only adds `service.py`.

**Result:** `[MARKER-1C-READ]` `[SKILL-2A-ACTIVE]` — Both instructions and skill were read from default branch.

#### Test 2B — Skill with Sub-Skill

**Branch:** `test/2b-agent-sub-skill` | **PR:** #9

**Setup:** `.github/skills/security-review/SKILL.md` (`[SKILL-2B-MAIN]`) and sub-skill (`[SUB-SKILL-2B-SEVERITY]`) merged into master (via PR #8). PR only adds `api.py`.

**Result:** `[MARKER-1C-READ]` `[SKILL-2B-MAIN]` `[SUB-SKILL-2B-SEVERITY]` — All three markers appeared. Sub-skills work.

### Test 3: Follow-up Tests

#### Test 3A — Skill in PR branch only

**Branch:** `test/3a-skill-pr-branch-only` | **PR:** #12

**Setup:** New skill `pr-only-marker` with `[SKILL-PR-ONLY]` exists only in PR branch. PR also adds `worker.py`.

**Result:** `[MARKER-1C-READ]` only — PR-branch-only skill was not read. Notably, existing default-branch skills also did not trigger.

#### Test 3B — Skills consistency check (no skill changes in PR)

**Branch:** `test/3b-skills-consistency-check` | **PR:** #13

**Setup:** No changes to `.github/skills/`. PR only adds `cache.py`.

**Result:** `[MARKER-1C-READ]` `[SKILL-2A-ACTIVE]` `[SKILL-2B-MAIN]` — Default-branch skills triggered (but sub-skill `[SUB-SKILL-2B-SEVERITY]` did not this time).
