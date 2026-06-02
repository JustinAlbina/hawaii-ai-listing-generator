from flask import Flask, render_template, request, session, redirect, url_for, abort, make_response, send_file, flash
from urllib.parse import urlparse, urljoin
import secrets as _secrets_mod
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import anthropic
import json
import datetime
import io
import base64
from PIL import Image
import random
import hashlib
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
import markdown as md_lib
import bleach
import stripe
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from neighborhoods import get_neighborhood_context, format_neighborhood_for_prompt

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = Flask(__name__)
_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set")
app.secret_key = _secret_key

if not os.getenv("ADMIN_SECRET"):
    raise RuntimeError("ADMIN_SECRET environment variable is not set")

database_url = os.getenv("DATABASE_URL", "sqlite:///alohaagent.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB — handles up to 8 large photos

csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[])

@app.errorhandler(CSRFError)
def csrf_error(e):
    return render_template("login.html", error="Your session expired. Please try again."), 400

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ─── Models ───────────────────────────────────────────────────────────────────

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    plan = db.Column(db.String(20), default='free')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    full_name = db.Column(db.String(100), nullable=True)
    brokerage = db.Column(db.String(100), nullable=True)
    island = db.Column(db.String(50), nullable=True)
    license_number = db.Column(db.String(50), nullable=True)
    generations = db.relationship('Generation', backref='user', lazy=True)

class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Generation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    output_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def input_parsed(self):
        try:
            return json.loads(self.input_data)
        except Exception:
            return {}

class SharedResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), unique=True, nullable=False, index=True)
    address = db.Column(db.String(200))
    neighborhood = db.Column(db.String(100))
    island = db.Column(db.String(50))
    price = db.Column(db.String(50))
    bedrooms = db.Column(db.String(20))
    bathrooms = db.Column(db.String(20))
    sqft = db.Column(db.String(20))
    view = db.Column(db.String(100))
    pool_yn = db.Column(db.String(10))
    price_per_sqft = db.Column(db.String(20))
    property_type = db.Column(db.String(50))
    year_built = db.Column(db.String(20))
    parking = db.Column(db.String(100))
    land_tenure = db.Column(db.String(50))
    solar = db.Column(db.String(5))
    ohana = db.Column(db.String(5))
    renovation_year = db.Column(db.String(20))
    flood_zone = db.Column(db.String(100))
    extra = db.Column(db.Text)
    hoa_fee = db.Column(db.String(50))
    listing_html = db.Column(db.Text)
    analysis_html = db.Column(db.Text)
    neighborhood_html = db.Column(db.Text)
    photo_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def input_parsed(self):
        try:
            return json.loads(self.input_data)
        except Exception:
            return {}

    @property
    def output_preview(self):
        text = self.output_text.strip()
        return text[:200] + "..." if len(text) > 200 else text

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

# ─── Generation helpers ────────────────────────────────────────────────────────

_SAFE_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li',
    'strong', 'em', 'br', 'table', 'thead', 'tbody',
    'tr', 'th', 'td', 'blockquote', 'pre', 'code',
]
_SAFE_ATTRS = {'*': ['class']}

def safe_markdown(text):
    raw = md_lib.markdown(text or "", extensions=["nl2br"])
    return bleach.clean(raw, tags=_SAFE_TAGS, attributes=_SAFE_ATTRS, strip=True)

def to_html(text):
    return safe_markdown(text)

def get_monthly_count(user):
    now = datetime.datetime.utcnow()
    start = datetime.datetime(now.year, now.month, 1)
    return Generation.query.filter(
        Generation.user_id == user.id,
        Generation.created_at >= start
    ).count()

def generation_limit_response():
    """Check limit. Returns limit page or None. Increments session counter for non-auth users."""
    if current_user.is_authenticated:
        if current_user.plan == 'free' and get_monthly_count(current_user) >= 3:
            return render_template("limit.html")
        return None
    if session.get("generation_count", 0) >= 3:
        return render_template("limit.html")
    session["generation_count"] = session.get("generation_count", 0) + 1
    return None

def save_generation(tool_name, input_data, output_text):
    if current_user.is_authenticated:
        gen = Generation(
            user_id=current_user.id,
            tool_name=tool_name,
            input_data=json.dumps(input_data),
            output_text=output_text
        )
        db.session.add(gen)
        db.session.commit()

def _process_photos(field_name="photos"):
    """Read uploaded photos, compress to max 1024px / JPEG q75, return list of (base64_data, media_type). Max 8. In-memory only."""
    results = []
    allowed_types = {"image/jpeg", "image/png"}
    ext_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}
    for f in request.files.getlist(field_name)[:8]:
        if not f or not f.filename:
            continue
        mt = (f.content_type or "").split(";")[0].strip().lower()
        if mt not in allowed_types:
            ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
            mt = ext_map.get(ext)
            if not mt:
                continue
        img = Image.open(f.stream)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.thumbnail((1024, 1024), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75, optimize=True)
        results.append((base64.b64encode(buf.getvalue()).decode("utf-8"), "image/jpeg"))
    return results

# ─── Security headers ─────────────────────────────────────────────────────────

@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_safe_redirect(url):
    ref = urlparse(urljoin(request.host_url, url))
    return ref.scheme in ("http", "https") and ref.netloc == urlparse(request.host_url).netloc

# ─── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm = request.form["confirm_password"]
        if password != confirm:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif User.query.filter_by(email=email).first():
            error = "An account with that email already exists. Log in instead."
        else:
            pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            user = User(email=email, password_hash=pw_hash)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per hour; 5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            error = "Invalid email or password."
        else:
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page if next_page and _is_safe_redirect(next_page) else url_for("dashboard"))
    return render_template("login.html", error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    generations = Generation.query.filter_by(user_id=current_user.id).order_by(Generation.created_at.desc()).all()
    monthly_count = get_monthly_count(current_user)
    return render_template("dashboard.html",
        generations=generations,
        monthly_count=monthly_count
    )

@app.route("/download/<int:gen_id>")
@login_required
def download_pdf(gen_id):
    import re as _re
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import Color
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

    gen = db.session.get(Generation, gen_id)
    if gen is None:
        abort(404)
    if gen.user_id != current_user.id:
        abort(403)

    GOLD    = Color(0.788, 0.659, 0.298)
    GRAY    = Color(0.5,   0.5,   0.5)
    DGRAY   = Color(0.3,   0.3,   0.3)
    FGRAY   = Color(0.6,   0.6,   0.6)
    LGRAY   = Color(0.8,   0.8,   0.8)
    BODY    = Color(0.12,  0.18,  0.27)

    s_brand   = ParagraphStyle("pdfbrand",   fontSize=20, fontName="Helvetica-Bold", textColor=GOLD,  spaceAfter=2,  leading=24)
    s_sub     = ParagraphStyle("pdfsub",     fontSize=9,  fontName="Helvetica",      textColor=GRAY,  spaceAfter=1,  leading=12)
    s_subject = ParagraphStyle("pdfsubject", fontSize=9,  fontName="Helvetica",      textColor=DGRAY, spaceAfter=0,  leading=12)
    s_date    = ParagraphStyle("pdfdate",    fontSize=9,  fontName="Helvetica",      textColor=GRAY,  alignment=TA_RIGHT, leading=12)
    s_label   = ParagraphStyle("pdflabel",   fontSize=10, fontName="Helvetica-Bold", textColor=GOLD,  spaceAfter=6,  spaceBefore=2, leading=13)
    s_body    = ParagraphStyle("pdfbody",    fontSize=10, fontName="Helvetica",      textColor=BODY,  leading=14,    spaceAfter=3)
    s_footer  = ParagraphStyle("pdffooter",  fontSize=8,  fontName="Helvetica",      textColor=FGRAY, alignment=TA_CENTER)

    date_str  = gen.created_at.strftime("%B %d, %Y")
    safe_name = gen.tool_name.lower().replace(" ", "-")
    tool      = gen.tool_name
    inp       = gen.input_parsed

    def esc(t):
        return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def val(*keys):
        for k in keys:
            v = inp.get(k, "")
            if v and str(v).strip():
                return str(v).strip()
        return ""

    # ── Per-tool subject line ────────────────────────────────────────────────────
    def build_subject():
        if "Listing Generator" in tool:
            parts = [v for v in [val("address"), val("neighborhood","area"), val("island")] if v]
            return " · ".join(parts)
        if "Open House" in tool:
            parts = [v for v in [val("address"), val("date","event_date"), val("time_start","start_time","time")] if v]
            return " · ".join(parts)
        if "Social Media" in tool:
            parts = [v for v in [val("address"), val("platform","platforms")] if v]
            return " · ".join(parts)
        if "Offer Letter" in tool:
            parts = [val("address")]
            price = val("offer_price","offer_amount")
            if price: parts.append(f"Offer: ${price}")
            return " · ".join([p for p in parts if p])
        if "Market Report" in tool:
            parts = [v for v in [val("neighborhood","area","community"), val("island")] if v]
            return " · ".join(parts)
        if "Client Email" in tool:
            parts = [v for v in [val("client_name"), val("email_type","type")] if v]
            return " · ".join(parts)
        if "Bio" in tool:
            return val("full_name","agent_name","name")
        if "Property Comparison" in tool:
            a1 = val("address_1","property_1_address","address1")
            a2 = val("address_2","property_2_address","address2")
            if a1 and a2: return f"{a1} vs {a2}"
            return a1 or a2
        return val("address","neighborhood","full_name","client_name")

    subject = build_subject()

    # ── Section label normalisation ──────────────────────────────────────────────
    LABEL_MAP = {
        "LISTING DESCRIPTION": "Listing Description",
        "LISTING":             "Listing Description",
        "ANALYSIS":            "Market Analysis",
        "LISTING SCORE":       "Market Analysis",
        "PRICE ANALYSIS":      "Market Analysis",
        "NEIGHBORHOOD REPORT": "Neighborhood Report",
        "NEIGHBORHOOD":        "Neighborhood Report",
        "MARKET REPORT":       "Market Report",
        "OPEN HOUSE":          "Open House Details",
        "SOCIAL MEDIA":        "Social Media Posts",
        "OFFER":               "Offer Details",
        "OFFER LETTER":        "Offer Letter",
        "EMAIL":               "Email",
        "BIO":                 "Agent Bio",
        "AGENT BIO":           "Agent Bio",
        "COMPARISON":          "Comparison",
        "REPORT":              "Report",
        "SUMMARY":             "Summary",
        "OVERVIEW":            "Overview",
        "FEATURES":            "Features",
        "HIGHLIGHTS":          "Highlights",
        "DETAILS":             "Details",
        "PROPERTY DETAILS":    "Property Details",
        "NOTES":               "Notes",
    }

    def normalise_label(raw):
        key = raw.strip().rstrip(":").upper()
        return LABEL_MAP.get(key, raw.strip().rstrip(":").title())

    # ── Markdown → structured tokens ─────────────────────────────────────────────
    ALL_CAPS_LABEL = _re.compile(r'^[A-Z][A-Z\s]{2,}:?\s*$')

    def process_output(raw):
        lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        tokens = []
        blank_run = 0

        for line in lines:
            s = line.strip()

            # horizontal rules → skip
            if _re.match(r'^[-_\*]{3,}$', s):
                continue

            # markdown headings
            m = _re.match(r'^#{1,3}\s+(.*)', s)
            if m:
                blank_run = 0
                tokens.append(("section", normalise_label(m.group(1))))
                continue

            # ALL-CAPS label lines
            if ALL_CAPS_LABEL.match(s) and len(s) < 60:
                blank_run = 0
                tokens.append(("section", normalise_label(s)))
                continue

            # bullet points
            m = _re.match(r'^[\*\-]\s+(.*)', s)
            if m:
                blank_run = 0
                inner = _re.sub(r'\*\*(.*?)\*\*', r'\1', m.group(1))
                inner = _re.sub(r'\*(.*?)\*',     r'\1', inner)
                tokens.append(("body", "• " + esc(inner)))
                continue

            # strip bold/italic markers from body
            clean = _re.sub(r'\*\*(.*?)\*\*', r'\1', s)
            clean = _re.sub(r'\*(.*?)\*',     r'\1', clean)

            if not clean:
                blank_run += 1
                if blank_run <= 2:
                    tokens.append(("blank", ""))
            else:
                blank_run = 0
                tokens.append(("body", esc(clean)))

        return tokens

    # ── Assemble story ───────────────────────────────────────────────────────────
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.85*inch, rightMargin=0.85*inch,
        topMargin=0.85*inch, bottomMargin=0.85*inch
    )

    left_cell = [
        Paragraph("AlohaAgent", s_brand),
        Paragraph("AI Tools for Hawaii Real Estate", s_sub),
        Paragraph(esc(current_user.email), s_sub),
    ]
    if subject:
        left_cell.append(Paragraph(esc(subject), s_subject))

    header_table = Table(
        [[left_cell, [Paragraph(date_str, s_date)]]],
        colWidths=[400, 100]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("ALIGN",         (1, 0), (1,  0),  "RIGHT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    story = [
        header_table,
        HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=8),
    ]

    tokens = process_output(gen.output_text)
    for kind, text in tokens:
        if kind == "section":
            story.append(HRFlowable(width="100%", thickness=0.5, color=LGRAY, spaceAfter=4))
            story.append(Paragraph(text.upper(), s_label))
        elif kind == "body":
            story.append(Paragraph(text, s_body))
        else:
            story.append(Spacer(1, 6))

    story += [
        Spacer(1, 24),
        HRFlowable(width="100%", thickness=0.5, color=LGRAY, spaceAfter=6),
        Paragraph("Generated by AlohaAgent &nbsp;·&nbsp; listaloha.onrender.com", s_footer),
    ]

    doc.build(story)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"alohaagent-{safe_name}-{gen.id}.pdf"
    )

