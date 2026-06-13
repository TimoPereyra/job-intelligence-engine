import os
import json
import re
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# Antes (incorrecto para Vercel)
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Después (correcto)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jobcore.orchestrator import run_automation_pipeline
from jobcore.services.pdf_generator import generate_cv_pdf
from jobcore.services.cv_data import PROFILE

class handler(BaseHTTPRequestHandler):

    def _send_json_response(self, status_code, data):
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') 
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.end_headers()
            
            response_bytes = json.dumps(data).encode('utf-8')
            self.wfile.write(response_bytes)
            self.wfile.flush() 
        except Exception as e:
            print(f"Error enviando respuesta JSON: {e}")

    def _send_pdf_response(self, status_code, pdf_bytes, filename="CV_Optimizado.pdf"):
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename={filename}')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.end_headers()
            
            self.wfile.write(pdf_bytes)
            self.wfile.flush()
        except Exception as e:
            print(f"Error enviando archivo PDF: {e}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()

    def do_POST(self):
        # 1. Capa de Seguridad Global
        auth_header = self.headers.get('Authorization', '')
        secret_key = os.environ.get("INTERNAL_API_KEY")

        if not secret_key:
            print("❌ ERROR: La variable de entorno INTERNAL_API_KEY está vacía o no se cargó.")
            return self._send_json_response(500, {"error": "Error interno del servidor: Falta configuración de seguridad."})

        expected_header = f"Bearer {secret_key}"
        if not auth_header or auth_header != expected_header:
            print("❌ ERROR: Credenciales inválidas.")
            return self._send_json_response(401, {"error": "Acceso denegado."})

        # 2. Enrutador por Path (Manejo de rutas múltiples)
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip('/')

        # Lectura segura del payload de la petición
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            # Ajuste de límite superior para cargas útiles complejas
            if content_length > 65536: 
                return self._send_json_response(400, {"error": "Petición demasiado grande."})

            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception as e:
            return self._send_json_response(400, {"error": f"JSON inválido o malformado: {str(e)}"})

        # --- Despacho de Rutas ---
        if path == "" or path == "/api/process-job":
            return self.handle_process_job(payload)
            
        elif path == "/api/generate-pdf":
            return self.handle_generate_pdf(payload)
            
        else:
            return self._send_json_response(404, {"error": f"Ruta '{path}' no encontrada."})

    # --- Controladores Aislados ---

    def handle_process_job(self, payload):
        print("🚀 Ejecutando handler: /api/process-job")
        try:
            job_url = payload.get("url", "").strip()

            if not job_url or not re.match(r'^https?://', job_url):
                return self._send_json_response(400, {"error": "URL inválida."})

            # Ejecución del pipeline de automatización
            resultado = run_automation_pipeline(job_url)
            
            if resultado.get("status") == "error":
                return self._send_json_response(400, resultado)
            
            return self._send_json_response(200, resultado)

        except Exception as e:
            print(f"💥 Error crítico en /api/process-job: {str(e)}")
            return self._send_json_response(500, {"error": "Fallo crítico al procesar la oferta laboral."})

    def handle_generate_pdf(self, payload):
        print("📄 Ejecutando handler: /api/generate-pdf")
        try:
            # Capturamos la vacante que viene estructurada desde el cliente
            scraped_data = payload.get("scraped_data")

            # Invocamos al generador pasándole el perfil estático y los datos de la vacante.
            # Si scraped_data existe, pdf_generator llamará internamente a la IA.
            pdf_bytes = generate_cv_pdf(PROFILE, scraped_data)
            
            # Formateamos un nombre limpio para la descarga del usuario
            filename = "CV_Timoteo_Pereyra_ATS.pdf"
            if scraped_data and scraped_data.get("company"):
                empresa_clean = "".join(c for c in scraped_data["company"] if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
                filename = f"CV_Timoteo_Pereyra_{empresa_clean}.pdf"

            return self._send_pdf_response(200, pdf_bytes, filename=filename)

        except Exception as e:
            print(f"💥 Error crítico en /api/generate-pdf: {str(e)}")
            return self._send_json_response(500, {"error": "Fallo crítico al generar el PDF adaptado."})


if __name__ == '__main__':
    from http.server import HTTPServer
    
    # --- Cargador Nativo Seguro de .env ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir)) 
    env_path = os.path.join(root_dir, '.env')

    if os.path.exists(env_path):
        print(f"📄 Cargando variables desde: {env_path}")
        with open(env_path, encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip("'\"")
                        os.environ[key] = value
    else:
        print(f"⚠️ ATENCIÓN: No se encontró el archivo .env en {env_path}")

    # Servidor multiruta listo
    server = HTTPServer(('localhost', 8000), handler)
    print("🚀 Servidor seguro multiruta corriendo en http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor apagado.")
        server.server_close()