import os
from core.query_generator import QueryGenerator
from adapters.jobspy_adapter import JobSpyAdapter
from services.filtering import FilteringService
from services.qualification import Qualification
from storage.manager import StorageManager

def run_test():
    print("\n🚀 INICIANDO PIPELINE AUTOMATIZADO - BOTJOBS (SUPABASE)")
    print("=" * 80)

    # ==========================================================================
    # 1. INICIALIZACIÓN DE COMPONENTES
    # ==========================================================================
    query_generator = QueryGenerator()
    adapter = JobSpyAdapter()
    filter_service = FilteringService()
    qualification = Qualification()
    storage = StorageManager()

    # ==========================================================================
    # 2. GENERACIÓN DE QUERIES DINÁMICAS
    # ==========================================================================
    query_data = query_generator.generate()
    queries = query_data.get("queries", [])
    print(f"\n📦 Se generaron {len(queries)} búsquedas para ejecutar.")

    # ==========================================================================
    # 3. SCRAPING EN LOTE (Ventana de 24 horas)
    # ==========================================================================
    all_scraped_jobs = []

    for i, query in enumerate(queries, 1):
        print(f"\n🔎 [{i}/{len(queries)}] Buscando: '{query}'...")
        try:
            jobs = adapter.search(query, hours_old=24)
            print(f"📥 Encontrados en bruto: {len(jobs)}")
            all_scraped_jobs.extend(jobs)
        except Exception as e:
            print(f"❌ Error buscando '{query}': {e}")

    print(f"\n📊 Total acumulado del scraping: {len(all_scraped_jobs)} ofertas.")

    # ==========================================================================
    # 4. FILTRADO ESTRICTO POR KEYWORDS (Ahorro de IA y limpieza)
    # ==========================================================================
    clean_jobs = filter_service.filter_jobs(all_scraped_jobs)

    # ==========================================================================
    # 5. PERSISTENCIA EN SUPABASE (Filtra duplicados históricos automáticamente)
    # ==========================================================================
    print(f"\n📤 Enviando lote a Supabase...")
    new_jobs_count = storage.save_raw_jobs(clean_jobs)
    print(f"✨ Nuevos registros únicos guardados en la DB: {new_jobs_count}")

    # ==========================================================================
    # 6. CARGA DE PENDIENTES Y CALIFICACIÓN CON IA
    # ==========================================================================
    jobs_to_qualify = storage.load_jobs()
    print(f"\n📚 Total de ofertas pendientes de evaluación en DB: {len(jobs_to_qualify)}")

    if not jobs_to_qualify:
        print("🛑 No hay ofertas nuevas para calificar en esta tanda. Fin del proceso.")
        return

    print("\n🧠 Evaluando perfiles con Inteligencia Artificial...")
    ranked_results = qualification.qualify_jobs(jobs_to_qualify)

    # Ordenamos de mayor a menor puntaje
    ranked_results_sorted = sorted(
        ranked_results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    # Guardamos las notas y cambiamos el estado a 'qualified' en la nube
    storage.save_ranked_jobs(ranked_results_sorted)

    # ==========================================================================
    # 7. REPORTE FINAL Y TOP 10
    # ==========================================================================
    recommended = [j for j in ranked_results_sorted if j.get("recommended")]

    print("\n" + "=" * 80)
    print("📊 RESUMEN EJECUTIVO DEL PIPELINE")
    print("=" * 80)
    print(f"📥 Traídos del scraping:    {len(all_scraped_jobs)}")
    print(f"🧹 Pasaron el filtro:       {len(clean_jobs)}")
    print(f"💾 Guardados como nuevos:   {new_jobs_count}")
    print(f"🧠 Calificados por IA:      {len(ranked_results_sorted)}")
    print(f"⭐ Recomendados finales:    {len(recommended)}")

    print("\n🏆 TOP 10 MEJORES OFERTAS ENCONTRADAS")
    print("=" * 80)
    for i, job in enumerate(ranked_results_sorted[:10], 1):
        print(f"\n[{i}] {job.get('title')} - 🏢 {job.get('company')}")
        print(f"   Puntaje: ⭐ {job.get('score')} | Recomendado: {'SÍ ✅' if job.get('recommended') else 'NO ❌'}")
        print(f"   Link:    🔗 {job.get('url')}")
        print(f"   Resumen: 🤖 {job.get('ai_summary')}")

    print("\n🏁 PIPELINE FINALIZADO CON ÉXITO")

if __name__ == "__main__":
    run_test()