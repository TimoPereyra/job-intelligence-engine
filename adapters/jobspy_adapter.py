import sys
import os
import site

# Agregar todas las rutas de usuario posibles al path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.append(user_site)

from jobspy import scrape_jobs
import logging
import re
class JobSpyAdapter:
    def __init__(self):
        self.default_results_wanted = 25
        self.default_hours_old = 72
        self.site_names = ["linkedin", "indeed"]
        self.skip_keywords = [
            "senior", "sr", "staff", "principal", "lead", "architect",
            "golang", "ruby", "rails", "scala",
            "ios", "android", "swift", "flutter",
            ".net", "c#", "java",
            "devops", "sre",
            "machine learning", "data engineer", "ai engineer",
            "salesforce", "sap", "qa automation",
        ]

    def _clean_text(self, text):
        if not text:
            return ""
        text = str(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _should_skip_job(self, title):
        title = title.lower()
        return any(k in title for k in self.skip_keywords)

    def search(self, query, results_wanted=None, hours_old=None):
        results_wanted = results_wanted or self.default_results_wanted
        hours_old = hours_old or self.default_hours_old

        try:
            print(f"\n🔍 BUSCANDO: {query}")
            jobs = scrape_jobs(
                site_name=self.site_names,
                search_term=query,
                location="Argentina",
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed="argentina",
                linkedin_fetch_description=True,
            )

            if jobs.empty:
                return []

            results = []
            for _, job in jobs.iterrows():
                title = self._clean_text(job.get("title", ""))
                if self._should_skip_job(title):
                    continue

                description = self._clean_text(job.get("description", ""))[:1500]
                results.append({
                    "title": title,
                    "company": self._clean_text(job.get("company", "")),
                    "location": self._clean_text(job.get("location", "")),
                    "description": description,
                    "url": job.get("job_url", ""),
                    "source": job.get("site", "unknown"),
                    "posted_at": str(job.get("date_posted", "")),
                })

            seen = set()
            unique = []
            for job in results:
                url = job.get("url")
                if url and url not in seen:
                    seen.add(url)
                    unique.append(job)

            return unique

        except Exception as e:
            logging.error(f"❌ ERROR JOBSPY: {e}")
            return []