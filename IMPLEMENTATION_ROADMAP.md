# Phase II Implementation Roadmap

**Purpose**: Visual guide showing task dependencies, parallelization opportunities, and critical path.

---

## Critical Path (MVP - Minimum Viable Product)

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE P1: FOUNDATION & SETUP (2-3 hours)                           │
│                                                                       │
│  T001: Backend project setup ────┐                                   │
│                                  │                                   │
│  T002: Database config ──────────┼──→ T003: Alembic init             │
│  T004: SQLModel entities ────────┼──→ T005: First migration          │
│  (T002, T003, T004 can run in parallel after T001)                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE P2: AUTHENTICATION (4-5 hours)                                │
│                                                                       │
│  T006: JWT utilities ─────────────────────────┐                      │
│  T007: Auth schemas ────────────────────────┐ │                      │
│  T008: AuthService ─────────────────────────┼─┼──┐                   │
│  T009: Auth routes ─────────────────────────┼─┼──┤ T010: CORS setup  │
│  (T006, T007, T008 can run in parallel)     └─┘  │                   │
│                                               │   │                   │
│                                               └───┘                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE P3: TASK API (3-4 hours)                                      │
│                                                                       │
│  T011: Task schemas ────────────────┐                                │
│  T012: TaskService ─────────────────┼──────────────┐                 │
│  T013: Task routes ─────────────────────────────┐  │                 │
│  (T011 and T012 can run in parallel)             │  │                 │
│                                                  └──┘                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ╔═══════════════════╗
                        ║  WORKING BACKEND  ║
                        ║  API Complete!    ║
                        ╚═══════════════════╝
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE P4: FRONTEND SETUP (2-3 hours)                                │
│                                                                       │
│  T014: Next.js init ────────────────┐                                │
│  T015: Better Auth config ─────────┬┼────────────────┐               │
│  T016: Auth hooks/types ───────────┤┼────────────────┤               │
│  T017: Routing & middleware ───────┴┼────────────────┘               │
│  (T015 and T016 can run in parallel after T014)                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE P5: FRONTEND UI (5-6 hours)                                   │
│                                                                       │
│  T018: Auth forms (Login/Register) ────┐                             │
│  T019: Task list & items ──────────────┼─────────┐                   │
│  T020: Task form & modal ──────────────┼─────────┼──┐                │
│  T021: Filters & sorting ──────────────┼─────────┤  │                │
│  T022: Dark mode toggle ───────────────┼─────────┤  │                │
│  (T019, T021, T022 can run in parallel after T018)   │                │
│                                        │         │  │                │
│                                        └─────────┘  │                │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE P6: INTEGRATION & POLISH (4-5 hours)                          │
│                                                                       │
│  T023: Wire mutations ─────────────────────────────────┐             │
│  T024: Toast notifications ─────────────────────────┐  │             │
│  T025: Delete confirmation ─────────────────────────┼──┘             │
│  T026: Loading states & errors ─────────────────────┤                │
│  T027: Standardize error responses ─────────────────┤                │
│  T028: Rate limiting ───────────────────────────────┤                │
│  T029: Input validation ────────────────────────────┤                │
│  T030: E2E testing & docs ──────────────────────────┤                │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ╔═══════════════════╗
                        ║  PRODUCTION MVP   ║
                        ║  Ready to Deploy! ║
                        ╚═══════════════════╝
