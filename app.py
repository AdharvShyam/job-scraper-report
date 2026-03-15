from flask import Flask, render_template, request, send_file, session
from scraper.scraper import scrape_jobs
from report.pdf_generator import generate_pdf
import os

app = Flask(__name__)
app.secret_key = "adharv_secret_key_2026"

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