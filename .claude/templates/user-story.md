# User Story Template

> Copy this template for each new story. File as `sprint-{N}/story-{ID}.md` or add directly to the sprint brief.

---

## Story Title
_Short imperative title, e.g. "Collect VAT status during onboarding"_

## Epic
E{N} — {Epic Name}

## Story
**As a** {role: Buyer / Supplier / Pro User / Admin},
**I want to** {action},
**so that** {outcome / business value}.

## Acceptance Criteria
- [ ] {Criterion 1 — specific, testable}
- [ ] {Criterion 2}
- [ ] {Criterion 3}
- [ ] Error states and edge cases handled
- [ ] i18n strings added for all new UI copy (Kazakh + Russian)
- [ ] Unit tests written (target: >70% coverage on new code)
- [ ] API endpoint documented in OpenAPI spec

## Definition of Done
- [ ] Code reviewed by at least one other team member
- [ ] Unit + integration tests passing
- [ ] Deployed to staging environment
- [ ] Acceptance criteria verified by PO or designated reviewer
- [ ] No hardcoded secrets introduced
- [ ] Commit message follows Conventional Commits format

## Estimate
`S` (< 1 day) / `M` (1–2 days) / `L` (3–5 days)

## Dependencies
_{List blocking stories, open decisions (from CLAUDE.md §11), or external integrations — or write "None"}_

## Notes
_{Technical notes, design links, relevant ADRs}_
