# algoritmo/monte_carlo_deuda_social.py — v1
# ════════════════════════════════════════════════════════════════════════════════
# Módulo Monte Carlo — Reloj de Deuda Social Acumulada
#
# Pregunta central:
#   Si el salón compra X prendas de fast fashion al año, ¿cuántos años tarda
#   en acumular una deuda social (brecha salarial no pagada) equivalente al
#   salario anual completo de un trabajador textil?
#
# Variables estocásticas:
#   • Tipo de cambio USD→MXN: distribución Normal (media=TC_MXN, σ=8%)
#     Refleja volatilidad cambiaria histórica del peso mexicano
#   • Factor de riesgo laboral por país: distribución Normal (media=fallback, σ=15%)
#     Refleja incertidumbre en los indicadores del Banco Mundial
#   • Brecha salarial (salario digno - mínimo): distribución Normal (media=db, σ=20%)
#     Refleja variación inter-fábrica y temporal en los datos de WageIndicator
#   • Prendas compradas por persona/año: distribución Normal (media=input, σ=20%)
#     Refleja heterogeneidad de consumo dentro del grupo

import numpy as np
from src.data.db import SALARIOS_PAIS, PRENDAS, EMPRESAS, TC_MXN
from src.data.world_bank import FALLBACK_RIESGO

# ─── Referencia de salario anual trabajador textil ──────────────────────────
# Umbral 1: Salario anual completo a salario MÍNIMO en Bangladesh (~$113/mes)
# Umbral 2: Salario anual a salario DIGNO en Bangladesh (~$490/mes)
# Umbral 3: Salario anual a salario mínimo en México (~$260/mes)
UMBRALES_REFERENCIA = {
    "Salario anual Bangladesh\n(mínimo, $113/mes)": 113 * 12,   # USD
    "Salario anual Vietnam\n(mínimo, $250/mes)": 250 * 12,       # USD
    "Salario anual México\n(mínimo, $260/mes)": 260 * 12,        # USD
    "Salario DIGNO Bangladesh\n($490/mes)": 490 * 12,            # USD
}


def _brecha_por_prenda_usd(
    empresa: dict,
    prenda_key: str,
    rng: np.random.Generator,
    n_sim: int,
) -> np.ndarray:
    """
    Calcula un vector (n_sim,) de brechas salariales en USD por prenda producida,
    ponderando por la distribución de manufactura de la empresa e inyectando
    incertidumbre estocástica en salarios y factor de riesgo.
    """
    horas = PRENDAS[prenda_key]["horas_manufactura"]
    brechas = np.zeros(n_sim)

    for iso, fraccion in empresa["manufactura"].items():
        sal = SALARIOS_PAIS.get(iso, {"salario_minimo_usd": 200, "salario_digno_usd": 500, "horas_mes": 200})
        horas_mes = sal["horas_mes"]

        # Brecha base (salario digno - mínimo) por hora
        brecha_hora_base = (sal["salario_digno_usd"] - sal["salario_minimo_usd"]) / horas_mes

        # Inyectar incertidumbre ±20% sobre la brecha
        brecha_hora = rng.normal(brecha_hora_base, brecha_hora_base * 0.20, size=n_sim)
        brecha_hora = np.clip(brecha_hora, 0, None)

        # Factor de riesgo laboral con incertidumbre ±15%
        f_base = FALLBACK_RIESGO.get(iso, 1.0)
        factor = rng.normal(f_base, f_base * 0.15, size=n_sim)
        factor = np.clip(factor, 0.3, 2.0)

        # Deuda social por prenda en este país
        deuda_pais = brecha_hora * horas * factor * fraccion
        brechas += deuda_pais

    return brechas


