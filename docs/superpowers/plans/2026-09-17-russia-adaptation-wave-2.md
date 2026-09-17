# Russia Adaptation Wave 2 Implementation Plan

**Goal:** Complete the next seven sections of the Russian edition: 02, 03, 04, 06, 10, 11 and 12.

**Architecture:** Keep the same `book/NN-*.md` paths, hidden cost-tag syntax and Russian card fields established in wave 1. Universal scientific evidence may remain international; all Russian legal, administrative, financial and business claims require current Russian sources and a freshness marker.

## Sections

- 02 — health habits: smoking, alcohol, exercise, sleep, diet, sedentary behavior.
- 03 — energy and cognitive load: sleep debt, multitasking, notifications, interruptions, conflict and decision fatigue.
- 04 — time: sunk costs, meetings, procrastination, notifications and low-value recurring work.
- 06 — negative list: interventions/products that look useful but have poor evidence or poor cost-benefit.
- 10 — relationships and marriage: keep evidence-based relationship material; replace China-specific marriage/property rules with Russian family/civil law where needed.
- 11 — legal risks for developers and technical specialists: personal data, software piracy, unauthorized access, malware, trade secrets and employment/IP boundaries under Russian law.
- 12 — business and entrepreneurship: registration, tax regime selection, consumer rules, online cash registers, personal data and basic contractor/employment distinctions in Russia.

## Verification

- Every completed card has `Стоимость`, `Простыми словами`, `Польза`, `Доказательность`, `Источник`.
- Hidden cost tags remain in upstream machine format.
- Russia-specific cards include `Актуальность РФ проверена: 17.09.2026.`.
- No Chinese government domains in completed sections.
- `docs/RUSSIA-MIGRATION.md` marks exactly the completed sections as `complete`.
- `python -m unittest tools.test_check_russia_adaptation -v` passes.
- `python tools/check_russia_adaptation.py` passes.
- Open a PR from `russia-adaptation-wave-2` to `main` only after CI is green.