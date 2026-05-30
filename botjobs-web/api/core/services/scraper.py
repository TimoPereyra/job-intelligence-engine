import urllib.request
import re
import json

def extract_content(url):
    print(f"--> [Scraper] Analizando: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Buscamos el texto en meta description
            match = re.search(r'meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE | re.DOTALL)
            
            # Buscamos imagen en meta og:image (la forma más fiable de detectar posts de LinkedIn)
            img_match = re.search(r'meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
            
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            email = re.findall(email_pattern, html)
            email = email[0] if email else None

            # Construcción de la data
            if match and len(match.group(1)) > 50:
                full_text = match.group(1)
                data = {"url": url, "title": full_text.split('\n')[0], "email": email, "description": full_text, "status": "success"}
            
            # Prioridad 2: Si hay og:image, detectamos imagen
            elif img_match:
                data = {"url": url, "title": "Post basado en imagen", "email": email, "description": f"Contenido detectado como imagen. URL: {img_match.group(1)}", "status": "image_detected"}
            
            # Prioridad 3: Fallback a búsqueda de imágenes genéricas
            elif len(re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)) > 2:
                data = {"url": url, "title": "Post basado en imagen", "email": email, "description": "Contenido detectado como imagen.", "status": "image_detected"}
            
            else:
                data = {"url": url, "title": "Error de extracción", "email": None, "description": "No se pudo extraer texto ni imagen.", "status": "error"}

            # AQUÍ EL PRINT DE TODA LA DATA
            print("\n" + "="*50)
            print("📊 DATOS EXTRAÍDOS POR EL SCRAPER:")
            print(json.dumps(data, indent=4, ensure_ascii=False))
            print("="*50 + "\n")
            
            return data
            
    except Exception as e:
        data = {"url": url, "title": "Error de conexión", "email": None, "description": str(e), "status": "error"}
        print(f"\n💥 SCRAPER EXCEPTION: {json.dumps(data, indent=4, ensure_ascii=False)}")
        return data