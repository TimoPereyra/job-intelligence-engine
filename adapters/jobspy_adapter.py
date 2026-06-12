import logging
import re
import time
import random
import pandas as pd
from jobspy import scrape_jobs

class JobSpyAdapter:
    def __init__(self):
        self.default_results_wanted = 25
        self.default_hours_old = 12
        self.stable_sites   = ["indeed", "google"]
        self.linkedin_sites = ["linkedin"]

        self.linkedin_searches = [
            {"location": "Buenos Aires, Argentina", "is_remote": False, "market": "latam-es"},
            {"location": "Argentina",               "is_remote": True,  "market": "latam-es"},
            {"location": "Uruguay",                 "is_remote": True,  "market": "latam-es"},
            {"location": "Chile",                   "is_remote": True,  "market": "latam-es"},
            {"location": "Colombia",                "is_remote": True,  "market": "latam-es"},
            {"location": "Mexico",                  "is_remote": True,  "market": "latam-es"},
        ]

        self.indeed_searches = [
            {"location": "Argentina", "is_remote": False, "market": "latam-es"},
            {"location": "Argentina", "is_remote": True,  "market": "latam-es"},
        ]

    SPAM_COUNTRIES = [
        "india", "israel", "china", "pakistan", "bangladesh",
        "nigeria", "philippines", "ukraine", "egypt", "kenya",
        "vietnam", "indonesia", "malaysia", "sri lanka",
        "mumbai", "bangalore", "bengaluru", "hyderabad", "delhi",
        "pune", "chennai", "kolkata", "ahmedabad", "noida", "gurugram",
        "tel aviv", "jerusalem", "haifa",
        "beijing", "shanghai", "shenzhen", "guangzhou",
        "karachi", "lahore", "islamabad",
        "manila", "cebu",
        "lagos", "nairobi",
        "hanoi", "ho chi minh",
        "jakarta", "kuala lumpur",
    ]

    MARKET_SEARCH_SUFFIX = {
        "latam-es":  "trabajo remoto",
        "global-en": "remote job",
    }

    def _safe_str(self, value) -> str:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        return str(value).strip()

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _should_skip_job(self, title: str) -> bool:
        skip_keywords = [
            "senior", "sr.", "sr ", "staff", "principal", "lead", "architect",
            "golang", "ruby", "rails", "scala",
            "ios", "android", "swift", "flutter",
            ".net", "c#", "java ",
            "devops", "sre",
            "machine learning", "data engineer", "ai engineer",
            "salesforce", "sap", "qa automation",
        ]
        return any(k in title.lower() for k in skip_keywords)

    def _should_skip_location(self, location: str) -> bool:
        loc = location.lower()
        return any(country in loc for country in self.SPAM_COUNTRIES)

    def _normalize_url(self, url: str) -> str:
        """Elimina parámetros de tracking para comparar URLs limpias."""
        if not url:
            return ""
        return url.split("?")[0].split("&")[0].strip().rstrip("/").lower()

    def _title_company_key(self, title: str, company: str) -> str:
        """Clave normalizada título+empresa para detectar duplicados con URL distinta."""
        t = re.sub(r"[^a-z0-9]", "", title.lower().strip())
        c = re.sub(r"[^a-z0-9]", "", company.lower().strip())
        return f"{t}|{c}"

    def _normalize_jobs(self, jobs, fallback_site: str) -> list[dict]:
        if isinstance(jobs, list):
            jobs = pd.DataFrame(jobs)
        if jobs is None or jobs.empty:
            return []

        normalized = []
        skipped_location = 0

        for _, job in jobs.iterrows():
            title = self._clean_text(self._safe_str(job.get("title")))
            if not title or self._should_skip_job(title):
                continue

            location = self._clean_text(self._safe_str(job.get("location")))
            if not location or self._should_skip_location(location):
                skipped_location += 1
                continue

            raw_desc = self._safe_str(job.get("description") or job.get("job_description"))

            normalized.append({
                "title":       title,
                "company":     self._clean_text(self._safe_str(job.get("company"))),
                "location":    location,
                "description": self._clean_text(raw_desc)[:1500],
                "url":         self._safe_str(job.get("job_url")),
                "source":      self._safe_str(job.get("site")) or fallback_site,
                "posted_at":   self._safe_str(job.get("date_posted")),
            })

        if skipped_location:
            logging.info(f"    🚫 {skipped_location} descartados por ubicación no deseada/vacía")

        return normalized

    def _scrape_indeed_google(self, query: str, results_wanted: int,
                               hours_old: int, location: str,
                               is_remote: bool, market: str) -> list[dict]:
        suffix = self.MARKET_SEARCH_SUFFIX.get(market, "")
        label  = f"Indeed+Google ({market} / {'remoto' if is_remote else location})"
        print(f"    🔎 {label}...")
        try:
            time.sleep(random.uniform(3, 7))
            jobs = scrape_jobs(
                site_name=self.stable_sites,
                search_term=query,
                google_search_term=f"{query} {suffix}",
                location="remote" if is_remote else location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed="argentina",
                linkedin_fetch_description=True,
                is_remote=is_remote,
            )
            results = self._normalize_jobs(jobs, label.lower())
            print(f"    ✅ {label}: {len(results)} empleos")
            return results
        except Exception as e:
            logging.error(f"    ⚠️ Error en {label}: {e}")
            return []

    def _scrape_linkedin(self, query: str, hours_old: int) -> list[dict]:
        all_results = []
        for item in self.linkedin_searches:
            loc_name  = item["location"]
            is_remote = item["is_remote"]
            market    = item["market"]
            label     = f"LinkedIn ({market} / {loc_name}{'- remoto' if is_remote else ''})"
            print(f"    🔎 {label}...")
            try:
                time.sleep(random.uniform(12, 20))
                jobs = scrape_jobs(
                    site_name=self.linkedin_sites,
                    search_term=query,
                    location=loc_name,
                    results_wanted=25,
                    hours_old=hours_old,
                    linkedin_fetch_description=True,
                    is_remote=is_remote,
                )
                results = self._normalize_jobs(jobs, f"linkedin-{market}")
                print(f"    ✅ {label}: {len(results)} empleos")
                all_results += results
            except Exception as e:
                logging.error(f"    ⚠️ {label} falló: {e}")
                continue
        return all_results

    def _deduplicate(self, jobs: list[dict]) -> list[dict]:
        seen_urls   = set()
        seen_titles = set()
        unique      = []
        dupes       = 0

        for job in jobs:
            url_key   = self._normalize_url(job.get("url", ""))
            title_key = self._title_company_key(job.get("title", ""), job.get("company", ""))

            if (url_key and url_key in seen_urls) or title_key in seen_titles:
                dupes += 1
                continue

            if url_key:
                seen_urls.add(url_key)
            if title_key:
                seen_titles.add(title_key)

            unique.append(job)

        if dupes:
            logging.info(f"    🔁 {dupes} duplicados eliminados en dedup del adapter")

        return unique

    def search(self, query: str, results_wanted: int = None, hours_old: int = None) -> list[dict]:
        results_wanted = results_wanted or self.default_results_wanted
        hours_old      = hours_old      or self.default_hours_old

        print(f"\n🚀 BÚSQUEDA: '{query}' | results={results_wanted} | hours={hours_old}")

        all_jobs = []

        for search in self.indeed_searches:
            all_jobs += self._scrape_indeed_google(
                query, results_wanted, hours_old,
                location=search["location"],
                is_remote=search["is_remote"],
                market=search["market"],
            )

        all_jobs += self._scrape_linkedin(query, hours_old)

        unique = self._deduplicate(all_jobs)
        print(f"📊 '{query}': {len(unique)} únicos")
        return unique