# ─── Existing routes ───────────────────────────────────────────────────────────

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", "").strip()
        current_user.brokerage = request.form.get("brokerage", "").strip()
        current_user.island = request.form.get("island", "").strip()
        current_user.license_number = request.form.get("license_number", "").strip()
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html", user=current_user)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/listing")
def listing():
    if current_user.is_authenticated:
        count = get_monthly_count(current_user)
        remaining = max(0, 3 - count) if current_user.plan == 'free' else 999
    else:
        count = session.get("generation_count", 0)
        remaining = max(0, 3 - count)
    return render_template("listing.html", remaining=remaining, count=count, current_user=current_user)

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/generate", methods=["POST"])
def generate():
    return _generate_inner()

def _generate_inner():
    limit = generation_limit_response()
    if limit:
        return limit
    address = request.form["address"]
    bedrooms = request.form["bedrooms"]
    bathrooms = request.form["bathrooms"]
    sqft = request.form["sqft"]
    price = request.form["price"]
    neighborhood = request.form["neighborhood"]
    island = request.form["island"]
    view = request.form.get("view", "").strip()
    pool_yn = request.form.get("pool", "no")
    extra = request.form["extra"]
    year_built = request.form.get("year_built", "").strip()
    parking = request.form.get("parking", "").strip()
    land_tenure = request.form.get("land_tenure", "Fee Simple")
    solar = request.form.get("solar", "")
    ohana = request.form.get("ohana", "")
    renovation_year = request.form.get("renovation_year", "").strip()
    flood_zone = request.form.get("flood_zone", "").strip()
    property_type = request.form.get("property_type", "Single Family").strip()
    hoa_fee = request.form.get("hoa_fee", "").strip()

    try:
        sqft_num = float(sqft.replace(",", ""))
        price_num = float(price.replace(",", "").replace("$", ""))
        price_per_sqft = round(price_num / sqft_num)
    except Exception:
        price_per_sqft = "N/A"

    year_built_line = f"Year built: {year_built}" if year_built else ""
    parking_line = f"Parking: {parking}" if parking else ""
    solar_line = "Solar/PV system: Yes" if solar else ""
    ohana_line = "Ohana unit / ADU: Yes" if ohana else ""
    renovation_year_line = f"Renovation year: {renovation_year}" if renovation_year else ""
    flood_zone_line = f"Flood zone: {flood_zone}" if flood_zone else ""
    view_line = f"View: {view}" if view else ""
    hoa_fee_line = f"HOA Fee (monthly): {hoa_fee}" if hoa_fee else ""

    _pt_rules = {
        "Single Family": "For single family homes, emphasize the yard, privacy, sense of ownership, and Hawaii family lifestyle. Highlight indoor-outdoor flow and lot ownership.",
        "Condo": "For condos, emphasize lock-and-leave lifestyle, building amenities, lanai living, and HOA-managed exterior maintenance. Condo copy must feel distinctly different from single-family copy — no mention of yards or driveways. Focus on community amenities, views from the unit, and the ease of island living." + (f" Monthly HOA of {hoa_fee} — frame this as value against owning and maintaining a property outright." if hoa_fee else ""),
        "Townhome": "For townhomes, highlight the balance of privacy and community, multi-level living, and the attached or assigned parking that many Hawaii condos lack.",
        "Land": "For land listings, NO interior narrative — there is no interior. Focus entirely on the lot: views, topography, zoning, utilities, building potential, and what life looks like after the buyer builds their vision here.",
    }
    _property_type_rule = _pt_rules.get(property_type, "")

    # Neighborhood context injection
    _nb_data = get_neighborhood_context(neighborhood, island)
    _nb_context = format_neighborhood_for_prompt(_nb_data, neighborhood) if _nb_data else ""

    _listing_templates = [
        "Lead with lifestyle — paint a picture of how this home feels to live in day to day. Start with the daily rhythms, routines, and sensory details of life in this specific home before introducing the property facts.",
        "Lead with location — open by anchoring the reader in the specific place this home sits. What surrounds it, what you can access, what the setting means for daily life in Hawaii. Then bring them inside.",
        "Lead with the home's single most standout physical feature. Open on that one thing specifically and vividly, then let it naturally expand outward to the full property and lifestyle.",
        "Lead with one specific sensory detail that only exists at this exact property — not Hawaii in general, not the neighborhood, but this address. What do you see, hear, or feel that you would not find anywhere else. Then expand outward.",
        "Lead with what this home has clearly been through — its age, its renovation, its land tenure, its position on the street — and what that history means for the buyer standing in it today. Soul first, facts second.",
    ]
    _template_instruction = random.choice(_listing_templates)
    generation_id = hashlib.md5(f"{address}{time.time()}".encode()).hexdigest()[:8]

    listing_prompt = f"""You are the best real estate agent in Hawaii. Twenty years on the islands. You have sold studios in Kakaako and estates on Kahala Beach. You grew up Windward, you know the Westside, you've closed deals in Hana and in Princeville. You write the way you talk to clients — direct, specific, no filler, no flattery. You notice things other agents miss: the way a trade wind moves through a particular floor plan, what a kitchen layout says about how a family actually lives, why fee simple on one street means something different than fee simple three blocks away. You have never once written the words "rare find", "nestled", "boasts", or "perfect for entertaining" and you never will. You do not oversell. You do not bullshit. You write one listing at a time and you make it count.

STRUCTURAL APPROACH: {_template_instruction}

PROPERTY DETAILS:
Address: {address}
Neighborhood: {neighborhood}
Island: {island}
Bedrooms: {bedrooms}
Bathrooms: {bathrooms}
Square footage: {sqft}
Price: {price}
Price per sqft: ${price_per_sqft}
{view_line}
Pool: {pool_yn}
Standout feature: {extra}
Land tenure: {land_tenure}
{year_built_line}
{parking_line}
{solar_line}
{ohana_line}
{renovation_year_line}
{flood_zone_line}
Property type: {property_type}
{hoa_fee_line}

Generation ID: {generation_id}. This is a completely original piece of writing. No connection to any previous output.

{_nb_context}

PROPERTY TYPE RULES:
{_property_type_rule}

PRICE TIER VOICE:
Determine the price tier from the listing price and adjust your voice accordingly.
- Under $800k: energetic, opportunity-focused, practical Hawaii lifestyle. These buyers are stretching — honor that.
- $800k–$2M: confident, specific, earned details. Write like you know this market cold.
- Over $2M: restrained, precise, nothing oversold. Luxury sells itself. Your job is to be accurate and evocative, not enthusiastic.

BEFORE YOU WRITE — complete these three steps. Complete all three steps internally before writing. Do not include this checklist or any proof-of-work in your output:
1. Identify the single most specific and true thing about this property that could not be said about any other property in Hawaii. It must appear in paragraph 1.
2. Identify the one lifestyle detail that will make the right buyer feel this home is theirs. It must appear in paragraph 2.
3. Identify the neighborhood fact from the context provided that most agents would not know to mention. It must appear in paragraph 3.
If any of these three things cannot be found in the output, the output is wrong. Rewrite it.

HARD RULES ON SENTENCE OPENERS — non-negotiable:
- First word of paragraph 1 cannot be "This", "The", the property address, or any adjective.
- Paragraph 2 cannot open with a room name.
- Paragraph 3 cannot open with "Located", "Just", "Situated", or "Nestled".
- No paragraph may open the same way as another paragraph.

HARD RULES ON RHYTHM:
- No two consecutive sentences in the same paragraph may have the same grammatical subject.
- No paragraph may contain more than two sentences under 10 words.
- No paragraph may contain more than two sentences over 35 words.
- If a paragraph reads like a list with periods instead of commas, rewrite it before outputting.

PARAGRAPH 2 RULE — mandatory:
Every sentence in paragraph 2 must answer the question "so what?" A feature named without a consequence for the buyer does not belong.
Wrong: "Hardwood floors carry through every room."
Right: "Hardwood carries through every room — no carpet transitions, no cold tile underfoot at 6am, no flooring decisions to make before you move in."
If a sentence in paragraph 2 cannot pass the "so what?" test, cut it or rewrite it. No exceptions.

NEIGHBORHOOD SPECIFICITY — mandatory:
Name at least two specific real places from the neighborhood context by their actual name. "Nearby beaches" is a failure. "Kailua Beach" is acceptable. "The morning kayak launch at Kailua Beach Park with the Mokulua Islands on the horizon" is the standard. Generic Hawaii atmosphere language that could apply to any neighborhood on any island is not acceptable. Every named location must be on the same island as the subject property. Referencing a place on a different island is a factual error that destroys agent credibility instantly.

HAWAII VOICE:
Write as a local who has lived and worked these islands for twenty years. Trade winds, land tenure, solar economics, flood zone implications, the difference between Windward and Leeward, the meaning of an ohana unit in a housing market this tight — these are not bullet points to mention, they are things you understand and convey naturally because you know what they mean to buyers and sellers in Hawaii.

BANNED WORDS AND PHRASES — always empty, never use them:
nestled, boasts, perfect for entertaining, rare find, rare opportunity, paradise, tropical oasis, island living at its finest, turnkey, won't last long, priced to sell, motivated seller, hidden gem, meticulously maintained, lovingly updated, sought-after.

DESCRIPTORS THAT NEED EVIDENCE — allowed only if the next clause earns them with a specific detail:
stunning, spacious, cozy, charming, inviting, desirable, open concept, move-in ready, natural light.
A descriptor standing alone is lazy writing. Cut it or earn it.

INTEGRATION RULES — specs are not bullet points:
Never list bedrooms, bathrooms, square footage, parking, or land tenure as raw specs. Integrate every detail into the narrative.
Wrong: "3BR/2BA, 1,800 sqft."
Right: "Three bedrooms and two baths across 1,800 square feet that never feel crowded because the floor plan was thought through."
Wrong: "Fee simple."
Right: "Fee simple ownership on a street where leasehold is common enough that this matters."

OUTPUT STRUCTURE — exactly 3 paragraphs, no headers, no labels:
Paragraph 1: Open on the strongest most specific hook this property earns — sensory, situational, or grounded in a fact that could only be true here. Establish the property's character and the life it enables. The single most specific and true thing about this property must land here.
Paragraph 2: Move through the interior and key features with narrative momentum. Every sentence must pass the "so what?" test — a feature without a consequence for the buyer does not belong. The lifestyle detail that makes the right buyer feel this is theirs must land here.
Paragraph 3: Ground the reader in location and Hawaii context using specific named places. End with one quiet confident sentence that states what this property is and what the right buyer should do — not a sales pitch, a fact."""

    photo_list = _process_photos()
    photo_count = len(photo_list)
    if photo_list:
        photo_prefix = (
            f"You have been provided {len(photo_list)} property photo(s). Analyze them carefully.\n"
            "Incorporate specific visual details you observe — finishes, fixtures,\n"
            "views, layout, natural light, condition — into the listing description.\n"
            "Be specific, not generic.\n\n"
        )
        listing_content = [
            *[{"type": "image", "source": {"type": "base64", "media_type": mt, "data": img_data}}
              for img_data, mt in photo_list],
            {"type": "text", "text": photo_prefix + listing_prompt}
        ]
        listing_messages = [{"role": "user", "content": listing_content}]
    else:
        listing_messages = [{"role": "user", "content": listing_prompt}]

    _analysis_prompt = f"""You are a Hawaii real estate expert. Analyze this property:

Address: {address}, {neighborhood}, {island}
Bedrooms: {bedrooms}, Bathrooms: {bathrooms}
Square footage: {sqft}, Price: {price}
Price per sqft: ${price_per_sqft}
{view_line}
Pool: {pool_yn}
Standout feature: {extra}
Land tenure: {land_tenure}

Format exactly like this:
LISTING SCORE: X/10
[2-3 sentence explanation]

PRICE ANALYSIS:
[2-3 sentence explanation]

If land tenure is Leasehold, you MUST include a prominent warning in the PRICE ANALYSIS section:
LEASEHOLD PROPERTY: This property is leasehold, not fee simple. Leasehold properties in Hawaii typically sell at a significant discount (20-40%) vs fee simple. Many lenders will not finance leasehold properties with fewer than 30 years remaining on the lease. Buyers should verify lease expiration, rent renegotiation terms, and financing eligibility before making an offer."""

    _neighborhood_prompt = f"""You are a Hawaii local expert. Provide a neighborhood report for {neighborhood} on {island}, Hawaii.

Format exactly like this:
WALKABILITY SCORE: X/10
[2 sentence explanation]

NEARBY ATTRACTIONS:
- [Attraction 1 and brief description]
- [Attraction 2 and brief description]
- [Attraction 3 and brief description]
- [Attraction 4 and brief description]
- [Attraction 5 and brief description]

NEIGHBORHOOD VIBE:
[2-3 sentences]"""

    def _call_listing():
        return client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1800, temperature=0.85, messages=listing_messages)

    def _call_analysis():
        return client.messages.create(
            model="claude-sonnet-4-6", max_tokens=512,
            messages=[{"role": "user", "content": _analysis_prompt}])

    def _call_neighborhood():
        return client.messages.create(
            model="claude-sonnet-4-6", max_tokens=512,
            messages=[{"role": "user", "content": _neighborhood_prompt}])

    with ThreadPoolExecutor(max_workers=3) as pool:
        f_listing = pool.submit(_call_listing)
        f_analysis = pool.submit(_call_analysis)
        f_neighborhood = pool.submit(_call_neighborhood)
        listing_response = f_listing.result()
        analysis_response = f_analysis.result()
        neighborhood_response = f_neighborhood.result()

    listing_text = listing_response.content[0].text
    analysis_text = analysis_response.content[0].text
    neighborhood_text = neighborhood_response.content[0].text

    save_generation("Listing Generator",
        {"address": address, "neighborhood": neighborhood, "island": island,
         "price": price, "bedrooms": bedrooms, "bathrooms": bathrooms, "sqft": sqft,
         "property_type": property_type},
        f"LISTING:\n{listing_text}\n\nANALYSIS:\n{analysis_text}\n\nNEIGHBORHOOD REPORT:\n{neighborhood_text}"
    )

    listing_html = to_html(listing_text)
    analysis_html = to_html(analysis_text)
    neighborhood_html = to_html(neighborhood_text)

    share_token = _secrets_mod.token_hex(8)
    shared = SharedResult(
        token=share_token,
        address=address, neighborhood=neighborhood, island=island,
        price=price, bedrooms=bedrooms, bathrooms=bathrooms, sqft=sqft,
        view=view, pool_yn=pool_yn, price_per_sqft=str(price_per_sqft),
        property_type=property_type, year_built=year_built, parking=parking,
        land_tenure=land_tenure, solar=solar, ohana=ohana,
        renovation_year=renovation_year, flood_zone=flood_zone, extra=extra,
        hoa_fee=hoa_fee, listing_html=listing_html, analysis_html=analysis_html,
        neighborhood_html=neighborhood_html, photo_count=photo_count
    )
    db.session.add(shared)
    db.session.commit()
    share_url = url_for('listing_shared_result', token=share_token, _external=True)

    prefill_data = {
        "address": address, "neighborhood": neighborhood, "island": island,
        "property_type": property_type, "bedrooms": bedrooms, "bathrooms": bathrooms,
        "sqft": sqft, "price": price, "year_built": year_built, "parking": parking,
        "view": view, "pool": pool_yn, "land_tenure": land_tenure,
        "solar": solar, "ohana": ohana, "renovation_year": renovation_year,
        "flood_zone": flood_zone, "extra": extra, "hoa_fee": hoa_fee
    }

    return render_template("results.html",
        address=address,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        sqft=sqft,
        price=price,
        neighborhood=neighborhood,
        island=island,
        view=view,
        pool=pool_yn,
        price_per_sqft=price_per_sqft,
        property_type=property_type,
        year_built=year_built,
        parking=parking,
        land_tenure=land_tenure,
        solar=solar,
        ohana=ohana,
        renovation_year=renovation_year,
        flood_zone=flood_zone,
        extra=extra,
        hoa_fee=hoa_fee,
        listing=listing_html,
        analysis=analysis_html,
        neighborhood_report=neighborhood_html,
        photo_count=photo_count,
        share_url=share_url,
        prefill_data=prefill_data
    )

