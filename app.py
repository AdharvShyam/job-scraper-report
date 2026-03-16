from flask import Flask, render_template, request, send_file, session
from scraper.scraper import scrape_jobs
from report.pdf_generator import generate_pdf
from collections import Counter
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

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

    return render_template("results.html", jobs=jobs, keyword=keyword, location=location)


@app.route("/analytics")
def analytics():
    jobs = session.get("jobs", [])
    keyword = session.get("keyword", "")
    location = session.get("location", "")

    if not jobs:
        return render_template("index.html", error="Session expired! Please search again.")

    # Top companies
    companies = [job.get("Company", "N/A") for job in jobs]
    top_companies = Counter(companies).most_common(8)

    # Top locations
    locations = [job.get("Location", "N/A") for job in jobs]
    top_locations = Counter(locations).most_common(6)

    # Jobs by date
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


if __name__ == "__main__":
    app.run(debug=True)