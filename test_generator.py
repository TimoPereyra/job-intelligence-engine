from core.query_generator import QueryGenerator
from adapters.jobspy_adapter import JobSpyAdapter
from services.qualification import Qualification
from storage.manager import StorageManager


def run_test():

    print("\n🧪 TEST PIPELINE REAL (24H)")
    print("=" * 80)

    # =========================================
    # INIT
    # =========================================

    query_generator = QueryGenerator()
    adapter = JobSpyAdapter()
    qualification = Qualification()
    storage = StorageManager()

    # =========================================
    # STEP 1: QUERIES DINÁMICAS
    # =========================================

    data = query_generator.generate()
    queries = data.get("queries", [])

    print(f"\n📦 QUERIES GENERADAS: {len(queries)}")

    # =========================================
    # STEP 2: SCRAPING (24H WINDOW)
    # =========================================

    all_jobs = []
    new_jobs = 0

    for i, query in enumerate(queries, 1):

        print("\n" + "=" * 80)
        print(f"🔎 [{i}/{len(queries)}] {query}")
        print("=" * 80)

        jobs = adapter.search(
            query,
            hours_old=24  # 🔥 SOLO 24 HORAS
        )

        print(f"📥 encontrados: {len(jobs)}")

        for job in jobs:

            try:
                if storage.mark_as_new(job):
                    new_jobs += 1
                    all_jobs.append(job)

            except Exception as e:
                print(f"❌ Error guardando: {e}")

    # =========================================
    # STEP 3: LOAD DB
    # =========================================

    jobs_db = storage.load_jobs()

    print("\n" + "=" * 80)
    print(f"📚 TOTAL DB: {len(jobs_db)}")
    print("=" * 80)

    if not jobs_db:
        print("❌ No hay jobs en DB")
        return

    # =========================================
    # STEP 4: QUALIFY
    # =========================================

    print("\n🧠 CALIFICANDO JOBS...")
    results = qualification.qualify_jobs(jobs_db)

    # =========================================
    # STEP 5: RANKING
    # =========================================

    results_sorted = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    storage.save_ranked_jobs(results_sorted)

    # =========================================
    # STEP 6: ANALYTICS
    # =========================================

    recommended = [r for r in results_sorted if r["recommended"]]

    print("\n📊 RESUMEN FINAL")
    print("=" * 80)

    print(f"📥 nuevos jobs: {new_jobs}")
    print(f"📚 total DB: {len(jobs_db)}")
    print(f"🏆 total calificados: {len(results_sorted)}")
    print(f"✅ recomendados: {len(recommended)}")

    # =========================================
    # TOP 10
    # =========================================

    print("\n🏆 TOP 10")
    print("=" * 80)

    for i, job in enumerate(results_sorted[:10], 1):

        print(f"\n[{i}] {job['title']}")
        print(f"🏢 {job['company']}")
        print(f"⭐ {job['score']}")
        print(f"🔗 {job['url']}")
        print(f"🤖 {job['ai_summary']}")

    print("\n🚀 PIPELINE COMPLETADO")


if __name__ == "__main__":
    run_test()