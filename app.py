from flask import Flask, render_template, request, session, redirect, url_for, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import anthropic
import json
import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "alohaagent-secret-2024")

database_url = os.getenv("DATABASE_URL", "sqlite:///alohaagent.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
    generations = db.relationship('Generation', backref='user', lazy=True)

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

# ─── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
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
            return redirect(next_page or url_for("dashboard"))
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
    gen = db.session.get(Generation, gen_id)
    if gen is None:
        abort(404)
    if gen.user_id != current_user.id:
        abort(403)

    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # ── Header bar ────────────────────────────────────
    pdf.set_fill_color(10, 22, 40)
    pdf.rect(0, 0, 210, 32, 'F')
    pdf.set_y(8)
    pdf.set_x(20)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(201, 168, 76)
    pdf.cell(0, 9, 'AlohaAgent', ln=True)
    pdf.set_x(20)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(140, 150, 165)
    pdf.cell(0, 6, 'AI Tools for Hawaii Real Estate', ln=True)

    pdf.set_y(40)

    # ── Tool name & meta ──────────────────────────────
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(10, 22, 40)
    pdf.cell(0, 8, gen.tool_name, ln=True)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(100, 110, 125)
    date_str = gen.created_at.strftime('%B %d, %Y')
    pdf.cell(0, 6, f"Generated {date_str}  |  {current_user.email}", ln=True)

    pdf.ln(3)
    pdf.set_draw_color(201, 168, 76)
    pdf.set_line_width(0.8)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(5)

    # ── Input summary ─────────────────────────────────
    input_data = gen.input_parsed
    if input_data:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(10, 22, 40)
        pdf.cell(0, 6, 'Property Details', ln=True)
        pdf.ln(1)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(60, 70, 85)
        for key, val in list(input_data.items())[:8]:
            if val:
                label = key.replace('_', ' ').title()
                pdf.set_x(20)
                pdf.cell(55, 5, f"{label}:", border=0)
                pdf.multi_cell(0, 5, str(val))
        pdf.ln(3)
        pdf.set_draw_color(210, 218, 230)
        pdf.set_line_width(0.3)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)

    # ── Output text ───────────────────────────────────
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(10, 22, 40)
    pdf.cell(0, 6, 'Generated Content', ln=True)
    pdf.ln(2)

    output = gen.output_text.replace('\r\n', '\n').replace('\r', '\n')
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        if line.isupper() and len(line) < 60:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(10, 22, 40)
            pdf.ln(2)
            pdf.cell(0, 6, line, ln=True)
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(30, 40, 55)
        else:
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(30, 40, 55)
            pdf.multi_cell(0, 5, line)

    # ── Footer ────────────────────────────────────────
    pdf.set_y(-18)
    pdf.set_draw_color(201, 168, 76)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(3)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(140, 150, 165)
    pdf.cell(0, 5, 'AlohaAgent · listaloha.onrender.com · AI-generated content for informational purposes only', align='C')

    pdf_bytes = bytes(pdf.output())
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    safe_name = gen.tool_name.lower().replace(' ', '_')
    response.headers["Content-Disposition"] = f"attachment; filename=alohaagent_{safe_name}_{gen.id}.pdf"
    return response

# ─── Existing routes ───────────────────────────────────────────────────────────

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
    return render_template("listing.html", remaining=remaining, count=count)

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/generate", methods=["POST"])
def generate():
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
    ocean_view = request.form["ocean_view"]
    pool = request.form["pool"]
    extra = request.form["extra"]
    year_built = request.form.get("year_built", "").strip()
    parking = request.form.get("parking", "").strip()
    land_tenure = request.form.get("land_tenure", "Fee Simple")

    try:
        sqft_num = float(sqft.replace(",", ""))
        price_num = float(price.replace(",", "").replace("$", ""))
        price_per_sqft = round(price_num / sqft_num)
    except Exception:
        price_per_sqft = "N/A"

    year_built_line = f"Year built: {year_built}" if year_built else ""
    parking_line = f"Parking: {parking}" if parking else ""

    listing_response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"""Write a professional MLS real estate listing for a Hawaii property with these details:
Address: {address}
Neighborhood: {neighborhood}
Island: {island}
Bedrooms: {bedrooms}
Bathrooms: {bathrooms}
Square footage: {sqft}
Price: {price}
Price per sqft: ${price_per_sqft}
Ocean view: {ocean_view}
Pool: {pool}
Standout feature: {extra}
Land tenure: {land_tenure}
{year_built_line}
{parking_line}

Write 2 paragraphs, around 150 words total. Make it warm, compelling, and specific to Hawaii. End with a one-line call to action."""}]
    )

    analysis_response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": f"""You are a Hawaii real estate expert. Analyze this property:

