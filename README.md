# AlohaAgent

**AI-powered toolkit built specifically for Hawaii real estate agents.**

Not a mainland tool with Hawaii tacked on — AlohaAgent knows the neighborhoods, the land tenure system, the island geography, and what makes each market a different conversation.

🌺 Live at [alohaagent.app](https://alohaagent.app)

---

## Overview

AlohaAgent is a production SaaS built on Flask + Anthropic's Claude API, giving Hawaii agents 8 AI tools that generate professional, publication-ready content in seconds. It handles auth, billing, rate limiting, PDF export, and multi-section parallel AI generation — all deployed on Render with a PostgreSQL backend.

---

## Tools

| Tool | What It Generates |
|---|---|
| **Listing Generator** | Full listing copy, property analysis, and neighborhood report — in parallel |
| **Open House Announcer** | Instagram post, Facebook post, and email — from one form |
| **Social Media Generator** | Platform-specific content with Hawaii voice and neighborhood context |
| **Offer Letter Assistant** | Structured offer letters tailored to Hawaii transaction norms |
| **Market Report Generator** | Buyer and seller reports with island-specific market framing |
| **Client Email Templates** | Situation-aware email drafts for common agent-client scenarios |
| **Bio Generator** | Agent bios that actually sound human |
| **Property Comparison** | Side-by-side analysis of 2–3 properties with narrative context |

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, Flask-Limiter, Flask-WTF |
| AI | Anthropic API (`claude-sonnet-4-6`), parallel generation via ThreadPoolExecutor, Claude Vision API |
| Database | PostgreSQL (Render), SQLite fallback for local dev |
| Payments | Stripe — live mode, checkout sessions, webhooks, subscription lifecycle |
| PDF | ReportLab — branded layout with per-tool subject lines and markdown-to-PDF token processing |
| Images | Pillow — 95% compression, base64 in-memory, never written to disk |
| Frontend | Vanilla JS + CSS transitions, no frameworks |
| Deploy | Render, Gunicorn |

---

## Technical Highlights

### Listing Prompt Engineering

The listing generator prompt is ~200 lines and functions more like a craft specification than a typical AI prompt. For every generation it:

- Randomly selects one of 5 structural templates (lead with lifestyle / lead with location / lead with the home's standout feature / lead with a sensory detail unique to this address / lead with the property's history)
- Enforces hard rules on sentence openers — paragraph 1 cannot open with "This", "The", the address, or any adjective; paragraph 2 cannot open with a room name; paragraph 3 cannot open with "Located", "Just", "Situated", or "Nestled"; no two paragraphs may open the same way
- Applies a rhythm constraint: no two consecutive sentences in the same paragraph may share a grammatical subject; no paragraph may contain more than two sentences under 10 words or more than two sentences over 35 words
- Requires every sentence in paragraph 2 to pass a "so what?" test — a feature named without a buyer consequence gets cut or rewritten
- Applies a price-tier voice system: under $800k gets energetic and opportunity-focused; $800k–$2M gets confident and specific; over $2M gets restrained and precise
- Applies property-type-specific rules: condo copy must be structurally distinct from single-family copy; land listings have no interior narrative
- Bans a hard list of words and phrases (`nestled`, `boasts`, `paradise`, `turnkey`, `rare find`, `hidden gem`, `tropical oasis`, `meticulously maintained`, `won't last long`, `priced to sell`, `sought-after`) across all tools
- Requires Claude to complete a three-step internal checklist before writing: identify the single most specific true thing about this property, identify the lifestyle detail that will make the right buyer feel it's theirs, and identify the neighborhood fact most agents wouldn't know — all three must appear in their respective paragraphs or the output is wrong

A `generation_id` (MD5 hash of address + timestamp) is injected into every prompt to prevent the model from repeating prior outputs.

### 87-Neighborhood Knowledge Base

`neighborhoods.py` is 1,362 lines of hand-curated data covering 87 neighborhoods across Oahu, Maui, Kauai, the Big Island, Molokai, and Lanai. Each entry includes `vibe`, `lifestyle`, `nearby`, `beaches`, `commute`, `market_notes`, `keywords`, and `aliases`. This context is injected directly into every relevant prompt.

Fuzzy neighborhood matching uses `difflib.SequenceMatcher` with an island guard — a cross-island match (e.g. Kailua on Oahu matching Kailua-Kona on the Big Island) returns `None` rather than wrong data. Aliases handle common misspellings and alternate names (e.g. "Kane'ohe", "Kailua Town", "Ala-Moana").

### Parallel AI Generation

The listing generator fires three simultaneous Claude API calls — listing copy, property analysis, and neighborhood report — using `ThreadPoolExecutor`. All three run concurrently and resolve before the response renders, cutting generation time roughly in thirds versus sequential calls.

### Claude Vision Integration

All tools that accept property photos process uploads through the Claude Vision API. Photos are validated with Pillow (not just headers — actual image file content), compressed to max 1024px JPEG at 75% quality, converted to base64, and sent inline with the prompt. Up to 8 photos per generation, 5MB per file, all in-memory — nothing written to disk.

### PDF Generation

ReportLab generates branded PDFs with a per-tool subject line (e.g. listing generator shows address + neighborhood; offer letter shows address + offer amount), gold header with the user's email and generation date, section labels derived from the AI output, and a footer. A markdown-to-token processor strips and normalizes headings, bullets, and bold markers before laying out the document.

### Production-Grade Security

- Rate limiting on all generate endpoints (10/min, 100/day per IP)
- Rate limiting on all refine endpoints (20/min, 200/day per IP)
- Full CSP header with Stripe allowlist
- HSTS, secure session cookies, HTTPONLY, SAMESITE=Lax
- CSRF protection via Flask-WTF
- Input validation and field-level max lengths on all form inputs
- Admin panel uses a per-session random token — the raw `ADMIN_SECRET` is never embedded in page source
- Global 404 and 500 error handlers with branded error pages

### Auth & Billing

- Free tier: 3 generations/month + daily hard cap of 10
- Pro tier: $79/mo — unlimited generations, saved history, PDF export, daily cap of 50
- Stripe webhooks handle full subscription lifecycle (created, cancelled, payment failed)
- Upgrade flow verifies `payment_status == "paid"` and email match from Stripe session before upgrading plan
- Admin panel with per-session token auth, plan management, usage stats, and tool breakdown

---

## Dashboard

- Saved generation history with search and filter
- Per-generation view page with markdown rendering
- Copy to clipboard and PDF download on all outputs
- Usage tracking and plan badge
- Dark theme — no white backgrounds anywhere

---

## Origin

`listing.py` is the original CLI prototype this project started as — a simple terminal tool that asked for property details and printed a listing. It's kept in the repo as a record of where AlohaAgent began before it became a full web application.

---

## What I Learned Building This

AlohaAgent was built from scratch — I came into this project knowing Python basics and left knowing how to ship a full production web application. Here's what that actually looked like.

**Flask and backend architecture** — I'd never built a web application before this. I learned how to structure a Flask app beyond a single file: blueprints, application factories, config management, and how the pieces (auth, billing, database, AI) fit together without turning into spaghetti.

**Databases and SQLAlchemy** — I had no prior experience with relational databases. I learned how to design schemas, write models, handle migrations, and manage the difference between a local SQLite setup and a production PostgreSQL instance on Render. Getting the DATABASE_URL fallback logic right taught me a lot about environment-aware configuration.

**Authentication from scratch** — I implemented full user auth using Flask-Login and Flask-Bcrypt: registration, login, session management, password hashing, and protecting routes. Understanding what a session cookie actually is, and why HTTPONLY and SAMESITE matter, came from building this rather than reading about it.

**Stripe and real payment flows** — Integrating Stripe in live mode was the steepest learning curve. Checkout sessions are straightforward — webhooks are not. I learned how to handle the full subscription lifecycle: successful payments, cancellations, failed renewals, and why you can't trust the frontend to tell you a payment succeeded. Getting the webhook signature verification right was a forcing function for understanding how event-driven systems work.

**Security** — I didn't know what a CSP header was when I started. By the end I had written one that allowlists Stripe's domains, configured HSTS, understood why CSRF tokens exist, and implemented rate limiting across every endpoint that touches the AI API. Most of this came from reading about what could go wrong rather than following a tutorial.

**AI API integration and prompt engineering** — Working directly with the Anthropic API taught me how to think about prompts as code: they have structure, edge cases, and failure modes. I learned how to use the Claude Vision API for photo uploads, how to run concurrent API calls with ThreadPoolExecutor to cut generation time, and how domain-specific context (87 neighborhood profiles, island guards, leasehold vs. fee simple distinctions) dramatically improves output quality over generic prompting. The listing generator prompt evolved from a paragraph to a ~200-line craft specification over the course of the project.

**Deploying and keeping something alive** — Render, Gunicorn, environment variables, build commands, log monitoring, and what happens when your app crashes at 2am and you have to read a stack trace to figure out why. Debugging a production environment where you can't just attach a debugger was a different skill from local development.

The honest version: most of what's in this repo I didn't know how to do when I started it. I built AlohaAgent by figuring things out as they broke.

---

## Local Development

```bash
git clone https://github.com/JustinAlbina/hawaii-ai-listing-generator
cd hawaii-ai-listing-generator
pip install -r requirements.txt --break-system-packages
python3 app.py
```

Required environment variables:

```
ANTHROPIC_API_KEY
DATABASE_URL
STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET
ADMIN_SECRET
SECRET_KEY
```

---

## Design Philosophy

- Dark theme only — brand colors defined once in `base.html` as CSS variables, never redefined per-template
- Shared animation layer (`shared.css` + `shared.js`) — no per-template duplication
- No animation libraries — CSS transitions and vanilla JS only
- No fake social proof

---

Built by Justin Albina · [alohaagent.app](https://alohaagent.app)
