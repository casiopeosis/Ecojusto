# algoritmo/ensamblaje.py
# Pipeline principal — Ensamblaje del Precio Justo
#
# P_justo = α_e · (P_comercial + C_ambiental + C_social)
#
# Corre para todas las empresas en la DB y devuelve resultados ordenados
# de mayor a menor P_justo.
#
# CAMBIOS v2:
# - calcular_c_social ahora retorna (c_social, factor_riesgo) — se desempaqueta aquí.
# - Se agrega 'penalizacion_opacidad' como campo calculado correctamente
#   (antes se calculaba mal en app.py y siempre daba 0).
# - Se agrega 'factor_riesgo_pais' al output para mostrarlo en el dashboard.
# - Se agrega 'iso_pais' al output para el panel de datos por país.

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
    alpha                    = calcular_alpha(empresa["transparencia"])
    vida_util, c_ambiental   = calcular_c_ambiental(empresa["transparencia"], material)
    c_social, factor_riesgo  = calcular_c_social(empresa, prenda)

    base_sin_alpha      = prenda["precio_base"] + c_ambiental + c_social
    penalizacion_opac   = round((alpha - 1) * base_sin_alpha, 2)
    p_justo             = round(alpha * base_sin_alpha)

    return {
        "empresa":               empresa["nombre"],
        "iso_pais":              empresa["iso_pais"],
        "precio_etiqueta":       prenda["precio_base"],
        "alpha_e":               round(alpha, 2),
        "c_ambiental":           round(c_ambiental),
        "c_social":              round(c_social),
        "penalizacion_opacidad": round(penalizacion_opac),
        "p_justo":               p_justo,
        "vida_util_meses":       vida_util,
        "transparencia_pct":     round(empresa["transparencia"] * 100),
        "factor_riesgo_pais":    factor_riesgo,
        "nivel":                 _badge(empresa["transparencia"]),
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
        raise ValueError(
            f"Material '{material_key}' no encontrado. Opciones: {list(MATERIALES)}"
        )
    if prenda_key not in PRENDAS:
        raise ValueError(
            f"Prenda '{prenda_key}' no encontrada. Opciones: {list(PRENDAS)}"
        )

    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]

    resultados = [calcular_precio_justo(e, mat, pre) for e in EMPRESAS]
    return sorted(resultados, key=lambda x: x["p_justo"], reverse=True)
