import time
import random
from adapters.jobspy_adapter import JobSpyAdapter
from services.filtering import FilteringService
from services.qualification import Qualification
from storage.manager import StorageManager

# ─── Configuración de Búsqueda ───────────────────────────────────────────────
QUERIES = [
    "backend developer", "fullstack developer", "software developer",
    "desarrollador backend", "desarrollador fullstack", "programador web",
    "php developer", "react developer", "node developer", "python developer",
    "ssr developer", "semi senior developer",
]

def run_production_test():
    print("\n🚀 EJECUTANDO PIPELINE COMPLETO (SCRAPING + FILTRO + IA)")
    print("=" * 60)

    # 1. Instanciación de servicios
    adapter    = JobSpyAdapter()
    filter_svc = FilteringService()
    qualifier  = Qualification()
    storage    = StorageManager()

    all_raw_jobs = []
    stats = {}

    # 2. Bucle de Scraping
    for i, query in enumerate(QUERIES, 1):
        print(f"\n🔎 [{i}/{len(QUERIES)}] Buscando: '{query}'")
        if i > 1:
            wait = random.uniform(20, 35)
            print(f"⏳ Pausa de seguridad: {wait:.1f}s...")
            time.sleep(wait)

        jobs = adapter.search(query, results_wanted=25, hours_old=48)
        
        fuente_count = {job.get("source", "unknown"): 0 for job in jobs}
        for job in jobs:
            src = job.get("source", "unknown")
            fuente_count[src] += 1
            
        stats[query] = {"bruto": len(jobs), "fuentes": fuente_count}
        all_raw_jobs.extend(jobs)

    # 3. Procesamiento (Deduplicación + Filtrado)
    seen, deduped = set(), []
    for job in all_raw_jobs:
        key = job.get("url") or f"{job['title']}|{job['company']}"
        if key not in seen:
            seen.add(key)
            deduped.append(job)

    clean_jobs = filter_svc.filter_jobs(deduped)
    
    # 4. Calificación directa con IA (Todo en la RAM de la máquina virtual)
    print("\n🧠 Calificando ofertas con IA...")
    if clean_jobs:
        # La IA califica la lista directamente en memoria
        ranked_jobs = qualifier.qualify_jobs(clean_jobs)
        
        # Le pasamos todo al manager, que filtra los > 0 antes de subir a Supabase
        saved_jobs = storage.save_ranked_jobs(ranked_jobs)
        
        print(f"✅ Calificación finalizada para {len(ranked_jobs)} ofertas.")
        
        # Resumen de recomendaciones basado en lo que realmente se guardó
        recom = [j for j in saved_jobs if j.get("recommended")]
        print(f"⭐ Ofertas recomendadas detectadas y guardadas: {len(recom)}")
    else:
        print("⚠️ No hay ofertas limpias para calificar.")

    print("\n🏁 PIPELINE FINALIZADO CON ÉXITO")

    # 5. Calificación con IA
    print("\n🧠 Calificando ofertas con IA...")
    pending_jobs = storage.load_jobs()
    if pending_jobs:
        ranked_jobs = qualifier.qualify_jobs(pending_jobs)
        storage.save_ranked_jobs(ranked_jobs)
        print(f"✅ Calificación finalizada para {len(ranked_jobs)} ofertas.")
        
        # Resumen de recomendaciones
        recom = [j for j in ranked_jobs if j.get("recommended")]
        print(f"⭐ Ofertas recomendadas detectadas: {len(recom)}")
    else:
        print("⚠️ No hay ofertas pendientes para calificar.")

    print("\n🏁 PIPELINE FINALIZADO CON ÉXITO")

if __name__ == "__main__":
    run_production_test()