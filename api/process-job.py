import os
import json
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

class handler(BaseHTTPRequestHandler):

    def _send_json_response(self, status_code, data):
        """Helper seguro para enviar la respuesta y CERRAR la conexión"""
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') 
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.end_headers()
            
            # Convertimos a bytes y enviamos
            response_bytes = json.dumps(data).encode('utf-8')
            self.wfile.write(response_bytes)
            # El truco para evitar el NO_RESPONSE: vaciar el buffer
            self.wfile.flush() 
        except Exception as e:
            print(f"Error enviando respuesta: {e}")

    def do_OPTIONS(self):
        """Responde a las peticiones preflight del navegador"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()

    def do_POST(self):
        # 1. VERIFICACIÓN DE SEGURIDAD: Validar Token de Autorización
        auth_header = self.headers.get('Authorization', '')
        secret_key = os.environ.get("INTERNAL_API_KEY")

        if not secret_key:
            print("❌ ALERTA: INTERNAL_API_KEY no configurada.")
            self._send_json_response(500, {
                "status": "error", 
                "message": "Configuración de seguridad incompleta en el servidor."
            })
            return

        if not auth_header or auth_header != f"Bearer {secret_key}":
            self._send_json_response(401, {
                "status": "error", 
                "message": "Acceso denegado: Credenciales inválidas."
            })
            return

        try:
            # 2. LIMITACIÓN DE TAMAÑO
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 4096:
                self._send_json_response(400, {"status": "error", "message": "Petición demasiado grande."})
                return

            # Leer cuerpo
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            job_url = payload.get("url", "").strip()

            # 3. SANITIZACIÓN Y VALIDACIÓN DE URL
            if not job_url:
                self._send_json_response(400, {"status": "error", "message": "Falta el parámetro 'url'."})
                return

            url_pattern = re.compile(
                r'^(https?://)'
                r'(([a-zA-Z0-9_]|-)+\.)+[a-zA-Z]{2,}'
                r'(/.*)?$'
            )
            
            if not url_pattern.match(job_url):
                self._send_json_response(400, {"status": "error", "message": "Formato de URL inválido o inseguro."})
                return

            # Si todo pasó con éxito, respondemos cerrando bien el canal:
            self._send_json_response(200, {
                "status": "success",
                "message": "Capa de seguridad aprobada. Listo para procesar.",
                "verified_domain": urlparse(job_url).netloc
            })

        except json.JSONDecodeError:
            self._send_json_response(400, {"status": "error", "message": "JSON malformado."})
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            self._send_json_response(500, {"status": "error", "message": "Error interno del servidor."})

if __name__ == '__main__':
    from http.server import HTTPServer
    # Levantamos el servidor nativo en el puerto 8000
    server = HTTPServer(('localhost', 8000), handler)
    print("🚀 Servidor seguro corriendo localmente en http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor apagado.")
        server.server_close()