```

---

## Full Dependency Graph

```
┌──────────┐
│   T001   │  Backend project setup
└────┬─────┘
     │
     ├─→ ┌──────────┐
     │   │   T002   │  Database config
     │   └────┬─────┘
     │        │
     │   ┌────┴──────┬──────────┬─────────┐
     │   ▼           ▼          ▼         ▼
     │  ┌──────┐  ┌──────┐  ┌──────┐ ┌────────┐
     │  │ T003 │  │ T004 │  │ T005 │ │ T006   │
     │  │      │  │      │  │      │ │ (JWT)  │
     │  └──────┘  └──────┘  └──────┘ └───┬────┘
     │                                    │
     └────────────────────────────────────┤
                                         │
                    ┌────────────────────┼───────────────┐
                    ▼                    ▼               ▼
                  ┌──────┐           ┌──────┐       ┌──────┐
                  │ T007 │           │ T008 │       │ T009 │
                  │(Schemas)         │(Service)     │(Routes)
                  └──────┘           └──────┘       └───┬──┘
                                       │               │
                                       └───────┬───────┘
                                               │
                                               ▼
                                           ┌──────┐
                                           │ T010 │ CORS setup
                                           └───┬──┘
                                               │
                    ┌──────────────────────────┼───────────────────┐
                    ▼                          ▼                   ▼
                  ┌──────┐               ┌──────┐           ┌──────┐
                  │ T011 │               │ T012 │           │ T013 │
                  │(Task schemas)        │(TaskService)     │(Task routes)
                  └──────┘               └──────┘           └───┬──┘
                                               │                 │
                                               └─────────┬───────┘
                                                         │
                    ════════════ BACKEND READY ══════════
                                         │
                    ┌────────────────────┼────────────────┐
                    ▼                    ▼                ▼
                  ┌──────┐           ┌──────┐       ┌──────┐
                  │ T014 │           │ T015 │       │ T016 │
                  │(Next.js init)    │(Better Auth) │(Hooks)
                  └───┬──┘           └──────┘       └──────┘
                      │                │               │
                      └────────────┬───┴───────────────┘
                                   │
                                   ▼
                               ┌──────┐
                               │ T017 │ Routing & middleware
                               └──┬───┘
                                  │
                    ┌─────────────┼──────────┬───────────────┐
                    ▼             ▼          ▼               ▼
                  ┌──────┐   ┌──────┐   ┌──────┐       ┌──────┐
                  │ T018 │   │ T019 │   │ T021 │       │ T022 │
                  │(Auth)│   │(List)│   │(Filter)      │(Theme)
                  └──────┘   └───┬──┘   └──────┘       └──────┘
                                  │
                                  ▼
                              ┌──────┐
                              │ T020 │ Task form
                              └───┬──┘
                                  │
                    ┌─────────────┬┴──────────┬─────────────┬──────────┐
                    ▼             ▼           ▼             ▼          ▼
                  ┌──────┐   ┌──────┐   ┌──────┐       ┌──────┐  ┌──────┐
                  │ T023 │   │ T024 │   │ T025 │       │ T026 │  │ T027 │
                  │(Mutations)│(Toast) │(Confirm)      │(Skele.) │(Errors)
                  └──────┘   └──────┘   └──────┘       └──────┘  └───┬──┘
                                                                      │
                    ┌─────────────────────────────────────────────────┤
                    ▼                                                 ▼
                  ┌──────┐                                       ┌──────┐
                  │ T028 │                                       │ T029 │
                  │(Rate limit)                                  │(Validation)
                  └──────┘                                       └──────┘
                                                                    │
                    ╔═══════════════════════════════════════════════╗
                    ║           T030: E2E Testing                   ║
                    ║      (All tasks must be complete first)       ║
                    ╚═══════════════════════════════════════════════╝
