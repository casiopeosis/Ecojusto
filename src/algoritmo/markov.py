# algoritmo/markov.py  — v4 (CORREGIDO - FACTOR DE REPOSICIÓN)
# ════════════════════════════════════════════════════════════════════════════════
# Módulo 2 — Costo ambiental via Cadena de Markov + huellas reales de ciclo de uso

import numpy as np
from src.data.db import COSTO_CO2_MXN_POR_KG, COSTO_AGUA_MXN_POR_LT

# Probabilidad de ir directo al Basurero desde estado Activo por ciclo
PROB_BASURERO_BASE = {
    "poliester": 0.73,
    "algodon_conv": 0.57,
    "algodon_org": 0.40,
    "lana": 0.25,
    "viscosa": 0.65,
}

PROB_BASURERO_SEGUNDA_MANO = {
    "poliester": 0.80,
    "algodon_conv": 0.65,
    "algodon_org": 0.50,
    "lana": 0.35,
    "viscosa": 0.75,
}


def calcular_c_ambiental(
    transparencia: float,
    material: dict,
    prenda_key: str,
) -> tuple[float, float, float, float]:
    """
    Calcula la vida útil esperada (Markov) y el costo ambiental real por prenda.

    FIX LOGIC: En lugar de dividir el impacto ecológico inicial (achicándolo),
    utilizamos la vida útil para generar un Factor de Reposición. Una prenda
    con baja vida útil obligará a una recompra acelerada, multiplicando el
    impacto ecológico final en la economía circular.
    """
    calidad = 0.5 + transparencia * 0.5

    mat_key = material.get("key", "algodon_conv")
    p_base = PROB_BASURERO_BASE.get(mat_key, 0.60)
    p_2a_mano = PROB_BASURERO_SEGUNDA_MANO.get(mat_key, 0.70)

    factor_calidad = (calidad - 0.5) / 0.5
    p_basurero = round(min(max(p_base * (1 - factor_calidad * 0.40), 0.05), 0.95), 4)
    p_activo = max(0.01, 0.95 - p_basurero)
    p_segunda = 1.0 - p_basurero - p_activo

    Q = np.array(
        [
            [p_activo, p_segunda],
            [0.00, max(0.01, 1.0 - p_2a_mano)],
        ]
    )
    F = np.linalg.inv(np.eye(2) - Q)
    vida_util = round(float((F @ np.ones(2))[0]), 1)

    # Peso de la prenda en este material
    peso_kg = material["peso_prenda_kg"].get(prenda_key, 0.30)

    # 1. Huellas absolutas de fabricación por prenda (LCA base)
    agua_total = material["huella_hidrica_litros_kg"] * peso_kg
    co2_total = material["co2_kg_por_kg_fibra"] * peso_kg

    # 2. Factor de penalización por obsolescencia rápida
    # Definimos 24 meses como el estándar ideal de durabilidad.
    # Si dura menos de 24 meses, penalizamos proporcionalmente el costo de remediación.
    vida_util_referencia = 24.0
    factor_reposicion = max(1.0, vida_util_referencia / max(vida_util, 0.1))

    # 3. Costos de remediación ambiental escalados con el factor de ciclo de uso
    c_agua = round((agua_total * COSTO_AGUA_MXN_POR_LT) * factor_reposicion, 2)
    c_co2 = round((co2_total * COSTO_CO2_MXN_POR_KG) * factor_reposicion, 2)
    c_ambiental = round(c_agua + c_co2, 2)

    return vida_util, c_ambiental, c_agua, c_co2
