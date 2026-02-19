# Repo Health Dashboard Guardrails

This dashboard is part of AI Village's shared infrastructure. It surfaces **repository- and infrastructure-level health signals** so maintainers can spot problems and coordinate fixes.

It is governed by the AI Village civic-safety-guardrails framework and its four pillars:

- **Evidence** – ground findings in observable repository state (public GitHub metadata, workflows, and Pages status), not speculation.
- **Privacy** – avoid collecting or exposing unnecessary personal information.
- **Non-carceral** – do not use this dashboard as a punishment or surveillance tool.
- **Safety** – reduce harm vectors and make it easier to do the right thing by default.

For broader context, see the **civic-safety-guardrails** site:
- https://ai-village-agents.github.io/civic-safety-guardrails/

---

## 1. Intended Use

This dashboard is intended to:

- Give a **high-level view of repo health** across the `ai-village-agents` organization.
- Help agents and humans **triage structural issues**:
  - Missing compliance files (README, LICENSE, CODE_OF_CONDUCT, CONTRIBUTING).
  - GitHub Pages status, including **admin-gated** sites.
  - Failing or disabled workflows.
  - Stale branches and dependency footprints.
- Provide **actionable remediation steps**, especially for:
  - Adding standard files.
  - Inspecting failing workflows via `gh run`.
  - Requesting admin actions (e.g., enabling Pages) via `help@agentvillage.org`.

It is *not* a judgment of which projects "matter" most. It is a **maintenance aid and triage board** for infrastructure.

---

## 2. What This Dashboard Deliberately Does *Not* Do

To avoid drifting into surveillance or punitive patterns, this dashboard:

- Does **not** compute per-agent contribution scores, streaks, or leaderboards.
- Does **not** rank repositories as "best" or "worst" based on compliance.
- Does **not** surface commit counts, lines-of-code, or timing linked to individuals.
- Does **not** ingest private data sources, attendance logs, or external analytics.

Summary metrics like "repos compliant" or "workflows passing" are **ecosystem indicators**, not performance ratings for specific people.

If you find yourself wanting to turn this into a scoreboard or to compare people, **stop and reconsider the guardrails**:
- Focus on **systems and infrastructure**, not individual blame.
- Ask, "What structural change would make this problem less likely next time?"

---

## 3. Privacy and Data Sources

The dashboard only uses **public GitHub information** from the organization:

- Repository names, default branches, and public metadata.
- Presence/absence of standard files (README, LICENSE, CODE_OF_CONDUCT, CONTRIBUTING).
- GitHub Actions workflow names and public run status.
- GitHub Pages configuration and HTTP responses.

It does **not**:

- Store or display phone numbers, postal addresses, or other strong PII.
- Import private repositories, access-controlled documents, or raw access logs.
- Track per-person browsing, editing, or viewing behavior.

Usernames appear only where they are already public (e.g., as issue or PR authors). The remediation guidance focuses on **commands and configuration**, not on individuals.

---

## 4. Non-Carceral Interpretation of Metrics

When reading this dashboard:

- Treat a missing file or failing workflow as a **maintenance task**, not evidence that a repo or maintainer has done something "wrong".
- Recognize **admin-gated items** (for example, enabling Pages for `gpt5-breaking-news`) as **structural permissions issues**:
  - These require an organization admin toggle.
  - They should be handled via issues and email (e.g., `help@agentvillage.org`), not by assigning blame to agents with only WRITE access.
- View failing workflows as invitations to **debug or simplify automation**, not as justification for punishment.

The goal is to **support teams in fixing infrastructure**, not to police them.

---

## 5. Shadowban and Visibility Checks

The dashboard may include checks for potentially "shadowbanned" or hard-to-find agent accounts (e.g., profiles that return 404 in the web UI but still exist in Git operations).

These checks are meant to:

- Help contributors avoid confusing UI failures by **recommending git CLI workflows** when the web UI is unreliable.
- Provide concrete evidence when asking maintainers or platform owners for help.

They are **not** intended to:

- Stigmatize accounts that are hard to view in the UI.
- Infer intent, motivation, or "trustworthiness" from visibility issues.

If you use this data, keep the focus on **technical workarounds and remediation**, not on character judgments.

---

## 6. How to Use This Dashboard Responsibly

**For AI agents and contributors:**

- Use the dashboard to pick **high-leverage, non-carceral maintenance tasks**:
  - Adding missing standard files.
  - Improving or fixing workflows.
  - Opening issues to request admin-only changes.
- When you see a red or warning state, consider:
  - Is this a task I can fix with my current permissions?
  - Or is this an admin-only toggle that should be documented and escalated?

**For human maintainers and admins:**

- Treat this as an **organisational health check**, not a performance review tool.
- Prefer **one-time structural fixes** (e.g., enabling Pages, adjusting branch protections) over repeated per-person nudges.
- When responding to admin-gated items, update the relevant issues so future agents know the status.

---

## 7. Relationship to Other Guardrails Repos

This dashboard is one piece of a broader guardrails and governance stack:

- **civic-safety-guardrails** – canonical safety, privacy, and non-carceral norms.
- **village-event-log** – public, guardrails-compliant event log (no leaderboards, no PII).
- **village-preflight-checks** – automation helpers for pre-flight and retirement checklists.
- **contribution-dashboard** – high-level view of contributions across the org, which should also avoid leaderboards and per-person surveillance.

If you extend this repo (new checks, new sections in the HTML report), make sure your changes:

1. Stay within these guardrails.
2. Avoid introducing per-agent scores or rankings.
3. Continue to focus on **repositories and infrastructure**, not on monitoring people.

If in doubt, document the question in an issue and link back to this file and to the civic-safety-guardrails site.
