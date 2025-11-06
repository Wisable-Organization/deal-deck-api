### DealDash (formerly DealStream) — README

#### Project overview
DealDash is a CRM/deal-management app for SMB brokerage with five core screens:
- Deal Pipeline (Kanban by stage; drag to update stage)
- Deal Detail (three panels: deal overview, activity timeline with quick actions, and a toggleable right drawer for Stage Checklist or Buyer Matches)
- Dashboard (KPIs and charts)
- Buying Groups (table of buyer groups with key attributes)
- Buying Group Detail (group profile, contacts, notes, and per-deal stage Kanban)

The frontend is implemented in React + Tailwind with React Router v6 for navigation. The backend is FastAPI with in-memory storage for local development, designed to be easily migrated to Supabase/PostgreSQL for production.

#### Repository structure
- `client/` — React app with React Router v6, UI components, pages, hooks, and query client
- `api/` — FastAPI backend with in-memory storage (local dev) and Supabase integration (production)
- `server/` — Legacy Express server (can be removed)
- `shared/schema.ts` — Drizzle ORM schema and TypeScript types used across client/server
- `Schema.csv` — High-level CSV of intended tables and columns
- `design_guidelines.md` — UI/UX notes
- `main.py` — Combined entry point for Replit deployment
- `requirements.txt` — Python dependencies for FastAPI backend

#### Deal Detail (highly detailed)
The Deal Detail route `/deals/:id` renders a HubSpot-style view with:
- Sticky header: Back to Pipeline, Deal Title, Stage Badge, Owner, Tools menu.
- Command bar: Schedule, Send for Signature, Add Doc, Create Invoice, Update Stage, and quick toggle buttons for Stage Checklist / Buying Parties drawer.
- Three-column layout:
  - Left: Deal Snapshot (Revenue, SDE, Valuation, Multiples, Commission, Age in Stage, Health score), Description, Notes (autosave), Seller Contacts, Key Documents (pinned and recent).
  - Middle: Activity Timeline with type filters and quick-add presets (email, meeting, request docs, send CIM/NDA, buyer outreach, note).
  - Right: Drawer toggles between Stage Checklist and Buyer Matches. For matches, each card shows buyer party name, primary contact, target acquisition, budget, match stage pill, an expandable checklist, and email/schedule buttons.

Note: `/api/meetings/latest-summary` is not implemented in the current Node server; it will be provided by FastAPI as a stub or real integration.

#### Dashboard
- KPI cards with icons and change indicators, charts scaffold. Data is currently mocked/static within the page.

#### Buying Groups
- Table/list of all `buying_parties` with key info; clicking navigates to detail.

#### Buying Group Detail
- Shows buying group profile, contacts, notes, and a Kanban of matches (uses `MatchesKanban`).

`MatchesKanban` navigates to deal details on card click:
```41:72:client/src/components/match/MatchesKanban.tsx
{(byStage.get(col.key) ?? []).map(({ match, deal }) => (
  <div
    key={match.id}
    className="p-3 border border-border rounded-md hover-elevate cursor-pointer"
    onClick={() => setLocation(`/deals/${deal.id}`)}
  >
```

The CSV `Schema.csv` provides a high-level, more expansive schema (companies, agreements, users, permissions, integrations, etc.). For the current UI and MVP backend, the `shared/schema.ts` entities are sufficient without schema changes. If we later expand to the CSV’s full domain (e.g., agreements, permissions, integrations), we can incrementally add tables while keeping current endpoints stable.

- MUST-change verdict: Nothing in the current schema must be changed to support the implemented UI. The only addition we’ll make backend-side is a dedicated notes endpoint for deals (purely a route/controller addition; no DB change).


Gaps to add in FastAPI (called by UI but not implemented in Node server today):
- PATCH `/api/deals/:id/notes` — autosave notes
- GET `/api/meetings/latest-summary?dealId=...` — latest meeting summary for the Deal Snapshot; can initially return null or mock, then integrate later

### FastAPI backend plan

We will implement a FastAPI backend that:
- Mirrors the REST endpoints above (including the two additional ones).
- Uses PostgreSQL (via SQLModel or SQLAlchemy) with the same schema as `shared/schema.ts`.
- Validates inputs via Pydantic models matching the zod insert schemas.
- Returns JSON payloads in the shapes already consumed by the frontend.
- Implements CORS for the Vite dev server origin.
- Provides OpenAPI docs at `/docs`.

