import os 
import time
import sqlite3
import requests
from datetime import datetime

# ==========================================
# CONFIGURACIÓN
# ==========================================
SHOKO_HOST = "127.0.0.1"
SHOKO_PORT = 8111
SHOKO_API_KEY = ""

ANILIST_TOKEN = "Bearer ""

SHOKO_API_URL = f"http://{SHOKO_HOST}:{SHOKO_PORT}/api/v3"
ANILIST_API_URL = "https://graphql.anilist.co"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "historial_anime.db")
INTERVALO_CONSULTA = 20  # Revisa cada 20 segundos
MAX_REINTENTOS = 5

SHOKO_HEADERS = {"apikey": SHOKO_API_KEY, "Accept": "application/json"}
ANILIST_HEADERS = {
    "Authorization": ANILIST_TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# ==========================================
# BASE DE DATOS LOCAL Y GESTIÓN DE COLA
# ==========================================
def inicializar_base_datos():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodios_sync (
            episode_id INTEGER PRIMARY KEY,
            series_id INTEGER,
            mal_id INTEGER,
            anilist_id INTEGER,
            numero_episodio INTEGER,
            estado TEXT CHECK(estado IN ('PENDIENTE', 'ENVIADO', 'ERROR')),
            intentos INTEGER DEFAULT 0,
            fecha_detectado TEXT,
            fecha_enviado TEXT
        )
    """)
    conexion.commit()
    conexion.close()

def obtener_estado_episodio(episode_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("SELECT estado, anilist_id FROM episodios_sync WHERE episode_id = ?", (episode_id,))
    res = cursor.fetchone()
    conexion.close()
    return res  # Devuelve (estado, anilist_id) o None si no existe

def encolar_episodio(episode_id, series_id, mal_id, numero_episodio):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO episodios_sync 
        (episode_id, series_id, mal_id, numero_episodio, estado, fecha_detectado)
        VALUES (?, ?, ?, ?, 'PENDIENTE', ?)
    """, (episode_id, series_id, mal_id, numero_episodio, fecha))
    conexion.commit()
    conexion.close()

def actualizar_estado_episodio(episode_id, estado, anilist_id=None):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if estado == 'ENVIADO' else None
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    if estado == 'ENVIADO':
        cursor.execute("""
            UPDATE episodios_sync 
            SET estado = ?, anilist_id = ?, fecha_enviado = ?
            WHERE episode_id = ?
        """, (estado, anilist_id, fecha, episode_id))
    else:
        cursor.execute("""
            UPDATE episodios_sync 
            SET estado = ?, intentos = intentos + 1
            WHERE episode_id = ?
        """, (estado, episode_id))
    conexion.commit()
    conexion.close()

