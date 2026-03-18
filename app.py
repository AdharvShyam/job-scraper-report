from flask import Flask, render_template, request, send_file, session, redirect, url_for
from scraper.scraper import scrape_jobs
from report.pdf_generator import generate_pdf
from collections import Counter
from dotenv import load_dotenv
from flask_mail import Mail, Message
from models import db, User, SearchHistory
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote_plus
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MySQL configuration

db_password = os.getenv('DB_PASSWORD', '')
db_password_encoded = quote_plus(db_password) if db_password else ''
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f"mysql+pymysql://root:{db_password_encoded}@localhost/jobscraper")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

db.init_app(app)
mail = Mail(app)

# Create tables
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user exists
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already taken!")
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Email already registered!")

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return render_template("login.html", success="Account created! Please login.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return render_template("login.html", error="Invalid username or password!")

        session["user_id"] = user.id
        session["username"] = user.username
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    searches = SearchHistory.query.filter_by(user_id=session["user_id"]).all()
    return render_template("dashboard.html", username=session["username"], searches=searches)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/generate", methods=["POST"])
def generate():
    keyword = request.form.get("keyword")
    location = request.form.get("location")

    if not keyword or not location:
        return render_template("index.html", error="Please enter both keyword and location!")

    jobs = scrape_jobs(keyword, location)

    if not jobs:
        return render_template("index.html", error="No jobs found! Try a different keyword or location.")

    session["jobs"] = jobs
    session["keyword"] = keyword
    session["location"] = location

    # Save search history if logged in
    if "user_id" in session:
        search = SearchHistory(
            user_id=session["user_id"],
            keyword=keyword,
            location=location,
            results_count=len(jobs)
        )
        db.session.add(search)
        db.session.commit()

    return render_template("results.html", jobs=jobs, keyword=keyword, location=location)


@app.route("/analytics")
def analytics():
    jobs = session.get("jobs", [])
    keyword = session.get("keyword", "")
    location = session.get("location", "")

    if not jobs:
        return render_template("index.html", error="Session expired! Please search again.")

    companies = [job.get("Company", "N/A") for job in jobs]
    top_companies = Counter(companies).most_common(8)

    locations = [job.get("Location", "N/A") for job in jobs]
    top_locations = Counter(locations).most_common(6)

    dates = [job.get("Posted", "N/A") for job in jobs if job.get("Posted", "N/A") != "N/A"]
    top_dates = Counter(dates).most_common(7)

    return render_template("analytics.html",
        jobs=jobs,
        keyword=keyword,
        location=location,
        top_companies=top_companies,
        top_locations=top_locations,
        top_dates=top_dates
    )


@app.route("/download")
def download():
    jobs = session.get("jobs", [])
    keyword = session.get("keyword", "jobs")
    location = session.get("location", "location")

    if not jobs:
        return render_template("index.html", error="Session expired! Please search again.")

    pdf_path = generate_pdf(jobs, keyword, location)
    return send_file(pdf_path, as_attachment=True, download_name=f"job_report_{keyword}.pdf")


@app.route("/email", methods=["POST"])
def email_report():
    jobs = session.get("jobs", [])
    keyword = session.get("keyword", "jobs")
    location = session.get("location", "location")
    recipient = request.form.get("email")

    if not jobs:
        return render_template("index.html", error="Session expired! Please search again.")

    if not recipient:
        return render_template("results.html", jobs=jobs, keyword=keyword, location=location, error="Please enter an email address!")

    pdf_path = generate_pdf(jobs, keyword, location)

    try:
        msg = Message(
            subject=f"Job Report - {keyword} in {location}",
            sender=os.getenv("MAIL_EMAIL"),
            recipients=[recipient]
        )
        msg.body = f"Hi!\n\nPlease find attached your job report for '{keyword}' in '{location}'.\n\nTotal jobs found: {len(jobs)}\n\nBuilt by Adharv Shyam"

        with app.open_resource(pdf_path) as pdf:
            msg.attach(f"job_report_{keyword}.pdf", "application/pdf", pdf.read())

        mail.send(msg)
        return render_template("results.html", jobs=jobs, keyword=keyword, location=location, success="Report sent successfully to " + recipient + "! 📧")

    except Exception as e:
        print(f"Email error: {e}")
        return render_template("results.html", jobs=jobs, keyword=keyword, location=location, error="Failed to send email. Please try again!")


if __name__ == "__main__":
    app.run(debug=False)