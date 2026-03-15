import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APP_ID = "8b9f3293"
APP_KEY = "4714e8a845ac18d61760f1a0ee9ef589"

def scrape_jobs(keyword, location):
    print(f"Scraping jobs for: {keyword} in {location}...")

    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 20,
        "what": keyword,
        "where": location,
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params, timeout=15, verify=False)
        response.raise_for_status()
        data = response.json()
        print(f"API returned {len(data.get('results', []))} jobs")
    except Exception as e:
        print(f"Error: {e}")
        return []

    jobs = []
    for job in data.get("results", []):
        try:
            title = job.get("title", "N/A")
            company = job.get("company", {}).get("display_name", "N/A")
            location_info = job.get("location", {}).get("display_name", "N/A")
            salary_min = job.get("salary_min", "N/A")
            salary_max = job.get("salary_max", "N/A")
            posted = job.get("created", "N/A")[:10] if job.get("created") else "N/A"
            description = job.get("description", "")[:80] + "..."

            salary = f"₹{int(salary_min):,} - ₹{int(salary_max):,}" if salary_min != "N/A" and salary_max != "N/A" else "Not specified"

            jobs.append({
                "Job Title": title,
                "Company": company,
                "Location": location_info,
                "Salary": salary,
                "Posted": posted,
                "Description": description
            })
        except Exception as e:
            print(f"Error parsing job: {e}")
            continue

    print(f"Found {len(jobs)} jobs!")
    return jobs