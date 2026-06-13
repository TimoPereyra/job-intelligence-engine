from google import genai
from google.genai import types
import os
import json

from jobcore.services.cv_data import PROFILE

API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    print("⚠️ [Aviso] GOOGLE_API_KEY no encontrada en .env, usando clave hardcodeada...")
    API_KEY = ""

client = genai.Client(api_key=API_KEY)


def call_llm(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )
    return response.text


# ─── Email ────────────────────────────────────────────────────────────────────

def generate_email_content(scraped_data: dict) -> dict:
    print("--> [IA] Generando email personalizado y asunto...")

    skills = PROFILE.get("skills", {})
    stack_principal = " · ".join([
        *skills.get("backend", []),
        *skills.get("frontend", []),
        *skills.get("databases", []),
    ])

    prompt = f"""
    Actúa como un recruiter senior especializado en perfiles IT.
    Tu tarea es redactar el asunto y un email de postulación altamente personalizado para la vacante.

    PERFIL DEL CANDIDATO
    Nombre: {PROFILE["name"]}
    Headline: {PROFILE["headline"]}
    Resumen: {PROFILE["summary"]}
    Stack: {stack_principal}
    Idiomas: {" | ".join(skills.get("languages", []))}

    DATOS DE LA VACANTE
    Título: {scraped_data.get("title", "")}
    Empresa: {scraped_data.get("company", "")}
    Contacto: {scraped_data.get("email", "")}
    Descripción: {scraped_data.get("description", "")}

    REGLAS ESTRICTAS:
    - Devolver SOLO un JSON con las claves "asunto" y "cuerpo".

    Reglas para el "asunto":
    - Profesional y directo.

    Reglas para el "cuerpo":
    - Máximo 150 palabras. Tono profesional y cercano.
    - Destacar experiencia relevante del perfil que haga match con la descripción.
    - No inventar información bajo ningún concepto.
    - No incluir firma ni saludos finales genéricos como "Atentamente, [Firma]".
    """

    try:
        return json.loads(call_llm(prompt))
    except Exception as e:
        print(f"Error generando email: {e}")
        titulo = scraped_data.get("title", "")
        return {
            "asunto": f"Postulación para la posición de {titulo}",
            "cuerpo": (
                f"Hola,\n\nMe gustaría postularme para la posición de {titulo}.\n\n"
                f"Cuento con experiencia en desarrollo Full Stack utilizando {stack_principal}.\n\n"
                f"Adjunto mi CV para su consideración.\n\nMuchas gracias por su tiempo."
            )
        }


# ─── CV ───────────────────────────────────────────────────────────────────────

def adapt_cv_for_job(scraped_data: dict) -> dict:
    """
    Adapta PROFILE (cv_data) a la vacante scrapeada.
    Se dispara desde un botón en el frontend, no desde el orquestador.
    """
    print("--> [IA] Adaptando CV a la vacante...")

    prompt = f"""
    Sos un redactor experto en CVs técnicos para el mercado IT latinoamericano.

    Tenés este perfil profesional real:
    {json.dumps(PROFILE, ensure_ascii=False, indent=2)}

    Y esta oferta de trabajo:
    Título: {scraped_data.get("title", "No especificado")}
    Descripción: {scraped_data.get("description", "No especificada")}

    Tu tarea es adaptar el perfil al puesto siguiendo estas reglas estrictas:

    1. SUMMARY: Reescribí "summary" en 3-4 oraciones resaltando lo más relevante para esta oferta.
    2. EXPERIENCE bullets: Reordenó los bullets de cada trabajo priorizando los más relevantes.
       Podés reformular levemente para usar palabras clave de la oferta, sin inventar nada.
    3. SKILLS: Dentro de cada categoría reordenó las tecnologías priorizando las de la oferta.
    4. HEADLINE: Podés adaptar las tecnologías del headline para alinearlas con la oferta, pero bajo NINGÚN concepto agregues palabras que reduzcan el seniority del candidato como "Junior", "Trainee" o "Principiante". Mantener el perfil enfocado a un nivel con autonomía (Semi-Senior / Ssr). Máximo 8 palabras.
    5. NO INVENTAR NI QUITAR EXPERIENCIA: Nunca agregues tecnologías, empresas, títulos o logros que no existan en el perfil. Tampoco reduzcas los años de experiencia totales del candidato.

    Respondé ÚNICAMENTE con el JSON del perfil adaptado, con exactamente la misma estructura
    que el perfil de entrada. Sin explicaciones, sin markdown, sin texto adicional.
    """

    try:
        clean = call_llm(prompt).strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except Exception as e:
        print(f"Error adaptando CV: {e}. Usando perfil original.")
        return PROFILE