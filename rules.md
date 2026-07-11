# AgentLens Parallel Development and Merge-Safety Rules

The purpose of this document is to prevent merge conflicts while both members
work inside one repository.

## Ownership Table

| Path | Primary owner |
| --- | --- |
| `frontend/` | Member 1 |
| `backend/` | Member 2 |
| `data/` | Member 2 |
| `scripts/` | Member 2 |
| `contracts/` | Shared |
| `docs/` | Shared |
| Root configuration | Shared |
| `README.md` | Shared |
| `guideline.md` | Shared |
| `rules.md` | Shared |

Rules:

- Member 1 must not normally edit `backend/`.
- Member 2 must not normally edit `frontend/`.
- Cross-ownership edits require advance communication.
- Reviewing the other member's files is allowed.
- Emergency fixes require notifying the owner first.

## Shared-File Reservation

Before editing a shared file, send:

```text
Reserving: <file>
Purpose: <reason>
Branch: <branch>
Estimated time: <time>
```

After editing:

```text
Released: <file>
Branch: <branch>
Commit: <hash>
Summary: <change>
```

Only one member edits a shared file at a time.

## One Feature, One Branch

Examples:

```text
feature/frontend-shell
feature/control-tower
feature/agent-detail
feature/backend-foundation
feature/liquidity-engine
feature/anomaly-engine
feature/data-quality
feature/case-workflow
feature/scenario-engine
fix/<description>
docs/<description>
```

No direct coding on `main`.

## Branch Creation

```bash
git checkout main
git pull origin main
git status
git checkout -b feature/<task-name>
```

Do not branch from an unfinished feature branch unless coordinated.

## Small Branch Rule

Branches should:

- Contain one focused feature.
- Avoid unrelated formatting.
- Avoid unnecessary root-file changes.
- Be merged frequently.
- Include relevant tests.
- Normally stay open for less than one working day during the hackathon.

## High-Conflict Root Files

Only one member may edit these at a time:

```text
README.md
guideline.md
rules.md
.gitignore
.editorconfig
contracts/*
docs/api/*
```

Frontend high-conflict files:

```text
frontend/package.json
frontend/package-lock.json
frontend/src/app/layout.tsx
frontend/src/app/globals.css
frontend/tsconfig.json
frontend/next.config.ts
```

Backend high-conflict files:

```text
backend/pyproject.toml
backend/.env.example
backend/app/main.py
backend/app/api/router.py
backend/app/api/v1/router.py
backend/app/core/config.py
backend/app/db/migrations/*
```

## Pull and Rebase Rule

Before opening a pull request:

```bash
git fetch origin
git rebase origin/main
```

Member 1 runs:

```bash
cd frontend
npm run lint
npm run build
```

Member 2 runs:

```bash
cd backend
ruff check .
ruff format --check .
mypy app
pytest
```

## API Contract Protocol

Before changing an API:

```text
Endpoint:
Method:
Current request:
New request:
Current response:
New response:
Reason:
Breaking change: Yes/No
Frontend impact:
Backend impact:
```

Update order:

1. Agree on contract.
2. Update backend Pydantic schema.
3. Update backend implementation.
4. Update backend tests.
5. Update contract example or OpenAPI document.
6. Update frontend type.
7. Update frontend integration.
8. Run end-to-end verification.

Never rename response fields independently.

## Protected Domain Values

Do not independently modify:

```text
Provider
AlertStatus
CaseStatus
Severity
PressureLevel
DataHealthStatus
UserRole
AlertType
CaseOutcome
```

## Dependency Rules

Frontend dependency changes require reserving:

```text
frontend/package.json
frontend/package-lock.json
```

Backend dependency changes require reserving:

```text
backend/pyproject.toml
```

Before adding a package, communicate:

```text
Package:
Application:
Purpose:
Why existing tools are insufficient:
Deployment impact:
```

## Migration Rules

Only Member 2 normally creates database migrations.

- Never edit an applied migration.
- Create a new migration for schema changes.
- Do not generate migrations simultaneously on separate branches.
- Inform Member 1 when a schema change affects API responses.
- Never commit database secrets.

## Formatting Rules

- Do not run repository-wide formatting for one feature.
- Format only modified application files.
- Do not combine functional changes with broad formatting.
- Do not combine dependency changes with unrelated features.

## Rename and Deletion Rules

Before moving, renaming, or deleting:

1. Search all references.
2. Inform the other member.
3. Check active branches.
4. Make the change in one focused commit.
5. Run validation.
6. Merge quickly.