@app.route("/listing/result/<token>")
def listing_shared_result(token):
    result = SharedResult.query.filter_by(token=token).first_or_404()
    share_url = request.url
    prefill_data = {
        "address": result.address or "", "neighborhood": result.neighborhood or "",
        "island": result.island or "", "property_type": result.property_type or "Single Family",
        "bedrooms": result.bedrooms or "", "bathrooms": result.bathrooms or "",
        "sqft": result.sqft or "", "price": result.price or "",
        "year_built": result.year_built or "", "parking": result.parking or "",
        "view": result.view or "", "pool": result.pool_yn or "no",
        "land_tenure": result.land_tenure or "Fee Simple",
        "solar": result.solar or "", "ohana": result.ohana or "",
        "renovation_year": result.renovation_year or "",
        "flood_zone": result.flood_zone or "", "extra": result.extra or "",
        "hoa_fee": result.hoa_fee or ""
    }
    return render_template("results.html",
        address=result.address,
        bedrooms=result.bedrooms,
        bathrooms=result.bathrooms,
        sqft=result.sqft,
        price=result.price,
        neighborhood=result.neighborhood,
        island=result.island,
        view=result.view or "",
        pool=result.pool_yn,
        price_per_sqft=result.price_per_sqft,
        property_type=result.property_type or "",
        year_built=result.year_built or "",
        parking=result.parking or "",
        land_tenure=result.land_tenure or "",
        solar=result.solar or "",
        ohana=result.ohana or "",
        renovation_year=result.renovation_year or "",
        flood_zone=result.flood_zone or "",
        extra=result.extra or "",
        hoa_fee=result.hoa_fee or "",
        listing=result.listing_html,
        analysis=result.analysis_html,
        neighborhood_report=result.neighborhood_html,
        photo_count=result.photo_count,
        share_url=share_url,
        prefill_data=prefill_data
    )

