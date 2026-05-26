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

    def _serialize_job(self, job) -> dict:
        """Limpia el objeto de JobSpy para que Supabase lo entienda sin romper"""
        # Si viene como objeto/DataFrame, lo pasamos a dict común
        job_dict = job if isinstance(job, dict) else job.__dict__
        
        return {
            "title": str(job_dict.get("title", "")),
            "company": str(job_dict.get("company", "")),
            "url": str(job_dict.get("job_url") or job_dict.get("url", "")),
            "description": str(job_dict.get("description", "")),
            "status": "pending"
        }

    def save_raw_jobs(self, jobs_list: list) -> int:
        if not jobs_list:
            return 0
        
        # 1. Serializamos y limpiamos los campos primero
        clean_jobs = [self._serialize_job(j) for j in jobs_list if j]
        
        # 2. 🔥 FILTRO ANTI-DUPLICADOS DENTRO DEL MISMO LOTE
        # Usamos la URL como clave en un dict para borrar repetidos en memoria
        unique_jobs_dict = {}
        for job in clean_jobs:
            url = job.get("url")
            if url:
                unique_jobs_dict[url] = job  # Si se repite, pisa el anterior y queda uno solo
        
        jobs_to_insert = list(unique_jobs_dict.values())

        # 3. Enviamos el lote limpio a Supabase
        try:
            res = self.supabase.table("jobs").upsert(jobs_to_insert, on_conflict="url").execute()
            return len(res.data) if res.data else 0
        except Exception as e:
            print(f"❌ Error insertando lote: {e}")
            return 0

    def load_jobs(self) -> list:
        """Trae únicamente los jobs pendientes de calificación"""
        try:
            # Corregimos sintaxis de la query para la versión actual de supabase-py
            res = self.supabase.from_("jobs").select("*").eq("status", "pending").execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"❌ Error cargando jobs: {e}")
            return []

    def save_ranked_jobs(self, ranked_jobs: list):
        if not ranked_jobs:
            return
        
        # Le mandamos el objeto completo para respetar los campos NOT NULL de la DB
        payload = [
            {
                "url": job.get("url"),
                "title": job.get("title"),
                "company": job.get("company"),
                "description": job.get("description"),
                "score": job.get("score", 0),
                "recommended": job.get("recommended", False),
                "ai_summary": job.get("ai_summary", ""),
                "status": "qualified"
            }
            for job in ranked_jobs
        ]
        try:
            self.supabase.table("jobs").upsert(payload, on_conflict="url").execute()
            print("💾 Calificaciones guardadas exitosamente en Supabase.")
        except Exception as e:
            print(f"❌ Error actualizando calificaciones: {e}")