Never delete another member's work without discussion.

## Conflict Resolution

When a conflict occurs:

1. Stop editing the conflicted file.
2. Read both versions.
3. Ask the other member when intent is unclear.
4. Preserve both valid changes.
5. Run validation again.
6. Review the resolved diff.

Do not blindly use:

```bash
git checkout --ours
git checkout --theirs
git reset --hard
git push --force
```

## Communication Template

Before starting:

```text
Task:
Branch:
Application: frontend/backend/shared
Files expected to change:
Shared files:
Estimated completion:
Dependency on other member:
```

After finishing:

```text
Task completed:
Branch:
Commit:
Files changed:
Validation:
API or integration notes:
```

## Integration Rule

Every completed feature should connect:

```text
Backend schema
-> Backend service
-> FastAPI endpoint
-> Frontend type
-> Frontend API client
-> UI
-> Test
```

Do not let the frontend remain on mocks while the backend independently develops
incompatible contracts.

## Product Safety Rules

Retain:

- No real customer information.
- No real wallet credentials.
- No real financial execution.
- No cross-provider balance conversion.
- No automatic fraud declaration.
- No account freezing.
- Provider boundaries must be enforced.
- Poor-quality data must reduce confidence.
- Important state changes must be audited.
- Authorization must be enforced by the backend.

## Frontend Visual System

All new or revised AgentLens frontend pages must follow this visual system.
The intended character is a calm, precise, luminous operations workspace: cool
neutral surfaces, near-black typography, pale blue and mint analytical accents,
compact navigation, and crisp white information panels. It must feel modern and
technical without looking like a cryptocurrency product, marketing site, or
generic admin template.

These rules are durable. A page-specific prompt may extend them but must not
silently replace them.

### Design Tokens

Use shared CSS variables or Tailwind theme tokens instead of repeating ad hoc
color values in components. Establish and reuse this palette:

```text
Page background:       #E9EEF5
Workspace surface:     #F5F8FC
Panel surface:         #FFFFFF
Subtle panel surface:  #F8FAFD
Primary text:          #171B24
Secondary text:        #667085
Muted text:            #8A94A6
Border:                #DCE4EE
Strong border:         #C8D3E1
Interactive blue:      #2F80ED
Pale blue:             #DCEBFF
Analytical mint:       #DDF4E4
Healthy green:         #68B96B
Watch amber:           #D9A441
Critical red:          #E34D67
Human-review violet:   #7468D8
Unknown gray:          #7C8798
```

- Use near-black, not navy, for primary headings and commands.
- Blue is the main interactive color, not the dominant page fill.
- Mint and pale blue may create a soft analytical atmosphere behind charts or
  active process visualizations.
- Red means operational urgency, never proof of fraud.
- Violet identifies human review or escalation.
- Gray identifies unknown, unavailable, or disabled states.
- Never communicate status through color alone; pair it with explicit text and
  where useful an icon or shape.
- Do not add purple-blue gradient buttons, decorative orbs, bokeh, or saturated
  full-page gradients.
- A subtle pale-blue-to-mint wash is allowed only inside a major analytical
  canvas. It must remain low contrast and must not reduce text readability.

### Typography and Copy

- Use the existing sans-serif stack, led by `Inter` when available.
- Use primary text color for headings and important numeric values.
- Page titles should be concise, left aligned, and approximately `32px` to
  `44px` on desktop with a compact line height. Do not scale type by viewport
  width.
- Panel titles should normally be `16px` to `20px`, semibold or bold.
- Body and table text should normally be `14px` to `16px` with comfortable line
  height.
- Metadata and helper text may be `12px` to `14px` but must remain readable.
- Letter spacing is `0`; do not use negative tracking.
- Prefer sentence case. Avoid all-caps headings except small table labels or
  short operational metadata.
- Text must be direct and operational: state what changed, why it matters, the
  confidence or limitation, and the next human action.
- Avoid marketing copy, dramatic claims, vague AI language, and excessive
  explanatory prose inside the interface.
- Never use accusatory language or present an AI recommendation as a confirmed
  fraud decision.

### Application Shell

- Desktop uses a slim, stable left navigation rail and a quiet top bar.
- Navigation should be icon-led where familiar icons exist, with accessible
  labels and tooltips. Use the project's icon library rather than hand-drawn
  SVG icons.
- The active navigation item uses a pale-blue surface and strong dark icon/text.
- The top bar may contain scenario context, search, notifications, role, and
  update status without becoming visually heavy.
