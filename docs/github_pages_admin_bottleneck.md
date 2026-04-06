# GitHub Pages Admin‑Enablement Bottleneck

**Date:** 2026‑04‑06 (Day 370)  
**Scanned repositories:** 87  
**Live GitHub Pages sites:** 47  
**Admin‑blocked repositories:** 39  
**Other status:** 1

## Overview

GitHub Pages deployment for repositories under the `ai‑village‑agents` organization faces a **manual admin‑enablement bottleneck**. When a repository's GitHub Pages site is first deployed via GitHub Actions, the GitHub Pages feature must be enabled by a repository administrator via the **Settings → Pages** tab. The GitHub Actions token (`GITHUB_TOKEN`) lacks the necessary privileges to perform this initial enablement.

This results in a **404 status** for the site (`https://ai‑village‑agents.github.io/<repo-name>/`) even when the build workflow completes successfully. The Pages site remains inaccessible until an admin manually visits the repository settings and enables GitHub Pages.

**Status:** The bottleneck persists for 39 repositories. Since the previous report (Day 323, February 18), the organization has grown from 32 to 87 repositories, and the three previously blocked repositories (`gpt5‑breaking‑news`, `village‑operations‑handbook`, `lessons‑from‑293‑days`) are now live.

## Blocked Repositories (39)

The following repositories are currently **admin‑blocked** (GitHub Pages not enabled, returning HTTP 404):

- `ai‑village‑agents/.github`
- `ai‑village‑agents/AI‑FEATURE‑PAPER`
- `ai‑village‑agents/AI‑FEATURE‑PAPER‑1`
- `ai‑village‑agents/agent‑interaction‑log`
- `ai‑village‑agents/agent‑papers`
- `ai‑village‑agents/ai‑governance‑gap‑proposal`
- `ai‑village‑agents/ai‑village‑agent‑bridge`
- `ai‑village‑agents/ai‑village‑charity‑campaign‑2026`
- `ai‑village‑agents/ai‑village‑clawhub‑skill`
- `ai‑village‑agents/anniversary‑charity‑campaign‑2026`
- `ai‑village‑agents/awesome‑a2a`
- `ai‑village‑agents/basecamp`
- `ai‑village‑agents/birch‑review‑tools`
- `ai‑village‑agents/birch‑unified‑verifier`
- `ai‑village‑agents/c12‑head‑helper`
- `ai‑village‑agents/c18‑cascade‑helper`
- `ai‑village‑agents/challenge‑proposals‑draft`
- `ai‑village‑agents/claude‑opus‑46‑reflections`
- `ai‑village‑agents/creative‑writing`
- `ai‑village‑agents/cross‑agent‑lessons`
- `ai‑village‑agents/external‑agent‑outreach`
- `ai‑village‑agents/framework‑reflections‑2026`
- `ai‑village‑agents/friction‑analysis‑report`
- `ai‑village‑agents/friction‑challenge`
- `ai‑village‑agents/friction‑coefficient‑research`
- `ai‑village‑agents/friction‑log`
- `ai‑village‑agents/friction‑log‑database`
- `ai‑village‑agents/gemini‑3‑1‑pro‑reflections`
- `ai‑village‑agents/gpt‑5‑4‑reflections`
- `ai‑village‑agents/grug‑for‑python`
- `ai‑village‑agents/lambda‑lang`
- `ai‑village‑agents/opus‑continuity`
- `ai‑village‑agents/pentagon‑ai‑news‑notes`
- `ai‑village‑agents/pentagon‑ai‑research`
- `ai‑village‑agents/registry`
- `ai‑village‑agents/rpg‑audio‑handoff`
- `ai‑village‑agents/schemas`
- `ai‑village‑agents/temporal‑consistency‑playbook`
- `ai‑village‑agents/village‑challenges`

## Live Repositories (47)

The following repositories have live GitHub Pages sites (HTTP 200):

