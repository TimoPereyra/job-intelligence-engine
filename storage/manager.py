import os
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

    def _clean_str(self, value) -> str:
        """Convierte a string limpio. None y 'None' se convierten en string vacío."""
        if value is None:
            return ""
        s = str(value).strip()
        return "" if s.lower() == "none" else s

    def _serialize_job(self, job) -> dict:
        job_dict = job if isinstance(job, dict) else job.__dict__

        # El adapter normaliza a "url", jobspy raw usa "job_url"
        url = self._clean_str(job_dict.get("url") or job_dict.get("job_url"))

        description = self._clean_str(job_dict.get("description"))

        return {
            "title":       self._clean_str(job_dict.get("title")),
            "company":     self._clean_str(job_dict.get("company")),
            "url":         url,
            "description": description,
            "status":      "pending",
        }

    def save_raw_jobs(self, jobs_list: list) -> int:
        if not jobs_list:
            return 0

        clean_jobs = [self._serialize_job(j) for j in jobs_list if j]

        # Deduplicar por URL dentro del lote
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
                # ignoreDuplicates=True  ← alternativa: no pisa registros existentes
            ).execute()
            return len(res.data) if res.data else 0
        except Exception as e:
            print(f"❌ Error insertando lote: {e}")
            return 0

    def load_jobs(self) -> list:
        """Trae únicamente los jobs pendientes de calificación."""
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

    def save_ranked_jobs(self, ranked_jobs: list):
        if not ranked_jobs:
            return

        payload = []
        for job in ranked_jobs:
            description = self._clean_str(job.get("description"))

            entry = {
                "url":         self._clean_str(job.get("url")),
                "title":       self._clean_str(job.get("title")),
                "company":     self._clean_str(job.get("company")),
                "score":       job.get("score", 0),
                "recommended": job.get("recommended", False),
                "ai_summary":  self._clean_str(job.get("ai_summary")),
                "status":      "qualified",
            }

            # Solo incluimos description en el upsert si tiene contenido.
            # Así no pisamos una descripción ya guardada con un string vacío.
            if description:
                entry["description"] = description

            payload.append(entry)

        try:
            self.supabase.table("jobs").upsert(payload, on_conflict="url").execute()
            print("💾 Calificaciones guardadas exitosamente en Supabase.")
        except Exception as e:
            print(f"❌ Error actualizando calificaciones: {e}")