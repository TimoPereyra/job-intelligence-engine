import sys
import os
from core.services.ai_handler import call_llm
from bs4 import BeautifulSoup
import urllib.request
import json
import re

def extract_content(target_url):
    print(f"\n--> [Scraper] Analizando: {target_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    try:
        req = urllib.request.Request(target_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 1. Extraer Imagen (sigue siendo útil)
            og_image = soup.find("meta", property="og:image")
            img_url = og_image["content"] if og_image and og_image.has_attr("content") else None
            
            # 2. Extraer Texto Bruto (el aspirador)
            for s in soup(["script", "style", "nav", "footer", "header"]):
                s.extract()
            raw_text = soup.get_text(separator=' ', strip=True)[:10000]

            # 3. Llamar a la IA para obtener datos estructurados
            prompt = f"""
            Analiza el siguiente texto de una oferta laboral y extrae la información.
            Devuelve un JSON estricto con: "titulo", "descripcion" (resumen corto), "email".
            Si no es una vacante o no hay datos, usa null.
            Texto: {raw_text}
            """
            
            # Aquí invocas a tu función que usa GOOGLE_API_KEY o el modelo que prefieras
            llm_response = call_llm(prompt) 
            datos = json.loads(llm_response)

            return {
                "url": target_url,
                "title": datos.get("titulo", "Sin título"),
                "description": datos.get("descripcion", "No disponible"),
                "email": datos.get("email"),
                "img_url": img_url,
                "status": "success"
            }

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        return {"url": target_url, "status": "error", "message": str(e)}