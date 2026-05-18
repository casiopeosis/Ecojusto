# algoritmo/social.py
# Módulo 3 — Costo social via Teoría de Juegos (Dilema del Prisionero Repetido)
#
# La relación empresa–maquiladora se modela como un juego donde la estrategia
# dominante en equilibrio de Nash estático es la explotación laboral.
# C_social estima la penalización financiera necesaria para que cooperar sea
# la estrategia dominante (el costo de "estabilización social").
#
# Fundamento: Teoría de Juegos, Dilema del Prisionero (Nash, 1950)
# Referencia del temario: Clases 23 y 24
#
# CAMBIOS v2:
# - El factor de riesgo país ya no es un número inventado en db.py.
#   Ahora se consulta en tiempo real desde la API del Banco Mundial
#   via data/world_bank.py, combinando:
#     · SL.EMP.VULN.ZS — % trabajadores vulnerables
#     · SL.UEM.TOTL.ZS — % desempleo total
#   Con fallback automático si la API no responde.

from data.world_bank import get_factor_riesgo_pais


def calcular_c_social(empresa: dict, prenda: dict) -> tuple[float, float]:
    """
    Estima el costo de estabilización social: la transferencia monetaria
    necesaria para alterar la matriz de pagos del juego empresa–maquiladora
    de modo que el salario digno sea el equilibrio dominante.

    Fórmula:
        C_social = precio_base × factor_riesgo_país × brecha_salarial_OIT

    Donde:
      - precio_base:           precio fijo de la prenda (no el de etiqueta,
                               para evitar circularidad — empresa más barata
                               no tiene menor deuda social)
      - factor_riesgo_país:    índice [0.3, 2.0] calculado desde indicadores
                               laborales reales del Banco Mundial para el
                               país principal de manufactura de la empresa
      - brecha_salarial_OIT:   fracción del precio base que representa la
                               brecha entre salario pagado y salario digno
                               estimado por la OIT para ese sector

    Args:
        empresa: dict con 'iso_pais' (str ISO3)
        prenda:  dict con 'precio_base' (MXN) y 'brecha_oit' (fracción [0, 1])

    Returns:
        (c_social_mxn: float, factor_riesgo: float)
        Se retorna el factor_riesgo también para mostrarlo en el dashboard.
    """
    factor_riesgo = get_factor_riesgo_pais(empresa["iso_pais"])
    c_social = prenda["precio_base"] * factor_riesgo * prenda["brecha_oit"]
    return round(c_social, 2), factor_riesgo
