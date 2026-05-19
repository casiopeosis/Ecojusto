# algoritmo/ensamblaje.py  — v4
# CAMBIO: calcular_c_social ahora retorna 5 valores incluyendo desglose por país.

from data.db import EMPRESAS, MATERIALES, PRENDAS, MARGEN_REINVERSION_DEFAULT
from algoritmo.opacidad import calcular_alpha
from algoritmo.markov import calcular_c_ambiental
from algoritmo.social import calcular_c_social


def _badge(transparencia: float) -> str:
    if transparencia >= 0.70:
        return "alta"
    elif transparencia >= 0.40:
        return "media"
    return "baja"


def _veredicto(precio_etiqueta: float, p_justo: float) -> str:
    ratio = precio_etiqueta / max(p_justo, 1)
    if ratio < 0.60:    return "externaliza"
    elif ratio < 0.90:  return "subestimado"
    elif ratio <= 1.15: return "alineado"
    elif ratio <= 1.50: return "margen_alto"
    else:               return "sobreprecio"


def calcular_precio_justo(
    empresa: dict,
    material: dict,
    prenda: dict,
    prenda_key: str,
    margen: float = MARGEN_REINVERSION_DEFAULT,
) -> dict:
    alpha                                           = calcular_alpha(empresa["transparencia"])
    vida_util, c_ambiental, c_agua, c_co2          = calcular_c_ambiental(empresa["transparencia"], material, prenda_key)
    c_social, c_lab_real, c_lab_digno, factor_prom, desglose = calcular_c_social(empresa, prenda)

    precio_etiqueta       = empresa["precios"][prenda_key]
    costo_base            = c_lab_digno + c_ambiental + c_social
    penalizacion_opacidad = round((alpha - 1) * costo_base, 2)
    p_justo               = round(alpha * costo_base * (1 + margen))
    brecha                = precio_etiqueta - p_justo

    # País principal = el de mayor fracción de manufactura
    pais_principal = max(empresa["manufactura"], key=empresa["manufactura"].get)

    return {
        "empresa":               empresa["nombre"],
        "pais_principal":        pais_principal,
        "n_paises":              len(empresa["manufactura"]),
        "transparencia_pct":     round(empresa["transparencia"] * 100),
        "nivel":                 _badge(empresa["transparencia"]),
        "precio_etiqueta":       precio_etiqueta,
        "p_justo":               p_justo,
        "brecha":                brecha,
        "veredicto":             _veredicto(precio_etiqueta, p_justo),
        "c_laboral_digno":       round(c_lab_digno),
        "c_laboral_real":        round(c_lab_real),
        "c_ambiental":           round(c_ambiental),
        "c_agua":                round(c_agua),
        "c_co2":                 round(c_co2),
        "c_social":              round(c_social),
        "penalizacion_opacidad": round(penalizacion_opacidad),
        "margen_reinversion":    round(alpha * costo_base * margen),
        "alpha_e":               round(alpha, 2),
        "vida_util_meses":       vida_util,
        "factor_riesgo_prom":    factor_prom,
        "desglose_paises":       desglose,   # dict por ISO3 para el dashboard
    }


def run_all(
    material_key: str,
    prenda_key: str,
    margen: float = MARGEN_REINVERSION_DEFAULT,
) -> list[dict]:
    if material_key not in MATERIALES:
        raise ValueError(f"Material '{material_key}' no encontrado.")
    if prenda_key not in PRENDAS:
        raise ValueError(f"Prenda '{prenda_key}' no encontrada.")

    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]

    resultados = [calcular_precio_justo(e, mat, pre, prenda_key, margen) for e in EMPRESAS]
    return sorted(resultados, key=lambda x: x["brecha"])
