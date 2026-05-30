from core.services.scraper import extract_content
from core.services.ai_handler import generate_email_body
from core.services.mailer import send_custom_email

def run_automation_pipeline(job_url):
    print("\n=== INICIANDO PIPELINE DE BOTJOBS ===")
    
    # PASO 1
    scraped_data = extract_content(job_url)
    if not scraped_data:
        print("⚠️ Pipeline abortado en el paso 1.")
        return {"status": "error", "step": "scraper", "message": "No se pudo extraer información de la URL."}

    # PASO 2 (Solo llega acá si el paso 1 tuvo éxito)
    email_body = generate_email_body(scraped_data)
    if not email_body:
        print("⚠️ Pipeline abortado en el paso 2.")
        return {"status": "error", "step": "ai", "message": "La IA falló al generar el correo."}

    # PASO 3 (Solo llega acá si el paso 2 tuvo éxito)
    email_sent = send_custom_email(email_body)
    if not email_sent:
        print("⚠️ Pipeline abortado en el paso 3.")
        return {"status": "error", "step": "mailer", "message": "Fallo en el servidor de correos."}

    print("=== PIPELINE COMPLETADO CON ÉXITO ===\n")
    return {
        "status": "success",
        "message": "Automatización ejecutada correctamente.",
        "job_title": scraped_data.get("title")
    }