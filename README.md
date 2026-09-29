# ApplyTrace 🎯

A job-application tracker + resume matcher for a 2027-batch fresher's placement hunt.
Track every application, paste a job description + your resume text, and get a
**match score with matched / missing keywords and tweak suggestions** — no external
API needed (pure stdlib TF keyword matcher).

Stack: **FastAPI + SQLAlchemy** · **React + TypeScript + Vite + Tailwind CSS**

## Project layout

```
applytrace/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, router wiring
│   │   ├── database.py        # Engine/session; DATABASE_URL, SQLite default
│   │   ├── models.py          # Application, ResumeKeyword
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── matcher.py         # TF keyword extraction + JD↔resume scoring
│   │   └── routers/
│   │       ├── applications.py# CRUD for applications
│   │       ├── analysis.py    # Analyze endpoints (persist match_score)
│   │       └── stats.py       # Dashboard stats + /api/seed demo data
│   ├── requirements.txt
│   └── .env.example
├── frontend/                  # Vite + React + TS + Tailwind
│   └── src/
│       ├── api.ts             # fetch wrapper for the FastAPI backend
│       ├── types.ts
│       ├── components/ui.tsx  # Layout, StatusBadge, StatusFilter
│       └── pages/
│           ├── Dashboard.tsx        # stats cards + filterable list
│           ├── AddApplication.tsx   # new application form
│           └── ApplicationDetail.tsx# JD/resume paste + analyze view
├── db/schema.sql            # MySQL schema + matching seed data
└── README.md
```

## Quick start (SQLite, zero setup)

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # SQLite default, nothing to edit
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173 (proxies /api → :8000)
```

Open `http://localhost:5173` — the dashboard auto-seeds 4 example applications
(`POST /api/seed` is idempotent) on first visit.

## Switching to MySQL (one line)

1. Uncomment `pymysql` in `backend/requirements.txt` and `pip install -r requirements.txt`.
2. Create the DB and load the schema:
   ```bash
   mysql -u root -p -e "CREATE DATABASE applytrace CHARACTER SET utf8mb4;"
   mysql -u root -p applytrace < db/schema.sql
   ```
3. In `backend/.env`, change **one line**:
   ```
   DATABASE_URL=mysql+pymysql://user:password@localhost:3306/applytrace
   ```
4. Restart uvicorn. Tables are created from the models automatically.

## API reference

| Method | Path | Description |
|---|---|---|
| GET | `/api/applications?status=` | List (filter by status) |
| POST | `/api/applications` | Create |
| GET / PATCH / DELETE | `/api/applications/{id}` | Read / update / delete |
| POST | `/api/analyze/application/{id}` | Score saved JD↔resume, persist `match_score` |
| POST | `/api/analyze` | Score arbitrary `{jd_text, resume_text}` |
| GET | `/api/stats` | Counts per status |
| POST | `/api/seed` | Load demo seed data (idempotent) |
| GET | `/api/health` | Health check |

## Roadmap

- [ ] **Auth** — JWT login so only Manas sees his data (backend already uses JWT-shaped patterns).
- [ ] **Gmail import** — pull HR mail (`mail me` threads) and auto-create applications via Gmail API.
- [ ] **Deadline reminders** — application deadlines + follow-up nudges (cron/email).
- [ ] Resume versioning — attach a resume file per application.
- [ ] Export applications to CSV for the master spreadsheet.
