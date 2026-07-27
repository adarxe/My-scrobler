# 🪵 Changelog - Shoko ➔ AniList Sync

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a [Versionado Semántico](https://semver.org/lang/es/), manteniéndose en la rama `0.x.x` durante su fase Alfa.

## [0.4.2] - 2026-07-27

### 🛠️ Modificado y Corregido
- **Filtro Estricto de Reproducción (`IsWatched`):** Eliminado el envío prematuro provocado por eventos de detención (`playbackstopped`). Ahora se valida incondicionalmente `UserStats.IsWatched == True` (API v3 de Shoko) para asegurar que la reproducción alcanzó el umbral del 85%.
- **Caché Local de IDs (MAL ID ➔ AniList ID):** Se añadió consulta previa a `historial_anime.db` para reutilizar identificadores de AniList conocidos, evitando tráfico y peticiones innecesarias a la red.
- **Saneamiento de Base de Datos:** Limpieza de la cola de reintentos (`ERROR` / `PENDIENTE`) e impermeabilización de la estructura SQL para trabajar de forma sincronizada con la nueva regla de estados.

---

## [0.4.0] - 2026-07-27

### 🚀 Añadido
- **Seguridad (`.env`):** Migración de credenciales de API (Shoko API Key y AniList Bearer Token) a variables de entorno mediante `python-dotenv`.
- **Visor de Base de Datos (`ver_db.py`):** Interfaz CLI limpia formateada con tablas ANSI para inspección del historial en tiempo real.
- **Archivo `.gitignore`:** Protección contra fugas accidentales de tokens o bases de datos locales en repositorios públicos.

### 🛠️ Modificado / Mejorado
- **Blindaje de Base de Datos SQLite:**
  - Lógica estricta de estado `ENVIADO` inamovible (regla de no sobreescritura ni reinicio de contador para episodios ya sincronizados).
  - Implementación de consultas parametrizadas `ON CONFLICT DO UPDATE SET ... WHERE estado != 'ENVIADO'` para garantizar idempotencia.
- **Manejo de Rutas Absolutas:** Uso de `BASE_DIR` para permitir la ejecución del demonio desde cualquier directorio del sistema sin perder la referencia a los archivos.
- **Resiliencia de Red y DNS:** Implementación de mecanismo de reintentos con aislamiento de fallos de DNS (`/etc/resolv.conf`).

---

## [0.1.0] - 2026-07-24

### 🚀 Añadido
- Primera Versión Funcional (PoC) desplegada en Termux/Ubuntu PRoot.
- Mapeo básico de IDs cruzados entre la API de Shoko (AniDB/MAL) y la API GraphQL de AniList.