```

---

## Task Duration Estimates

### Phase P1: Foundation (2-3 hours)
| Task | Duration | Notes |
|------|----------|-------|
| T001 | 20 min | Project scaffolding |
| T002 | 20 min | Config setup |
| T003 | 15 min | Alembic init |
| T004 | 15 min | Model definitions |
| T005 | 10 min | Run migration |
| **P1 Total** | **1.5-2 hours** | Can parallelize T002, T003, T004 |

### Phase P2: Auth (4-5 hours)
| Task | Duration | Notes |
|------|----------|-------|
| T006 | 30 min | JWT utilities |
| T007 | 15 min | Schemas |
| T008 | 1 hour | Service logic |
| T009 | 1 hour | Routes + testing |
| T010 | 30 min | CORS + middleware |
| **P2 Total** | **3-3.5 hours** | Sequential (T006→T007→T008→T009→T010) |

### Phase P3: Task API (3-4 hours)
| Task | Duration | Notes |
|------|----------|-------|
| T011 | 15 min | Schemas |
| T012 | 1 hour | Service logic (CRUD + filtering) |
| T013 | 1.5 hours | Routes + validation |
| **P3 Total** | **2.5-3 hours** | T011 & T012 can run in parallel |

### Phase P4: Frontend Setup (2-3 hours)
| Task | Duration | Notes |
|------|----------|-------|
| T014 | 30 min | Next.js scaffolding |
| T015 | 30 min | Better Auth config |
| T016 | 30 min | Types + hooks |
| T017 | 45 min | Routing + middleware |
| **P4 Total** | **2.25-2.5 hours** | T015 & T016 can parallelize |

### Phase P5: Frontend UI (5-6 hours)
| Task | Duration | Notes |
|------|----------|-------|
| T018 | 1 hour | Auth forms |
| T019 | 1 hour | Task list display |
| T020 | 1 hour | Task form + modal |
| T021 | 45 min | Filters + sorting |
| T022 | 30 min | Dark mode |
| **P5 Total** | **4-4.5 hours** | T019, T021, T022 can parallelize |

### Phase P6: Polish (4-5 hours)
| Task | Duration | Notes |
|------|----------|-------|
| T023 | 1 hour | Wire mutations |
| T024 | 45 min | Toast system |
| T025 | 30 min | Delete dialog |
| T026 | 1 hour | Loading/error states |
| T027 | 45 min | Error standardization |
| T028 | 30 min | Rate limiting |
| T029 | 30 min | Input validation |
| T030 | 1 hour | Testing + docs |
| **P6 Total** | **5.5-6 hours** | Mostly sequential |

### Overall Timeline
- **Sequential Execution**: 18-22 hours
- **With Parallelization**: 14-17 hours
- **Recommended**: 2-3 days (5-7 hour days) for 1 developer, or 1-2 days with 2 developers

---

## Parallelization Opportunities

### Quick Wins (Run These in Parallel)

**After T001**:
- T002 (Database config) + T003 (Alembic) can run together
- T004 (SQLModel) can run alongside T002/T003

**After T008**:
- T006 (JWT) + T007 (Auth Schemas) can run in parallel

**After T014** (Next.js init):
- T015 (Better Auth) + T016 (Types/hooks) can parallelize

**After T018** (Auth forms):
- T019 (Task list) + T021 (Filters) + T022 (Dark mode) can parallelize

### Team Distribution (2 Developers)

**Developer A (Backend)**:
- Weeks 1: P1 (Foundation) → P2 (Auth) → P3 (Task API)
- Weeks 2: P6 (Backend polish: T027, T028, T029)
- ~10 hours total

**Developer B (Frontend)**:
- Week 1: Start P4 (Frontend setup) while Dev A finishes P2
- Week 2: P5 (UI) + P6 (Frontend polish: T023-T026)
- ~10 hours total

**Shared**: T030 (E2E testing) - both developers

**Timeline**: Both complete in parallel, 1-2 weeks

---

## Recommended Execution Strategy

### Option A: Sequential (Single Developer)
**Best for**: Learning the full stack, understanding every detail
**Time**: 18-22 hours across 1-2 weeks

1. Do P1-P3 fully (backend complete)
2. Do P4-P6 fully (frontend complete)
3. Do P6 polish
4. Run E2E tests

### Option B: Parallel (2 Developers)
**Best for**: Faster delivery, parallel development
**Time**: 14-17 hours across 1 week

1. Dev A: P1 (backend foundation)
2. Dev B: Waits 2 hours, starts P4 (frontend setup)
3. Dev A: P2-P3 (auth + task API)
4. Dev B: P5 (UI components)
5. Both: P6 (integration & polish)
6. Both: T030 (E2E testing & deployment)

### Option C: Spike-Based (Rapid Prototyping)
**Best for**: Quick MVP to validate concept
**Time**: 8-10 hours for core features only

Focus on critical path only:
- T001-T005 (Foundation)
- T006-T010 (Auth - basic version)
- T011-T013 (Task CRUD - basic version)
- T014-T017 (Frontend setup)
- T018-T020 (Auth forms + Task list)
- T023 (Wire mutations)
- Skip T024-T030 (polish can come later)

---

## Progress Tracking Template

Use this to track your implementation:

```markdown
# Phase II Implementation Progress

