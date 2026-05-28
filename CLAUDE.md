# AlohaAgent — Claude Code Context

## Project
Hawaii real estate AI SaaS · alohaagent.app · justin@alohaagent.app
Local: ~/Desktop/Projects/ · `python3 app.py` · Port 5000
Deploy: Render $7/mo · auto-deploy on git push

## Stack
Flask · Flask-SQLAlchemy · Flask-Login · Flask-Bcrypt · Python 3.14
Anthropic: model=`claude-sonnet-4-5` · key=`os.getenv("ANTHROPIC_API_KEY")`
DB: `os.getenv("DATABASE_URL")` (PostgreSQL/Render) · fallback SQLite
Stripe: `os.getenv("STRIPE_SECRET_KEY")` · LIVE mode
PDF: reportlab · MD: markdown + bleach via safe_markdown() · Gunicorn timeout: 120s

## Hard Rules
- Never hardcode API keys, Stripe keys, or secrets — always os.getenv()
- Model always `claude-sonnet-4-5` — never change
- No white backgrounds — ever
- All routes return 200 after every change
- pip installs always `--break-system-packages`
- Flask/Jinja2 only — no React, no Next.js
- No animation libraries — CSS transitions + vanilla JS only
- No fake social proof — no testimonials, no brokerage logos
- Never duplicate animation/form logic per template — shared.css + shared.js only
- Never touch Stripe, auth, or DB logic during UI tasks

## Env Vars (Render)
ANTHROPIC_API_KEY · DATABASE_URL · ADMIN_SECRET
STRIPE_SECRET_KEY · STRIPE_PUBLISHABLE_KEY · STRIPE_WEBHOOK_SECRET

## Design Tokens (defined in base.html — never redefine elsewhere)
--navy:#061326 · --card:#0d1b34 · --card-border:rgba(201,168,76,0.15)
--input:#1a2f45 · --gold:#c9a84c · --gold-light:#e8c97a · --gold-btn:#d4a843
--text-primary:#fff · --text-secondary:rgba(255,255,255,0.6) · --labels:#8892a4
--live-green:#22c55e
Spacing: 4·8·12·16·24·32·48·64px · Radius: cards 12px · inputs/buttons 8px · badges 20px
Primary btn: bg --gold-btn · color #000 · weight 600 · hover brightness(1.1) scale(1.01)
Ghost btn: transparent · border rgba(255,255,255,0.2) · hover border+color --gold

## File Structure
app.py · listing.py
static/css/shared.css · static/js/shared.js · static/images/hero/ (10 scenic Hawaii photos)
templates/: base.html · index.html · dashboard.html · admin.html · login.html · register.html
· profile.html · pricing.html · limit.html · terms.html · privacy.html · waitlist_success.html
· listing.html · results.html
· open_house.html · open_house_results.html
· social_media.html · social_media_results.html
· offer_letter.html · offer_letter_results.html
· market_report.html · market_report_results.html
· client_emails.html · client_emails_results.html
· bio_generator.html · bio_generator_results.html
· property_comparison.html · property_comparison_results.html

## What's Built

### 8 AI Tools
/listing /open-house /social-media /offer-letter
/market-report /client-emails /bio-generator /property-comparison

### Generation Quality
- Hawaii voice rules · 5 rotating templates per creative tool
- 85 neighborhood profiles across all 4 islands
- Clichés — never use anywhere including demo content:
  "welcome to paradise" "rare find" "nestled" "turnkey" "don't miss"
  "stunning" "breathtaking" "dream home" "piece of paradise" "one of a kind"
- Listing output: hook → interior narrative → location/lifestyle/CTA (3 paragraphs)
- Listing fields: View · Solar/PV · Ohana/ADU · Flood Zone · Renovation Year
- Parallel API calls via ThreadPoolExecutor · generation ID hashing · temperature tuning
- All "AI" / "Claude" references replaced with "AlohaAgent" in UI

### Core Features
- Auth: Flask-Login + Flask-Bcrypt · DB models: User · Generation · Waitlist
- Dashboard: saved generations · usage · plan badge · search/filter
- Free tier: 3 gen/mo · Pro: $79/mo unlimited · Stripe LIVE (checkout/webhooks/cancellation)
- Admin: /admin?secret= · user list · waitlist · stats · Set Pro/Free
- Photo upload: /listing /social-media /open-house /property-comparison
  Pillow 95% compression · base64 in-memory · Claude vision API · preview carousel
- Refine Output: /listing · /bio-generator
- PDF export · copy to clipboard · HAR disclaimer on all tools
- CSRF · rate limiting · security headers · XSS via safe_markdown()

### Landing Page (index.html)
- Hero carousel: CSS-only crossfade · 10 scenic Hawaii photos in static/images/hero/
  10s hold + 2.5s dissolve · rgba(0,0,0,0.45) overlay · infinite loop
  Photos = scenic only (beach/aerial/waterfall/golden hour) — never staged real estate
- Typewriter demo: 3-phase loop (no login required)
  P1: form fields auto-fill ~35ms/char · gold checkmark per field · Generate button pulses
  P2: button click animation · gold spinner · "Generating your listing..." · 1.5s hold
  P3: form fades · listing reveals section by section · holds 4s · loops to P1
  Demo text must match real AlohaAgent output quality — read system prompt before writing
- Sample output card: Kailua 4BD/3BA $1,450,000 · enhanced prompt quality
  gold "📍 Kailua neighborhood profile applied" badge

### Shared Animation Layer (shared.css + shared.js only — never per-template)
Results reveal (.reveal-section — all 8 result pages):
  opacity 0→1 · translateY 20px→0 (10px mobile) · 0.6s · 0.3s stagger
  Triggers on DOM population only · MutationObserver or IntersectionObserver per tool pattern
  Must not break: copy · PDF export · Refine Output

Form animations (all 8 form pages):
  Fields: IntersectionObserver fade-in on scroll (opacity 0→1 · translateY 15px→0 · 0.4s)
  Checkmark: gold ✓ on field right when valid+non-empty (CSS :valid · JS fallback)
  Generate btn: gold glow pulse when required fields filled · gold loader while generating · disabled+dimmed during generation
  Upload zones: gold drag-over highlight · fade+scale-in thumbnail · file size below thumbnail

## Session Rules
- Read this file fully before starting
- One file at a time: read → rewrite → save → verify → next
- Never read all templates at once — context overflow
- Syntax check: `python3 -c "import py_compile; py_compile.compile('app.py', doraise=True)"`
- End-of-session checklist:
  [ ] All 14 routes return 200
  [ ] No white backgrounds
  [ ] Dashboard loads with real data
  [ ] Hero carousel cycling
  [ ] Typewriter demo looping (all 3 phases)
  [ ] Results reveal firing on all 8 result pages
  [ ] Form animations working on all 8 form pages
  [ ] Photo upload visible on /listing

## Next Priorities
1. Loom demo video — script ready, record ASAP
2. Pitch emails — Team Lally · 808 Team · Daniel Ulu — send with Loom
3. Brokerage dashboard — seat management, usage tracking
4. Hawaii Information Service API — property data auto-fill
5. Google Places API — neighborhood lookup beyond knowledge base
6. Stripe customer portal