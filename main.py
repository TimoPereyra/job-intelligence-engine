import os
from dotenv import load_dotenv
from google import genai

# Importamos tus módulos
from core.query_generator import QueryGenerator
from adapters.jobspy_adapter import JobSpyAdapter
from storage.manager import StorageManager
from services.qualification import QualificationService

# Cargamos variables de entorno
load_dotenv()

def main():
    # 1. SETUP: Inicializamos todo
    storage = StorageManager()
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    gen = QueryGenerator()
    adapter = JobSpyAdapter()
    qualifier = QualificationService(client)

    print("🚀 Iniciando ciclo de búsqueda...")

    # 2. BÚSQUEDA Y PERSISTENCIA (El Scraper llena el "buffer" de nuevas)
    queries = gen.generate("Desarrollador Python y React en Buenos Aires")
    for q in queries:
        jobs = adapter.search(q)
        for job in jobs:
            # Aquí el StorageManager verifica si es nuevo y lo guarda
            storage.mark_as_new(job)

    # 3. CALIFICACIÓN (Procesamos solo lo que está en 'new')
    new_jobs = storage.get_jobs_by_status('new')
    print(f"🔍 Encontradas {len(new_jobs)} ofertas nuevas.")
    
    for job in new_jobs:
        # Calificamos con la IA
        try:
            score_data = qualifier.qualify(job, "Desarrollador Python/React")
            # Actualizamos en el JSON con el score y el nuevo estado
            storage.update_job_status(
                job_url=job['url'], 
                status='scored', 
                score=score_data['score']
            )
            print(f"✅ Calificada: {job['title']} (Score: {score_data['score']})")
        except Exception as e:
            print(f"❌ Error al calificar {job['title']}: {e}")

    # 4. DISPATCHER (Próximo paso: Aquí iría tu lógica de Webhook)
    scored_jobs = storage.get_jobs_by_status('scored')
    # filtered = [j for j in scored_jobs if j.get('score', 0) >= 7]
    # send_to_webhook(filtered)

    print("🏁 Ciclo finalizado.")

if __name__ == "__main__":
    main()