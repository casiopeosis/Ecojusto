# algoritmo/ensamblaje.py — v5 (REFACTORED WITH REAL COSTS)
# ════════════════════════════════════════════════════════════════════════════════
# Ensamblaje final de P_justo incorporando:
# 1. Costo de producción REAL (FOB + Landed)
# 2. Costos ambientales (Markov)
# 3. Costos sociales (Juegos + Banco Mundial)
# 4. Penalización opacidad (KL divergence)
# 5. Markups minoristas realistas

from src.data.db import (
    EMPRESAS,
    MATERIALES,
    PRENDAS,
    TC_MXN,
    MARGEN_REINVERSION_DEFAULT,
    MARKUP_FACTOR_RETAIL_DEFAULT,
)
from costo_produccion import (
    calcular_landed_cost_ponderado,
    calcular_fob_ponderado,
)
from opacidad import calcular_alpha
from markov import calcular_c_ambiental
from social import calcular_c_social


def _badge(transparencia: float) -> str:
    """Categoría de transparencia (baja, media, alta)."""
    if transparencia >= 0.70:
        return "alta"
    elif transparencia >= 0.40:
        return "media"
    return "baja"


def _veredicto(precio_etiqueta: float, p_justo: float) -> str:
    """Veredicto sobre alineación de precios."""
    ratio = precio_etiqueta / max(p_justo, 1)
    if ratio < 0.60:
        return "externaliza"
    elif ratio < 0.90:
        return "subestimado"
    elif ratio <= 1.15:
        return "alineado"
    elif ratio <= 1.50:
        return "margen_alto"
    else:
        return "sobreprecio"


