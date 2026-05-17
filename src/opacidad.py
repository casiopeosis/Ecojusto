# algoritmo/opacidad.py
# Módulo 1 — Penalización por opacidad informacional
# Métrica: Divergencia KL entre distribución ideal de reporte (P) y real de la empresa (Q_e)

import numpy as np


def calcular_alpha(transparencia: float, gamma: float = 0.3) -> float:
    """
    Calcula el factor multiplicador de penalización α_e basado en la
    Divergencia de Kullback-Leibler entre la distribución ideal de reporte
    y la distribución real de la empresa.

    La distribución ideal P es uniforme sobre todas las dimensiones evaluadas
    por el Fashion Transparency Index (FTI). Una empresa con transparencia = 1.0
    no recibe penalización (α_e = 1.0). A menor transparencia, mayor D_KL y
    mayor multiplicador.

    Args:
        transparencia: índice FTI normalizado en [0, 1]
        gamma:         parámetro de escala (hiperparámetro de diseño, default 0.3)

    Returns:
        α_e ≥ 1.0
    """
    p = 1.0
    q = max(transparencia, 1e-9)  # evitar log(0) cuando transparencia → 0
    dkl = p * np.log(p / q)       # D_KL(P || Q_e) con P = distribución ideal uniforme
    return round(1 + gamma * dkl, 4)