Suggested structure:
- `api/main.py` — FastAPI app factory, CORS, router registration
- `api/models.py` — SQLAlchemy/SQLModel models aligned to `shared/schema.ts`
- `api/schemas.py` — Pydantic request/response models
- `api/routers/` — resource routers: deals.py, contacts.py, buying_parties.py, activities.py, documents.py, matches.py, meetings.py
- `api/db.py` — session management, engine setup, migrations configured via Alembic
- `alembic/` — migrations to reflect the schema

Key endpoints and behaviors:

- Deals
  - GET `/api/deals` → List<Deal>
  - GET `/api/deals/{id}` → Deal or 404
  - POST `/api/deals` → create Deal (validate stage ∈ allowed, decimals are strings or numbers; normalize to strings in responses for UI consistency)
  - PATCH `/api/deals/{id}` → partial update; supports `{ stage }` for Kanban drag/drop and any other fields
  - PATCH `/api/deals/{id}/notes` → `{ notes: string }` autosave; returns updated Deal
  - DELETE `/api/deals/{id}` → 204

- Deal buyer matches composite
  - GET `/api/deals/{id}/buyers` → [{ match, party, contact }]
    - `party` is the BuyingParty
    - `contact` is the first contact for that party (if any), same as current UI expectation

- Contacts
  - GET `/api/contacts?entityId=...&entityType=deal|buying_party` → List<Contact>
  - POST `/api/contacts` → create Contact
  - DELETE `/api/contacts/{id}` → 204

- Buying Parties
  - GET `/api/buying-parties` → List<BuyingParty>
  - GET `/api/buying-parties/{id}` → BuyingParty
  - POST `/api/buying-parties` → create BuyingParty
  - PATCH `/api/buying-parties/{id}` → partial update
  - DELETE `/api/buying-parties/{id}` → 204

- Activities
  - GET `/api/activities?entityId=...` → activities for a deal or buyer group
  - POST `/api/activities` → create Activity; allow setting `type`, `title`, `status`, `dealId` or `buyingPartyId`
  - PATCH `/api/activities/{id}` → partial update (`status`, `completedAt`, etc.)
  - DELETE `/api/activities/{id}` → 204

- Documents
  - GET `/api/documents?entityId=...` → documents for a deal or buyer group
  - POST `/api/documents` → create Document (support upload URL or external linking)
  - DELETE `/api/documents/{id}` → 204

- Matches
  - POST `/api/deal-buyer-matches` → create match
  - DELETE `/api/deal-buyer-matches/{id}` → 204

- Meetings (stub for snapshot)
  - GET `/api/meetings/latest-summary?dealId=...` → `{ summary, createdAt, source } | null` for the Deal Snapshot card. Initially returns null if not integrated.

Security and safety:
- Input validation with Pydantic; reject invalid enums/stages.
- Use parameterized queries via ORM; no string-built SQL.
- Return 4xx for validation errors and 404 for missing resources.
- Encode/escape output where needed; set proper content types.
- Log request IDs and errors; avoid leaking internal details in errors.

Pagination and filtering (future-ready):
- Support `?limit` and `?offset` on list endpoints with sensible defaults and maximums.
- Filtering by `stage`, `owner`, `status` on `/api/deals` and `/api/buying-parties` as needed.

Idempotency and race-safety:
- For autosave notes, accept repeated payloads and update `updated_at` only when content changes.
- Use transactions around multi-write operations (e.g., creating a match plus initial checklist, if applicable in future).

Response payload shapes
- Follow the `shared/schema.ts` types. Frontend expects numeric-decimal fields as strings (e.g., `"2800000"`); the backend should serialize decimals to strings to avoid floating point inconsistencies.

Example requests
- Update stage after drag:
```bash
curl -X PATCH http://localhost:8000/api/deals/DEAL_ID \
  -H "Content-Type: application/json" \
  -d '{"stage":"buyer_matching"}'
```
- Autosave notes:
```bash
curl -X PATCH http://localhost:8000/api/deals/DEAL_ID/notes \
  -H "Content-Type: application/json" \
  -d '{"notes":"Followed up with CFO re: Q4."}'
```
- Fetch deal buyers composite:
```bash
curl http://localhost:8000/api/deals/DEAL_ID/buyers
```

