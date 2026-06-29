# Sapiaverse Demo

Sapiaverse Demo is an LLM-powered social simulation of synthetic San Francisco residents. It models 30 PUMS-grounded agents with Roles, Memory Streams, persistent simulation state, and in-character responses to world events, encounters, and behavioral scenarios.

The app is split into two parts:

- `backend/`: FastAPI service that loads agents, advances the simulation, streams events over SSE, calls Groq for live simulation turns, and calls Anthropic Claude for behavioral scenario experiments.
- `frontend/`: Next.js + Phaser interface for watching the simulated city, running the live simulation, and launching behavioral scenarios.

## Prerequisites

- Python 3.10+
- Node.js 20+
- npm
- A Groq API key for LLM-backed simulation calls.
- An Anthropic API key for behavioral scenario calls.

## Setup

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and set:

```bash
GROQ_API_KEY=your_groq_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
SIM_DATA_PATH=../sim-data
SIM_LOGS_PATH=../sim-logs
MODEL=llama-3.3-70b-versatile
BEHAVIOR_MODEL=claude-sonnet-4-5-20250929
```

`GROQ_API_KEY` is required for LLM-backed simulation turns. `ANTHROPIC_API_KEY` is required for behavioral scenario experiments.

Then install the frontend dependencies:

```bash
cd ../frontend
npm install
```

## How To Run

Start the backend from `backend/`:

```bash
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

In a second terminal, start the frontend from `frontend/`:

```bash
npm run dev
```

Open the app at:

```text
http://localhost:3000
```

The frontend expects the backend at:

```text
http://localhost:8000/api
```

## Data And Logs

The generated resident Agents live in `sim-data/agent-1` through `sim-data/agent-30`. Each Agent has:

- `ROLE.md`: stable identity, demographics, communication style, personality, beliefs, and behavioral constraints.
- `MEMORY.md`: chronological Memory Stream for the Agent.

Persistent simulation state is stored in `sim-data/SIM_STATE.json`. Simulation and experiment logs are written to `sim-logs/`.

## Data Sources Used

The synthetic population is based on:

- U.S. Census Bureau ACS 2022 ACS 5-year PUMS API.
- California `state=06`.
- San Francisco PUMA10 codes `07501`, `07502`, `07503`, and `07504`.
- PUMS variables: `SERIALNO`, `SPORDER`, `AGEP`, `SEX`, `RAC1P`, `HISP`, `OCCP`, `PINCP`, `HINCP`, `TEN`, `PWGTP`, `PUMA10`.

Important caveats:

- PUMS records are anonymized individual records, not exact real people.
- Names, exact neighborhoods, short life histories, and some narrative details are synthetic overlays.
- Age, PUMA, race code, Hispanic-origin code, occupation code, person income, household income, tenure, and person weight come from sampled PUMS records.
- OCEAN personality scores are synthetic but rule-derived from PUMS fields and broad context, not directly observed Census data.

See `sim-data/SF_CENSUS_SOURCES.md` for the full source and derivation notes.
