# algoritmo/monte_carlo.py — v1
# ════════════════════════════════════════════════════════════════════════════════
# Módulo de Simulación Monte Carlo para evaluar la resiliencia financiera del Fast Fashion

import numpy as np
from src.data.db import MATERIALES, PRENDAS, EMPRESAS
from .ensamblaje import calcular_precio_justo


def simular_umbrales_co2(
    empresa_nombre: str, material_key: str, prenda_key: str, n_simulaciones: int = 2000
) -> dict:
    """
    Ejecuta una simulación de Monte Carlo variando las condiciones de costos ambientales.
    Encuentra el percentil 90 del precio del CO2 donde la externalización deja de ser negocio.
    """
    # Buscar la empresa por nombre
    empresa = next(
        (e for e in EMPRESAS if e["nombre"].lower() == empresa_nombre.lower()), None
    )
    if not empresa:
        raise ValueError(f"Empresa '{empresa_nombre}' no encontrada.")

    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]

    # 1. Definir distribuciones de probabilidad para las variables inciertas
    # Precio CO2: Fluctúa entre el valor actual (3.50) y un escenario de impuesto carbono severo (25.0 MXN/kg)
    sim_costo_co2 = np.random.uniform(3.50, 25.00, n_simulaciones)

    # Costo Agua: Fluctúa con una distribución normal alrededor de 0.25 MXN/litro
    sim_costo_agua = np.random.normal(0.25, 0.08, n_simulaciones)
    sim_costo_agua = np.clip(
        sim_costo_agua, 0.05, 0.60
    )  # Evitar valores negativos o absurdos

    precios_justos_simulados = []
    escenarios_quiebre = 0

    # 2. Correr la simulación iterando sobre los vectores estocásticos
    for i in range(n_simulaciones):
        # Inyectamos temporalmente las variables estocásticas simuladas en el entorno de evaluación
        import src.algoritmo.markov as markov

        orig_co2 = markov.COSTO_CO2_MXN_POR_KG
        orig_agua = markov.COSTO_AGUA_MXN_POR_LT

        markov.COSTO_CO2_MXN_POR_KG = sim_costo_co2[i]
        markov.COSTO_AGUA_MXN_POR_LT = sim_costo_agua[i]

        # Calcular el impacto con los costos de este escenario
        res = calcular_precio_justo(empresa, mat, pre, prenda_key)
        p_justo = res["p_justo_mxn"]
        p_etiqueta = res["precio_etiqueta_mxn"]

        precios_justos_simulados.append(p_justo)

        if p_justo > p_etiqueta:
            escenarios_quiebre += 1

        # Restaurar constantes originales
        markov.COSTO_CO2_MXN_POR_KG = orig_co2
        markov.COSTO_AGUA_MXN_POR_LT = orig_agua

    precios_justos_simulados = np.array(precios_justos_simulados)

    # 3. Encontrar el umbral donde P_justo supera a la etiqueta en el 90% de los escenarios
    # Evaluamos en qué punto de la distribución acumulada se cruza el precio real de etiqueta
    brechas = precios_justos_simulados - empresa["precios"][prenda_key]

    # El valor del bono CO2 donde el 90% de las simulaciones provocan pérdidas por externalización
    idx_ordenados = np.argsort(precios_justos_simulados)
    co2_ordenados = sim_costo_co2[idx_ordenados]

    # Percentil 90 del riesgo
    umbral_co2_quiebre = np.percentile(co2_ordenados, 90)

    return {
        "empresa": empresa_nombre,
        "prenda": pre["label"],
        "material": mat["label"],
        "precio_etiqueta": empresa["precios"][prenda_key],
        "p_justo_promedio": round(float(np.mean(precios_justos_simulados))),
        "p_justo_max": round(float(np.max(precios_justos_simulados))),
        "p_justo_min": round(float(np.min(precios_justos_simulados))),
        "pct_escenarios_insostenible": round(
            (escenarios_quiebre / n_simulaciones) * 100, 1
        ),
        "umbral_co2_percentil_90": round(float(umbral_co2_quiebre), 2),
        "historico_precios_justos": precios_justos_simulados.tolist(),
    }
