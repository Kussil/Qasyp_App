# Build E6 — Dashboard Subagent

> Implements the user dashboard: match results page with cards, scores, and explanations.
> Runs inside an isolated worktree.

---

## Context

Read these files before starting:
- `.claude/CLAUDE.md` §9 — usability (mobile-first, responsive)
- `.claude/skills/api-spec/SKILL.md` — endpoint patterns
- `.claude/context/profile-schema.md` — profile fields displayed on cards

---

## Working Directory

```
.claude/worktrees/build-e6-dashboard/
```

---

## Stories to Implement

### E6-01: Match Results Page (Free Shortlist)
**Page:** `/dashboard`
**Layout:** Sidebar navigation + main content area
**Components:**
- **DashboardHeader** — greeting with user name, role badge (Buyer/Supplier)
- **MatchResultsList** — grid/list of match cards
- **MatchCard** — individual match card showing:
  - Company name
  - Industry sector badge
  - Operating regions (tags)
  - Match score (percentage badge, color-coded: >80% green, >60% amber, <60% grey)
  - 1–2 sentence explanation text
  - "View details" button (placeholder for future expansion)
- **EmptyState** — shown when user has no matches yet (prompt to complete survey)
- **LoadingState** — skeleton cards while API loads

**Data Flow:**
1. Page loads → call `GET /api/v1/matches?limit=20`
2. If user has no profile → show EmptyState with link to /onboarding/survey
3. If matches returned → render MatchCard grid
4. If `has_more: true` → show locked cards from E4 paywall
5. Handle loading and error states gracefully

**Responsive Design (mobile-first):**
- Mobile (< 640px): single column, full-width cards
- Tablet (640–1024px): two-column grid
- Desktop (> 1024px): three-column grid with sidebar visible

### E6-02: Seed Data — Demo Profiles (backend only, listed here for dashboard dependency)
This story is handled by the `seed-demo-data` subagent. The dashboard depends on seed data
to display meaningful results during demos.

---

## Files to Create / Modify

### New Files
```
frontend/src/app/dashboard/page.tsx                # Full dashboard implementation
frontend/src/components/features/dashboard/
├── DashboardHeader.tsx
├── MatchResultsList.tsx
├── MatchCard.tsx
├── MatchScoreBadge.tsx
├── EmptyState.tsx
└── LoadingState.tsx
frontend/src/hooks/useMatches.ts                   # Hook: fetch and cache matches
frontend/src/lib/matches.ts                        # API calls for matches
```

### Modified Files
```
frontend/src/app/dashboard/layout.tsx              # Add sidebar with nav links
frontend/src/components/layout/Sidebar.tsx         # Add dashboard navigation items
frontend/src/i18n/kk.json                          # Add dashboard keys
frontend/src/i18n/ru.json                          # Add dashboard keys
frontend/src/i18n/en.json                          # Add dashboard keys
```

---

## Design Specifications

**Color Palette (match score badges):**
- Score > 80%: `#16a34a` (green-600) — "Excellent match"
- Score 60–80%: `#d97706` (amber-600) — "Good match"
- Score < 60%: `#6b7280` (gray-500) — "Potential match"

**Card Design:**
- White background, subtle shadow, rounded corners (8px)
- Company name: 16px bold
- Industry: small badge (pill shape, teal background)
- Regions: small tags, grey background
- Score: circular badge in top-right corner
- Explanation: 14px grey text, max 2 lines with ellipsis

**Empty State:**
- Illustration placeholder (simple SVG)
- Text: "Complete your profile survey to see matching partners"
- CTA button linking to /onboarding/survey

---

## Test Requirements

**Frontend tests** (if testing framework set up):
- MatchCard renders with all fields
- EmptyState shown when no matches
- Loading skeleton shown during fetch
- Score badge color matches threshold

**Backend** — no new endpoints (uses existing GET /matches from E3)

---

## Commit

```bash
git add -A
git commit -m "feat(E6): implement match results dashboard with responsive card grid

- Dashboard page with DashboardHeader and MatchResultsList
- MatchCard: company name, industry badge, regions, score badge, explanation
- MatchScoreBadge with color-coded thresholds (green/amber/grey)
- EmptyState for users without profiles
- LoadingState with skeleton cards
- Mobile-first responsive grid (1/2/3 columns)
- useMatches hook with loading/error state
- i18n labels for Kazakh, Russian, English

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] Dashboard page renders match cards from API
- [ ] Each card shows: company name, industry, regions, score, explanation
- [ ] Score badge color-coded by threshold
- [ ] Empty state with survey link when no matches
- [ ] Loading skeleton while fetching
- [ ] Responsive: 1 column mobile, 2 tablet, 3 desktop
- [ ] Integrates with E4 paywall (locked cards visible if free user)
- [ ] i18n keys added for all three languages
- [ ] `npm run lint` passes
