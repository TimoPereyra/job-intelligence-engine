import google.generativeai as genai
import os

API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    print("⚠️ [Aviso] GOOGLE_API_KEY no encontrada en .env, usando clave hardcodeada...")
    API_KEY = ""

genai.configure(api_key=API_KEY)
def call_llm(prompt):
    model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
    response = model.generate_content(prompt)
    # Limpieza básica por si la IA responde con formato markdown ```json ... ```
    text = response.text.replace('```json', '').replace('```', '')
    return text
    
def generate_email_body(scraped_data):
    print("--> [IA] Conectando con el LLM (Groq/Gemini/OpenRouter)...")
    
    # Aquí irá tu lógica real usando urllib.request para hacer el POST a la API de IA
    titulo_oferta = scraped_data.get("title", "la posición")
    descripcion = scraped_data.get("description")
    contacto = scraped_data.get("email")
    
    # Simulación de la respuesta del bot para la prueba
    correo_generado = f"Hola,\n\nLes escribo para postularme a la oferta de: {titulo_oferta}."
    if descripcion and descripcion != "No se encontró descripción disponible.":
        correo_generado += f"\n\nResumen de la oferta: {descripcion[:200]}..."
    if contacto:
        correo_generado += f"\n\nHe encontrado el contacto: {contacto}."
    correo_generado += "\n\nAdjunto mi CV.\n\nSaludos cordiales."
    
    return correo_generado