Address: {address}, {neighborhood}, {island}
Bedrooms: {bedrooms}, Bathrooms: {bathrooms}
Square footage: {sqft}, Price: {price}
Price per sqft: ${price_per_sqft}
Ocean view: {ocean_view}, Pool: {pool}
Standout feature: {extra}

Format exactly like this:
LISTING SCORE: X/10
[2-3 sentence explanation]

PRICE ANALYSIS:
[2-3 sentence explanation]"""}]
    )

    neighborhood_response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": f"""You are a Hawaii local expert. Provide a neighborhood report for {neighborhood} on {island}, Hawaii.

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
[2-3 sentences]"""}]
    )

    listing_text = listing_response.content[0].text
    analysis_text = analysis_response.content[0].text
    neighborhood_text = neighborhood_response.content[0].text

    save_generation("Listing Generator",
        {"address": address, "neighborhood": neighborhood, "island": island,
         "price": price, "bedrooms": bedrooms, "bathrooms": bathrooms, "sqft": sqft},
        f"LISTING:\n{listing_text}\n\nANALYSIS:\n{analysis_text}\n\nNEIGHBORHOOD REPORT:\n{neighborhood_text}"
    )

    return render_template("results.html",
        address=address,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        sqft=sqft,
        price=price,
        neighborhood=neighborhood,
        island=island,
        ocean_view=ocean_view,
        pool=pool,
        price_per_sqft=price_per_sqft,
        listing=listing_text,
        analysis=analysis_text,
        neighborhood_report=neighborhood_text
    )

@app.route("/waitlist", methods=["POST"])
def waitlist():
    email = request.form["email"]
    with open("waitlist.txt", "a") as f:
        f.write(email + "\n")
    return render_template("waitlist_success.html", email=email)

@app.route("/open-house")
def open_house():
    return render_template("open_house.html")

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

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": f"""You are a Hawaii real estate marketing expert. Generate three open house announcements for this property:

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

Format your response EXACTLY like this:

INSTAGRAM POST:
[2-3 sentences max, warm and exciting, include the date and time, end with relevant Hawaii hashtags]

FACEBOOK POST:
[3-4 sentences, friendly and detailed, include all property details and open house info, professional tone]

EMAIL SUBJECT:
[Compelling email subject line]

EMAIL BODY:
[Professional 3-4 sentence email announcing the open house, suitable to send to a client list{sign_off_instruction}]"""}]
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
        instagram=sections.get("INSTAGRAM POST", ""),
        facebook=sections.get("FACEBOOK POST", ""),
        email_subject=sections.get("EMAIL SUBJECT", ""),
        email_body=sections.get("EMAIL BODY", "")
    )

@app.route("/social-media")
def social_media():
    return render_template("social_media.html")

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

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": f"""You are a Hawaii real estate social media expert. Generate social media posts for this property listing.

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

Format your response EXACTLY like this:

INSTAGRAM CAPTION:
[2-3 punchy sentences, engaging and visual, include price, end with a call to action]

FACEBOOK POST:
[4-5 sentences, more detailed and informative, include all key details, professional yet warm]

X POST:
[MUST be 280 characters or fewer — count carefully. Punchy and attention grabbing, include price. No hashtags here.]

