# adapters/jobspy_adapter.py
import logging
import re
import time
import random
import pandas as pd
from jobspy import scrape_jobs

class JobSpyAdapter:
    def __init__(self):
        self.default_results_wanted = 25
        self.default_hours_old = 48
        self.stable_sites   = ["indeed", "google"]
        self.linkedin_sites = ["linkedin"]

        # Locations para LinkedIn — cada una trae un conjunto distinto de avisos
        self.linkedin_locations = [
            "Argentina",
            "Buenos Aires, Argentina",
            "Remote",
        ]

    def _clean_text(self, text):
        if not text:
            return ""
        text = str(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _should_skip_job(self, title):
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

    def _normalize_jobs(self, jobs, fallback_site: str) -> list[dict]:
        # Si es una lista, la convertimos a DataFrame
        if isinstance(jobs, list):
            jobs = pd.DataFrame(jobs)
        
        if jobs is None or jobs.empty:
            return []

        normalized = []
        # iteramos directamente sobre el DataFrame
        for _, job in jobs.iterrows():
            # Extraemos usando acceso directo al índice del objeto Series
            title = self._clean_text(job.get("title", ""))
            
            if not title or self._should_skip_job(title):
                continue
            
            # ACCESO SEGURO A PANDAS: usamos .get() sobre el objeto Series
            # Si el valor es NaN (propio de pandas), lo convertimos a vacío
            raw_desc = job.get("description", "")
            if pd.isna(raw_desc):
                raw_desc = job.get("job_description", "")
            
            normalized.append({
                "title":       title,
                "company":     self._clean_text(job.get("company", "")),
                "location":    self._clean_text(job.get("location", "")),
                "description": self._clean_text(raw_desc)[:1500],
                "url":         job.get("job_url", ""),
                "source":      job.get("site", fallback_site),
                "posted_at":   str(job.get("date_posted", "")),
            })
        return normalized
    def _scrape_indeed_google(self, query: str, results_wanted: int,
                               hours_old: int, location: str = "Argentina",
                               is_remote: bool = False) -> list[dict]:
        label = f"Indeed+Google ({'remoto' if is_remote else location})"
        print(f"   🔎 {label}...")
        try:
            time.sleep(random.uniform(3, 7))
            google_term = f"{query} {'remote job' if is_remote else f'trabajo {location}'}"
            jobs = scrape_jobs(
                site_name=self.stable_sites,
                search_term=query,
                google_search_term=google_term,
                location="remote" if is_remote else location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed="argentina",
                linkedin_fetch_description=True,
                is_remote=is_remote,
            )
            results = self._normalize_jobs(jobs, label.lower())
            print(f"   ✅ {label}: {len(results)} empleos")
            return results
        except Exception as e:
            logging.error(f"   ⚠️ Error en {label}: {e}")
            return []

    def _scrape_linkedin(self, query: str, hours_old: int) -> list[dict]:
        """
        Llama a LinkedIn una vez por cada location.
        Delay de 12-20s entre llamadas para no disparar el rate limit.
        """
        all_results = []
        for location in self.linkedin_locations:
            print(f"   🔎 LinkedIn ({location})...")
            try:
                time.sleep(random.uniform(12, 20))
                jobs = scrape_jobs(
                    site_name=self.linkedin_sites,
                    search_term=query,
                    location=location,
                    results_wanted=25,          # techo fijo por llamada
                    hours_old=hours_old,
                    linkedin_fetch_description=True,
                )
                results = self._normalize_jobs(jobs, f"linkedin-{location.split(',')[0].lower()}")
                print(f"   ✅ LinkedIn ({location}): {len(results)} empleos")
                all_results += results
            except Exception as e:
                logging.error(f"   ⚠️ LinkedIn ({location}) falló: {e}")
                continue
        return all_results

    def _deduplicate(self, jobs: list[dict]) -> list[dict]:
        seen, unique = set(), []
        for job in jobs:
            url = job.get("url", "").strip()
            key = url if url else f"{job['title']}|{job['company']}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        return unique

    def search(self, query: str, results_wanted: int = None, hours_old: int = None) -> list[dict]:
        results_wanted = results_wanted or self.default_results_wanted
        hours_old      = hours_old      or self.default_hours_old

        print(f"\n🚀 BÚSQUEDA: '{query}' | results={results_wanted} | hours={hours_old}")

        all_jobs = []

        # 1. Indeed + Google: presencial Argentina
        all_jobs += self._scrape_indeed_google(query, results_wanted, hours_old,
                                                location="Argentina", is_remote=False)
        # 2. Indeed + Google: solo remoto (trae avisos distintos)
        all_jobs += self._scrape_indeed_google(query, results_wanted, hours_old,
                                                is_remote=True)
        # 3. LinkedIn: 3 locations, ~25 resultados c/u
        all_jobs += self._scrape_linkedin(query, hours_old)

        unique = self._deduplicate(all_jobs)
        print(f"📊 '{query}': {len(unique)} únicos")
        return unique