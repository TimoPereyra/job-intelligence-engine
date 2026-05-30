def generate_email_body(scraped_data):
    print("--> [IA] Conectando con el LLM (Groq/Gemini/OpenRouter)...")
    
    # Aquí irá tu lógica real usando urllib.request para hacer el POST a la API de IA
    titulo_oferta = scraped_data.get("title", "la posición")
    
    # Simulación de la respuesta del bot para la prueba
    correo_generado = f"Hola,\n\nLes escribo para postularme a la oferta de: {titulo_oferta}.\nAdjunto mi CV.\n\nSaludos cordiales."
    
    return correo_generado