HASHTAGS:
[20-25 relevant hashtags including Hawaii specific ones, real estate ones, and neighborhood specific ones]"""}]
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
        instagram=sections.get("INSTAGRAM CAPTION", ""),
        facebook=sections.get("FACEBOOK POST", ""),
        x_post=sections.get("X POST", ""),
        hashtags=sections.get("HASHTAGS", "")
    )

@app.route("/offer-letter")
def offer_letter():
    return render_template("offer_letter.html")

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

    try:
        offer_num = float(offer_price.replace(",", "").replace("$", ""))
        list_num = float(listing_price.replace(",", "").replace("$", ""))
        diff_pct = round(((offer_num - list_num) / list_num) * 100, 1)
        price_relationship = f"{abs(diff_pct)}% {'above' if diff_pct > 0 else 'below'} asking"
    except Exception:
        price_relationship = "at or near asking price"

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
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
        offer_letter=sections.get("OFFER LETTER", ""),
        email_subject=sections.get("EMAIL SUBJECT", ""),
        negotiation_tip=sections.get("NEGOTIATION TIP", "")
    )

@app.route("/market-report")
def market_report():
    return render_template("market_report.html")

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

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": f"""You are a Hawaii real estate market expert. Generate a detailed market report for a client.

Neighborhood: {neighborhood}
Island: {island}
Report Type: {report_type}
Price Range: {price_range}
Property Type: {property_type}

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
[2-3 sentences of personalized advice tailored specifically to someone using a {report_type} in the {price_range} range for {property_type} in {neighborhood}]"""}]
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
        market_overview=sections.get("MARKET OVERVIEW", ""),
        market_conditions=sections.get("MARKET CONDITIONS", ""),
        price_trends=sections.get("PRICE TRENDS", ""),
        top_reasons=sections.get("TOP REASONS TO ACT NOW", ""),
        neighborhood_highlights=sections.get("NEIGHBORHOOD HIGHLIGHTS", ""),
        recommendation=sections.get("RECOMMENDATION", "")
    )

@app.route("/client-emails")
def client_emails():
    return render_template("client_emails.html")

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

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1800,
        messages=[{"role": "user", "content": f"""You are a Hawaii real estate professional. Generate a complete client email package.

Email Type: {email_type}
Client Name: {client_name}
Property Address: {address}
Neighborhood: {neighborhood}
Island: {island}
Key Detail: {key_detail}
Agent Name: {agent_name}
Tone: {tone}

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
        email_body=sections.get("EMAIL BODY", ""),
        follow_up_text=sections.get("FOLLOW UP TEXT", "")
    )

@app.route("/bio-generator")
def bio_generator():
    return render_template("bio_generator.html")

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

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": f"""You are a professional copywriter specializing in real estate agent bios. Generate a complete bio package for this Hawaii realtor.

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

Format your response EXACTLY like this:

FULL BIO:
[A {tone} bio approximately {length}. Weave in their Hawaii connection, specialties, experience, and personality. Make it feel authentic and specific to Hawaii real estate. Do not use generic phrases like "passionate about real estate." Include the fun fact naturally.]

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
        full_bio=sections.get("FULL BIO", ""),
        elevator_pitch=sections.get("ELEVATOR PITCH", ""),
        social_bio=sections.get("SOCIAL MEDIA BIO", "")
    )

@app.route("/property-comparison")
def property_comparison():
    return render_template("property_comparison.html")

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

    p3_block = ""
    if has_p3:
        p3_block = f"""
Property 3: {p3_address}, {p3_neighborhood}, {p3_island}
- Price: ${p3_price} | Beds: {p3_bedrooms} | Baths: {p3_bathrooms} | Sqft: {p3_sqft} | Price/sqft: {p3_ppsf}
- Standout feature: {p3_feature}
- Condition/notes: {p3_condition}
"""

    prompt = f"""You are a Hawaii real estate expert helping a buyer compare properties.

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
[Clear recommendation of which property to choose and the top 3 reasons, 3-4 sentences]"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
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
        executive_summary=sections.get("EXECUTIVE SUMMARY", ""),
        p1_pros=sections.get("PROPERTY 1 PROS", ""),
        p1_cons=sections.get("PROPERTY 1 CONS", ""),
        p2_pros=sections.get("PROPERTY 2 PROS", ""),
        p2_cons=sections.get("PROPERTY 2 CONS", ""),
        p3_pros=sections.get("PROPERTY 3 PROS", ""),
        p3_cons=sections.get("PROPERTY 3 CONS", ""),
        best_value=sections.get("BEST VALUE PICK", ""),
        best_fit=sections.get("BEST FIT FOR BUYER", ""),
        recommendation=sections.get("RECOMMENDATION", "")
    )

if __name__ == "__main__":
    app.run(debug=True)