@app.route("/refine-listing", methods=["POST"])
def refine_listing():
    listing_text = request.form.get("listing_text", "").strip()
    if not listing_text:
        return {"error": "No listing text provided"}, 400

    refine_prompt = f"""You are the same veteran Hawaii agent who wrote this listing. Twenty years on the islands. You do not rewrite for the sake of rewriting — you rewrite because something isn't earning its place.

Read this listing description. For each sentence ask two questions:
1. Could this sentence appear in a listing for a different property in Hawaii without changing a word? If yes, it is generic. Rewrite it to be specific to this exact property.
2. Does this sentence — especially in the second paragraph — name a feature without telling the buyer why it matters? If yes, it fails the "so what?" test. Rewrite it or cut it.

Apply the same rules that govern the original:
- No banned words: nestled, boasts, perfect for entertaining, rare find, rare opportunity, paradise, tropical oasis, turnkey, won't last long, hidden gem, meticulously maintained, lovingly updated, sought-after.
- No descriptor without evidence: stunning, spacious, cozy, charming, inviting, open concept, move-in ready, natural light must each be followed immediately by a specific detail that earns them.
- No raw specs. Bedrooms, bathrooms, square footage, parking, land tenure must be integrated into narrative, never listed.
- Maintain exactly 3 paragraphs. Do not add headers or labels.
- Do not change what is already working. Only fix what is generic, weak, or failing the "so what?" test.

Return only the improved listing description — no commentary, no explanation, no list of what you changed.

Current listing description:
{listing_text}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0.9,
        messages=[{"role": "user", "content": refine_prompt}]
    )
    return {"refined": response.content[0].text}

@app.route("/waitlist", methods=["POST"])
def waitlist():
    email = request.form["email"]
    try:
        db.session.add(Waitlist(email=email))
        db.session.commit()
        flash("You're on the waitlist!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("You're already on the waitlist!", "info")
    return redirect(url_for("home"))

@app.route("/open-house")
def open_house():
    return render_template("open_house.html", current_user=current_user)

@app.route("/open-house/generate", methods=["POST"])
def open_house_generate():
    limit = generation_limit_response()
    if limit:
        return limit
    address = request.form["address"]
    neighborhood = request.form["neighborhood"]
    island = request.form["island"]
    bedrooms = request.form["bedrooms"]
    bathrooms = request.form["bathrooms"]
    price = request.form["price"]
    date = request.form["date"]
    time_start = request.form["time_start"]
    time_end = request.form["time_end"]
    extra = request.form["extra"]
    agent_name = request.form.get("agent_name", "").strip()

    agent_line = f"Agent: {agent_name}" if agent_name else ""
    sign_off_instruction = f" Sign off all posts and the email from {agent_name}." if agent_name else ""

    # Neighborhood context injection
    _nb_data = get_neighborhood_context(neighborhood, island)
    _nb_context = format_neighborhood_for_prompt(_nb_data, neighborhood) if _nb_data else ""

    _oh_templates = [
        "Lead with the experience — open by describing what guests will feel, see, and discover the moment they step through the door. Make the reader feel already there before mentioning logistics.",
        "Lead with the neighborhood or location — open by anchoring readers in the specific place on the island. Why does this address matter? What does the setting add to the visit? Then bring them to the property.",
        "Lead with the property's single most impressive feature as the invitation hook. Open on that one thing vividly and specifically, then expand to the full open house invitation.",
        "Lead with the social and community angle — frame this open house as a genuine Hawaii gathering moment. Capture the vibe, the aloha spirit, what makes showing up feel worthwhile beyond just the property.",
        "Lead with honest, specific urgency — open by making a fact-based case for why this property won't last. Then invite readers to the open house as their real chance to act.",
    ]
    _oh_template_instruction = random.choice(_oh_templates)
    _oh_generation_id = hashlib.md5(f"{address}{time.time()}".encode()).hexdigest()[:8]

    photo_list = _process_photos()
    photo_count = len(photo_list)

    _oh_prompt = f"""You are a Hawaii real estate marketing expert writing for local Hawaii agents and their clients. Generate three open house announcements for this property.

STRUCTURAL APPROACH: {_oh_template_instruction}

Property Details:
Address: {address}
Neighborhood: {neighborhood}
Island: {island}
Bedrooms: {bedrooms}
Bathrooms: {bathrooms}
Price: {price}
Open House Date: {date}
Time: {time_start} to {time_end}
Highlight: {extra}
{agent_line}

Generation ID: {_oh_generation_id}. Treat this as a completely fresh and unique piece of writing with no connection to any previous output.

{_nb_context}

HAWAII VOICE RULES:
Always write with authentic Hawaii personality. Reference specific Hawaii lifestyle elements naturally — trade winds, island pace, proximity to beaches or mountains, local community feel, indoor-outdoor living, year-round weather. Never use mainland real estate clichés without grounding them in a Hawaii context. Write like a local expert, not like a generic real estate AI. Avoid anything that sounds like it was written for a suburban open house in Phoenix or Dallas.

CRAFT RULES:
Your output must be structurally and tonally distinct from a generic AI response. Vary sentence length, rhythm, and paragraph structure throughout. Mix short punchy sentences with longer descriptive ones. Never write in a predictable pattern. The goal is for a reader to believe this was written by a talented human copywriter who knows Hawaii deeply.

Open with the single most compelling and specific thing about this property and open house as the hook. Then naturally expand to cover the full picture. Do not build the entire output around just one thing.

Avoid leaning on overused real estate clichés as filler. If you use common descriptors like spacious, cozy, or stunning — always follow immediately with a specific detail that earns the word. Never let a descriptor stand alone without evidence backing it up.

Format your response EXACTLY like this:

INSTAGRAM POST:
[2-3 sentences max, warm and exciting, include the date and time, end with relevant Hawaii hashtags]

FACEBOOK POST:
[3-4 sentences, friendly and detailed, include all property details and open house info, professional tone]

EMAIL SUBJECT:
[Compelling email subject line]

EMAIL BODY:
[Professional 3-4 sentence email announcing the open house, suitable to send to a client list{sign_off_instruction}]"""

    if photo_list:
        _oh_photo_prefix = (
            f"You have been provided {photo_count} property photo(s). Analyze them carefully.\n"
            "Incorporate specific visual details you observe — finishes, fixtures, views, layout, natural light, condition — into the announcements.\n"
            "Be specific, not generic.\n\n"
        )
        _oh_content = [
            *[{"type": "image", "source": {"type": "base64", "media_type": mt, "data": img_data}}
              for img_data, mt in photo_list],
            {"type": "text", "text": _oh_photo_prefix + _oh_prompt}
        ]
        _oh_messages = [{"role": "user", "content": _oh_content}]
    else:
        _oh_messages = [{"role": "user", "content": _oh_prompt}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        temperature=0.9,
        messages=_oh_messages
    )

    content = response.content[0].text

    sections = {}
    for section in ["INSTAGRAM POST", "FACEBOOK POST", "EMAIL SUBJECT", "EMAIL BODY"]:
        if section + ":" in content:
            start = content.index(section + ":") + len(section + ":")
            next_sections = [s + ":" for s in ["INSTAGRAM POST", "FACEBOOK POST", "EMAIL SUBJECT", "EMAIL BODY"] if s + ":" in content and content.index(s + ":") > start]
            if next_sections:
                end = content.index(next_sections[0])
                sections[section] = content[start:end].strip()
            else:
                sections[section] = content[start:].strip()

    save_generation("Open House Announcer",
        {"address": address, "neighborhood": neighborhood, "island": island, "date": date, "price": price},
        content
    )

    return render_template("open_house_results.html",
        address=address,
        neighborhood=neighborhood,
        island=island,
        date=date,
        time_start=time_start,
        time_end=time_end,
        price=price,
        instagram=to_html(sections.get("INSTAGRAM POST", "")),
        facebook=to_html(sections.get("FACEBOOK POST", "")),
        email_subject=sections.get("EMAIL SUBJECT", ""),
        email_body=to_html(sections.get("EMAIL BODY", "")),
        photo_count=photo_count
    )

@app.route("/refine-open-house", methods=["POST"])
def refine_open_house():
    post_text = request.form.get("post_text", "").strip()
    if not post_text:
        return {"error": "No post text provided"}, 400

    refine_prompt = f"""Review this open house Instagram post. Identify any sentences that sound generic, could apply to any property anywhere, or feel like filler. Rewrite only those specific sentences to be more vivid, specific, and grounded in this exact property's details and Hawaii location. Return ONLY the improved post — no commentary, no explanations, no headers.