### React Router v6 migration plan
Current router uses Wouter. We will:
1. Install React Router v6 and wrap the app with `BrowserRouter`.
2. Replace `wouter` `Link`, `useLocation`, and `useRoute` with React Router equivalents (`Link`, `useNavigate`, `useParams`, `useLocation`).
3. Update route definitions to v6 `<Routes><Route ... /></Routes>`.
4. Replace `setLocation` navigation with `useNavigate()` calls.
5. Ensure `Navigation` active state uses `useLocation()` pathname.

This can be done incrementally: route-by-route migration while keeping path structure identical so APIs remain unaffected.

### Seeding and test data
The current Node in-memory store seeds representative deals, contacts, activities, documents, buying parties, and matches on boot:
```82:110:server/storage.ts
// Seed sample deals [...]
companyName: "TechFlow Industries",
revenue: "2800000",
sde: "950000",
valuationMin: "8500000",
valuationMax: "12000000",
...
stage: "valuation",
priority: "high",
...
```
We will port a similar seed routine to FastAPI for dev environments using Alembic seed scripts or a simple bootstrap job guarded by an environment variable.

### Integrations and future endpoints
- The Tools menu links (MiniVal, CIM Tool, Deck Tool, Narrative) open external routes. Backend can later add service endpoints if needed for document generation.
- Meetings summary endpoint can later integrate call transcripts or calendar sources.
- Documents could integrate with Box for storage; schema fields (e.g., `url`) already allow external references.

### Running the Application

#### Local Development

**Option 1: Combined (Recommended for Replit)**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Start both FastAPI backend and Vite frontend
python main.py
```
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:5173
- API Docs: http://localhost:8000/docs

**Option 2: Separate Processes**
```bash
# Terminal 1: Start FastAPI backend
npm run api
# or: uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Start Vite frontend
npm run dev
```

Authentication:
1. Utilities
- Password hashing with bcrypt
- JWT token creation and verification
- Password reset token generation
- User authentication dependency
2. Routes
- POST /api/auth/register - Register new users
- POST /api/auth/login - Login and get JWT token
- POST /api/auth/password-reset-request - Request password reset
- POST /api/auth/password-reset-confirm - Confirm password reset with token
- GET /api/auth/me - Get current authenticated user

#### Replit Deployment
1. Upload the entire folder to Replit
2. Run `python main.py` in the Replit console
3. The app will be available at the Replit-provided URL

#### Production (Supabase)
1. Create a Supabase project
2. Set up the database schema (see Database Schema section)
3. Configure environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your Supabase credentials
   ```
4. Deploy FastAPI backend to your hosting platform
5. Deploy Vite frontend to your CDN/hosting platform

### Environment Variables

**Required for Supabase (Production):**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anonymous key (safe for frontend)
- `SUPABASE_SERVICE_ROLE_KEY` - Your Supabase service role key (backend only, keep secret)
- `DATABASE_URL` - PostgreSQL connection string

**Development:**
- No environment variables required (uses in-memory storage)
- CORS configured for `http://localhost:5173`

### Database Schema (Supabase Setup)

**For production with Supabase, create these tables:**

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Deals table
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT NOT NULL,
    revenue DECIMAL(15,2) NOT NULL,
    sde DECIMAL(15,2),
    valuation_min DECIMAL(15,2),
    valuation_max DECIMAL(15,2),
    sde_multiple DECIMAL(5,2),
    revenue_multiple DECIMAL(5,2),
    commission DECIMAL(5,2),
    stage TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',
    description TEXT,
    notes TEXT,
    next_step_days INTEGER,
    touches INTEGER NOT NULL DEFAULT 0,
    age_in_stage INTEGER NOT NULL DEFAULT 0,
    health_score INTEGER NOT NULL DEFAULT 85,
    owner TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contacts table
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    entity_id UUID NOT NULL,
    entity_type TEXT NOT NULL
);

-- Buying parties table
CREATE TABLE buying_parties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    target_acquisition_min INTEGER,
    target_acquisition_max INTEGER,
    budget_min DECIMAL(15,2),
    budget_max DECIMAL(15,2),
    timeline TEXT,
    status TEXT NOT NULL DEFAULT 'evaluating',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deal-buyer matches table
