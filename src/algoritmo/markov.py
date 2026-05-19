# algoritmo/markov.py  — v3
# Módulo 2 — Costo ambiental via Cadena de Markov + huellas reales
#
# CAMBIOS v3:
# - C_ambiental ya no usa un 'costo_remediacion' inventado.
#   Ahora se calcula desde métricas reales LCA:
#     · Huella hídrica (litros/kg) × peso prenda × costo tratamiento agua
#     · Huella de carbono (kg CO₂/kg) × peso prenda × precio bono carbono
# - El ciclo de Markov sigue determinando la vida útil para ponderar
#   el costo: prenda que dura menos → más frecuencia de reposición →
#   mayor huella acumulada → mayor C_ambiental por ciclo de uso.

import numpy as np
from data.db import COSTO_CO2_MXN_POR_KG, COSTO_AGUA_MXN_POR_LT

# Probabilidad de ir directo al Basurero desde estado Activo por ciclo,
# por material. Refleja durabilidad intrínseca independiente de la empresa.
# Fuente: Ellen MacArthur Foundation "A New Textiles Economy" 2017, p.38
PROB_BASURERO_BASE = {
    "poliester":    0.73,
    "algodon_conv": 0.57,
    "algodon_org":  0.40,
    "lana":         0.25,
    "viscosa":      0.65,
}

PROB_BASURERO_SEGUNDA_MANO = {
    "poliester":    0.80,
    "algodon_conv": 0.65,
    "algodon_org":  0.50,
    "lana":         0.35,
    "viscosa":      0.75,
}


def calcular_c_ambiental(
    transparencia: float,
    material: dict,
    prenda_key: str,
) -> tuple[float, float, float, float]:
    """
    Calcula la vida útil esperada (Markov) y el costo ambiental real por prenda.

    El costo ambiental se descompone en:
      C_agua = huella_hidrica_litros_kg × peso_prenda × COSTO_AGUA / vida_util
      C_co2  = co2_kg_por_kg_fibra × peso_prenda × COSTO_CO2 / vida_util

    Dividir por vida_util_meses normaliza el costo al ciclo de uso:
    una prenda que dura 2 meses genera el doble de huella acumulada que
    una que dura 4, porque hay que reponerla el doble de veces.

    Args:
        transparencia: índice FTI normalizado [0,1]
        material:      dict con huella_hidrica, co2, peso_prenda_kg, etc.
        prenda_key:    clave de prenda para buscar el peso correcto

    Returns:
        (vida_util_meses, c_ambiental_total, c_agua, c_co2)
    """
    calidad = 0.5 + transparencia * 0.5

    mat_key   = material.get("key", "algodon_conv")
    p_base    = PROB_BASURERO_BASE.get(mat_key, 0.60)
    p_2a_mano = PROB_BASURERO_SEGUNDA_MANO.get(mat_key, 0.70)

    factor_calidad = (calidad - 0.5) / 0.5
    p_basurero = round(min(max(p_base * (1 - factor_calidad * 0.40), 0.05), 0.95), 4)
    p_activo   = max(0.01, 0.95 - p_basurero)
    p_segunda  = 1.0 - p_basurero - p_activo

    Q = np.array([
        [p_activo,               p_segunda],
        [0.00,                   max(0.01, 1.0 - p_2a_mano)],
    ])
    F = np.linalg.inv(np.eye(2) - Q)
    vida_util = round(float((F @ np.ones(2))[0]), 1)

    # Peso de la prenda en este material
    peso_kg = material["peso_prenda_kg"].get(prenda_key, 0.30)

    # Costos de remediación ambiental reales
    agua_total = material["huella_hidrica_litros_kg"] * peso_kg
    co2_total  = material["co2_kg_por_kg_fibra"] * peso_kg

    c_agua = round((agua_total * COSTO_AGUA_MXN_POR_LT) / max(vida_util, 0.1), 2)
    c_co2  = round((co2_total  * COSTO_CO2_MXN_POR_KG)  / max(vida_util, 0.1), 2)
    c_ambiental = round(c_agua + c_co2, 2)

    return vida_util, c_ambiental, c_agua, c_co2