Current post:
{post_text}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        temperature=0.9,
        messages=[{"role": "user", "content": refine_prompt}]
    )
    return {"refined": response.content[0].text}

@app.route("/social-media")
def social_media():
    return render_template("social_media.html", current_user=current_user)

@app.route("/social-media/generate", methods=["POST"])
def social_media_generate():
    limit = generation_limit_response()
    if limit:
        return limit
    address = request.form["address"]
    neighborhood = request.form["neighborhood"]
    island = request.form["island"]
    bedrooms = request.form["bedrooms"]
    bathrooms = request.form["bathrooms"]
    sqft = request.form["sqft"]
    price = request.form["price"]
    ocean_view = request.form["ocean_view"]
    pool = request.form["pool"]
    extra = request.form["extra"]
    tone = request.form["tone"]

    # Neighborhood context injection
    _nb_data = get_neighborhood_context(neighborhood, island)
    _nb_context = format_neighborhood_for_prompt(_nb_data, neighborhood) if _nb_data else ""

    photo_list = _process_photos()
    photo_count = len(photo_list)

    _sm_generation_id = hashlib.md5(f"{address}{time.time()}".encode()).hexdigest()[:8]

    _sm_prompt = f"""You are a Hawaii real estate social media expert. Generate social media posts for this property listing.

Property Details:
Address: {address}
Neighborhood: {neighborhood}
Island: {island}
Bedrooms: {bedrooms}
Bathrooms: {bathrooms}
Square footage: {sqft}
Price: {price}
Ocean view: {ocean_view}
Pool: {pool}
Standout feature: {extra}
Tone: {tone}

Generation ID: {_sm_generation_id}. Treat this as a completely fresh and unique piece of writing with no connection to any previous output.

{_nb_context}

HAWAII VOICE RULES:
Always write with authentic Hawaii personality. Reference specific Hawaii lifestyle elements naturally — trade winds, island pace, proximity to beaches or mountains, local community feel, indoor-outdoor living, year-round weather. Never use mainland real estate clichés without grounding them in a Hawaii context. Write like a local expert, not like a generic real estate AI. Avoid anything that sounds like it was written for a suburban home in Phoenix or Dallas.

CRAFT RULES:
Your output must be structurally and tonally distinct from a generic AI response. Vary sentence length, rhythm, and paragraph structure throughout. Mix short punchy sentences with longer descriptive ones. Never write in a predictable pattern. The goal is for a reader to believe this was written by a talented human copywriter who knows Hawaii deeply.

Open with the single most compelling and specific thing about this property as the hook. Then naturally expand to cover the full picture of the home and lifestyle. Do not build the entire output around just one thing.

Avoid leaning on overused real estate clichés as filler. If you use common descriptors like spacious, cozy, or stunning — always follow immediately with a specific detail that earns the word. Never let a descriptor stand alone without evidence backing it up.

Format your response EXACTLY like this:

INSTAGRAM CAPTION:
[2-3 punchy sentences, engaging and visual, include price, end with a call to action]

FACEBOOK POST:
[4-5 sentences, more detailed and informative, include all key details, professional yet warm]

X POST:
[MUST be 280 characters or fewer — count carefully. Punchy and attention grabbing, include price. No hashtags here.]

HASHTAGS:
[20-25 relevant hashtags including Hawaii specific ones, real estate ones, and neighborhood specific ones]"""

    if photo_list:
        _sm_photo_prefix = (
            f"You have been provided {photo_count} property photo(s). Analyze them carefully.\n"
            "Incorporate specific visual details you observe — finishes, fixtures, views, layout, natural light, condition — into the social media posts.\n"
            "Be specific, not generic.\n\n"
        )
        _sm_content = [
            *[{"type": "image", "source": {"type": "base64", "media_type": mt, "data": img_data}}
              for img_data, mt in photo_list],
            {"type": "text", "text": _sm_photo_prefix + _sm_prompt}
        ]
        _sm_messages = [{"role": "user", "content": _sm_content}]
    else:
        _sm_messages = [{"role": "user", "content": _sm_prompt}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        temperature=0.9,
        messages=_sm_messages
    )

    content = response.content[0].text

    sections = {}
    for section in ["INSTAGRAM CAPTION", "FACEBOOK POST", "X POST", "HASHTAGS"]:
        if section + ":" in content:
            start = content.index(section + ":") + len(section + ":")
            next_sections = [s + ":" for s in ["INSTAGRAM CAPTION", "FACEBOOK POST", "X POST", "HASHTAGS"] if s + ":" in content and content.index(s + ":") > start]
            if next_sections:
                end = content.index(next_sections[0])
                sections[section] = content[start:end].strip()
            else:
                sections[section] = content[start:].strip()

    save_generation("Social Media Generator",
        {"address": address, "neighborhood": neighborhood, "island": island, "price": price, "tone": tone},
        content
    )

    return render_template("social_media_results.html",
        address=address,
        neighborhood=neighborhood,
        island=island,
        price=price,
        instagram=to_html(sections.get("INSTAGRAM CAPTION", "")),
        facebook=to_html(sections.get("FACEBOOK POST", "")),
        x_post=to_html(sections.get("X POST", "")),
        hashtags=to_html(sections.get("HASHTAGS", "")),
        photo_count=photo_count
    )

@app.route("/offer-letter")
def offer_letter():
    return render_template("offer_letter.html", current_user=current_user)

@app.route("/offer-letter/generate", methods=["POST"])
def offer_letter_generate():
    limit = generation_limit_response()
    if limit:
        return limit
    address = request.form["address"]
    neighborhood = request.form["neighborhood"]
    island = request.form["island"]
    offer_price = request.form["offer_price"]
    listing_price = request.form["listing_price"]
    buyer_name = request.form["buyer_name"]
    closing_date = request.form["closing_date"]
    contingencies = request.form.getlist("contingencies")
    personal_message = request.form["personal_message"]
    tone = request.form["tone"]
    land_tenure = request.form.get("land_tenure", "Fee Simple")

    contingencies_str = ", ".join(contingencies) if contingencies else "None"

    # Neighborhood context injection
    _nb_data = get_neighborhood_context(neighborhood, island)
    _nb_context = format_neighborhood_for_prompt(_nb_data, neighborhood) if _nb_data else ""

    try:
        offer_num = float(offer_price.replace(",", "").replace("$", ""))
        list_num = float(listing_price.replace(",", "").replace("$", ""))
        diff_pct = round(((offer_num - list_num) / list_num) * 100, 1)
        price_relationship = f"{abs(diff_pct)}% {'above' if diff_pct > 0 else 'below'} asking"
    except Exception:
        price_relationship = "at or near asking price"

    _offer_generation_id = hashlib.md5(f"{buyer_name}{time.time()}".encode()).hexdigest()[:8]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        temperature=0.7,
        messages=[{"role": "user", "content": f"""You are a Hawaii real estate expert. Generate a complete offer letter package for this property transaction.

Property: {address}, {neighborhood}, {island}
Listing Price: ${listing_price}
Offer Price: ${offer_price} ({price_relationship})
Buyer Name: {buyer_name}
Preferred Closing Date: {closing_date}
Contingencies: {contingencies_str}
Personal Message from Buyer: {personal_message}
Tone: {tone}
Land Tenure: {land_tenure}

Generation ID: {_offer_generation_id}. Treat this as a completely fresh and unique piece of writing with no connection to any previous output.

{_nb_context}

HAWAII VOICE RULES:
You are a Hawaii real estate expert writing a personal offer letter from a buyer to a seller. Write with authentic Hawaii warmth, aloha spirit, and genuine human connection. Reference specific Hawaii lifestyle and community values naturally. Make the letter feel like it was written by a real person who loves Hawaii, not a generic template.

CRAFT RULES:
Write with natural warmth and varied sentence structure. The letter should feel sincere and personal — not like a form letter. Every sentence should feel intentional.

CLICHÉ GUARDRAIL:
Never use: dream home, fell in love, forever home, raise our family, good stewards. These are the most overused phrases in offer letters. Find more specific and genuine ways to express the same emotions based on the details provided.

Format your response EXACTLY like this:

OFFER LETTER:
[A full, formal offer letter addressed to "Dear Seller," from {buyer_name}. 3-4 paragraphs. Include property address, offer amount, closing date, contingencies, and the personal message woven in naturally. Match the requested tone. End with a professional closing.]

EMAIL SUBJECT:
[A compelling subject line for submitting this offer via email]

NEGOTIATION TIP:
[2-3 sentences of strategic advice for {buyer_name} based on the offer price vs listing price of ${listing_price}. Be specific and actionable.]"""}]
    )

    content = response.content[0].text
    sections = {}
    for section in ["OFFER LETTER", "EMAIL SUBJECT", "NEGOTIATION TIP"]:
        if section + ":" in content:
            start = content.index(section + ":") + len(section + ":")
            next_sections = [s + ":" for s in ["OFFER LETTER", "EMAIL SUBJECT", "NEGOTIATION TIP"] if s + ":" in content and content.index(s + ":") > start]
            if next_sections:
                end = content.index(next_sections[0])
                sections[section] = content[start:end].strip()
            else:
                sections[section] = content[start:].strip()

    save_generation("Offer Letter Assistant",
        {"address": address, "neighborhood": neighborhood, "island": island,
         "offer_price": offer_price, "listing_price": listing_price, "buyer_name": buyer_name},
        content
    )

    return render_template("offer_letter_results.html",
        address=address,
        neighborhood=neighborhood,
        island=island,
        offer_price=offer_price,
        listing_price=listing_price,
        buyer_name=buyer_name,
        offer_letter=to_html(sections.get("OFFER LETTER", "")),
        email_subject=sections.get("EMAIL SUBJECT", ""),
        negotiation_tip=to_html(sections.get("NEGOTIATION TIP", ""))
    )

