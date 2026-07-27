import requests
import json

SHOKO_HOST = "127.0.0.1"
SHOKO_PORT = 8111

# Endpoint estándar donde Shoko guarda su especificación OpenAPI/Swagger
swagger_url = f"http://{SHOKO_HOST}:{SHOKO_PORT}/swagger/v3/swagger.json"

print("🔍 Inspectando el mapa de endpoints (Swagger/OpenAPI) de Shoko Server...")

try:
    r = requests.get(swagger_url, timeout=5)
    if r.status_code == 200:
        swagger = r.json()
        paths = swagger.get("paths", {})
        print(f"✓ Éxito: Se encontraron {len(paths)} rutas registradas en la API.\n")
        
        # Filtramos las rutas relacionadas con historial o episodios
        palabras_clave = ["watched", "history", "recent", "dashboard", "episode"]
        rutas_filtradas = []

        for path in paths.keys():
            path_lower = path.lower()
            if any(kw in path_lower for kw in palabras_clave):
                rutas_filtradas.append(path)

        print("📌 Rutas encontradas para episodios/vistos/historial en v5.3.3:")
        print("---------------------------------------------------------")
        for ruta in sorted(rutas_filtradas):
            print(f"  • /api/v3{ruta}")
        print("---------------------------------------------------------")
    else:
        print(f"❌ HTTP {r.status_code}: No se pudo obtener la especificación de Swagger.")
except Exception as e:
    print(f"💥 Error al conectar con Swagger: {e}")

