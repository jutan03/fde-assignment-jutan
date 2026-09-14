# CampusSwap (Python) — AI-enabled campus marketplace demo

Same demo as the Node version, rebuilt as a Flask app: browse listings, search in
plain language, and ask a grounded Q&A assistant about the catalogue. Built for
the CognitioLabs Associate FDE assessment.

## What's inside

- **Browse + item detail** — server-rendered, mobile-friendly, no sign-in required
  (`templates/index.html`, `templates/item.html`, routes in `app.py`).
- **Natural-language search** — embeds the catalogue and your query with
  `openai/text-embedding-3-small` and ranks by cosine similarity (`search.py`,
  the `/api/search` route in `app.py`).
- **Catalogue Q&A** — retrieves the closest listings, then answers with
  `gpt-5.6-terra`, grounded only in those listings (the `/api/qna` route).
- **/notes page** — explains the demo's scope and decisions
  (`templates/notes.html`) — edit this before you submit, it's a draft.
- The seeded catalogue lives in `catalogue.py` — 15 fictional listings across
  furniture, textbooks, electronics, bikes, and dorm essentials.

The API key is only ever read server-side (`gateway.py`, used by `search.py` and
the API routes in `app.py`). It's never sent to the browser — the frontend
(`static/app.js`) only ever talks to your own `/api/...` routes.

## 1. Requirements

- Python 3.9 or newer (check with `python3 --version`).

## 2. Install

Unzip the project, then in a terminal:

```bash
cd campus-swap-py
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Add your gateway credentials

Copy the example env file:

```bash
cp .env.example .env
```

Open `.env` and fill in the two values from your candidate console:

```
GATEWAY_BASE_URL=https://your-gateway-domain
CLASSGW_KEY=your-api-key-here
```

`GATEWAY_BASE_URL` is just the domain (no `/v1` or trailing slash — the code adds
the right path for each call). `.env` is already in `.gitignore`, so it won't be
committed.

If you skip this step, the app still runs: search falls back to plain keyword
matching and the Q&A assistant returns a clearly labelled simulated response,
instead of crashing.

## 4. Run it

```bash
python3 app.py
```

Open **http://localhost:5000**. Try:

- Browsing the catalogue and opening an item.
- Searching something like *"cheap desk lamp"* or *"textbook for calculus"*.
- Asking the assistant *"which desk is cheapest?"* or *"compare the two bikes"*.
- Visiting **http://localhost:5000/notes**.