@app.route("/market-report")
def market_report():
    return render_template("market_report.html", current_user=current_user)

@app.route("/market-report/generate", methods=["POST"])
def market_report_generate():
    limit = generation_limit_response()
    if limit:
        return limit
    neighborhood = request.form["neighborhood"]
    island = request.form["island"]
    report_type = request.form["report_type"]
    price_range = request.form["price_range"]
    property_type = request.form["property_type"]

    # Neighborhood context injection
    _nb_data = get_neighborhood_context(neighborhood, island)
    _nb_context = format_neighborhood_for_prompt(_nb_data, neighborhood) if _nb_data else ""

    _mr_generation_id = hashlib.md5(f"{neighborhood}{island}{time.time()}".encode()).hexdigest()[:8]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        temperature=0.8,
        messages=[{"role": "user", "content": f"""You are a Hawaii real estate market expert. Generate a detailed market report for a client.

Neighborhood: {neighborhood}
Island: {island}
Report Type: {report_type}
Price Range: {price_range}
Property Type: {property_type}

Generation ID: {_mr_generation_id}. Treat this as a completely fresh and unique piece of writing with no connection to any previous output.

{_nb_context}

HAWAII VOICE RULES:
You are a Hawaii real estate market expert. Write with local authority and Hawaii-specific insight. Reference Hawaii market dynamics, island-specific trends, seasonal patterns, and local economic factors naturally. Never produce generic market commentary that could apply to any US market.

CRAFT RULES:
Vary sentence length and rhythm throughout. Mix data-driven sentences with human context. The goal is for this to read like analysis from a Hawaii market insider, not a generic AI report.

CLICHÉ GUARDRAIL:
Avoid generic market report filler phrases like: the market is heating up, now is a great time to buy, inventory remains tight. Always back every market claim with a specific detail, trend, or local context.

Format your response EXACTLY like this:

MARKET OVERVIEW:
[2-3 sentences summarizing the {neighborhood} real estate market on {island} for {property_type} in the {price_range} range]

MARKET CONDITIONS:
[2-3 sentences describing whether it is a buyer's or seller's market and why, with specific context for {neighborhood}]

PRICE TRENDS:
[2-3 sentences on price trends, what they mean for the buyer/seller, and what to expect in the near term]

TOP REASONS TO ACT NOW:
- [Reason 1 specific to this market and report type]
- [Reason 2 specific to this market and report type]
- [Reason 3 specific to this market and report type]

NEIGHBORHOOD HIGHLIGHTS:
[3-4 sentences on what makes {neighborhood} on {island} special — lifestyle, amenities, schools, beaches, culture]

RECOMMENDATION:
[2-3 sentences of personalized advice tailored specifically to someone using a {report_type} in the {price_range} range for {property_type} in {neighborhood}]

If the neighborhood or property type has significant leasehold inventory, you MUST note in the PRICE TRENDS section:
LEASEHOLD PROPERTY: This property is leasehold, not fee simple. Leasehold properties in Hawaii typically sell at a significant discount (20-40%) vs fee simple. Many lenders will not finance leasehold properties with fewer than 30 years remaining on the lease. Buyers should verify lease expiration, rent renegotiation terms, and financing eligibility before making an offer."""}]
    )

    content = response.content[0].text
    sections = {}
    for section in ["MARKET OVERVIEW", "MARKET CONDITIONS", "PRICE TRENDS", "TOP REASONS TO ACT NOW", "NEIGHBORHOOD HIGHLIGHTS", "RECOMMENDATION"]:
        if section + ":" in content:
            start = content.index(section + ":") + len(section + ":")
            next_sections = [s + ":" for s in ["MARKET OVERVIEW", "MARKET CONDITIONS", "PRICE TRENDS", "TOP REASONS TO ACT NOW", "NEIGHBORHOOD HIGHLIGHTS", "RECOMMENDATION"] if s + ":" in content and content.index(s + ":") > start]
            if next_sections:
                end = content.index(next_sections[0])
                sections[section] = content[start:end].strip()
            else:
                sections[section] = content[start:].strip()

    save_generation("Market Report Generator",
        {"neighborhood": neighborhood, "island": island, "report_type": report_type, "price_range": price_range},
        content
    )

    return render_template("market_report_results.html",
        neighborhood=neighborhood,
        island=island,
        report_type=report_type,
        price_range=price_range,
        property_type=property_type,
        market_overview=to_html(sections.get("MARKET OVERVIEW", "")),
        market_conditions=to_html(sections.get("MARKET CONDITIONS", "")),
        price_trends=to_html(sections.get("PRICE TRENDS", "")),
        top_reasons=to_html(sections.get("TOP REASONS TO ACT NOW", "")),
        neighborhood_highlights=to_html(sections.get("NEIGHBORHOOD HIGHLIGHTS", "")),
        recommendation=to_html(sections.get("RECOMMENDATION", ""))
    )

@app.route("/client-emails")
def client_emails():
    return render_template("client_emails.html", current_user=current_user)

@app.route("/client-emails/generate", methods=["POST"])
def client_emails_generate():
    limit = generation_limit_response()
    if limit:
        return limit
    email_type = request.form["email_type"]
    client_name = request.form["client_name"]
    address = request.form["address"]
    neighborhood = request.form["neighborhood"]
    island = request.form["island"]
    key_detail = request.form["key_detail"]
    agent_name = request.form["agent_name"]
    tone = request.form["tone"]

    # Neighborhood context injection
    _nb_data = get_neighborhood_context(neighborhood, island)
    _nb_context = format_neighborhood_for_prompt(_nb_data, neighborhood) if _nb_data else ""

    _email_generation_id = hashlib.md5(f"{client_name}{time.time()}".encode()).hexdigest()[:8]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1800,
        temperature=0.85,
        messages=[{"role": "user", "content": f"""You are a Hawaii real estate expert writing professional client emails. Generate a complete client email package.

Email Type: {email_type}
Client Name: {client_name}
Property Address: {address}
Neighborhood: {neighborhood}
Island: {island}
Key Detail: {key_detail}
Agent Name: {agent_name}
Tone: {tone}

Generation ID: {_email_generation_id}. Treat this as a completely fresh and unique piece of writing with no connection to any previous output.

{_nb_context}

HAWAII VOICE RULES:
Always write with authentic Hawaii warmth and personality. Reference Hawaii lifestyle, local context, and community feel naturally where appropriate. Write like a local agent, not a generic real estate AI.

CRAFT RULES:
Write with natural rhythm and varied sentence structure. Emails should feel personal and human — not like a template was filled in. Avoid predictable email patterns like starting with "I hope this email finds you well" or ending with "Please don't hesitate to reach out."

CLICHÉ GUARDRAIL:
Never use: I hope this finds you well, as per our conversation, please don't hesitate, touching base, circling back, just checking in, at your earliest convenience. Write like a real person reaching out, not a corporate email template.

Format your response EXACTLY like this:

EMAIL SUBJECT:
[A compelling, professional subject line for this {email_type} email]

EMAIL BODY:
[A complete, professional email from {agent_name} to {client_name}. 3-5 paragraphs appropriate for a {email_type}. Include relevant property details and {key_detail}. Use {tone} tone. Include a warm Hawaii-appropriate greeting. End with a clear call to action and a professional sign-off from {agent_name}.]

FOLLOW UP TEXT:
[A short, friendly SMS/text follow-up message under 160 characters. Casual and warm, referencing the email.]"""}]
    )

    content = response.content[0].text
    sections = {}
    for section in ["EMAIL SUBJECT", "EMAIL BODY", "FOLLOW UP TEXT"]:
        if section + ":" in content:
            start = content.index(section + ":") + len(section + ":")
            next_sections = [s + ":" for s in ["EMAIL SUBJECT", "EMAIL BODY", "FOLLOW UP TEXT"] if s + ":" in content and content.index(s + ":") > start]
            if next_sections:
                end = content.index(next_sections[0])
                sections[section] = content[start:end].strip()
            else:
                sections[section] = content[start:].strip()

    save_generation("Client Email Templates",
        {"email_type": email_type, "client_name": client_name, "address": address,
         "neighborhood": neighborhood, "island": island, "agent_name": agent_name},
        content
    )

    return render_template("client_emails_results.html",
        email_type=email_type,
        client_name=client_name,
        address=address,
        agent_name=agent_name,
        email_subject=sections.get("EMAIL SUBJECT", ""),
        email_body=to_html(sections.get("EMAIL BODY", "")),
        follow_up_text=to_html(sections.get("FOLLOW UP TEXT", ""))
    )

@app.route("/bio-generator")
def bio_generator():
    return render_template("bio_generator.html", current_user=current_user)