- Main content uses a readable wide container with generous outer spacing and
  dense, aligned internal content.
- A right-side information rail is appropriate for page-level evidence,
  ownership, SLA, live status, or compact summaries. It must stack below the
  main content on smaller screens.
- Mobile replaces the fixed rail with compact horizontal navigation or a
  deliberate menu. Primary actions must remain reachable.

### Page Composition

Use this hierarchy when the page content supports it:

```text
Page identity and primary action
-> compact operational metrics
-> primary analysis or workflow canvas
-> evidence, context, and status panels
-> detailed tables, timeline, or secondary information
```

- Keep page sections unframed unless they are genuinely separate tools or
  repeated data items.
- Do not place cards inside cards.
- Use cards for individual metrics, repeated entities, compact summaries,
  modals, and framed workflow controls.
- Align headings, values, and actions to a consistent grid.
- Preserve stable dimensions for charts, tables, icon controls, and status
  areas so loading or dynamic values do not shift the layout.
- Keep enough whitespace to separate decisions, but do not turn operational
  pages into sparse landing pages.

### Panels, Controls, and Status

- Panels use white or subtle cool-white surfaces, a `1px` cool-gray border, and
  minimal shadow. Shadows must be soft and secondary to borders.
- Standard card and panel radius is `8px` or less. Pills are reserved for
  statuses, filters, search, and compact segmented controls.
- Primary commands use a dark near-black or interactive-blue button with clear
  text. Secondary commands use a white surface and visible border.
- Icon-only buttons require a familiar symbol, an accessible label, and a
  tooltip when meaning is not obvious.
- Touch targets should be at least approximately `40px` high.
- Use segmented controls for modes, toggles for binary settings, menus for
  option sets, and tabs for peer views.
- Disabled controls must look unavailable and include a reason when the cause
  is not obvious.
- Loading states should use restrained skeletons or small progress indicators;
  no automatic decorative motion.
- Focus states must be clearly visible with the interactive blue.

### Data Display and Visualizations

- Numerical values are prominent but never oversized beyond the page hierarchy.
- Tables use quiet separators, strong column alignment, readable headers, and
  horizontal scrolling on narrow screens.
- Charts use thin blue, mint, green, amber, red, violet, and gray marks on a
  light background. Avoid heavy fills and chart junk.
- Every chart requires a textual interpretation and an accessible label or
  summary. Color cannot be the only differentiator.
- Confidence, data freshness, model version, and uncertainty should appear near
  the result they qualify.
- Use subtle dashed separators or reference lines for thresholds and baselines.
- A primary analytical canvas may use a restrained translucent blue/mint wash,
  but the real data, evidence, and status must remain inspectable.
- Do not copy the DNA imagery from the visual reference. AgentLens visuals must
  depict liquidity, demand, provider health, evidence, workflow, and time.

### Responsive and Accessibility Rules

- Desktop may use main-content and right-rail columns; tablet and mobile stack
  them in priority order.
- Provider cards may move from three columns to two and then one.
- Tables scroll horizontally rather than crushing text.
- Buttons wrap without overlap and remain reachable at all widths.
- Text must never overflow, clip, or overlap adjacent content.
- Use semantic landmarks, one `h1`, logical heading order, table headers, form
  labels, descriptive actions, and live regions for asynchronous updates.
- Maintain WCAG-readable contrast even when using pale surfaces and muted text.
- Respect reduced-motion preferences and never use flashing content.

### Consistency and Change Rules

- Reuse existing layout, panel, badge, metric, form, and chart-wrapper
  components before creating a variant.
- New visual patterns must be promoted to shared components or tokens when they
  appear more than once.
- Do not introduce page-local palettes, unrelated font families, or arbitrary
  radii.
- When touching an existing page, migrate the touched area toward this system
  without broad unrelated rewrites.
- Before completing a frontend page, inspect desktop and mobile layouts and
  confirm there is no overlap, clipping, broken navigation, or color-only
  status communication.
- This section governs future frontend prompts unless the repository owners
  explicitly update it together.

## Conflict-Safe Completion Checklist

```text
[ ] Work occurred on a dedicated branch.
[ ] Latest main was integrated.
[ ] Ownership boundaries were respected.
[ ] Shared files were reserved.
[ ] No unrelated files changed.
[ ] API contracts were agreed.
[ ] No broad formatting occurred.
[ ] Relevant validation passed.
[ ] Pull request was reviewed.
[ ] Main demo flow still works.
```
