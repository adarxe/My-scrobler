# Shoko-AniList Scrobbler (Termux/Ubuntu PRoot)

Sistema automático para scrobblear episodios desde Shoko Server hacia AniList.

## Instalación
1. Clonar el repositorio.
2. Instalar dependencias: `pip install requests python-dotenv`
3. Crear un archivo `.env` en la raíz con tu token:
   `ANILIST_TOKEN=tu_token_aqui`

## Archivos Principales
* **`shoko_anilist.py`**: Demonio principal (idempotente).
* **`ver_db.py`**: Visor CLI de la base de datos local.
