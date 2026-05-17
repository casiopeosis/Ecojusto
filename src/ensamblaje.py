# algoritmo/ensamblaje.py
# Pipeline principal — Ensamblaje del Precio Justo
#
# P_justo = α_e · (P_comercial + C_ambiental + C_social)
#
# Corre para todas las empresas en la DB y devuelve resultados ordenados
# de mayor a menor P_justo.

from data.db import EMPRESAS, MATERIALES, PRENDAS
from algoritmo.opacidad import calcular_alpha
from algoritmo.markov import calcular_c_ambiental
from algoritmo.social import calcular_c_social


def _badge(transparencia: float) -> str:
    """Semáforo de nivel ético basado en índice FTI."""
    if transparencia >= 0.70:
        return "alta"
    elif transparencia >= 0.40:
        return "media"
    else:
        return "baja"


def calcular_precio_justo(empresa: dict, material: dict, prenda: dict) -> dict:
    """
    Calcula el precio justo real para una empresa × material × prenda.

    Returns:
        dict con todos los campos necesarios para el dashboard.
    """
    alpha = calcular_alpha(empresa["transparencia"])
    vida_util, c_ambiental = calcular_c_ambiental(empresa["transparencia"], material)
    c_social = calcular_c_social(empresa, prenda)

    p_justo = round(alpha * (prenda["precio_base"] + c_ambiental + c_social))

    return {
        "empresa":          empresa["nombre"],
        "precio_etiqueta":  prenda["precio_base"],
        "alpha_e":          round(alpha, 2),
        "c_ambiental":      round(c_ambiental),
        "c_social":         round(c_social),
        "p_justo":          p_justo,
        "vida_util_meses":  vida_util,
        "transparencia_pct": round(empresa["transparencia"] * 100),
        "nivel":            _badge(empresa["transparencia"]),
    }


def run_all(material_key: str, prenda_key: str) -> list[dict]:
    """
    Corre el pipeline completo para todas las empresas.

    Args:
        material_key: clave de MATERIALES (e.g. "poliester")
        prenda_key:   clave de PRENDAS    (e.g. "playera")

    Returns:
        Lista de resultados ordenada de mayor a menor P_justo.
    """
    if material_key not in MATERIALES:
        raise ValueError(f"Material '{material_key}' no encontrado. Opciones: {list(MATERIALES)}")
    if prenda_key not in PRENDAS:
        raise ValueError(f"Prenda '{prenda_key}' no encontrada. Opciones: {list(PRENDAS)}")

    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]

    resultados = [calcular_precio_justo(e, mat, pre) for e in EMPRESAS]
    return sorted(resultados, key=lambda x: x["p_justo"], reverse=True)
