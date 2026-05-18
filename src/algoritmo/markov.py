# algoritmo/markov.py
# Módulo 2 — Costo ambiental via Cadena de Markov Absorbente
#
# Estados: {Activo, Segunda Mano, Basurero}. "Basurero" es el único estado absorbente.
# Tiempo esperado hasta absorción: t = (I - Q)^{-1} · 1  (Matriz Fundamental de Kemeny)
#
# Fundamento: Cadenas de Markov absorbentes (Kemeny & Snell, 1960)
# Referencia del temario: Clases 20, 21 y 22
#
# CAMBIOS v2:
# - La matriz de transición Q ahora varía de forma INDEPENDIENTE por:
#     (a) material — probabilidad de desecho base según literatura científica
#     (b) empresa  — calidad de manufactura (proxy del índice FTI)
#   Antes solo variaba por empresa, lo que ignoraba que el poliéster se
#   degrada mucho más rápido que la lana independientemente de quién lo fabrique.
#
# Fuente probabilidades por material:
#   Ellen MacArthur Foundation, "A New Textiles Economy", 2017, p. 38
#   https://ellenmacarthurfoundation.org/a-new-textiles-economy

import numpy as np

# Probabilidad de ir directamente al Basurero desde estado Activo por ciclo,
# específica para cada material. Refleja durabilidad intrínseca del material,
# independiente de la empresa que lo manufacture.
#
# Interpretación: un valor de 0.73 significa que en cada ciclo de uso,
# el 73% de las prendas de ese material terminan desechadas (no reparadas
# ni revendidas), asumiendo manufactura promedio.
PROB_BASURERO_BASE: dict[str, float] = {
    "poliester":    0.73,   # degrada rápido, no biodegradable, baja tasa de reciclaje
    "algodon_conv": 0.57,   # más durable, pero cultivo intensivo en agua
    "algodon_org":  0.40,   # mayor calidad de fibra, más durable
    "lana":         0.25,   # muy durable, mercado de segunda mano activo
    "viscosa":      0.65,   # fibra semisintética, baja durabilidad
}

# Probabilidad de ir al Basurero desde Segunda Mano (constante por material —
# una vez en segunda mano, la probabilidad de desecho no depende del fabricante)
PROB_BASURERO_SEGUNDA_MANO: dict[str, float] = {
    "poliester":    0.80,
    "algodon_conv": 0.65,
    "algodon_org":  0.50,
    "lana":         0.35,
    "viscosa":      0.75,
}


def calcular_c_ambiental(transparencia: float, material: dict) -> tuple[float, float]:
    """
    Estima la vida útil esperada de la prenda (meses) y el costo ambiental
    por ciclo de reposición acortado.

    La calidad de manufactura se aproxima linealmente desde el índice FTI:
        calidad ∈ [0.5, 1.0]
        0.5 = empresa muy opaca → manufactura mínima
        1.0 = empresa totalmente transparente → manufactura óptima

    La calidad de manufactura reduce la probabilidad de desecho prematuro
    hasta un 40% respecto a la base del material:
        p_basurero_ajustada = p_base × (1 − (calidad − 0.5) × 0.4 / 0.5)

    Ejemplo:
        Poliéster (p_base=0.73) + Shein (calidad=0.525):
            p_ajustada = 0.73 × (1 − 0.025×0.8) ≈ 0.715  → vida corta
        Poliéster (p_base=0.73) + Patagonia (calidad=0.96):
            p_ajustada = 0.73 × (1 − 0.46×0.8) ≈ 0.461   → más durable

    Args:
        transparencia: índice FTI normalizado en [0, 1]
        material:      dict con keys 'key', 'vida_base', 'costo_remediacion'

    Returns:
        (vida_util_meses: float, c_ambiental_mxn: float)
    """
    calidad = 0.5 + transparencia * 0.5   # mapeo lineal [0,1] → [0.5, 1.0]

    mat_key = material.get("key", "algodon_conv")

    # Probabilidad base de desecho por material
    p_base    = PROB_BASURERO_BASE.get(mat_key, 0.60)
    p_2a_mano = PROB_BASURERO_SEGUNDA_MANO.get(mat_key, 0.70)

    # Ajuste por calidad de manufactura de la empresa
    # calidad en [0.5, 1.0] → factor_calidad en [0, 1]
    factor_calidad = (calidad - 0.5) / 0.5
    p_basurero = p_base * (1 - factor_calidad * 0.40)
    p_basurero = round(min(max(p_basurero, 0.05), 0.95), 4)

    # Probabilidad de permanecer Activo o pasar a Segunda Mano
    p_activo      = max(0.01, 0.95 - p_basurero)
    p_segunda     = 1.0 - p_basurero - p_activo

    p_segunda_mano_remain = max(0.01, 1.0 - p_2a_mano)

    # Submatriz Q de estados transitorios (Activo, Segunda Mano)
    Q = np.array([
        [p_activo,              p_segunda],
        [0.00,                  p_segunda_mano_remain],
    ])

    I = np.eye(2)
    F = np.linalg.inv(I - Q)   # Matriz Fundamental: F = (I − Q)⁻¹
    t = F @ np.ones(2)          # Número esperado de pasos hasta absorción

    # t[0]: tiempo esperado desde estado Activo (prenda nueva)
    vida_util_meses = round(float(t[0]), 1)

    # A menor vida útil → mayor frecuencia de reposición → mayor costo ambiental
    c_ambiental = round(material["costo_remediacion"] / max(vida_util_meses, 0.1), 2)

    return vida_util_meses, c_ambiental
