import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "historial_anime.db")

# Colores ANSI
VERDE = "\033[92m"
AMARILLO = "\033[93m"
ROJO = "\033[91m"
CIAN = "\033[96m"
NEGRITA = "\033[1m"
RESET = "\033[0m"

def mostrar_tabla():
    if not os.path.exists(DB_PATH):
        print(f"\n{ROJO}[!] No existe la base de datos en: {DB_PATH}{RESET}\n")
        return

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT episode_id, series_id, mal_id, anilist_id, numero_episodio, estado, fecha_enviado 
        FROM episodios_sync 
        ORDER BY episode_id DESC
    """)
    filas = cursor.fetchall()
    conexion.close()

    if not filas:
        print(f"\n{AMARILLO}📁 La base de datos está vacía.{RESET}\n")
        return

    print(f"\n{NEGRITA}{CIAN}📊 HISTORIAL DE SINCRONIZACIÓN (SHOKO ➔ ANILIST){RESET}\n")
    print("┌──────────┬──────────┬──────────┬──────────┬────────┬────────────┬─────────────────────┐")
    print(f"│ {NEGRITA}{'Ep ID':<8}{RESET} │ {NEGRITA}{'Serie ID':<8}{RESET} │ {NEGRITA}{'MAL ID':<8}{RESET} │ {NEGRITA}{'AniList':<8}{RESET} │ {NEGRITA}{'Cap #':<6}{RESET} │ {NEGRITA}{'Estado':<10}{RESET} │ {NEGRITA}{'Fecha Enviado':<19}{RESET} │")
    print("├──────────┼──────────┼──────────┼──────────┼────────┼────────────┼─────────────────────┤")

    for f in filas:
        ep_id, series_id, mal_id, anilist_id, num_ep, estado, f_env = f
        
        # Color según el estado
        if estado == "ENVIADO":
            estado_fmt = f"{VERDE}{estado:<10}{RESET}"
        elif estado == "PENDIENTE":
            estado_fmt = f"{AMARILLO}{estado:<10}{RESET}"
        else:
            estado_fmt = f"{ROJO}{estado:<10}{RESET}"

        f_env_str = f_env if f_env else "Pendiente..."
        anilist_str = str(anilist_id) if anilist_id else "N/A"

        print(f"│ {ep_id:<8} │ {series_id:<8} │ {mal_id:<8} │ {anilist_str:<8} │ {num_ep:<6} │ {estado_fmt} │ {f_env_str:<19} │")

    print("└──────────┴──────────┴──────────┴──────────┴────────┴────────────┴─────────────────────┘\n")

if __name__ == "__main__":
    mostrar_tabla()
