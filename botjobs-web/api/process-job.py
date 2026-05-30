import os
import json
import re
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# Para asegurar que Python encuentre la carpeta 'core' al ejecutar localmente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.orchestrator import run_automation_pipeline

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
            print(f"Error enviando respuesta: {e}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()

    def do_POST(self):
        # 1. Capturamos los valores
        auth_header = self.headers.get('Authorization', '')
        secret_key = os.environ.get("INTERNAL_API_KEY")

        # 2. DEBUG VISUAL EN CONSOLA
        print("\n--- 🔍 DEBUG DE SEGURIDAD ---")
        print(f"Variable de entorno (INTERNAL_API_KEY): '{secret_key}'")
        print(f"Header recibido (Authorization): '{auth_header}'")
        print("-----------------------------\n")

        # 3. Validación de Entorno (Servidor)
        if not secret_key:
            print("❌ ERROR: La variable de entorno INTERNAL_API_KEY está vacía o no se cargó.")
            return self._send_json_response(500, {"error": "Error interno del servidor: Falta configuración de seguridad."})

        # 4. Validación de Petición (Cliente)
        expected_header = f"Bearer {secret_key}"
        if not auth_header or auth_header != expected_header:
            print(f"❌ ERROR: Credenciales inválidas. Se esperaba '{expected_header}'")
            return self._send_json_response(401, {"error": "Acceso denegado."})

        print("✅ Seguridad aprobada. Procesando petición...")

        # 5. Resto de tu lógica
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 4096:
                return self._send_json_response(400, {"error": "Petición grande."})

            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            job_url = payload.get("url", "").strip()

            if not job_url or not re.match(r'^https?://', job_url):
                return self._send_json_response(400, {"error": "URL inválida."})

            # === EJECUCIÓN DEL PIPELINE ORQUESTADO ===
            resultado = run_automation_pipeline(job_url)
            
            # Si el orquestador cortó temprano por un error esperado
            if resultado.get("status") == "error":
                # Usamos 400 (Bad Request) o 422 (Unprocessable Entity) porque el servidor anda bien, pero el proceso rebotó
                return self._send_json_response(400, resultado)
            
            # Si llegó al final con éxito
            self._send_json_response(200, resultado)

        except Exception as e:
            # Esto ahora SOLO va a saltar si hay un error catastrófico (ej: se cae la base de datos, error de sintaxis)
            print(f"💥 Error crítico no controlado: {str(e)}")
            self._send_json_response(500, {"error": "Fallo crítico en el servidor."})

if __name__ == '__main__':
    from http.server import HTTPServer
    
    # --- CARGADOR NATIVO DE .env (Ruta Absoluta y Seguro) ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir)) 
    env_path = os.path.join(root_dir, '.env')

    if os.path.exists(env_path):
        print(f"📄 Cargando variables desde: {env_path}")
        # El utf-8-sig es la magia que elimina los caracteres ocultos de Windows
        with open(env_path, encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip() # Limpiamos espacios en el nombre
                        value = parts[1].strip().strip("'\"") # Limpiamos espacios y comillas en el valor
                        os.environ[key] = value
    else:
        print(f"⚠️ ATENCIÓN: No se encontró el archivo .env en {env_path}")
    # -----------------------------------------------

    server = HTTPServer(('localhost', 8000), handler)
    print("🚀 Servidor seguro corriendo localmente en http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor apagado.")
        server.server_close()