import os
import json
import re
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, "/var/task/api")

from jobcore.orchestrator import run_automation_pipeline
from jobcore.services.pdf_generator import generate_cv_pdf
from jobcore.services.cv_data import PROFILE

ALLOWED_ORIGIN = "https://job-intelligence-engine-nu.vercel.app"

class handler(BaseHTTPRequestHandler):

    def _send_json_response(self, status_code, data):
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
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
            self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.end_headers()
            
            self.wfile.write(pdf_bytes)
            self.wfile.flush()
        except Exception as e:
            print(f"Error enviando archivo PDF: {e}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()
        
    def do_GET(self):
        self._send_json_response(200, {"status": "ok"})

        
    def do_POST(self):
        # 1. Verificación de origen
        origin = self.headers.get('Origin', '')
        if origin != ALLOWED_ORIGIN:
            print(f"❌ Origen no permitido: {origin}")
            return self._send_json_response(403, {"error": "Origen no permitido."})

        # 2. Verificar que la API key está configurada en el servidor
        secret_key = os.environ.get("INTERNAL_API_KEY")
        if not secret_key:
            print("❌ ERROR: INTERNAL_API_KEY no configurada.")
            return self._send_json_response(500, {"error": "Error interno del servidor."})

        # 3. Enrutador por Path
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip('/')

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 65536: 
                return self._send_json_response(400, {"error": "Petición demasiado grande."})

            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception as e:
            return self._send_json_response(400, {"error": f"JSON inválido o malformado: {str(e)}"})

        if path == "" or path == "/api/process-job":
            return self.handle_process_job(payload)
            
        elif path == "/api/generate-pdf":
            return self.handle_generate_pdf(payload)
            
        else:
            return self._send_json_response(404, {"error": f"Ruta '{path}' no encontrada."})

    def handle_process_job(self, payload):
        print("🚀 Ejecutando handler: /api/process-job")
        try:
            job_url = payload.get("url", "").strip()

            if not job_url or not re.match(r'^https?://', job_url):
                return self._send_json_response(400, {"error": "URL inválida."})

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
            scraped_data = payload.get("scraped_data")
            pdf_bytes = generate_cv_pdf(PROFILE, scraped_data)
            
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

    server = HTTPServer(('localhost', 8000), handler)
    print("🚀 Servidor seguro multiruta corriendo en http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor apagado.")
        server.server_close()