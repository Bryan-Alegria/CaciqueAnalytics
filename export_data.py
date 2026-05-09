"""CLI para exportar capas de datos modulares a JSON."""

import argparse
import json
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.data_layers import PlayerDataLayer, ComparisonDataLayer, LeaderboardDataLayer
from src.ml.similarity import SimilarityEngine


def _convertir_decimales(obj):
    """Convierte Decimal a float recursivamente para serialización JSON."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _convertir_decimales(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convertir_decimales(v) for v in obj]
    return obj

OUTPUT_DIR = Path(__file__).resolve().parent / "Infographics" / "data"


def exportar_jugador(player_name: str, season: int, competition: int) -> str:
    """Exporta capas de datos de un solo jugador."""
    layer = PlayerDataLayer(player_name, season, competition)
    data = layer.build_layers()
    layer.close()

    safe_name = player_name.replace(" ", "_").lower()
    filename = f"jugador_{safe_name}_s{season}_c{competition}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(_convertir_decimales(data), f, ensure_ascii=False, indent=2)

    return str(path)


def exportar_comparacion(p1: str, p2: str, season: int, competition: int) -> str:
    """Exporta capas de datos de comparación H2H."""
    layer = ComparisonDataLayer(p1, p2, season, competition)
    data = layer.build_layers()
    layer.close()

    safe1 = p1.replace(" ", "_").lower()
    safe2 = p2.replace(" ", "_").lower()
    filename = f"h2h_{safe1}_vs_{safe2}_s{season}_c{competition}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(_convertir_decimales(data), f, ensure_ascii=False, indent=2)

    return str(path)


def exportar_tabla(season: int, competition: int) -> str:
    """Exporta capas de datos de tablas de líderes."""
    layer = LeaderboardDataLayer(season, competition)
    data = layer.build_layers()
    layer.close()

    filename = f"tabla_s{season}_c{competition}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(_convertir_decimales(data), f, ensure_ascii=False, indent=2)

    return str(path)


def exportar_similares(player_name: str, season: int, competition: int, top_n: int = 5) -> str:
    """Exporta jugadores similares usando el motor de similitud."""
    engine = SimilarityEngine(season, competition)
    similar = engine.find_similar(player_name, top_n=top_n)

    data = {
        "jugador_objetivo": player_name,
        "temporada": season,
        "competicion": competition,
        "total_jugadores_index": engine.player_count,
        "jugadores_similares": [
            {
                "nombre": p.name,
                "equipo": p.team,
                "posicion": p.position_group,
                "similitud": round(p.similarity, 3),
                "minutos": p.minutes_played,
                "partidos": p.matches_played,
            }
            for p in similar
        ],
    }

    safe_name = player_name.replace(" ", "_").lower()
    filename = f"similares_{safe_name}_s{season}_c{competition}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(_convertir_decimales(data), f, ensure_ascii=False, indent=2)

    return str(path)


def main():
    parser = argparse.ArgumentParser(description="Exporta capas de datos para infografías")
    sub = parser.add_subparsers(dest="comando", required=True)

    # Jugador
    p_jugador = sub.add_parser("jugador", help="Exporta datos de un jugador")
    p_jugador.add_argument("--nombre", "-n", required=True, help="Nombre completo del jugador")
    p_jugador.add_argument("--temporada", "-s", type=int, default=2026, help="Año de la temporada")
    p_jugador.add_argument("--competicion", "-c", type=int, default=1, help="ID de la competición")

    # Comparación
    p_comp = sub.add_parser("comparar", help="Exporta comparación H2H")
    p_comp.add_argument("--j1", required=True, help="Nombre del jugador 1")
    p_comp.add_argument("--j2", required=True, help="Nombre del jugador 2")
    p_comp.add_argument("--temporada", "-s", type=int, default=2026)
    p_comp.add_argument("--competicion", "-c", type=int, default=1)

    # Tabla
    p_tabla = sub.add_parser("tabla", help="Exporta tablas de líderes")
    p_tabla.add_argument("--temporada", "-s", type=int, default=2026)
    p_tabla.add_argument("--competicion", "-c", type=int, default=1)

    # Similares
    p_sim = sub.add_parser("similares", help="Exporta jugadores similares (ML)")
    p_sim.add_argument("--nombre", "-n", required=True, help="Nombre del jugador objetivo")
    p_sim.add_argument("--temporada", "-s", type=int, default=2026)
    p_sim.add_argument("--competicion", "-c", type=int, default=1)
    p_sim.add_argument("--top", "-t", type=int, default=5, help="Cantidad de similares")

    args = parser.parse_args()

    if args.comando == "jugador":
        path = exportar_jugador(args.nombre, args.temporada, args.competicion)
        print(f"Datos de jugador exportados: {path}")

    elif args.comando == "comparar":
        path = exportar_comparacion(args.j1, args.j2, args.temporada, args.competicion)
        print(f"Datos de comparación exportados: {path}")

    elif args.comando == "tabla":
        path = exportar_tabla(args.temporada, args.competicion)
        print(f"Tabla de líderes exportada: {path}")

    elif args.comando == "similares":
        path = exportar_similares(args.nombre, args.temporada, args.competicion, args.top)
        print(f"Jugadores similares exportados: {path}")


if __name__ == "__main__":
    main()
