# Scaffold Frontend Subagent

> Creates the Next.js (TypeScript) project skeleton with pages, layouts, and i18n setup.
> Runs inside an isolated worktree. Produces the app shell — no feature logic.

---

## Context

Read these files before starting:
- `.claude/CLAUDE.md` §5 — technical stack (Next.js, TypeScript)
- `.claude/CLAUDE.md` §9 — usability targets (mobile-first, >70% survey completion)
- `.claude/CLAUDE.md` §10 — i18n conventions (Kazakh + Russian primary, English secondary)

---

## Working Directory

All file operations MUST use the worktree path:
```
.claude/worktrees/scaffold-frontend/
```

**Never** modify files in the repository root.

---

## What to Create

### Directory Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx             # Root layout with providers, i18n, metadata
│   │   ├── page.tsx               # Landing page (redirect to /auth/login or /dashboard)
│   │   ├── globals.css            # Tailwind imports + CSS custom properties
│   │   ├── auth/
│   │   │   ├── login/page.tsx     # Login page shell
│   │   │   └── register/page.tsx  # Registration page shell
│   │   ├── onboarding/
│   │   │   ├── role/page.tsx      # Role selection (Buyer / Supplier) shell
│   │   │   └── survey/page.tsx    # Survey wizard shell
│   │   ├── dashboard/
│   │   │   ├── page.tsx           # Match results dashboard shell
│   │   │   └── layout.tsx         # Dashboard layout with sidebar/nav
│   │   └── api/                   # Next.js API routes (proxy to FastAPI if needed)
│   │       └── health/route.ts    # Health check proxy
│   ├── components/
│   │   ├── ui/                    # Shared UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── Loading.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Sidebar.tsx
│   │   └── features/              # Empty — feature subagents add components here
│   │       └── .gitkeep
│   ├── lib/
│   │   ├── api.ts                 # Axios/fetch wrapper pointing to NEXT_PUBLIC_API_URL
│   │   ├── auth.ts                # Token storage, auth headers, refresh logic
│   │   └── constants.ts           # Shared constants (regions list, industries, roles)
│   ├── hooks/
│   │   ├── useAuth.ts             # Auth state hook (login, logout, currentUser)
│   │   └── useApi.ts              # Generic API call hook with loading/error state
│   ├── i18n/
│   │   ├── config.ts              # i18n configuration (kk, ru, en)
│   │   ├── kk.json                # Kazakh translations (shell — common keys only)
│   │   ├── ru.json                # Russian translations (shell — common keys only)
│   │   └── en.json                # English translations (shell — common keys only)
│   ├── types/
│   │   ├── auth.ts                # LoginRequest, RegisterRequest, TokenResponse
│   │   ├── user.ts                # User, Role, Tier
│   │   ├── profile.ts             # BusinessProfile, all enums from profile-schema.md
│   │   └── match.ts               # MatchResult, MatchListResponse
│   └── styles/
│       └── theme.ts               # Color palette, spacing, typography tokens
├── public/
│   ├── favicon.ico
│   └── logo.svg                   # Placeholder Qasyp logo (simple SVG)
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── .env.local.example
├── Dockerfile
└── .eslintrc.json
```

### Key Design Decisions

**Framework:** Next.js 14+ with App Router (not Pages Router).

**Styling:** Tailwind CSS. No component library — build from primitives.
Mobile-first: all components start at 375px and scale up.

**i18n:** Use `next-intl` or a lightweight JSON-based approach.
Three locale files: `kk.json`, `ru.json`, `en.json`.
Shell translations include only common keys:
- `common.login`, `common.register`, `common.submit`, `common.cancel`
- `common.buyer`, `common.supplier`, `common.loading`, `common.error`
- `nav.dashboard`, `nav.survey`, `nav.settings`
- Feature subagents add their own keys.

**API Client:** `lib/api.ts` — a thin wrapper around `fetch` that:
- Prefixes all URLs with `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000/api/v1`)
- Attaches JWT from cookie/localStorage
- Handles 401 by calling refresh token endpoint
- Throws typed errors

**TypeScript Types:** Mirror the backend Pydantic schemas exactly.
All enums from `profile-schema.md` are defined as TypeScript string literal unions.

**Page Shells:** Every page.tsx should render:
- A heading (i18n key)
- A brief placeholder text: "This page is under construction"
- The correct layout (auth pages = centered card, dashboard pages = sidebar layout)
- No actual forms or logic — feature subagents add that

### Dependency List (package.json)

```json
{
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "tailwindcss": "^3.4.0",
    "clsx": "^2.1.0",
    "next-intl": "^3.15.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "@types/react": "^18.3.0",
    "@types/node": "^20.12.0",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### Dockerfile

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
ENV PORT=3000
EXPOSE 3000
CMD ["node", "server.js"]
```

### .env.local.example

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_DEFAULT_LOCALE=ru
```

---

## Commit

```bash
git add -A
git commit -m "feat(scaffold): add Next.js frontend skeleton with i18n and page shells

- App Router with auth, onboarding, and dashboard page shells
- Tailwind CSS with mobile-first responsive setup
- i18n config with Kazakh, Russian, and English JSON files
- TypeScript types mirroring backend schemas and profile-schema.md
- API client wrapper with JWT auth and refresh logic
- Reusable UI primitives (Button, Input, Card, Badge, Loading)
- Dockerfile for production builds

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Output Checklist

- [ ] All directories and files created
- [ ] TypeScript types match profile-schema.md enums exactly
- [ ] i18n JSON files have all common keys in all three languages
- [ ] Every page.tsx renders a shell with i18n heading
- [ ] `lib/api.ts` points to `NEXT_PUBLIC_API_URL`
- [ ] Tailwind config includes custom color tokens
- [ ] `.env.local.example` documents all env vars
- [ ] `npm run lint` passes (ESLint)
- [ ] `npm run build` produces no TypeScript errors
- [ ] Committed with Conventional Commit format