CREATE TABLE deal_buyer_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id),
    buying_party_id UUID NOT NULL REFERENCES buying_parties(id),
    target_acquisition INTEGER,
    budget DECIMAL(15,2),
    status TEXT NOT NULL DEFAULT 'interested',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activities table
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID REFERENCES deals(id),
    buying_party_id UUID REFERENCES buying_parties(id),
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    assigned_to TEXT,
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID REFERENCES deals(id),
    buying_party_id UUID REFERENCES buying_parties(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Schema Notes:**
- This includes only the tables actively used by the current UI
- The full `Schema.csv` contains additional tables for future features (agreements, permissions, integrations)
- No schema changes are required for the current implementation

### Validation against schema.csv
- The CSV contains a superset for a more comprehensive CRM (companies, agreements, permissions, integration events). The current feature set uses `deals`, `contacts`, `buying_parties`, `deal_buyer_matches`, `activities`, `documents`.
- No MUST changes are required. We'll add tables incrementally if/when we implement those extra modules.

### Non-functional requirements
- Error handling: consistent 4xx/5xx with JSON `{error, details?}`.
- Observability: structured logs with request IDs; simple access logs in dev.
- Security: parameterized DB access, validation at API boundaries, avoid exposing stack traces.

### Appendix: Current Node endpoints (reference for parity)
The existing Express `server/routes.ts` shows the full list we will replicate, plus two additions noted (deal notes and meeting summary).

```6:19:server/routes.ts
app.get("/api/deals", ...)
app.get("/api/deals/:id", ...)
app.post("/api/deals", ...)
app.patch("/api/deals/:id", ...)
```

```47:62:server/routes.ts
app.get("/api/deals/:id/buyers", ...)
```

```136:171:server/routes.ts
app.get("/api/activities", ...)
app.post("/api/activities", ...)
app.patch("/api/activities/:id", ...)
app.delete("/api/activities/:id", ...)
```

```typescript
// Deals
GET    /api/deals
GET    /api/deals/:id
POST   /api/deals
PATCH  /api/deals/:id
DELETE /api/deals/:id
```

```typescript
// Deal-specific buyer matches (composite response for the right drawer)
GET /api/deals/:id/buyers   // returns [{ match, party, contact }]
```

```typescript
// Contacts
GET    /api/contacts?entityId=...&entityType=deal|buying_party
POST   /api/contacts
DELETE /api/contacts/:id
```

```typescript
// Buying Parties
GET    /api/buying-parties
GET    /api/buying-parties/:id
POST   /api/buying-parties
PATCH  /api/buying-parties/:id
DELETE /api/buying-parties/:id
```

```typescript
// Activities
GET    /api/activities?entityId=...
POST   /api/activities
PATCH  /api/activities/:id
DELETE /api/activities/:id
```

```typescript
// Documents
GET    /api/documents?entityId=...
POST   /api/documents
DELETE /api/documents/:id
```

```typescript
// Deal-Buyer Matches
POST   /api/deal-buyer-matches
DELETE /api/deal-buyer-matches/:id
```

```shellscript
curl -X PATCH http://localhost:8000/api/deals/DEAL_ID \
  -H "Content-Type: application/json" \
  -d '{"stage":"buyer_matching"}'
```

```shellscript
curl -X PATCH http://localhost:8000/api/deals/DEAL_ID/notes \
  -H "Content-Type: application/json" \
  -d '{"notes":"Followed up with CFO re: Q4."}'
```

```shellscript
curl http://localhost:8000/api/deals/DEAL_ID/buyers
```

```typescript
// Seed sample deals [...]
companyName: "TechFlow Industries",
revenue: "2800000",
sde: "950000",
valuationMin: "8500000",
valuationMax: "12000000",
...
stage: "valuation",
priority: "high",
...
```

```typescript
app.get("/api/deals", ...)
app.get("/api/deals/:id", ...)
app.post("/api/deals", ...)
app.patch("/api/deals/:id", ...)
```

```typescript
app.get("/api/deals/:id/buyers", ...)
```

```typescript
app.get("/api/activities", ...)
app.post("/api/activities", ...)
app.patch("/api/activities/:id", ...)
app.delete("/api/activities/:id", ...)
```

# deal-deck-api
# deal-deck-api
# deal-deck-client
# deal-deck-api
