# AlohaAgent — Claude Code Context

## Project
AI SaaS toolkit for Hawaii real estate agents.
Live: alohaagent.app · Contact: justin@alohaagent.app
Local: ~/Desktop/Projects/ · Run: python3 app.py · Port 5000

## Stack
- Python 3.14 · Flask · Flask-SQLAlchemy · Flask-Login · Flask-Bcrypt
- Anthropic API: model always `claude-sonnet-4-5` · key always `os.getenv("ANTHROPIC_API_KEY")`
- DB: `DATABASE_URL` (PostgreSQL on Render) · fallback `instance/alohaagent.db` (SQLite)
- PDF: reportlab · Markdown: markdown + bleach (safe_markdown() wrapper for XSS)
- Stripe: `os.getenv("STRIPE_SECRET_KEY")` — sandbox mode
- Deploy: Render $7/month Starter · auto-deploy on git push

## File Structure
```
~/Desktop/Projects/
├── app.py                          # All routes, models, auth, API calls
├── listing.py                      # Listing-specific logic
├── templates/
│   ├── base.html                   # Global nav, tokens, shared CSS
│   ├── index.html                  # Landing page
│   ├── dashboard.html              # User dashboard
│   ├── admin.html                  # Admin panel (/admin?secret=)
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── pricing.html
│   ├── limit.html                  # Free tier limit page
│   ├── waitlist_success.html
│   ├── terms.html
│   ├── privacy.html
│   ├── listing.html                # + photo upload zone
│   ├── results.html
│   ├── open_house.html
│   ├── open_house_results.html
│   ├── social_media.html
│   ├── social_media_results.html
│   ├── offer_letter.html
│   ├── offer_letter_results.html
│   ├── market_report.html
│   ├── market_report_results.html
│   ├── client_emails.html
│   ├── client_emails_results.html
│   ├── bio_generator.html
│   ├── bio_generator_results.html
│   ├── property_comparison.html
│   └── property_comparison_results.html
```

## Hard Rules — Never Break
- API key: always `os.getenv("ANTHROPIC_API_KEY")` — never hardcode
- Model: always `claude-sonnet-4-5` — never change
- Stripe keys: always `os.getenv()` — never hardcode
- No white backgrounds on any template — ever
- All existing routes must return 200 after every change
- pip installs must always use `--break-system-packages`
- No framework migrations — stack is Flask/Jinja2, not Next.js/React
- No fake social proof — no testimonials, no brokerage logos
- CSS transitions only — no animation libraries

## Design Tokens (defined in base.html)
```css
--navy:           #061326;
--card:           #0d1b34;
--card-border:    rgba(201,168,76,0.15);
--input:          #1a2f45;
--gold:           #c9a84c;
--gold-light:     #e8c97a;
--gold-btn:       #d4a843;
--text-primary:   #ffffff;
--text-secondary: rgba(255,255,255,0.6);
--labels:         #8892a4;
--live-green:     #22c55e;
```

Spacing scale: 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64px only
Border radius: cards 12px · inputs 8px · buttons 8px · badges 20px

## Button Variants
- Primary: `background: var(--gold-btn)` · `color: #000` · `font-weight: 600` · hover: brightness(1.1) scale(1.01)
- Ghost: transparent · `border: 1px solid rgba(255,255,255,0.2)` · hover: border --gold · color --gold

## LIVE Badge Component
```css
.live-badge {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.3);
  color: #22c55e; font-size: 10px; font-weight: 600;
  letter-spacing: 0.1em; padding: 3px 8px; border-radius: 20px;
}
.live-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #22c55e; animation: pulse 2s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
```

## What's Built
- 8 AI tools: /listing /open-house /social-media /offer-letter /market-report /client-emails /bio-generator /property-comparison
- Full auth: register / login / logout (Flask-Login + Flask-Bcrypt)
- PostgreSQL: User, Generation, Waitlist models
- Dashboard: saved generations, usage, plan badge, search/filter
- PDF export · Copy to clipboard · HAR disclaimer on all tools
- Free tier: 3 generations/month · Pro: unlimited ($79/month)
- Stripe billing: sandbox mode
- Admin panel: /admin?secret= · shows users, waitlist, stats · Set Pro/Free buttons
- Photo upload on /listing: base64, in-memory only, passes images to Claude vision API
- Agent profile: /profile · Legal: /terms · /privacy
- XSS protection: bleach.clean() via safe_markdown() on all AI output

## Render Environment Variables Required
```
ANTHROPIC_API_KEY
DATABASE_URL
ADMIN_SECRET
STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET
```

## Next Build Priorities
1. Brokerage dashboard — seat management, usage tracking
2. Stripe go-live — swap sandbox keys
3. Output quality improvements
4. Loom demo video

## Claude Code Session Rules
- Work one file at a time: read → rewrite → save → confirm → next
- Never read all templates at once — causes context overflow and compaction
- Always verify syntax before finishing: `python3 -c "import py_compile; py_compile.compile('app.py', doraise=True)"`
- Test checklist before ending any session:
  - [ ] All 8 tool routes return 200
  - [ ] No white backgrounds on any page
  - [ ] Dashboard loads with real user data
  - [ ] Photo upload zone visible on /listing
