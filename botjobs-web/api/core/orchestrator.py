from core.services.scraper import extract_content
from core.services.ai_handler import generate_email_content

def run_automation_pipeline(job_url):
    print("\n=== INICIANDO PIPELINE DE BOTJOBS ===")

    scraped_data = extract_content(job_url)

    if not scraped_data:
        return {
            "status": "error",
            "step": "scraper",
            "message": "No se pudo extraer información de la URL."
        }

    email_body = generate_email_content(scraped_data)

    if not email_body:
        return {
            "status": "error",
            "step": "ai",
            "message": "La IA falló al generar el correo."
        }

    return {
        "status": "preview",
        "job_title": scraped_data.get("title"),
        "description": scraped_data.get("description"),
        "contact_email": scraped_data.get("email"),
        "email_preview": email_body
    }