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
| **Property Comparison** | Side-by-side analysis of two properties with narrative context |

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, Flask-Limiter, Flask-WTF |
| AI | Anthropic API (`claude-sonnet-4-6`), parallel generation via ThreadPoolExecutor, Claude Vision API |
| Database | PostgreSQL (Render), SQLite fallback for local dev |
| Payments | Stripe — live mode, checkout sessions, webhooks, subscription lifecycle |
| PDF | ReportLab |
| Images | Pillow — 95% compression, base64 in-memory, never written to disk |
| Frontend | Vanilla JS + CSS transitions, no frameworks |
| Deploy | Render, Gunicorn |

---

## Technical Highlights

### Parallel AI Generation
Multi-section outputs (listing copy + property analysis + neighborhood report) run as concurrent Claude API calls via `ThreadPoolExecutor`, cutting generation time significantly versus sequential calls.

### 85+ Neighborhood Profiles
Covers Oahu, Maui, Kauai, Big Island, Molokai, and Lanai. Fuzzy neighborhood matching with an island guard — cross-island matches return `None`, preventing hallucinated geography.

### Production-Grade Security
- Rate limiting on all generate endpoints (10/min, 100/day per IP)
- Rate limiting on all refine endpoints (20/min, 200/day per IP)
- Full CSP header with Stripe allowlist
- HSTS, secure session cookies, HTTPONLY, SAMESITE=Lax
- CSRF protection via Flask-WTF
- Input validation and max length on all fields
- Global 404 and 500 error handlers

### Auth & Billing
- Free tier: 3 generations/month
- Pro tier: $79/mo — unlimited generations, saved history, PDF export
- Stripe webhooks handle full subscription lifecycle (created, cancelled, payment failed)
- Daily generation caps enforced by plan (free=10, pro=50, unauthenticated=3)
- Admin panel with plan management and usage stats

### Prompt Engineering
- 5 rotating structural templates per creative tool to avoid repetitive outputs
- Photo upload support (up to 8 photos via Claude Vision API)
- Refine Output endpoint on all tools
- Explicit cliché ban across all prompts — the following words never appear in output:

> `nestled` `boasts` `paradise` `turnkey` `rare find` `hidden gem` `tropical oasis`
> `meticulously maintained` `won't last long` `priced to sell` `sought-after`

Output reads like it was written by a veteran Hawaii agent, not a content generator.

---

## Dashboard

- Saved generation history with search and filter
- Per-generation view page with markdown rendering
- Copy to clipboard and PDF download on all outputs
- Usage tracking and plan badge
- Dark theme — no white backgrounds anywhere

---

## What I Learned Building This

AlohaAgent was built from scratch — I came into this project knowing Python basics and left knowing how to ship a full production web application. Here's what that actually looked like.

**Flask and backend architecture** — I'd never built a web application before this. I learned how to structure a Flask app beyond a single file: blueprints, application factories, config management, and how the pieces (auth, billing, database, AI) fit together without turning into spaghetti.

**Databases and SQLAlchemy** — I had no prior experience with relational databases. I learned how to design schemas, write models, handle migrations, and manage the difference between a local SQLite setup and a production PostgreSQL instance on Render. Getting the DATABASE_URL fallback logic right taught me a lot about environment-aware configuration.

**Authentication from scratch** — I implemented full user auth using Flask-Login and Flask-Bcrypt: registration, login, session management, password hashing, and protecting routes. Understanding what a session cookie actually is, and why HTTPONLY and SAMESITE matter, came from building this rather than reading about it.

**Stripe and real payment flows** — Integrating Stripe in live mode was the steepest learning curve. Checkout sessions are straightforward — webhooks are not. I learned how to handle the full subscription lifecycle: successful payments, cancellations, failed renewals, and why you can't trust the frontend to tell you a payment succeeded. Getting the webhook signature verification right was a forcing function for understanding how event-driven systems work.

**Security** — I didn't know what a CSP header was when I started. By the end I had written one that allowlists Stripe's domains, configured HSTS, understood why CSRF tokens exist, and implemented rate limiting across every endpoint that touches the AI API. Most of this came from reading about what could go wrong rather than following a tutorial.

**AI API integration and prompt engineering** — Working directly with the Anthropic API taught me how to think about prompts as code: they have structure, edge cases, and failure modes. I learned how to use the Claude Vision API for photo uploads, how to run concurrent API calls with ThreadPoolExecutor to cut generation time, and how domain-specific context (85 neighborhood profiles, island guards, leasehold vs. fee simple distinctions) dramatically improves output quality over generic prompting.

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
```

---

## Design Philosophy

- Dark theme only — brand colors defined once in `base.html` as CSS variables, never redefined per-template
- Shared animation layer (`shared.css` + `shared.js`) — no per-template duplication
- No animation libraries — CSS transitions and vanilla JS only
- No fake social proof

---

Built by Justin Albina · [alohaagent.app](https://alohaagent.app)
