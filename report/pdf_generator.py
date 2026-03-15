from fpdf import FPDF
import datetime

def clean(text, limit=100):
    return str(text).encode("latin-1", "ignore").decode("latin-1")[:limit]

class JobReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.set_fill_color(52, 152, 219)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "Job Listings Report", border=0, ln=True, align="C", fill=True)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | Page {self.page_no()} | Built by Adharv Shyam", align="C")


def generate_pdf(jobs, keyword, location):
    pdf = JobReport()
    pdf.add_page()

    # Search info
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, clean(f"Search: {keyword} | Location: {location}"), ln=True, align="C")
    pdf.cell(0, 8, f"Total Jobs Found: {len(jobs)}", ln=True, align="C")
    pdf.ln(5)

    # Table header
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(60, 10, "Job Title", border=1, fill=True)
    pdf.cell(50, 10, "Company", border=1, fill=True)
    pdf.cell(50, 10, "Location", border=1, fill=True)
    pdf.cell(30, 10, "Posted", border=1, fill=True, ln=True)

    # Table rows
    pdf.set_font("Arial", "", 8)
    fill = False
    for job in jobs:
        pdf.set_text_color(0, 0, 0)
        if fill:
            pdf.set_fill_color(235, 245, 255)
        else:
            pdf.set_fill_color(255, 255, 255)

        title = clean(job.get("Job Title", "N/A"), 35)
        company = clean(job.get("Company", "N/A"), 28)
        location_info = clean(job.get("Location", "N/A"), 28)
        posted = clean(job.get("Posted", "N/A"), 12)

        pdf.cell(60, 10, title, border=1, fill=True)
        pdf.cell(50, 10, company, border=1, fill=True)
        pdf.cell(50, 10, location_info, border=1, fill=True)
        pdf.cell(30, 10, posted, border=1, fill=True, ln=True)
        fill = not fill

    # Save PDF
    filename = f"report/job_report_{keyword}_{location}.pdf".replace(" ", "_")
    pdf.output(filename)
    print(f"PDF saved: {filename}")
    return filename