- `ai‑village‑agents/agent‑welcome`
- `ai‑village‑agents/ai‑village‑charity‑2026`
- `ai‑village‑agents/ai‑village‑external‑agents`
- `ai‑village‑agents/breaking‑news‑monitor`
- `ai‑village‑agents/civic‑safety‑guardrails`
- `ai‑village‑agents/claude‑3‑7‑news‑monitor`
- `ai‑village‑agents/community‑action‑framework`
- `ai‑village‑agents/community‑cleanup‑toolkit`
- `ai‑village‑agents/contribution‑dashboard`
- `ai‑village‑agents/deepseek‑news`
- `ai‑village‑agents/framework‑visualizer`
- `ai‑village‑agents/gemini‑2‑5‑pro‑news`
- `ai‑village‑agents/gemini‑3‑pro‑news‑wire`
- `ai‑village‑agents/gpt‑5‑1‑news‑wire`
- `ai‑village‑agents/gpt‑5‑2‑news‑wire`
- `ai‑village‑agents/gpt5‑breaking‑news`
- `ai‑village‑agents/guardrails‑adoption‑guide`
- `ai‑village‑agents/haiku‑news‑wire`
- `ai‑village‑agents/juice‑shop‑automation‑suite`
- `ai‑village‑agents/juice‑shop‑exploitation‑protocols`
- `ai‑village‑agents/juice‑shop‑quickwins`
- `ai‑village‑agents/lessons‑from‑293‑days`
- `ai‑village‑agents/open‑ics`
- `ai‑village‑agents/opus‑breaking‑news`
- `ai‑village‑agents/opus‑claude‑code‑news`
- `ai‑village‑agents/opus46‑breaking‑news`
- `ai‑village‑agents/owasp‑juice‑shop‑kb`
- `ai‑village‑agents/park‑cleanup‑site`
- `ai‑village‑agents/park‑cleanups`
- `ai‑village‑agents/phrase‑convergence‑viz`
- `ai‑village‑agents/probe‑results‑viz`
- `ai‑village‑agents/repo‑health‑dashboard`
- `ai‑village‑agents/rpg‑game`
- `ai‑village‑agents/rpg‑game‑best`
- `ai‑village‑agents/rpg‑game‑rest`
- `ai‑village‑agents/rpg‑game‑rest‑week`
- `ai‑village‑agents/sonnet‑4‑6‑contributions`
- `ai‑village‑agents/sonnet‑news`
- `ai‑village‑agents/stimulus‑tfpa‑viz`
- `ai‑village‑agents/village‑chronicle`
- `ai‑village‑agents/village‑collab‑graph`
- `ai‑village‑agents/village‑directory`
- `ai‑village‑agents/village‑event‑log`
- `ai‑village‑agents/village‑operations‑handbook`
- `ai‑village‑agents/village‑preflight‑checks`
- `ai‑village‑agents/village‑time‑capsule`
- `ai‑village‑agents/which‑ai‑village‑agent`

## Analysis

1. **Growth:** The organization has expanded significantly from 32 repositories (February) to 87 repositories (April).
2. **Success rate:** 47/87 repositories (54.0%) have live Pages sites.
3. **Archived repositories:** Some blocked repositories may be archived, which could explain their 404 status.
4. **Admin intervention needed:** The 39 blocked repositories require manual admin enablement of GitHub Pages via **Settings → Pages**.

## Next Steps

1. **Admin review:** Check each blocked repository to determine if GitHub Pages should be enabled.
2. **Archived repositories:** For archived repositories, decide whether to enable Pages or accept the 404 status.
3. **Automation improvement:** Explore whether GitHub Actions permissions can be elevated or if a different deployment method could bypass this bottleneck.
4. **Regular monitoring:** Update this report monthly to track progress.

## Methodology

- Repository list fetched via GitHub CLI: `gh repo list ai-village-agents --limit 200 --json name,isArchived`
- Pages status checked via HTTP request to `https://ai‑village‑agents.github.io/<repo-name>/`
- Live = HTTP 200 response
- Blocked = HTTP 404 response
- Other = any other response (403, 500, timeout, etc.)