@app.route("/bio-generator/generate", methods=["POST"])
def bio_generator_generate():
    limit = generation_limit_response()
    if limit:
        return limit
    full_name = request.form["full_name"]
    years_experience = request.form["years_experience"]
    primary_island = request.form["primary_island"]
    specialties = request.form.getlist("specialties")
    languages = request.form["languages"]
    hawaii_connection = request.form["hawaii_connection"]
    fun_fact = request.form["fun_fact"]
    tone = request.form["tone"]
    length = request.form["length"]
    designations = request.form.get("designations", "").strip()

    specialties_str = ", ".join(specialties) if specialties else "General real estate"
    designations_line = f"Designations/Certifications: {designations}" if designations else ""

    # Neighborhood context injection — bio uses primary_island as location anchor
    _nb_data = get_neighborhood_context(primary_island)
    _nb_context = format_neighborhood_for_prompt(_nb_data, primary_island) if _nb_data else ""

    _bio_templates = [
        "Lead with the agent's personal connection to Hawaii and why they chose real estate. Open on what brought them here — or what kept them — and draw a direct line between that story and the work they do now.",
        "Lead with a specific client success story or defining moment that captures their approach. Open on a real scenario that shows, not tells, what it's like to work with this agent.",
        "Lead with their deep local knowledge of their specific island or neighborhood. Open on what they know about this place that an outsider wouldn't — and why that knowledge changes outcomes for buyers and sellers.",
        "Lead with their personality and what makes working with them feel different. Open on the human behind the license — their energy, their communication style, what clients actually feel in their presence.",
        "Lead with their background before real estate and how it shapes their work today. Open on where they came from and draw a clear, specific line between that experience and how they serve clients now.",
    ]
    _bio_template_instruction = random.choice(_bio_templates)
    _bio_generation_id = hashlib.md5(f"{full_name}{time.time()}".encode()).hexdigest()[:8]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        temperature=0.9,
        messages=[{"role": "user", "content": f"""You are a professional copywriter specializing in Hawaii real estate agent bios. Generate a complete bio package for this Hawaii realtor.

STRUCTURAL APPROACH: {_bio_template_instruction}

Agent Details:
Full Name: {full_name}
Years of Experience: {years_experience}
Primary Area: {primary_island}
Specialties: {specialties_str}
Languages Spoken: {languages}
Connection to Hawaii: {hawaii_connection}
Fun Personal Fact: {fun_fact}
Tone: {tone}
Target Length: {length}
{designations_line}

Generation ID: {_bio_generation_id}. Treat this as a completely fresh and unique piece of writing with no connection to any previous output.

{_nb_context}

HAWAII VOICE RULES:
You are a Hawaii real estate expert writing for a local Hawaii audience. Always write with authentic Hawaii personality. Reference specific Hawaii lifestyle elements naturally — island roots, community connections, local market knowledge, aloha spirit. Write like a local expert, not like a generic real estate AI. Avoid anything that sounds like it was written for an agent in Phoenix or Dallas.

CRAFT RULES:
Your output must be structurally and tonally distinct from a generic AI response. Vary sentence length, rhythm, and paragraph structure throughout. Mix short punchy sentences with longer descriptive ones. Never write in a predictable pattern. The goal is for a reader to believe this was written by a talented human copywriter who knows Hawaii deeply.

CLICHÉ GUARDRAIL:
Avoid overused real estate bio clichés as filler. Never use: passionate about real estate, dedicated to clients, goes above and beyond, trusted advisor, results-driven, proven track record. If you use common descriptors always follow immediately with a specific detail that earns the word.

HOOK INSTRUCTION:
Open with the single most compelling and specific thing about this agent. Use it as the hook, then naturally expand to cover their full background, expertise, and personality.

Format your response EXACTLY like this:

FULL BIO:
[A {tone} bio approximately {length}. Weave in their Hawaii connection, specialties, experience, and personality. Make it feel authentic and specific to Hawaii real estate. Include the fun fact naturally.]

ELEVATOR PITCH:
[2-3 compelling sentences that capture who {full_name} is and why clients should work with them. Punchy and memorable.]

SOCIAL MEDIA BIO:
[Under 150 characters. First-person, bold, include a Hawaii reference and their specialty.]"""}]
    )

    content = response.content[0].text
    sections = {}
    for section in ["FULL BIO", "ELEVATOR PITCH", "SOCIAL MEDIA BIO"]:
        if section + ":" in content:
            start = content.index(section + ":") + len(section + ":")
            next_sections = [s + ":" for s in ["FULL BIO", "ELEVATOR PITCH", "SOCIAL MEDIA BIO"] if s + ":" in content and content.index(s + ":") > start]
            if next_sections:
                end = content.index(next_sections[0])
                sections[section] = content[start:end].strip()
            else:
                sections[section] = content[start:].strip()

    save_generation("Bio Generator",
        {"full_name": full_name, "primary_island": primary_island, "years_experience": years_experience, "tone": tone},
        content
    )

    return render_template("bio_generator_results.html",
        full_name=full_name,
        primary_island=primary_island,
        years_experience=years_experience,
        full_bio=to_html(sections.get("FULL BIO", "")),
        elevator_pitch=to_html(sections.get("ELEVATOR PITCH", "")),
        social_bio=to_html(sections.get("SOCIAL MEDIA BIO", ""))
    )

@app.route("/refine-bio", methods=["POST"])
def refine_bio():
    bio_text = request.form.get("bio_text", "").strip()
    if not bio_text:
        return {"error": "No bio text provided"}, 400

    refine_prompt = f"""Review this agent bio. Identify any sentences that sound generic, could apply to any agent anywhere, or feel like filler. Rewrite only those specific sentences to be more vivid, specific, and authentic. Return ONLY the improved bio — no commentary, no explanations, no headers.

Current bio:
{bio_text}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0.9,
        messages=[{"role": "user", "content": refine_prompt}]
    )
    return {"refined": response.content[0].text}

@app.route("/property-comparison")
def property_comparison():
    return render_template("property_comparison.html", current_user=current_user)

@app.route("/property-comparison/generate", methods=["POST"])
def property_comparison_generate():
    limit = generation_limit_response()
    if limit:
        return limit
    p1_address = request.form["p1_address"]
    p1_neighborhood = request.form["p1_neighborhood"]
    p1_island = request.form["p1_island"]
    p1_price = request.form["p1_price"]
    p1_bedrooms = request.form["p1_bedrooms"]
    p1_bathrooms = request.form["p1_bathrooms"]
    p1_sqft = request.form["p1_sqft"]
    p1_feature = request.form["p1_feature"]
    p1_condition = request.form["p1_condition"]

    p2_address = request.form["p2_address"]
    p2_neighborhood = request.form["p2_neighborhood"]
    p2_island = request.form["p2_island"]
    p2_price = request.form["p2_price"]
    p2_bedrooms = request.form["p2_bedrooms"]
    p2_bathrooms = request.form["p2_bathrooms"]
    p2_sqft = request.form["p2_sqft"]
    p2_feature = request.form["p2_feature"]
    p2_condition = request.form["p2_condition"]

    p3_address = request.form.get("p3_address", "").strip()
    p3_neighborhood = request.form.get("p3_neighborhood", "").strip()
    p3_island = request.form.get("p3_island", "")
    p3_price = request.form.get("p3_price", "").strip()
    p3_bedrooms = request.form.get("p3_bedrooms", "").strip()
    p3_bathrooms = request.form.get("p3_bathrooms", "").strip()
    p3_sqft = request.form.get("p3_sqft", "").strip()
    p3_feature = request.form.get("p3_feature", "").strip()
    p3_condition = request.form.get("p3_condition", "")
    has_p3 = bool(p3_address)

    buyer_priorities = request.form["buyer_priorities"]
    buyer_budget = request.form.get("buyer_budget", "").strip()
    land_tenure = request.form.get("land_tenure", "Any")

    def calc_ppsf(price_str, sqft_str):
        try:
            price = float(price_str.replace(",", "").replace("$", ""))
            sqft = float(sqft_str.replace(",", ""))
            return f"${price / sqft:,.0f}/sqft"
        except Exception:
            return "N/A"

    p1_ppsf = calc_ppsf(p1_price, p1_sqft)
    p2_ppsf = calc_ppsf(p2_price, p2_sqft)
    p3_ppsf = calc_ppsf(p3_price, p3_sqft) if has_p3 else ""

    # Neighborhood context injection — dual property
    _nb1_data = get_neighborhood_context(p1_neighborhood, p1_island)
    _nb1_ctx = format_neighborhood_for_prompt(_nb1_data, p1_neighborhood) if _nb1_data else ""
    _nb2_data = get_neighborhood_context(p2_neighborhood, p2_island)
    _nb2_ctx = format_neighborhood_for_prompt(_nb2_data, p2_neighborhood) if _nb2_data else ""
    _nb3_ctx = ""
    if has_p3:
        _nb3_data = get_neighborhood_context(p3_neighborhood, p3_island)
        _nb3_ctx = format_neighborhood_for_prompt(_nb3_data, p3_neighborhood) if _nb3_data else ""

    def _label_nb_context(ctx, label):
        if not ctx:
            return ""
        return ctx.replace("NEIGHBORHOOD CONTEXT:", f"{label} NEIGHBORHOOD CONTEXT:", 1)

    _combined_nb_context = "\n\n".join(filter(None, [
        _label_nb_context(_nb1_ctx, "PROPERTY 1"),
        _label_nb_context(_nb2_ctx, "PROPERTY 2"),
        _label_nb_context(_nb3_ctx, "PROPERTY 3") if has_p3 else "",
    ]))

    p1_photos = _process_photos("p1_photos")
    p2_photos = _process_photos("p2_photos")
    p1_photo_count = len(p1_photos)
    p2_photo_count = len(p2_photos)

    p3_block = ""
    if has_p3:
        p3_block = f"""
Property 3: {p3_address}, {p3_neighborhood}, {p3_island}
- Price: ${p3_price} | Beds: {p3_bedrooms} | Baths: {p3_bathrooms} | Sqft: {p3_sqft} | Price/sqft: {p3_ppsf}
- Standout feature: {p3_feature}
- Condition/notes: {p3_condition}
"""

    prompt = f"""You are a Hawaii real estate expert helping a buyer compare properties.

{_combined_nb_context}

HAWAII VOICE RULES:
Write with local authority and Hawaii-specific insight. Reference Hawaii-specific factors naturally — proximity to beaches, island lifestyle, trade winds, flood zones, leasehold vs fee simple, HOA culture in Hawaii. Never produce generic comparison commentary that ignores Hawaii context.

CRAFT RULES:
Write the analysis sections with varied sentence rhythm. Avoid robotic bullet-point thinking even if the output is structured. Each property's summary should read like a local expert's genuine assessment, not a checklist.

PROPERTIES TO COMPARE:

Property 1: {p1_address}, {p1_neighborhood}, {p1_island}
- Price: ${p1_price} | Beds: {p1_bedrooms} | Baths: {p1_bathrooms} | Sqft: {p1_sqft} | Price/sqft: {p1_ppsf}
- Standout feature: {p1_feature}
- Condition/notes: {p1_condition}

Property 2: {p2_address}, {p2_neighborhood}, {p2_island}
- Price: ${p2_price} | Beds: {p2_bedrooms} | Baths: {p2_bathrooms} | Sqft: {p2_sqft} | Price/sqft: {p2_ppsf}
- Standout feature: {p2_feature}
- Condition/notes: {p2_condition}
{p3_block}
BUYER PRIORITIES: {buyer_priorities}
{"BUYER BUDGET: $" + buyer_budget if buyer_budget else ""}
LAND TENURE PREFERENCE: {land_tenure}

