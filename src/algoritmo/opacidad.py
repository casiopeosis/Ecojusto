# algoritmo/opacidad.py
# Módulo 1 — Penalización por opacidad informacional
# Métrica: Divergencia KL entre distribución ideal de reporte (P) y real de la empresa (Q_e)
#
# Fundamento: Teoría de la Información (Shannon, 1948; Kullback-Leibler, 1951)
# Referencia del temario: Clases 7 y 8

import numpy as np


def calcular_alpha(transparencia: float, gamma: float = 0.3) -> float:
    """
    Calcula el factor multiplicador de penalización α_e basado en la
    Divergencia de Kullback-Leibler entre la distribución ideal de reporte
    y la distribución real de la empresa.

    D_KL(P || Q_e) = P(x) * log(P(x) / Q_e(x))

    Donde:
      P = distribución ideal uniforme (empresa totalmente transparente)
          Proxy: empresa con mayor puntaje en Fashion Transparency Index
      Q_e = distribución real de la empresa, normalizada desde su índice FTI

    Factor de penalización:
      α_e = 1 + γ · D_KL(P || Q_e)

    Si transparencia = 1.0 → D_KL = 0 → α_e = 1.0 (sin penalización)
    Si transparencia = 0.05 → D_KL ≈ 3.0 → α_e ≈ 1.9 (penalización alta)

    Args:
        transparencia: índice FTI normalizado en [0, 1]
        gamma:         parámetro de escala (hiperparámetro, default 0.3)

    Returns:
        α_e ≥ 1.0
    """
    p = 1.0
    q = max(transparencia, 1e-9)   # evitar log(0) cuando transparencia → 0
    dkl = p * np.log(p / q)        # D_KL(P || Q_e)
    return round(1 + gamma * dkl, 4)
