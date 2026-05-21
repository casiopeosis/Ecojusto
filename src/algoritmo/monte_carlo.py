# algoritmo/monte_carlo.py — v2 (REDISEÑADO)
# ════════════════════════════════════════════════════════════════════════════════
#
# DIAGNÓSTICO v1 (bug):
#   El umbral_co2 era idéntico para todas las empresas (~22.74 MXN/kg) porque
#   el código calculaba np.percentile(co2_ordenados_por_p_justo, 90), que
#   equivale al P90 de Uniform(3.5, 25) = 22.85 — una constante de distribución,
#   no una propiedad de la empresa.
#
# REDISEÑO v2:
#   Pregunta real: "Si el precio del bono de carbono subiera, ¿cuánto MXN
#   adicional debería costar la prenda de CADA marca para ser ambientalmente
#   honesta?"
#
#   Variables estocásticas:
#     • Precio CO₂: Uniform(3.5, 200) MXN/kg
#       Rango cubre desde precio actual MX hasta escenarios IPCC 2°C
#     • Precio agua: Normal(0.25, σ=0.08) MXN/L (incertidumbre metodológica LCA)
#     • Tasa crecimiento consumo: Normal(1.0, σ=0.05) por año
#       Refleja que el consumo de fast fashion puede subir o bajar
#
#   KPI diferenciado por empresa:
#     co2_breakeven: precio CO₂ donde el c_co2_solo iguala X% del precio etiqueta
#     sensibilidad: Δc_co2 / Δprecio_co2 (MXN/prenda por MXN/kg_CO2)
#     — Esta métrica SÍ varía por empresa (depende de vida_util y transparencia)

import numpy as np
import src.algoritmo.markov as markov_mod
from src.data.db import MATERIALES, PRENDAS, EMPRESAS, COSTO_CO2_MXN_POR_KG, COSTO_AGUA_MXN_POR_LT
from src.algoritmo.markov import calcular_c_ambiental


# Rango de precios CO₂ basado en escenarios IPCC / política climática
CO2_PRECIO_MIN = 3.50    # MXN/kg — precio actual bonos voluntarios México
CO2_PRECIO_MAX = 200.0   # MXN/kg — ~$10 USD/kg, extremo escenario 1.5°C (IPCC AR6)
CO2_PRECIO_REFERENCIA_PARIS = 35.0  # MXN/kg — ~$2 USD/kg objetivo Acuerdo de París


