# algoritmo/monte_carlo_hidrico.py — v1
# ════════════════════════════════════════════════════════════════════════════════
# Módulo Monte Carlo — Simulación de Agotamiento Hídrico Acumulado
#
# Pregunta central:
#   Si el salón compra X prendas de algodón al año, ¿cuántos años tarda
#   en equivaler al consumo anual de agua de la CDMX?
#
# Variables estocásticas:
#   • Huella hídrica por kg de fibra: distribución Normal (media=db, σ=30%)
#     Refleja incertidumbre en metodologías LCA y variaciones de cultivo/año
#   • Prendas compradas por persona/año: distribución Normal (media=input, σ=25%)
#     Refleja heterogeneidad de consumo dentro del grupo

import numpy as np
from src.data.db import MATERIALES, PRENDAS

# ─── Referencia urbana ───────────────────────────────────────────────────────
# Consumo anual de agua potable CDMX ≈ 1,100 millones de m³/año
# Fuente: SACMEX / Reporte Anual 2023
CDMX_LITROS_AÑO = 1.1e12

# Ciudades de referencia para comparativa (litros/año)
CIUDADES_REFERENCIA = {
    "CDMX": 1.1e12,
    "Guadalajara": 3.8e11,
    "Monterrey": 3.2e11,
    "Puebla": 2.1e11,
    "Ciudad del Cabo": 2.5e11,
}


def simular_huella_hidrica(
    material_key: str,
    prenda_key: str,
    n_personas: int = 30,
    prendas_por_persona: float = 25.0,
    anos: int = 15,
    n_sim: int = 2000,
    seed: int | None = None,
) -> dict:
    """
    Simula n_sim trayectorias de consumo hídrico acumulado a lo largo de `anos` años.

    Para cada simulación s y cada año t:
        litros_s_t = n_personas
                     × Nₜ(prendas_por_persona, σ=25%)   [prendas consumidas]
                     × peso_kg
                     × Nₜ(huella_hidrica_L_kg, σ=30%)   [litros por prenda]

    Returns:
        dict con trayectorias (lista de listas), percentiles finales,
        años estimados para equiparar ciudades de referencia,
        y arrays por año para graficar bandas de incertidumbre.
    """
    rng = np.random.default_rng(seed)

    mat = MATERIALES[material_key]
    prenda = PRENDAS[prenda_key]
    peso_kg = mat["peso_prenda_kg"].get(prenda_key, 0.25)
    litros_base = mat["huella_hidrica_litros_kg"]

    # Matrices estocásticas: shape (n_sim, anos)
    # Prendas por persona por año — truncadas a min=1
    prendas_mat = rng.normal(
        loc=prendas_por_persona,
        scale=prendas_por_persona * 0.25,
        size=(n_sim, anos),
    )
    prendas_mat = np.clip(prendas_mat, 1, None)

    # Litros por kg de fibra — truncados a min=50
    litros_mat = rng.normal(
        loc=litros_base,
        scale=litros_base * 0.30,
        size=(n_sim, anos),
    )
    litros_mat = np.clip(litros_mat, 50, None)

    # Consumo anual por simulación (litros)
    consumo_anual = n_personas * prendas_mat * peso_kg * litros_mat  # (n_sim, anos)

    # Consumo acumulado: columna 0 = año 0 = 0
    ceros = np.zeros((n_sim, 1))
    acumulado = np.hstack([ceros, np.cumsum(consumo_anual, axis=1)])  # (n_sim, anos+1)

    # ─── Percentiles por año (para bandas de incertidumbre) ──────────────────
    p10 = np.percentile(acumulado, 10, axis=0).tolist()
    p25 = np.percentile(acumulado, 25, axis=0).tolist()
    p50 = np.percentile(acumulado, 50, axis=0).tolist()
    p75 = np.percentile(acumulado, 75, axis=0).tolist()
    p90 = np.percentile(acumulado, 90, axis=0).tolist()
    p99 = np.percentile(acumulado, 99, axis=0).tolist()

    # ─── Valores finales (año N) ──────────────────────────────────────────────
    finales = acumulado[:, -1]
    p50_final = float(np.percentile(finales, 50))
    p90_final = float(np.percentile(finales, 90))
    p99_final = float(np.percentile(finales, 99))

    # ─── Años equivalentes a ciudades de referencia (P50 y P90) ─────────────
    equivalencias = {}
    for ciudad, vol_anual in CIUDADES_REFERENCIA.items():
        # Interpolación lineal para encontrar año de cruce en la mediana
        cruce_p50 = _anos_hasta_cruce(p50, vol_anual, anos)
        cruce_p90 = _anos_hasta_cruce(p90, vol_anual, anos)
        equivalencias[ciudad] = {
            "vol_litros_año": vol_anual,
            "años_p50": cruce_p50,
            "años_p90": cruce_p90,
        }

    # ─── Submuestra de trayectorias para visualización (máx 500 líneas) ──────
    idx_muestra = rng.choice(n_sim, size=min(500, n_sim), replace=False)
    trayectorias_muestra = acumulado[idx_muestra].tolist()

    return {
        # Identificación
        "material": mat["label"],
        "prenda": prenda["label"],
        "material_key": material_key,
        "prenda_key": prenda_key,
        "n_personas": n_personas,
        "prendas_por_persona": prendas_por_persona,
        "anos": anos,
        "n_sim": n_sim,
        "peso_kg": peso_kg,
        "litros_base_por_kg": litros_base,
        # Trayectorias para el haz de líneas
        "trayectorias_muestra": trayectorias_muestra,
        # Bandas de percentiles por año
        "p10": p10,
        "p25": p25,
        "p50": p50,
        "p75": p75,
        "p90": p90,
        "p99": p99,
        # Valores finales resumen
        "p50_final": p50_final,
        "p90_final": p90_final,
        "p99_final": p99_final,
        # Equivalencias urbanas
        "equivalencias": equivalencias,
        # Porcentaje de simulaciones que superan CDMX al año N
        "pct_supera_cdmx": round(float(np.mean(finales > CDMX_LITROS_AÑO)) * 100, 1),
        # Referencia CDMX (línea recta acumulada para graficar)
        "cdmx_acumulada": [CDMX_LITROS_AÑO * i for i in range(anos + 1)],
        "cdmx_litros_año": CDMX_LITROS_AÑO,
    }


def _anos_hasta_cruce(serie: list, umbral: float, max_anos: int) -> float | None:
    """
    Dado un array de valores acumulados anuales, encuentra el año (interpolado)
    en que la serie cruza el umbral. Retorna None si no cruza dentro del horizonte.
    """
    for i in range(1, len(serie)):
        if serie[i] >= umbral:
            # Interpolación lineal entre año i-1 e i
            frac = (umbral - serie[i - 1]) / max(serie[i] - serie[i - 1], 1e-9)
            return round((i - 1) + frac, 1)
    return None
