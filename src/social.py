# algoritmo/social.py
# Módulo 3 — Costo social via Teoría de Juegos (Dilema del Prisionero Repetido)
#
# La relación empresa–maquiladora se modela como un juego donde la estrategia
# dominante en equilibrio de Nash estático es la explotación laboral.
# C_social estima la penalización financiera necesaria para que cooperar sea
# la estrategia dominante, es decir, el costo de "estabilización social".


def calcular_c_social(empresa: dict, prenda: dict) -> float:
    """
    Estima el costo de estabilización social: la transferencia monetaria
    necesaria para alterar la matriz de pagos del juego empresa–maquiladora
    de modo que el salario digno sea el equilibrio dominante.

    Fórmula:
        C_social = precio_base × factor_riesgo_país × brecha_salarial_OIT

    Se usa precio_base (no precio de etiqueta) para evitar circularidad:
    una empresa que vende más barato no tiene menor deuda social.

    Args:
        empresa: dict con 'pais_riesgo' (float, índice CSI, rango ~[0.3, 1.8])
        prenda:  dict con 'precio_base' (MXN) y 'brecha_oit' (fracción [0, 1])

    Returns:
        c_social en MXN (float)
    """
    c_social = prenda["precio_base"] * empresa["pais_riesgo"] * prenda["brecha_oit"]
    return round(c_social, 2)
