# algoritmo/social.py  — v4
# CAMBIO PRINCIPAL:
# - La empresa ya no tiene un solo 'iso_pais'.
#   Ahora tiene 'manufactura': {ISO3: fracción} con distribución real.
# - C_social = promedio PONDERADO de la brecha salarial de cada país,
#   según qué porcentaje de la producción ocurre ahí.
#
# Ejemplo Adidas: 27% Vietnam + 19% Indonesia + 16% China + ...
# C_social_Adidas = 0.27 × C_social_VNM + 0.19 × C_social_IDN + ...
#
# Esto refleja que una empresa que fabrica 30% en Bangladesh
# y 20% en México tiene una deuda social intermedia entre ambos países,
# no solo la del país "principal".

# algoritmo/social.py — v4 (Corregido)
from src.data.db import SALARIOS_PAIS, TC_MXN  # <─── Agregar 'src.' aquí
from src.data.world_bank import (
    get_factor_riesgo_pais,
)  # <─── Asegúrate de que este también tenga 'src.'


def _c_social_pais(iso: str, horas_manufactura: float) -> tuple[float, float, float]:
    """
    Calcula el costo social para UN país específico.

    Returns:
        (c_social_mxn, costo_real_mxn, costo_digno_mxn)
    """
    sal = SALARIOS_PAIS.get(
        iso,
        {
            "salario_minimo_usd": 200,
            "salario_digno_usd": 500,
            "horas_mes": 200,
        },
    )

    horas_mes = sal["horas_mes"]
    sal_minimo_hora = sal["salario_minimo_usd"] / horas_mes
    sal_digno_hora = sal["salario_digno_usd"] / horas_mes

    costo_real_usd = sal_minimo_hora * horas_manufactura
    costo_digno_usd = sal_digno_hora * horas_manufactura

    factor_riesgo = get_factor_riesgo_pais(iso)
    brecha_usd = max(0.0, costo_digno_usd - costo_real_usd)
    c_social_mxn = round(brecha_usd * factor_riesgo * TC_MXN, 2)

    return (
        c_social_mxn,
        round(costo_real_usd * TC_MXN, 2),
        round(costo_digno_usd * TC_MXN, 2),
    )


def calcular_c_social(
    empresa: dict,
    prenda: dict,
) -> tuple[float, float, float, float, dict]:
    """
    Calcula el C_social como promedio PONDERADO por distribución de manufactura.

    Args:
        empresa: dict con 'manufactura' {ISO3: fracción} y 'nombre'
        prenda:  dict con 'horas_manufactura'

    Returns:
        (c_social_ponderado, costo_real_ponderado, costo_digno_ponderado,
         factor_riesgo_promedio, desglose_por_pais)

    desglose_por_pais: {ISO3: {c_social, fraccion, pais_nombre}} — para el dashboard
    """
    manufactura = empresa["manufactura"]
    horas_manufactura = prenda["horas_manufactura"]

    c_social_total = 0.0
    costo_real_total = 0.0
    costo_digno_total = 0.0
    factor_prom = 0.0
    desglose = {}

    for iso, fraccion in manufactura.items():
        c_s, c_r, c_d = _c_social_pais(iso, horas_manufactura)
        factor = get_factor_riesgo_pais(iso)
        sal = SALARIOS_PAIS.get(iso, {})

        c_social_total += c_s * fraccion
        costo_real_total += c_r * fraccion
        costo_digno_total += c_d * fraccion
        factor_prom += factor * fraccion

        desglose[iso] = {
            "pais_nombre": sal.get("pais_nombre", iso),
            "fraccion_pct": round(fraccion * 100),
            "c_social": round(c_s, 2),
            "factor_riesgo": factor,
            "sal_minimo_usd": sal.get("salario_minimo_usd", "?"),
            "sal_digno_usd": sal.get("salario_digno_usd", "?"),
        }

    return (
        round(c_social_total, 2),
        round(costo_real_total, 2),
        round(costo_digno_total, 2),
        round(factor_prom, 2),
        desglose,
    )