def calcular_precio_justo(
    empresa: dict,
    material: dict,
    prenda: dict,
    prenda_key: str,
    mercado_destino: str = "USA",
    margen: float = MARGEN_REINVERSION_DEFAULT,
    markup_retail: float = MARKUP_FACTOR_RETAIL_DEFAULT,
) -> dict:
    """
    Calcula P_justo con estructura COMPLETA y REALISTA de costos.
    
    Args:
        empresa: dict empresa (nombre, manufactura, precios, transparencia)
        material: dict material (costos fibra, acabado, huellas)
        prenda: dict prenda (horas, complejidad)
        prenda_key: key de prenda ("playera", "jeans", etc.)
        mercado_destino: "USA" o "EU"
        margen: Margen de reinversión (ej. 0.15 = 15%)
        markup_retail: Factor markup minorista (ej. 2.8)
    
    Returns:
        dict amplio con todos los costos y métricas
    """
    
    # ─── CAPA 1: COSTO DE PRODUCCIÓN (FOB + Landed) ───────────────────────
    
    # FOB ponderado (fabricación multi-país)
    fob_result = calcular_fob_ponderado(material["key"], prenda_key, empresa["manufactura"])
    fob_ponderado_usd = fob_result["fob_ponderado_usd"]
    desglose_fob = fob_result["desglose_por_pais"]
    
    # Landed cost ponderado
    landed_result = calcular_landed_cost_ponderado(
        material["key"],
        prenda_key,
        empresa["manufactura"],
        mercado_destino,
    )
    landed_ponderado_usd = landed_result["landed_cost_ponderado_usd"]
    desglose_landed = landed_result["desglose_por_pais"]
    
    # ─── CAPA 2-5: EXTERNALIDADES + OPACIDAD ─────────────────────────────
    
    # Opacidad (KL divergence)
    alpha = calcular_alpha(empresa["transparencia"])
    
    # Ambiental (Markov)
    vida_util, c_ambiental, c_agua, c_co2 = calcular_c_ambiental(
        empresa["transparencia"],
        material,
        prenda_key,
    )
    
    # Social (Teoría de juegos)
    c_social, c_lab_real, c_lab_digno, factor_prom, desglose_paises = calcular_c_social(
        empresa,
        prenda,
    )
    
    # ─── CONVERSIÓN A MXN ──────────────────────────────────────────────────
    
    landed_mxn = landed_ponderado_usd * TC_MXN
    c_ambiental_mxn = c_ambiental
    c_social_mxn = c_social * TC_MXN
    
    # ─── ENSAMBLAJE FINAL ──────────────────────────────────────────────────
    
    # Costo base: landed + externalidades (sin opacidad aún)
    costo_base_mxn = landed_mxn + c_ambiental_mxn + c_social_mxn
    
    # Aplicar penalización opacidad
    penalizacion_opacidad_mxn = (alpha - 1) * costo_base_mxn
    costo_con_opacidad_mxn = costo_base_mxn * alpha
    
    # Aplicar margen de reinversión (sostenibilidad)
    margen_reinversion_mxn = costo_con_opacidad_mxn * margen
    
    # Aplicar markup retail
    p_justo_mxn = (costo_con_opacidad_mxn + margen_reinversion_mxn) * markup_retail
    
    # ─── COMPARATIVA CON ETIQUETA ──────────────────────────────────────────
    
    precio_etiqueta = empresa["precios"][prenda_key]
    brecha_mxn = precio_etiqueta - p_justo_mxn
    
    # ─── RESULTADO FINAL ───────────────────────────────────────────────────
    
    return {
        # IDENTIDAD
        "empresa": empresa["nombre"],
        "material": material["label"],
        "prenda": prenda["label"],
        "mercado_destino": mercado_destino,
        
        # TRANSPARENCIA
        "transparencia_pct": round(empresa["transparencia"] * 100),
        "nivel": _badge(empresa["transparencia"]),
        "alpha_opacidad": round(alpha, 4),
        
        # PRECIO ETIQUETA vs JUSTO
        "precio_etiqueta_mxn": precio_etiqueta,
        "p_justo_mxn": round(p_justo_mxn),
        "brecha_mxn": round(brecha_mxn),
        "ratio_etiqueta_justo": round(precio_etiqueta / max(p_justo_mxn, 1), 1),
        "veredicto": _veredicto(precio_etiqueta, p_justo_mxn),
        
        # DESGLOSE COSTO DE PRODUCCIÓN
        "landed_cost_usd": round(landed_ponderado_usd, 2),
        "landed_cost_mxn": round(landed_mxn),
        "fob_ponderado_usd": round(fob_ponderado_usd, 2),
        "desglose_fob_por_pais": desglose_fob,
        "desglose_landed_por_pais": desglose_landed,
        
        # DESGLOSE EXTERNALIDADES
        "c_ambiental_mxn": round(c_ambiental_mxn),
        "c_agua_mxn": round(c_agua),
        "c_co2_mxn": round(c_co2),
        "c_social_mxn": round(c_social_mxn),
        "c_laboral_digno_mxn": round(c_lab_digno * TC_MXN),
        "factor_riesgo_prom": factor_prom,
        "desglose_paises_social": desglose_paises,
        
        # DESGLOSE ENSAMBLAJE
        "costo_base_mxn": round(costo_base_mxn),
        "penalizacion_opacidad_mxn": round(penalizacion_opacidad_mxn),
        "costo_con_opacidad_mxn": round(costo_con_opacidad_mxn),
        "margen_reinversion_pct": round(margen * 100, 1),
        "margen_reinversion_mxn": round(margen_reinversion_mxn),
        "factor_markup_retail": markup_retail,
        
        # AMBIENTAL
        "vida_util_meses": vida_util,
        "huella_hidrica_litros": round(material["huella_hidrica_litros_kg"] * material["peso_prenda_kg"].get(prenda_key, 0.30)),
        "co2_kg": round(material["co2_kg_por_kg_fibra"] * material["peso_prenda_kg"].get(prenda_key, 0.30), 2),
        
        # MANUFACTURA
        "paises_manufactura": list(empresa["manufactura"].keys()),
        "n_paises_manufactura": len(empresa["manufactura"]),
    }


def run_all(
    material_key: str,
    prenda_key: str,
    mercado_destino: str = "USA",
    margen: float = MARGEN_REINVERSION_DEFAULT,
    markup_retail: float = MARKUP_FACTOR_RETAIL_DEFAULT,
) -> list[dict]:
    """
    Calcula P_justo para todas las empresas con los mismos parámetros.
    
    Args:
        material_key: "poliester", "algodon_conv", etc.
        prenda_key: "playera", "jeans", etc.
        mercado_destino: "USA" o "EU"
        margen: Margen de reinversión
        markup_retail: Factor markup minorista
    
    Returns:
        Lista de dicts (uno por empresa), ordenada por brecha (externalizadores primero)
    """
    
    if material_key not in MATERIALES:
        raise ValueError(f"Material '{material_key}' not found.")
    if prenda_key not in PRENDAS:
        raise ValueError(f"Prenda '{prenda_key}' not found.")
    
    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]
    
    resultados = [
        calcular_precio_justo(e, mat, pre, prenda_key, mercado_destino, margen, markup_retail)
        for e in EMPRESAS
    ]
    
    # Ordenar por brecha: mayores externalizadores primero
    return sorted(resultados, key=lambda x: x["brecha_mxn"])