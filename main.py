import sys
import logging
from core.query_generator import QueryGenerator
from adapters.jobspy_adapter import JobSpyAdapter
from services.filtering import FilteringService
from services.qualification import Qualification
from storage.manager import StorageManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("🚀 INICIANDO PIPELINE DE JOBBOT")

    # 1. Inicialización
    try:
        query_gen  = QueryGenerator()
        adapter    = JobSpyAdapter()
        filter_svc = FilteringService()
        qualifier  = Qualification()
        storage    = StorageManager()
    except Exception as e:
        logger.error(f"Error inicializando componentes: {e}")
        return

    # 2. Scraping
    queries = query_gen.generate().get("queries", [])
    logger.info(f"📦 Ejecutando {len(queries)} búsquedas...")

    all_jobs = []
    for query in queries:
        try:
            jobs = adapter.search(query, hours_old=24)
            all_jobs.extend(jobs)
        except Exception as e:
            logger.warning(f"Error en búsqueda '{query}': {e}")

    if not all_jobs:
        logger.info("🛑 No se encontraron ofertas nuevas. Finalizando.")
        return

    # 3. Filtrado y persistencia inicial
    clean_jobs = filter_svc.filter_jobs(all_jobs)
    new_count  = storage.save_raw_jobs(clean_jobs)
    logger.info(f"✨ Guardados {new_count} registros nuevos únicos.")

    # 4. Calificación IA
    to_qualify = storage.load_jobs()
    if not to_qualify:
        logger.info("✅ Todo está al día. Nada para calificar.")
        return

    logger.info(f"🧠 Calificando {len(to_qualify)} ofertas con IA...")
    ranked = qualifier.qualify_jobs(to_qualify)
    ranked.sort(key=lambda x: x.get("score", 0), reverse=True)

    # 5. Guardar resultados finales
    storage.save_ranked_jobs(ranked)

    # 6. Reporte final
    recommended = [j for j in ranked if j.get("recommended")]
    logger.info(f"🏁 Finalizado. Total calificados: {len(ranked)} | Recomendados: {len(recommended)}")

if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        logger.info("Proceso detenido por el usuario.")
    except Exception as e:
        logger.error(f"Error crítico en el pipeline: {e}")
        sys.exit(1)