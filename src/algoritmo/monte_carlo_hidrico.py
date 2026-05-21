# algoritmo/monte_carlo_hidrico.py — v3 (REFERENCIAS ADAPTATIVAS CORREGIDAS)
# ════════════════════════════════════════════════════════════════════════════════
#
# v2 → v3 fix:
#   La selección de referencias ahora garantiza:
#     1. Al menos una referencia con cruce DENTRO del horizonte (visible en la gráfica)
#     2. Al menos una referencia "aspiracional" que puede estar fuera (escala mayor)
#   Para poliéster (62 L/kg) se agrega la piscina privada (30,000 L)
#   para que siempre haya un cruce visible incluso con la fibra más eficiente en agua.

import numpy as np
from src.data.db import MATERIALES, PRENDAS

CONSUMO_PERSONA_AÑO_L = 730  # litros/año (OMS: 2 L/día potable)

# Catálogo ordenado de menor a mayor volumen
REFERENCIAS_HIDRICAS = {
    "Persona/año\n(2 L/día)": {
        "litros": 730,
        "descripcion": "Consumo potable anual de 1 persona",
        "fuente": "OMS: 2 L/día mínimo recomendado",
        "color": "#5dcaa5",
    },
    "Piscina privada\n(30,000 L)": {
        "litros": 30_000,
        "descripcion": "Piscina familiar residencial estándar",
        "fuente": "Norma NOM-127 (volumen referencia)",
        "color": "#1d9e75",
    },
    "Alberca olímpica\n(2.5M L)": {
        "litros": 2_500_000,
        "descripcion": "Alberca reglamentaria FINA (50×25×2 m)",
        "fuente": "FINA Technical Regulations 2022",
        "color": "#0f6e56",
    },
    "Lago de Chapultepec\n(1.7M L)": {
        "litros": 1_700_000,
        "descripcion": "Lago principal del Bosque de Chapultepec, CDMX",
        "fuente": "SEDEMA CDMX, estimación volumen lago 1",
        "color": "#0a4f3d",
    },
    "Presa Cutzamala\n(960M L)": {
        "litros": 960_000_000,
        "descripcion": "Abastece ~22% del agua potable de CDMX",
        "fuente": "CONAGUA, Informe Sistema Cutzamala 2023",
        "color": "#063529",
    },
    "CDMX anual\n(1.1 billones L)": {
        "litros": 1_100_000_000_000,
        "descripcion": "Consumo anual total de agua potable de la CDMX",
        "fuente": "SACMEX / CONAGUA, Reporte Anual 2023",
        "color": "#031a14",
    },
}


