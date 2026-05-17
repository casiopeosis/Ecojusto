# algoritmo/markov.py
# Módulo 2 — Costo ambiental via Cadena de Markov Absorbente
# Estados: {Activo, Segunda Mano, Basurero}. "Basurero" es el único estado absorbente.
# Tiempo esperado hasta absorción: t = (I - Q)^{-1} · 1  (Matriz Fundamental de Kemeny)

import numpy as np


def calcular_c_ambiental(transparencia: float, material: dict) -> tuple[float, float]:
    """
    Estima la vida útil esperada de la prenda (en meses) y el costo ambiental
    anualizado por ciclo de reposición acortado.

    La calidad de manufactura se aproxima linealmente con el índice FTI:
        calidad ∈ [0.5, 1.0]   (empresa opaca → calidad mínima 0.5)

    La matriz de transición Q sobre los estados transitorios {Activo, Segunda Mano}
    escala con la calidad: mejor manufactura → menor probabilidad de ir al basurero
    en cada paso.

    Args:
        transparencia: índice FTI normalizado en [0, 1]
        material:      dict con keys:
                         'vida_base'         (int, meses de referencia)
                         'costo_remediacion' (int, MXN por ciclo de remediación)

    Returns:
        (vida_util_meses, c_ambiental_mxn)
    """
    # Proxy de calidad de manufactura a partir del índice de transparencia
    calidad = 0.5 + transparencia * 0.5  # mapeo lineal: [0,1] → [0.5, 1.0]

    # Submatriz Q de estados transitorios (Activo, Segunda Mano)
    # Las probabilidades de permanecer en cada estado escalan con la calidad
    Q = np.array([
        [0.20 * calidad, 0.10],           # desde Activo
        [0.00,           0.30 * calidad], # desde Segunda Mano
    ])

    I = np.eye(2)
    F = np.linalg.inv(I - Q)  # Matriz Fundamental: F = (I - Q)^{-1}
    t = F @ np.ones(2)         # Número esperado de pasos hasta absorción

    # t[0]: tiempo esperado desde estado Activo (el relevante para una prenda nueva)
    vida_util_meses = round(t[0], 1)

    # A menor vida útil → mayor frecuencia de reposición → mayor costo ambiental acumulado
    c_ambiental = round(material["costo_remediacion"] / vida_util_meses, 2)

    return vida_util_meses, c_ambiental