## Phase P1: Foundation & Setup
- [ ] T001: Backend project setup
- [ ] T002: Database config
- [ ] T003: Alembic init
- [ ] T004: SQLModel entities
- [ ] T005: First migration
**Status**: [ ] Not Started [ ] In Progress [ ] Complete

## Phase P2: Authentication
- [ ] T006: JWT utilities
- [ ] T007: Auth schemas
- [ ] T008: AuthService
- [ ] T009: Auth routes
- [ ] T010: CORS setup
**Status**: [ ] Not Started [ ] In Progress [ ] Complete

## Phase P3: Task API
- [ ] T011: Task schemas
- [ ] T012: TaskService
- [ ] T013: Task routes
**Status**: [ ] Not Started [ ] In Progress [ ] Complete

## Phase P4: Frontend Setup
- [ ] T014: Next.js init
- [ ] T015: Better Auth config
- [ ] T016: Auth hooks/types
- [ ] T017: Routing & middleware
**Status**: [ ] Not Started [ ] In Progress [ ] Complete

## Phase P5: Frontend UI
- [ ] T018: Auth forms
- [ ] T019: Task list
- [ ] T020: Task form
- [ ] T021: Filters & sorting
- [ ] T022: Dark mode
**Status**: [ ] Not Started [ ] In Progress [ ] Complete

## Phase P6: Integration & Polish
- [ ] T023: Wire mutations
- [ ] T024: Toast notifications
- [ ] T025: Delete confirmation
- [ ] T026: Loading states
- [ ] T027: Error standardization
- [ ] T028: Rate limiting
- [ ] T029: Input validation
- [ ] T030: E2E testing
**Status**: [ ] Not Started [ ] In Progress [ ] Complete

## Overall
- Backend Complete: [ ]
- Frontend Complete: [ ]
- Integration Complete: [ ]
- MVP Ready: [ ]
- Production Ready: [ ]
```

---

## Common Bottlenecks & Solutions

| Bottleneck | Cause | Solution |
|-----------|-------|----------|
| Database connection fails | PostgreSQL not running | Use Docker: `docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres` |
| CORS errors | Frontend/Backend origin mismatch | Check `NEXT_PUBLIC_API_URL` and `CORSMiddleware` settings |
| Auth not persisting | Cookie not set | Ensure `credentials: "include"` in fetch calls |
| Tasks show but not filtered | Query not using user_id | Check TaskService.get_tasks() is filtering by user_id |
| Form validation too strict | Pydantic schema too strict | Adjust field constraints in schemas.py |
| Dark mode not applying | CSS not including dark classes | Check `tailwind.config.js` has dark mode plugin |
| Rate limiting breaks dev | Threshold too low | Temporarily disable for development, enable before deploy |

---

## Next Steps

1. **Read the full specifications** in order:
   - `specs/phase-ii-web-app/spec.md` (understand requirements)
   - `specs/phase-ii-web-app/plan.md` (understand architecture)
   - `specs/phase-ii-web-app/tasks.md` (understand implementation tasks)

2. **Choose your execution strategy**: A (sequential), B (parallel), or C (spike)

3. **Set up development environment**:
   - PostgreSQL running
   - Python 3.10+ with venv
   - Node.js 18+ with npm

4. **Start with T001** (Backend project setup)

5. **Use this roadmap** as your checklist - mark tasks as complete as you finish them

6. **Reference the task details** in `tasks.md` when stuck on implementation

---

**Status**: ✅ Ready to implement Phase II