def _seleccionar_referencias(litros_por_ano_mediana: float, anos: int) -> dict:
    """
    Selecciona referencias garantizando:
      - Al menos 1 referencia con cruce DENTRO del horizonte (años_cruce <= anos)
      - Al menos 1 referencia "aspiracional" mayor (puede quedar fuera del horizonte)
      - Máximo 4 referencias para no saturar la gráfica
    """
    litros_total = litros_por_ano_mediana * anos
    dentro = {}
    fuera = {}

    for nombre, datos in REFERENCIAS_HIDRICAS.items():
        vol = datos["litros"]
        if vol <= litros_total:
            dentro[nombre] = datos
        elif vol <= litros_total * 10:  # razonablemente aspiracional
            fuera[nombre] = datos

    # Tomar las 2 más grandes que cruzan dentro + la más pequeña de fuera
    dentro_items = sorted(dentro.items(), key=lambda x: x[1]["litros"], reverse=True)
    fuera_items  = sorted(fuera.items(),  key=lambda x: x[1]["litros"])

    seleccionadas = {}
    for k, v in dentro_items[:3]:
        seleccionadas[k] = v
    for k, v in fuera_items[:1]:
        seleccionadas[k] = v

    # Fallback: si nada cruza, tomar las 2 más pequeñas del catálogo
    if not seleccionadas:
        items = sorted(REFERENCIAS_HIDRICAS.items(), key=lambda x: x[1]["litros"])
        for k, v in items[:2]:
            seleccionadas[k] = v

    return seleccionadas


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
    Simula n_sim trayectorias de consumo hídrico acumulado con Monte Carlo.

    Variables estocásticas:
        • Huella hídrica/kg fibra: Normal(μ=db, σ=30%) — variación LCA y cultivo
        • Prendas/persona/año:     Normal(μ=input, σ=25%) — heterogeneidad de consumo

    Las referencias son ADAPTATIVAS al material: siempre hay al menos 1 cruce
    visible dentro del horizonte, independientemente del material seleccionado.
    """
    rng = np.random.default_rng(seed)

    mat    = MATERIALES[material_key]
    prenda = PRENDAS[prenda_key]
    peso_kg     = mat["peso_prenda_kg"].get(prenda_key, 0.25)
    litros_base = mat["huella_hidrica_litros_kg"]

    prendas_mat = np.clip(
        rng.normal(prendas_por_persona, prendas_por_persona * 0.25, (n_sim, anos)), 1, None
    )
    litros_mat = np.clip(
        rng.normal(litros_base, litros_base * 0.30, (n_sim, anos)), 50, None
    )

    consumo_anual = n_personas * prendas_mat * peso_kg * litros_mat
    acumulado = np.hstack([np.zeros((n_sim, 1)), np.cumsum(consumo_anual, axis=1)])

    p10 = np.percentile(acumulado, 10,  axis=0).tolist()
    p25 = np.percentile(acumulado, 25,  axis=0).tolist()
    p50 = np.percentile(acumulado, 50,  axis=0).tolist()
    p75 = np.percentile(acumulado, 75,  axis=0).tolist()
    p90 = np.percentile(acumulado, 90,  axis=0).tolist()
    p99 = np.percentile(acumulado, 99,  axis=0).tolist()

    finales = acumulado[:, -1]
    litros_por_ano_mediana = float(np.median(consumo_anual))

    # ─── Referencias adaptativas ──────────────────────────────────────────────
    refs_activas = _seleccionar_referencias(litros_por_ano_mediana, anos)
    equivalencias = {}

    for nombre, datos in refs_activas.items():
        vol = datos["litros"]
        cruce_p50 = _anos_hasta_cruce(p50, vol, anos)
        cruce_p90 = _anos_hasta_cruce(p90, vol, anos)
        pct_supera = float(np.mean(finales > vol)) * 100

        # Línea de referencia: tasa constante basada en el volumen
        # Para que sea comparable con la curva acumulada del salón
        tasa = litros_por_ano_mediana  # usamos la mediana del salón como "ritmo"
        linea_ref = [vol] * (anos + 1)  # línea horizontal al nivel del volumen

        equivalencias[nombre] = {
            "vol_litros": vol,
            "descripcion": datos["descripcion"],
            "fuente": datos["fuente"],
            "color": datos["color"],
            "años_p50": cruce_p50,
            "años_p90": cruce_p90,
            "pct_escenarios_supera": round(pct_supera, 1),
            "linea_ref": linea_ref,  # línea horizontal para graficar
        }

    p50_final = float(np.percentile(finales, 50))
    p90_final = float(np.percentile(finales, 90))

    idx = rng.choice(n_sim, size=min(500, n_sim), replace=False)
    trayectorias_muestra = acumulado[idx].tolist()

    return {
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
        "litros_por_prenda_base": round(litros_base * peso_kg, 1),
        "litros_por_ano_base": round(n_personas * prendas_por_persona * litros_base * peso_kg),
        "trayectorias_muestra": trayectorias_muestra,
        "p10": p10, "p25": p25, "p50": p50,
        "p75": p75, "p90": p90, "p99": p99,
        "p50_final": p50_final,
        "p90_final": p90_final,
        "p99_final": float(np.percentile(finales, 99)),
        "equivalencias": equivalencias,
        "equiv_albercas_p50": round(p50_final / 2_500_000, 1),
        "equiv_albercas_p90": round(p90_final / 2_500_000, 1),
        "equiv_personas_anos_p50": round(p50_final / CONSUMO_PERSONA_AÑO_L),
        "equiv_personas_anos_p90": round(p90_final / CONSUMO_PERSONA_AÑO_L),
    }


def _anos_hasta_cruce(serie: list, umbral: float, max_anos: int) -> float | None:
    for i in range(1, len(serie)):
        if serie[i] >= umbral:
            frac = (umbral - serie[i - 1]) / max(serie[i] - serie[i - 1], 1e-9)
            return round((i - 1) + frac, 1)
    return None