def obtener_pendientes_o_errores():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT episode_id, series_id, mal_id, anilist_id, numero_episodio, intentos 
        FROM episodios_sync 
        WHERE estado IN ('PENDIENTE', 'ERROR') AND intentos < ?
    """, (MAX_REINTENTOS,))
    filas = cursor.fetchall()
    conexion.close()
    return filas

# ==========================================
# INTEGACIÓN ANILIST
# ==========================================
def resolver_mal_a_anilist(mal_id):
    query = """
    query ($malId: Int) {
      Media (idMal: $malId, type: ANIME) {
        id
      }
    }
    """
    try:
        resp = requests.post(ANILIST_API_URL, json={'query': query, 'variables': {"malId": int(mal_id)}}, headers=ANILIST_HEADERS, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("Media", {}).get("id")
    except Exception:
        pass
    return None

def enviar_a_anilist(anilist_id, numero_episodio):
    mutation = """
    mutation ($mediaId: Int, $progress: Int) {
      SaveMediaListEntry (mediaId: $mediaId, progress: $progress) {
        id
        progress
      }
    }
    """
    try:
        resp = requests.post(
            ANILIST_API_URL,
            json={'query': mutation, 'variables': {"mediaId": int(anilist_id), "progress": int(numero_episodio)}},
            headers=ANILIST_HEADERS,
            timeout=5
        )
        if resp.status_code == 200 and "errors" not in resp.json():
            return True
        else:
            print(f"[x ERROR] AniList rechazó la actualización: {resp.text}")
    except Exception as e:
        print(f"[!] Error de red al conectar con AniList: {e}")
    return False

def obtener_numero_episodio(episode_id):
    try:
        url = f"{SHOKO_API_URL}/Episode/{episode_id}/AniDB"
        resp = requests.get(url, headers=SHOKO_HEADERS, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("EpisodeNumber")
    except Exception:
        pass
    return None

# ==========================================
# ETAPA 1: ESCANEO Y ENCOLADO (PRODUCTOR)
# ==========================================
def escanear_y_encolar_shoko():
    try:
        series_resp = requests.get(f"{SHOKO_API_URL}/Series?pageSize=50", headers=SHOKO_HEADERS, timeout=5)
        if series_resp.status_code != 200:
            return

        series_list = series_resp.json().get("List", [])

        for s in series_list:
            series_id = s.get("IDs", {}).get("ID")
            mal_ids = s.get("IDs", {}).get("MAL", [])
            mal_id = mal_ids[0] if mal_ids else None

            if not series_id or not mal_id:
                continue

            ep_resp = requests.get(f"{SHOKO_API_URL}/Series/{series_id}/Episode", headers=SHOKO_HEADERS, timeout=5)
            if ep_resp.status_code != 200:
                continue

            episodios = ep_resp.json()
            if isinstance(episodios, dict):
                episodios = episodios.get("List", [])

            for ep in episodios:
                ep_id = ep.get("IDs", {}).get("ID") or ep.get("ID")
                fecha_visto = ep.get("Watched")
                watch_count = ep.get("WatchCount", 0)

                es_visto = (fecha_visto is not None) or (watch_count > 0)
                if not ep_id or not es_visto:
                    continue

                # VERIFICACIÓN DE IDEMPOTENCIA
                info_db = obtener_estado_episodio(ep_id)
                if info_db:
                    estado_actual = info_db[0]
                    if estado_actual == 'ENVIADO':
                        # Proceso muere para este episodio
                        continue

                # Si no está en DB, obtenemos el número de episodio y lo encolamos
                num_ep = obtener_numero_episodio(ep_id)
                if not num_ep:
                    continue

                if not info_db:
                    print(f"[+] Nuevo capítulo visto detectado en Shoko: Serie {series_id} | Ep {num_ep} (Encolando...)")
                    encolar_episodio(ep_id, series_id, mal_id, num_ep)

    except Exception as e:
        print(f"[!] Error durante el escaneo de Shoko: {e}")

# ==========================================
# ETAPA 2: PROCESAMIENTO DE LA COLA (CONSUMIDOR)
# ==========================================
def procesar_cola_anilist():
    pendientes = obtener_pendientes_o_errores()
    if not pendientes:
        return

    for ep_id, series_id, mal_id, anilist_id, num_ep, intentos in pendientes:
        # Resolver AniList ID si no lo tenemos guardado aún
        if not anilist_id:
            anilist_id = resolver_mal_a_anilist(mal_id)

        if not anilist_id:
            print(f"[!] No se pudo resolver MAL ID {mal_id} en AniList (Intento {intentos + 1})")
            actualizar_estado_episodio(ep_id, 'ERROR')
            continue

        print(f"[⚡] Procesando envío a AniList -> Media ID: {anilist_id} | Ep: {num_ep}")
        exito = enviar_a_anilist(anilist_id, num_ep)

        if exito:
            print(f"[✓ EXITOSO] Sincronizado en AniList: Media {anilist_id} | Ep {num_ep}")
            actualizar_estado_episodio(ep_id, 'ENVIADO', anilist_id)
        else:
            print(f"[!] Falló el envío a AniList. Queda pendiente para reintento (Intento {intentos + 1})")
            actualizar_estado_episodio(ep_id, 'ERROR')

# ==========================================
# BUCLE PRINCIPAL
# ==========================================
def main():
    inicializar_base_datos()
    print("[🚀] Demonio Shoko-AniList Sync iniciado (Arquitectura Idempotente).")
    print(f"[⚙️] Escaneando y sincronizando cada {INTERVALO_CONSULTA} segundos...")

    while True:
        escanear_y_encolar_shoko()
        procesar_cola_anilist()
        time.sleep(INTERVALO_CONSULTA)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Servicio detenido.")