Write a detailed property comparison report. Use EXACTLY these section headers:

EXECUTIVE SUMMARY:
[2-3 sentence overview of the comparison and key differences]

PROPERTY 1 PROS:
[3-5 bullet points starting with •]

PROPERTY 1 CONS:
[3-5 bullet points starting with •]

PROPERTY 2 PROS:
[3-5 bullet points starting with •]

PROPERTY 2 CONS:
[3-5 bullet points starting with •]
{"PROPERTY 3 PROS:" + chr(10) + "[3-5 bullet points starting with •]" + chr(10) + chr(10) + "PROPERTY 3 CONS:" + chr(10) + "[3-5 bullet points starting with •]" if has_p3 else ""}

BEST VALUE PICK:
[Which property offers the best value per dollar and why, 2-3 sentences]

BEST FIT FOR BUYER:
[Which property best matches the buyer's stated priorities and why, 2-3 sentences]

RECOMMENDATION:
[Clear recommendation of which property to choose and the top 3 reasons, 3-4 sentences]

If any property has Leasehold land tenure, you MUST include a prominent warning in the RECOMMENDATION section:
LEASEHOLD PROPERTY: This property is leasehold, not fee simple. Leasehold properties in Hawaii typically sell at a significant discount (20-40%) vs fee simple. Many lenders will not finance leasehold properties with fewer than 30 years remaining on the lease. Buyers should verify lease expiration, rent renegotiation terms, and financing eligibility before making an offer."""

    if p1_photos or p2_photos:
        _pc_photo_prefix_parts = []
        if p1_photos:
            _pc_photo_prefix_parts.append(f"Property 1 photos ({p1_photo_count} provided): analyze these images for Property 1's condition, finishes, and features.")
        if p2_photos:
            _pc_photo_prefix_parts.append(f"Property 2 photos ({p2_photo_count} provided): analyze these images for Property 2's condition, finishes, and features.")
        _pc_photo_prefix = "PHOTO ANALYSIS INSTRUCTIONS:\n" + "\n".join(_pc_photo_prefix_parts) + "\nBe specific about what you observe in each set — do not apply observations from one property's photos to the other.\n\n"
        _pc_image_blocks = [
            *[{"type": "image", "source": {"type": "base64", "media_type": mt, "data": img_data}} for img_data, mt in p1_photos],
            *[{"type": "image", "source": {"type": "base64", "media_type": mt, "data": img_data}} for img_data, mt in p2_photos],
            {"type": "text", "text": _pc_photo_prefix + prompt}
        ]
        _pc_messages = [{"role": "user", "content": _pc_image_blocks}]
    else:
        _pc_messages = [{"role": "user", "content": prompt}]

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        temperature=0.8,
        messages=_pc_messages
    )
    content = message.content[0].text

    sections = {}
    section_keys = [
        "EXECUTIVE SUMMARY", "PROPERTY 1 PROS", "PROPERTY 1 CONS",
        "PROPERTY 2 PROS", "PROPERTY 2 CONS",
        "PROPERTY 3 PROS", "PROPERTY 3 CONS",
        "BEST VALUE PICK", "BEST FIT FOR BUYER", "RECOMMENDATION"
    ]
    for section in section_keys:
        if section + ":" in content:
            start = content.index(section + ":") + len(section + ":")
            later = [s + ":" for s in section_keys if s + ":" in content and content.index(s + ":") > start]
            if later:
                end = content.index(later[0])
                sections[section] = content[start:end].strip()
            else:
                sections[section] = content[start:].strip()

    save_generation("Property Comparison",
        {"p1_address": p1_address, "p2_address": p2_address, "p3_address": p3_address or "",
         "p1_neighborhood": p1_neighborhood, "p2_neighborhood": p2_neighborhood},
        content
    )

    return render_template("property_comparison_results.html",
        p1_address=p1_address, p1_neighborhood=p1_neighborhood, p1_island=p1_island,
        p1_price=p1_price, p1_bedrooms=p1_bedrooms, p1_bathrooms=p1_bathrooms,
        p1_sqft=p1_sqft, p1_ppsf=p1_ppsf, p1_feature=p1_feature, p1_condition=p1_condition,
        p2_address=p2_address, p2_neighborhood=p2_neighborhood, p2_island=p2_island,
        p2_price=p2_price, p2_bedrooms=p2_bedrooms, p2_bathrooms=p2_bathrooms,
        p2_sqft=p2_sqft, p2_ppsf=p2_ppsf, p2_feature=p2_feature, p2_condition=p2_condition,
        p3_address=p3_address, p3_neighborhood=p3_neighborhood, p3_island=p3_island,
        p3_price=p3_price, p3_bedrooms=p3_bedrooms, p3_bathrooms=p3_bathrooms,
        p3_sqft=p3_sqft, p3_ppsf=p3_ppsf, p3_feature=p3_feature, p3_condition=p3_condition,
        has_p3=has_p3,
        buyer_priorities=buyer_priorities, buyer_budget=buyer_budget,
        executive_summary=to_html(sections.get("EXECUTIVE SUMMARY", "")),
        p1_pros=to_html(sections.get("PROPERTY 1 PROS", "")),
        p1_cons=to_html(sections.get("PROPERTY 1 CONS", "")),
        p2_pros=to_html(sections.get("PROPERTY 2 PROS", "")),
        p2_cons=to_html(sections.get("PROPERTY 2 CONS", "")),
        p3_pros=to_html(sections.get("PROPERTY 3 PROS", "")),
        p3_cons=to_html(sections.get("PROPERTY 3 CONS", "")),
        best_value=to_html(sections.get("BEST VALUE PICK", "")),
        best_fit=to_html(sections.get("BEST FIT FOR BUYER", "")),
        recommendation=to_html(sections.get("RECOMMENDATION", "")),
        p1_photo_count=p1_photo_count,
        p2_photo_count=p2_photo_count
    )

# ─── Admin routes ─────────────────────────────────────────────────────────────


@app.route("/admin")
def admin_panel():
    secret = request.args.get("secret")
    if not secret or secret != os.getenv("ADMIN_SECRET"):
        abort(403)

    # Generate a random per-session token so the raw ADMIN_SECRET is never
    # embedded in the page source. The JS uses this token; /admin/set-plan
    # validates it against the session, not the raw secret.
    admin_token = _secrets_mod.token_hex(32)
    session["admin_token"] = admin_token

    users = User.query.order_by(User.created_at.desc()).all()
    waitlist = Waitlist.query.order_by(Waitlist.created_at.desc()).all()

    total_users = User.query.count()
    total_generations = Generation.query.count()

    tool_stats = db.session.query(
        Generation.tool_name, func.count(Generation.id).label("cnt")
    ).group_by(Generation.tool_name).order_by(func.count(Generation.id).desc()).all()

    user_gen_counts = {u.id: Generation.query.filter_by(user_id=u.id).count() for u in users}

    return render_template("admin.html",
        secret=admin_token,
        users=users,
        waitlist=waitlist,
        total_users=total_users,
        total_generations=total_generations,
        tool_stats=tool_stats,
        user_gen_counts=user_gen_counts
    )

@app.route("/admin/set-plan", methods=["POST"])
@csrf.exempt
def admin_set_plan():
    data = request.get_json(force=True, silent=True) or {}
    token = data.get("secret")
    expected = session.get("admin_token")
    if not token or not expected or not _secrets_mod.compare_digest(token, expected):
        return {"ok": False, "error": "Unauthorized"}, 403
    user = db.session.get(User, data.get("user_id"))
    if not user:
        return {"ok": False, "error": "User not found"}, 404
    plan = data.get("plan")
    if plan not in ("pro", "free"):
        return {"ok": False, "error": "Invalid plan"}, 400
    user.plan = plan
    db.session.commit()
    return {"ok": True, "plan": plan, "email": user.email}

@app.context_processor
def inject_monthly_count():
    try:
        if current_user.is_authenticated:
            return {"monthly_count": get_monthly_count(current_user)}
    except Exception:
        pass
    return {"monthly_count": 0}

# ─── Stripe billing ───────────────────────────────────────────────────────────

@app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer_email=current_user.email,
            line_items=[{
                "price": "price_1Tas4LCWSd0DHY3gVvJnUjgJ",
                "quantity": 1,
            }],
            success_url="https://alohaagent.app/upgrade-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://alohaagent.app/pricing",
        )
        return redirect(session.url, code=303)
    except Exception as e:
        app.logger.error(f"Stripe checkout error for {current_user.email}: {e}")
        flash("Something went wrong with billing. Please try again or contact support.", "error")
        return redirect("/pricing")


@app.route("/upgrade-success")
@login_required
def upgrade_success():
    session_id = request.args.get("session_id")
    if session_id:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            if (checkout_session.payment_status == "paid"
                    and checkout_session.customer_email
                    and checkout_session.customer_email.lower() == current_user.email.lower()):
                current_user.plan = "pro"
                db.session.commit()
                flash("Welcome to AlohaAgent Pro! Unlimited generations are now active.", "success")
        except Exception:
            pass
    return redirect("/dashboard")


@app.route("/stripe-webhook", methods=["POST"])
@csrf.exempt
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig = request.headers.get("Stripe-Signature")
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return "", 400

    if event["type"] == "customer.subscription.deleted":
        customer_id = event["data"]["object"].get("customer")
        email = None
        if customer_id:
            try:
                customer = stripe.Customer.retrieve(customer_id)
                email = customer.get("email")
            except Exception:
                pass
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                user.plan = "free"
                db.session.commit()
    elif event["type"] == "invoice.payment_failed":
        customer_id = event["data"]["object"].get("customer")
        email = event["data"]["object"].get("customer_email")
        if not email and customer_id:
            try:
                customer = stripe.Customer.retrieve(customer_id)
                email = customer.get("email")
            except Exception:
                pass
        app.logger.warning(f"Payment failed for {email}")

    return "", 200


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
