import os
import re
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class StorageManager:

    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("❌ Falta configurar SUPABASE_URL o SUPABASE_KEY en el .env")
        self.supabase: Client = create_client(url, key)

    def _clean_str(self, value) -> str | None:
        if value is None:
            return None
        s = str(value).strip()
        return None if s.lower() in ("none", "") else s

    def _title_company_key(self, title: str, company: str) -> str:
        t = re.sub(r"[^a-z0-9]", "", (title or "").lower().strip())
        c = re.sub(r"[^a-z0-9]", "", (company or "").lower().strip())
        return f"{t}|{c}"

    def _serialize_job(self, job) -> dict:
        job_dict = job if isinstance(job, dict) else job.__dict__
        url = self._clean_str(job_dict.get("url") or job_dict.get("job_url"))
        description = self._clean_str(job_dict.get("description"))

        return {
            "title":       self._clean_str(job_dict.get("title")),
            "company":     self._clean_str(job_dict.get("company")),
            "location":    self._clean_str(job_dict.get("location")),
            "url":         url,
            "description": description,
            "status":      "pending",
        }

    def save_raw_jobs(self, jobs_list: list) -> int:
        if not jobs_list:
            return 0

        clean_jobs = [self._serialize_job(j) for j in jobs_list if j]

        unique_jobs_dict = {}
        for job in clean_jobs:
            url = job.get("url")
            if url:
                unique_jobs_dict[url] = job

        jobs_to_insert = list(unique_jobs_dict.values())

        try:
            res = self.supabase.table("jobs").upsert(
                jobs_to_insert,
                on_conflict="url",
            ).execute()
            return len(res.data) if res.data else 0
        except Exception as e:
            print(f"❌ Error insertando lote: {e}")
            return 0

    def load_jobs(self) -> list:
        try:
            res = (
                self.supabase
                .from_("jobs")
                .select("*")
                .eq("status", "pending")
                .execute()
            )
            return res.data if res.data else []
        except Exception as e:
            print(f"❌ Error cargando jobs: {e}")
            return []

    def save_ranked_jobs(self, ranked_jobs: list) -> list:
        if not ranked_jobs:
            return []

        # 1. Filtrar — score debe ser número entero/float estrictamente > 0
        worthy = [
            j for j in ranked_jobs
            if isinstance(j.get("score"), (int, float)) and j["score"] > 0
        ]

        if not worthy:
            print("🛑 Ningún empleo superó score 0. Nada guardado.")
            return []

        discarded = len(ranked_jobs) - len(worthy)
        if discarded:
            print(f"🗑️  {discarded} empleos descartados (score ≤ 0)")

        # 2. Dedup por título+empresa dentro del lote
        seen, deduped = set(), []
        for job in worthy:
            key = self._title_company_key(job.get("title", ""), job.get("company", ""))
            if key not in seen:
                seen.add(key)
                deduped.append(job)

        dupes = len(worthy) - len(deduped)
        if dupes:
            print(f"🔁 {dupes} duplicados eliminados antes de guardar")

        # 3. Armar payload y guardar
        payload = []
        for job in deduped:
            description = self._clean_str(job.get("description"))
            entry = {
                "url":         self._clean_str(job.get("url")),
                "title":       self._clean_str(job.get("title")),
                "company":     self._clean_str(job.get("company")),
                "location":    self._clean_str(job.get("location")),
                "score":       int(job["score"]),  # garantizamos que sea int
                "recommended": bool(job.get("recommended", False)),
                "ai_summary":  self._clean_str(job.get("ai_summary")),
                "status":      "qualified",
            }
            if description:
                entry["description"] = description
            payload.append(entry)

        try:
            self.supabase.table("jobs").upsert(payload, on_conflict="url").execute()
            print(f"💾 {len(payload)} empleos guardados en Supabase.")
            return payload
        except Exception as e:
            print(f"❌ Error actualizando calificaciones: {e}")
            return []