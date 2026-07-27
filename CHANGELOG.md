# 🪵 Changelog - Shoko ➔ AniList Sync

Todos los cambios notables en este proyecto serán documentados en este archivo.

# 🪵 Changelog - Shoko ➔ AniList Sync

## [0.4.2] - 2026-07-27

### 🛠️ Modificado y Corregido
- **Filtro Estricto de Reproducción (`IsWatched`):** Eliminado el envío prematuro provocado por eventos de detención (`playbackstopped`). Ahora se valida incondicionalmente `UserStats.IsWatched == True` (API v3 de Shoko) para asegurar que la reproducción alcanzó el umbral del 85%.
- **Caché Local de IDs (MAL ID ➔ AniList ID):** Se añadió consulta previa a `historial_anime.db` para reutilizar identificadores de AniList conocidos, evitando tráfico y peticiones innecesarias a la red.
- **Saneamiento de Base de Datos:** Limpieza de la cola de reintentos (`ERROR` / `PENDIENTE`) e impermeabilización de la estructura SQL para trabajar sincronizada con la nueva regla de estados.

---


## [1.1.0] - 2026-07-27

### 🚀 Añadido
- **Seguridad (.env):** Migración de credenciales de API (Shoko API Key y AniList Bearer Token) a variables de entorno mediante `python-dotenv`.
- **Visor de Base de Datos (`ver_db.py`):** Interfaz CLI limpia formateada con tablas ANSI para inspección en tiempo real.
- **Archivo `.gitignore`:** Protección contra fugas accidentalmente de tokens o bases de datos SQLite en repositorios públicos.

### 🛠️ Modificado / Mejorado
- **Blindaje de Base de Datos SQLite:**
  - Lógica estricta de estado `ENVIADO` inamovible (regla de no sobreescritura/reinicio de contador).
  - Uso de consultas parametrizadas `ON CONFLICT DO UPDATE SET ... WHERE estado != 'ENVIADO'`.
- **Manejo de Rutas Absolutas:** Uso de `BASE_DIR` para permitir ejecución del demonio desde cualquier directorio del sistema.
- **Resiliencia de Red y DNS:** Implementación de mecanismo de reintentos con aislamiento de fallos de DNS (`/etc/resolv.conf`).

---

## [1.0.0] - 2026-07-24
- 🚀 Primera Versión Funcional (PoC) en Termux/Ubuntu PRoot.
- Mapeo básico de IDs cruzados entre Shoko (AniDB/MAL) y GraphQL de AniList.

