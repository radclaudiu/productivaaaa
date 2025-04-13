import http.server
import socketserver
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Definir puerto
PORT = 5000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Registrar la solicitud
        logger.info(f"Solicitud GET recibida en la ruta: {self.path}")
        
        # Respuesta simple para la ruta raíz
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Contenido HTML básico
            content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Servidor de Prueba</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    h1 { color: #4CAF50; }
                    .container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Servidor de Prueba - Funcionando Correctamente</h1>
                    <p>Este es un servidor HTTP simple para verificar que el entorno puede ejecutar servicios web.</p>
                    <p>Si puedes ver esta página, significa que el servidor está funcionando correctamente.</p>
                    <hr>
                    <p><strong>Próximos pasos:</strong></p>
                    <ul>
                        <li>Configurar un workflow adecuado para la aplicación Flask</li>
                        <li>Verificar la integración del módulo de horarios</li>
                        <li>Probar la funcionalidad completa</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(content.encode())
            return
        
        # Para otras rutas, comportamiento por defecto
        super().do_GET()

logger.info(f"Iniciando servidor HTTP en puerto {PORT}...")

# Crear y configurar el servidor
with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    logger.info(f"Servidor corriendo en http://0.0.0.0:{PORT}")
    
    # Mantener el servidor ejecutándose
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    finally:
        httpd.server_close()
        logger.info("Servidor cerrado")