def simular_sensibilidad_co2(
    empresa_nombre: str,
    material_key: str,
    prenda_key: str,
    n_simulaciones: int = 2000,
    seed: int | None = None,
) -> dict:
    """
    Simula la exposición al riesgo de precio de carbono para UNA empresa específica.

    Para cada escenario i:
        c_co2_i = co2_kg_prenda × factor_reposicion × precio_co2_i
        c_agua_i = agua_litros_prenda × factor_reposicion × precio_agua_i
        Δcosto_ambiental_i = (c_co2_i + c_agua_i) vs. base actual

    KPI principal: co2_breakeven_precio
        El precio del bono de carbono donde el COSTO AMBIENTAL SOLO (c_co2)
        supera el X% del precio de etiqueta (umbral_pct configurable).
        ESTE VALOR SÍ VARÍA POR EMPRESA (depende de vida_util/factor_reposicion).
    """
    rng = np.random.default_rng(seed)

    empresa = next((e for e in EMPRESAS if e["nombre"].lower() == empresa_nombre.lower()), None)
    if not empresa:
        raise ValueError(f"Empresa '{empresa_nombre}' no encontrada.")

    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]
    precio_etiqueta = empresa["precios"][prenda_key]

    # ─── Métricas base (precio CO2 actual) ───────────────────────────────────
    markov_mod.COSTO_CO2_MXN_POR_KG = COSTO_CO2_MXN_POR_KG
    markov_mod.COSTO_AGUA_MXN_POR_LT = COSTO_AGUA_MXN_POR_LT
    vida_util_base, c_amb_base, c_agua_base, c_co2_base = calcular_c_ambiental(
        empresa["transparencia"], mat, prenda_key
    )

    # Sensibilidad analítica: Δc_co2 / Δprecio_co2
    # c_co2 = co2_kg * factor_reposicion * precio_co2
    # → sensibilidad = c_co2_base / COSTO_CO2_MXN_POR_KG
    sensibilidad_co2 = c_co2_base / max(COSTO_CO2_MXN_POR_KG, 1e-9)  # MXN por MXN/kg_CO2

    # ─── Vectores estocásticos ────────────────────────────────────────────────
    sim_precio_co2 = rng.uniform(CO2_PRECIO_MIN, CO2_PRECIO_MAX, n_simulaciones)
    sim_precio_agua = np.clip(
        rng.normal(COSTO_AGUA_MXN_POR_LT, COSTO_AGUA_MXN_POR_LT * 0.30, n_simulaciones),
        0.05, 1.20
    )

    # ─── Calcular c_ambiental para cada escenario ─────────────────────────────
    # Usamos la relación lineal analítica para evitar 2000 llamadas a calcular_c_ambiental:
    #   c_co2(precio) = sensibilidad_co2 × precio
    #   c_agua(precio_agua) = (c_agua_base / COSTO_AGUA_MXN_POR_LT) × precio_agua
    sensibilidad_agua = c_agua_base / max(COSTO_AGUA_MXN_POR_LT, 1e-9)

    c_co2_sim = sensibilidad_co2 * sim_precio_co2
    c_agua_sim = sensibilidad_agua * sim_precio_agua
    c_ambiental_sim = c_co2_sim + c_agua_sim

    # Δ sobre el base actual
    delta_ambiental_sim = c_ambiental_sim - c_amb_base

    # ─── KPI 1: co2_breakeven (precio CO2 donde c_co2 solo = umbral del precio etiqueta) ─
    # Umbral = 10% del precio de etiqueta (umbral razonable de 'impacto material')
    umbral_10pct = precio_etiqueta * 0.10
    umbral_25pct = precio_etiqueta * 0.25
    umbral_50pct = precio_etiqueta * 0.50

    co2_break_10pct = umbral_10pct / max(sensibilidad_co2, 1e-9)
    co2_break_25pct = umbral_25pct / max(sensibilidad_co2, 1e-9)
    co2_break_50pct = umbral_50pct / max(sensibilidad_co2, 1e-9)

    # ─── KPI 2: % escenarios donde c_ambiental > precio_etiqueta ─────────────
    pct_c_amb_supera_etiqueta = float(np.mean(c_ambiental_sim > precio_etiqueta)) * 100

    # ─── KPI 3: distribución de precios CO₂ críticos (escenarios "materiales") ─
    # % escenarios donde delta_ambiental > 10% / 25% / 50% de la etiqueta
    pct_impacto_10 = float(np.mean(delta_ambiental_sim > precio_etiqueta * 0.10)) * 100
    pct_impacto_25 = float(np.mean(delta_ambiental_sim > precio_etiqueta * 0.25)) * 100
    pct_impacto_50 = float(np.mean(delta_ambiental_sim > precio_etiqueta * 0.50)) * 100

    # ─── Curva de sensibilidad (para gráfica de líneas) ──────────────────────
    precios_curva = np.linspace(CO2_PRECIO_MIN, CO2_PRECIO_MAX, 80).tolist()
    c_co2_curva = [sensibilidad_co2 * p for p in precios_curva]
    c_ambiental_curva = [
        sensibilidad_co2 * p + sensibilidad_agua * COSTO_AGUA_MXN_POR_LT
        for p in precios_curva
    ]

    return {
        # Identidad
        "empresa": empresa_nombre,
        "transparencia_pct": round(empresa["transparencia"] * 100),
        "material": mat["label"],
        "prenda": pre["label"],
        "precio_etiqueta": precio_etiqueta,
        "vida_util_meses": vida_util_base,
        # Base ambiental actual
        "c_co2_base": round(c_co2_base, 2),
        "c_agua_base": round(c_agua_base, 2),
        "c_ambiental_base": round(c_amb_base, 2),
        "pct_ambiental_vs_etiqueta": round(c_amb_base / max(precio_etiqueta, 1) * 100, 1),
        # Sensibilidad analítica (diferenciador real por empresa)
        "sensibilidad_co2_mxn_por_mxn_kg": round(sensibilidad_co2, 3),
        # Breakeven prices (donde el impacto CO2 se vuelve "material")
        "co2_breakeven_10pct_etiqueta": round(co2_break_10pct, 2),
        "co2_breakeven_25pct_etiqueta": round(co2_break_25pct, 2),
        "co2_breakeven_50pct_etiqueta": round(co2_break_50pct, 2),
        # Escenarios estocásticos
        "n_simulaciones": n_simulaciones,
        "pct_c_ambiental_supera_etiqueta": round(pct_c_amb_supera_etiqueta, 1),
        "pct_impacto_mayor_10pct": round(pct_impacto_10, 1),
        "pct_impacto_mayor_25pct": round(pct_impacto_25, 1),
        "pct_impacto_mayor_50pct": round(pct_impacto_50, 1),
        # Distribuciones para histograma
        "sim_c_ambiental": c_ambiental_sim.tolist(),
        "sim_delta_ambiental": delta_ambiental_sim.tolist(),
        "sim_precio_co2": sim_precio_co2.tolist(),
        # Curva de sensibilidad para gráfica de líneas
        "precios_curva": precios_curva,
        "c_co2_curva": c_co2_curva,
        "c_ambiental_curva": c_ambiental_curva,
        # Umbrales de referencia para anotaciones
        "co2_precio_paris": CO2_PRECIO_REFERENCIA_PARIS,
        "co2_precio_actual": COSTO_CO2_MXN_POR_KG,
    }


def comparar_sensibilidad_todas(
    material_key: str,
    prenda_key: str,
    n_simulaciones: int = 1000,
) -> list[dict]:
    """
    Corre simular_sensibilidad_co2 para TODAS las empresas.
    Retorna lista ordenada por sensibilidad_co2 (mayor a menor).
    """
    resultados = []
    for e in EMPRESAS:
        try:
            r = simular_sensibilidad_co2(e["nombre"], material_key, prenda_key, n_simulaciones)
            resultados.append(r)
        except Exception:
            continue
    return sorted(resultados, key=lambda x: x["sensibilidad_co2_mxn_por_mxn_kg"], reverse=True)


# ─── Mantener la función original con nombre legacy para compatibilidad ───────
def simular_umbrales_co2(empresa_nombre, material_key, prenda_key, n_simulaciones=2000):
    """Wrapper legacy — redirige al nuevo método."""
    r = simular_sensibilidad_co2(empresa_nombre, material_key, prenda_key, n_simulaciones)
    # Mantener las claves que usa el tab CO2 original en app.py
    return {
        **r,
        "umbral_co2_percentil_90": r["co2_breakeven_25pct_etiqueta"],
        "pct_escenarios_insostenible": r["pct_impacto_mayor_25pct"],
        "historico_precios_justos": r["sim_c_ambiental"],
        "precio_etiqueta": r["precio_etiqueta"],
        "p_justo_promedio": round(r["c_ambiental_base"]),
    }