def simular_deuda_social(
    empresa_nombre: str,
    prenda_key: str,
    n_personas: int = 30,
    prendas_por_persona: float = 25.0,
    anos: int = 15,
    n_sim: int = 2000,
    seed: int | None = None,
) -> dict:
    """
    Simula n_sim trayectorias de deuda social acumulada en USD y MXN.

    Para cada simulación s y año t:
        deuda_s_t = n_personas
                    × Nₜ(prendas_por_persona, σ=20%)   [prendas/año]
                    × brecha_usd_por_prenda_s           [USD/prenda, estocástico]
                    × TC_s                               [USD→MXN, estocástico]

    La 'deuda social' representa la brecha entre lo que se pagó a los trabajadores
    y lo que un salario digno requeriría — la externalidad no compensada.

    Returns:
        dict con trayectorias, percentiles, años hasta equiparar umbrales de referencia.
    """
    rng = np.random.default_rng(seed)

    empresa = next((e for e in EMPRESAS if e["nombre"].lower() == empresa_nombre.lower()), None)
    if not empresa:
        raise ValueError(f"Empresa '{empresa_nombre}' no encontrada en EMPRESAS.")

    prenda = PRENDAS[prenda_key]

    # ─── Tipo de cambio estocástico (n_sim,) ─────────────────────────────────
    tc_sims = rng.normal(TC_MXN, TC_MXN * 0.08, size=n_sim)
    tc_sims = np.clip(tc_sims, TC_MXN * 0.7, TC_MXN * 1.5)

    # ─── Brecha por prenda en USD (n_sim,) ───────────────────────────────────
    brecha_usd_vec = _brecha_por_prenda_usd(empresa, prenda_key, rng, n_sim)

    # ─── Prendas anuales (n_sim, anos) ───────────────────────────────────────
    prendas_mat = rng.normal(prendas_por_persona, prendas_por_persona * 0.20, size=(n_sim, anos))
    prendas_mat = np.clip(prendas_mat, 1, None)

    # ─── Consumo anual de deuda social en USD (n_sim, anos) ──────────────────
    # brecha_usd_vec: (n_sim,) → broadcasting con prendas_mat: (n_sim, anos)
    deuda_anual_usd = n_personas * prendas_mat * brecha_usd_vec[:, np.newaxis]

    # ─── Acumulado en USD y MXN ──────────────────────────────────────────────
    ceros = np.zeros((n_sim, 1))
    acum_usd = np.hstack([ceros, np.cumsum(deuda_anual_usd, axis=1)])  # (n_sim, anos+1)
    acum_mxn = acum_usd * tc_sims[:, np.newaxis]

    # ─── Percentiles por año ─────────────────────────────────────────────────
    def pct_por_año(arr, p):
        return np.percentile(arr, p, axis=0).tolist()

    # En USD (para comparar con umbrales de referencia)
    p10_usd = pct_por_año(acum_usd, 10)
    p25_usd = pct_por_año(acum_usd, 25)
    p50_usd = pct_por_año(acum_usd, 50)
    p75_usd = pct_por_año(acum_usd, 75)
    p90_usd = pct_por_año(acum_usd, 90)
    p99_usd = pct_por_año(acum_usd, 99)

    # En MXN (para mostrar en interfaz)
    p50_mxn = pct_por_año(acum_mxn, 50)
    p90_mxn = pct_por_año(acum_mxn, 90)

    finales_usd = acum_usd[:, -1]
    finales_mxn = acum_mxn[:, -1]

    # ─── Años hasta equiparar umbrales de referencia ─────────────────────────
    años_cruce = {}
    for etiqueta, umbral_usd in UMBRALES_REFERENCIA.items():
        cruce_p50 = _anos_hasta_cruce(p50_usd, umbral_usd, anos)
        cruce_p90 = _anos_hasta_cruce(p90_usd, umbral_usd, anos)
        pct_supera = float(np.mean(finales_usd > umbral_usd)) * 100
        años_cruce[etiqueta] = {
            "umbral_usd": umbral_usd,
            "años_p50": cruce_p50,
            "años_p90": cruce_p90,
            "pct_escenarios_supera": round(pct_supera, 1),
        }

    # ─── Submuestra de trayectorias para visualización ───────────────────────
    idx_muestra = rng.choice(n_sim, size=min(500, n_sim), replace=False)
    trayectorias_mxn = acum_mxn[idx_muestra].tolist()

    # ─── Deuda social promedio por prenda (para interpretación) ──────────────
    brecha_prom_usd = float(np.mean(brecha_usd_vec))
    brecha_prom_mxn = brecha_prom_usd * TC_MXN

    return {
        # Identidad
        "empresa": empresa["nombre"],
        "transparencia_pct": round(empresa["transparencia"] * 100),
        "prenda": prenda["label"],
        "prenda_key": prenda_key,
        "n_personas": n_personas,
        "prendas_por_persona": prendas_por_persona,
        "anos": anos,
        "n_sim": n_sim,
        # Trayectorias para el haz de líneas (en MXN)
        "trayectorias_mxn": trayectorias_mxn,
        # Bandas de percentiles por año (USD para referencia, MXN para display)
        "p10_usd": p10_usd,
        "p25_usd": p25_usd,
        "p50_usd": p50_usd,
        "p75_usd": p75_usd,
        "p90_usd": p90_usd,
        "p99_usd": p99_usd,
        "p50_mxn": p50_mxn,
        "p90_mxn": p90_mxn,
        # Valores finales resumen
        "p50_final_usd": round(float(np.percentile(finales_usd, 50)), 2),
        "p90_final_usd": round(float(np.percentile(finales_usd, 90)), 2),
        "p50_final_mxn": round(float(np.percentile(finales_mxn, 50))),
        "p90_final_mxn": round(float(np.percentile(finales_mxn, 90))),
        # Años hasta cruce con umbrales de referencia
        "años_cruce_umbrales": años_cruce,
        # Brecha por prenda (interpretación)
        "brecha_prom_usd_por_prenda": round(brecha_prom_usd, 3),
        "brecha_prom_mxn_por_prenda": round(brecha_prom_mxn, 2),
        # Manufactura para contexto
        "paises_manufactura": list(empresa["manufactura"].keys()),
    }


def comparar_empresas_deuda(
    prenda_key: str,
    n_personas: int = 30,
    prendas_por_persona: float = 25.0,
    anos: int = 10,
    n_sim: int = 1000,
) -> list[dict]:
    """
    Corre simular_deuda_social para TODAS las empresas con los mismos parámetros.
    Retorna lista ordenada por deuda social P50 final (mayor a menor).
    """
    resultados = []
    for empresa in EMPRESAS:
        try:
            r = simular_deuda_social(
                empresa["nombre"], prenda_key, n_personas,
                prendas_por_persona, anos, n_sim,
            )
            resultados.append(r)
        except Exception:
            continue
    return sorted(resultados, key=lambda x: x["p50_final_usd"], reverse=True)


def _anos_hasta_cruce(serie: list, umbral: float, max_anos: int) -> float | None:
    """
    Interpola el año en que la serie acumulada cruza el umbral.
    Retorna None si no cruza dentro del horizonte.
    """
    for i in range(1, len(serie)):
        if serie[i] >= umbral:
            frac = (umbral - serie[i - 1]) / max(serie[i] - serie[i - 1], 1e-9)
            return round((i - 1) + frac, 1)
    return None
