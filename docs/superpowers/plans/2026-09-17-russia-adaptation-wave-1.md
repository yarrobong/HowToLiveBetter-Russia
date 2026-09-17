# Russia Adaptation Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the fork into a visibly Russian edition and fully adapt the first country-dependent batch: README plus sections 1, 5, 7, 8, 9, 19 and 24.

**Architecture:** Preserve the upstream Markdown-first structure and the static `index.html` parser. Keep internal Chinese filenames in wave 1 to reduce upstream merge conflicts, but translate user-visible headings and card fields to Russian. Every Russia-specific legal, financial, social and administrative claim must use a current primary/official source and include `Актуальность РФ проверена: 17.09.2026.`.

**Tech Stack:** Markdown, static HTML/JavaScript, Python 3 standard library for repository checks, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-17-russia-adaptation-design.md`

## Global Constraints

- Keep all 31 sections and the existing `book/01-*.md` … `book/31-*.md` structure.
- Preserve the existing hidden cost-tag syntax in wave 1 so `index.html` remains compatible.
- Do not import Chinese laws, prices, government services or administrative procedures into Russian cards.
- Prefer official Russian primary sources: official legal publication, government agencies, Gosuslugi, Bank of Russia, SFR, FNS, МВД, МЧС, Роспотребнадзор, Минздрав, Росстат.
- Keep WHO/Cochrane/peer-reviewed research where the evidence is jurisdiction-independent.
- Do not guess current sums, limits, deadlines, fines or eligibility rules.
- Mark regional rules explicitly as regional.
- Keep Unlicense and attribution to the upstream project.

---

### Task 1: Migration controls and automated structure audit

**Files:**
- Create: `docs/RUSSIA-MIGRATION.md`
- Create: `tools/check_russia_adaptation.py`
- Create: `tools/test_check_russia_adaptation.py`

**Interfaces:**
- Consumes: `README.md`, `book/*.md`, the card field conventions from the design spec.
- Produces: `python tools/check_russia_adaptation.py` with exit code 0 on structural success and non-zero on violations; `docs/RUSSIA-MIGRATION.md` as the source of truth for section status.

- [ ] **Step 1: Write failing tests** covering: exactly 31 `book/*.md` section files; target sections 1/5/7/8/9/19/24 exist; an adapted Russian card must contain `Стоимость`, `Простыми словами`, `Польза`, `Доказательность`, `Источник`; Russia-specific cards must contain the freshness marker; forbidden China-government domains are reported for sections marked complete.
- [ ] **Step 2: Run tests and confirm RED** with `python -m unittest tools.test_check_russia_adaptation -v`; expected failures because the checker and migration manifest do not yet exist.
- [ ] **Step 3: Implement the checker** using only Python standard library (`pathlib`, `re`, `sys`). It must print actionable file/line diagnostics and must not require network access.
- [ ] **Step 4: Create migration manifest** with all 31 section numbers and statuses `not-started`, `in-progress`, or `complete`; set 1/5/7/8/9/19/24 to `in-progress` and the rest to `not-started`.
- [ ] **Step 5: Run tests and checker**; expected: unit tests pass and checker reports remaining localization violations without treating in-progress sections as complete.
- [ ] **Step 6: Commit** with `chore: add Russia migration checks`.

### Task 2: Russian project front page and methodology

**Files:**
- Modify: `README.md`
- Create: `docs/RUSSIA-SOURCES.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: design spec and source policy.
- Produces: Russian project identity, contributor rules for Russian claims, and an explicit upstream attribution.

- [ ] **Step 1: Add checker expectations** for Russian project title, upstream attribution, source-policy link and freshness rule.
- [ ] **Step 2: Run tests and confirm RED** because current README is Chinese and lacks Russian policy text.
- [ ] **Step 3: Rewrite README user-facing introduction and reading guide in Russian** while preserving the 31-section table and parser-discoverable links to `book/*.md`.
- [ ] **Step 4: Create `docs/RUSSIA-SOURCES.md`** describing source hierarchy, freshness dates, federal-vs-regional labeling, international evidence reuse and verification workflow.
- [ ] **Step 5: Update repository working rules** in `CLAUDE.md` with Russian-edition constraints without deleting upstream evidence-quality rules.
- [ ] **Step 6: Re-run checker/tests**; expected: project-level Russian metadata checks pass.
- [ ] **Step 7: Commit** with `docs: establish Russian edition rules`.

### Task 3: Section 1 — safety and prevention

**Files:**
- Modify: `book/01-不要早死.md`
- Modify: `docs/RUSSIA-MIGRATION.md`

**Interfaces:**
- Consumes: universal evidence from upstream plus current official Russian safety/health sources.
- Produces: a Russian-language section 1 with every card classified as universal/adapted/replaced/removed in migration notes.

- [ ] **Step 1: Inventory every card** and classify it as universal, Russia-adaptable, Russia-replacement or China-only.
- [ ] **Step 2: Verify current Russian sources** for emergency number/response, road safety, fire/gas safety, vaccination/screening and other country-dependent items; keep international primary evidence where appropriate.
- [ ] **Step 3: Rewrite all user-visible card text in Russian** using the required fields and preserving hidden cost tags.
- [ ] **Step 4: Add freshness markers** to every Russia-specific administrative/legal card.
- [ ] **Step 5: Run checker** and manually inspect every source/number changed in this section.
- [ ] **Step 6: Mark section 1 complete** in migration manifest only when the checker finds no China-government references in it.
- [ ] **Step 7: Commit** with `content: adapt safety section for Russia`.

### Task 4: Section 5 — money and consumer finance

**Files:**
- Modify: `book/05-不要浪费钱.md`
- Modify: `docs/RUSSIA-MIGRATION.md`

**Interfaces:**
- Consumes: Bank of Russia, FNS, SFR, official consumer-protection sources plus jurisdiction-independent evidence.
- Produces: Russian money/consumer-finance guidance.

- [ ] Inventory cards and remove China-only financial infrastructure.
- [ ] Verify current Russian banking, deposits, fraud-prevention, pension, insurance and consumer rules from official sources.
- [ ] Rewrite all cards in Russian, preserving evidence grades and cost tags.
- [ ] Add freshness markers to Russian financial/regulatory cards.
- [ ] Run checker and source audit; then mark section complete.
- [ ] Commit with `content: adapt money section for Russia`.

### Task 5: Section 7 — no-money / social safety net

**Files:**
- Modify: `book/07-没钱的时候怎么活.md`
- Modify: `docs/RUSSIA-MIGRATION.md`

**Interfaces:**
- Consumes: SFR, Работа России, Госуслуги, МЧС/municipal emergency resources, federal/regional social-support sources.
- Produces: actionable Russian unemployment, benefits, documents, emergency housing and assistance guidance.

- [ ] Inventory all upstream cards and map each to a Russian analogue or removal.
- [ ] Verify unemployment benefits, social assistance, OMS continuity, identity-document recovery and public employment services from official sources.
- [ ] Clearly label region-dependent benefits and avoid presenting local sums as federal.
- [ ] Rewrite section, add freshness markers, run checker/source audit, mark complete.
- [ ] Commit with `content: adapt social safety net section for Russia`.

### Task 6: Sections 8 and 9 — legal/property safety and common legal red lines

**Files:**
- Modify: `book/08-别把自己搭进去.md`
- Modify: `book/09-普通人容易踩的法律红线.md`
- Modify: `docs/RUSSIA-MIGRATION.md`

**Interfaces:**
- Consumes: current Russian codes/laws and official law-enforcement/judicial guidance.
- Produces: Russian legal-risk guidance with process costs and no unsupported legal conclusions.

- [ ] Classify every card by Russian applicability.
- [ ] Verify cited Russian legal rules from official texts; record article/law identifiers and current effective status.
- [ ] Rewrite cards so civil/administrative/criminal consequences are not conflated.
- [ ] For any “the law protects you” card, include realistic process cost/time caveats required by the upstream project rules.
- [ ] Add freshness markers, run checker and source audit, mark both sections complete.
- [ ] Commit with `content: adapt legal safety sections for Russia`.

### Task 7: Section 19 — employment, dismissal and work injury

**Files:**
- Modify: `book/19-在职离职和工伤.md`
- Modify: `docs/RUSSIA-MIGRATION.md`

**Interfaces:**
- Consumes: ТК РФ, Роструд/Онлайнинспекция, СФР and official work-injury regulations.
- Produces: Russian employment rights, dismissal compensation, leave/overtime and workplace-injury guidance.

- [ ] Map upstream employment cards to Russian labor-law equivalents.
- [ ] Verify current statutory deadlines, compensation formulas and injury procedures.
- [ ] Rewrite in Russian and distinguish statutory federal rules from employer-specific benefits.
- [ ] Add freshness markers, run checker/source audit, mark complete.
- [ ] Commit with `content: adapt employment section for Russia`.

### Task 8: Section 24 — healthcare navigation

**Files:**
- Modify: `book/24-看病.md`
- Modify: `docs/RUSSIA-MIGRATION.md`

**Interfaces:**
- Consumes: Минздрав, ФФОМС/territorial OMS sources, official clinical/triage guidance and jurisdiction-independent medical evidence.
- Produces: Russian healthcare-navigation guidance without replacing clinical advice with administrative rules.

- [ ] Classify universal clinical advice versus Russia-specific routing/payment cards.
- [ ] Verify OMS, emergency care, referral/triage and disability-assessment processes from current official sources.
- [ ] Rewrite all user-visible text in Russian and add freshness markers to Russia-specific system guidance.
- [ ] Run checker/source audit, mark complete.
- [ ] Commit with `content: adapt healthcare navigation for Russia`.

### Task 9: Russian static search UI

**Files:**
- Modify: `index.html`
- Modify: `tools/test_check_russia_adaptation.py`

**Interfaces:**
- Consumes: Russian README/book cards while retaining upstream hidden-tag syntax.
- Produces: Russian UI labels, project title, freshness display and unchanged static/no-build architecture.

- [ ] Write failing tests/HTML assertions for Russian title and labels plus continued recognition of existing hidden cost tags.
- [ ] Run tests and confirm RED.
- [ ] Translate UI strings and add freshness-marker rendering without changing the card-source format.
- [ ] Run tests/checker and manually verify README-driven section discovery remains intact.
- [ ] Commit with `feat: localize search UI for Russia`.

### Task 10: Wave-1 verification and review

**Files:**
- Modify only files required to fix verification findings.

**Interfaces:**
- Consumes: all previous tasks.
- Produces: a reviewable branch/PR with seven completed sections and a functioning Russian front end.

- [ ] Run `python -m unittest tools.test_check_russia_adaptation -v`.
- [ ] Run `python tools/check_russia_adaptation.py` and require exit code 0 for all sections marked `complete`.
- [ ] Verify the migration manifest marks exactly 1/5/7/8/9/19/24 complete for wave 1.
- [ ] Search completed sections for Chinese official-government domains and unresolved China-specific administrative references; expected: none.
- [ ] Check every Russia-specific numeric/legal claim against its cited source and date.
- [ ] Compare branch to `main` and confirm unrelated sections were not rewritten.
- [ ] Open a PR from `russia-adaptation-wave-1` to `main` with a checklist of completed sections and known remaining 24 sections.
