# algoritmo/ensamblaje.py — v5+

from algoritmo.costo_produccion import calcular_fob, calcular_landed_cost
from algoritmo.opacidad import calcular_alpha
from algoritmo.markov import calcular_c_ambiental
from algoritmo.social import calcular_c_social
from data.db import MARKUP_FACTOR_RETAIL, MARGEN_REINVERSION_DEFAULT


def calcular_precio_justo(
    empresa: dict,
    material: dict,
    prenda: dict,
    prenda_key: str,
    mercado_destino: str = "USA",  # Nuevo parámetro
    margen: float = MARGEN_REINVERSION_DEFAULT,
) -> dict:
    """
    Calcula P_justo con estructura REAL de costos.
    
    Flujo:
    1. FOB = materiales + labor (variable por país)
    2. Landed = FOB + logística (variable por ruta)
    3. C_ambiental = ciclo de vida (Markov)
    4. C_social = brecha salarial (Juegos)
    5. α_e = penalización opacidad (KL)
    6. P_justo = (Landed + C_amb + C_soc) × α_e × markup_retail × (1 + margen)
    """
    
    # ─── CAPA 1: Costo de producción ─────────────────────────────────────
    # Calcular FOB ponderado por país de manufactura
    fob_ponderado = 0.0
    desglose_fob = {}
    
    for pais_iso, fraccion_manufactura in empresa["manufactura"].items():
        fob_calc = calcular_fob(material["key"], prenda_key, pais_iso)
        fob_unitario = fob_calc["fob_usd"]
        fob_ponderado += fob_unitario * fraccion_manufactura
        
        desglose_fob[pais_iso] = {
            "fob": fob_unitario,
            "fraccion": fraccion_manufactura,
            "aporte": fob_unitario * fraccion_manufactura,
        }
    
    # Calcular Landed cost ponderado
    peso_kg = material["peso_prenda_kg"].get(prenda_key, 0.30)
    landed_ponderado = 0.0
    desglose_landed = {}
    
    for pais_iso, fraccion in empresa["manufactura"].items():
        landed_calc = calcular_landed_cost(
            fob_calc_for_pais = desglose_fob[pais_iso]["fob"],
            pais_origen_iso = pais_iso,
            mercado_destino = mercado_destino,
            peso_kg = peso_kg,
        )
        landed_ponderado += landed_calc["landed_cost_usd"] * fraccion
        desglose_landed[pais_iso] = landed_calc
    
    # ─── CAPA 2-4: Costos de externalidades (como antes) ─────────────────
    alpha = calcular_alpha(empresa["transparencia"])
    vida_util, c_ambiental, c_agua, c_co2 = calcular_c_ambiental(
        empresa["transparencia"], material, prenda_key
    )
    c_social, c_lab_real, c_lab_digno, factor_prom, desglose_paises = calcular_c_social(
        empresa, prenda
    )
    
    # ─── CAPA 5: Ensamblaje ────────────────────────────────────────────
    # Convertir USD a MXN para reporte
    TC_MXN = 17.5  # De db.py
    
    landed_mxn = landed_ponderado * TC_MXN
    c_ambiental_mxn = c_ambiental
    c_social_mxn = c_social * TC_MXN
    
    # Costo base REAL (sin margen, sin penalización opacidad aún)
    costo_base = landed_mxn + c_ambiental_mxn + c_social_mxn
    
    # Aplicar penalización opacidad ANTES de multiplicar por markup retail
    penalizacion_opacidad_mxn = (alpha - 1) * costo_base
    costo_con_opacidad = costo_base * alpha
    
    # Aplicar margen de reinversión (sostenibilidad)
    margen_reinversion = costo_con_opacidad * margen
    
    # Aplicar markup minorista (factor 2.5-3.5× depending on positioning)
    # Patagonia: 3.0×, Nike: 2.8×, Shein: 2.2×
    markup_retail = MARKUP_FACTOR_RETAIL.get(empresa["nombre"], 2.8)
    p_justo_final = (costo_con_opacidad + margen_reinversion) * markup_retail
    
    # ─── Comparativa con precio etiqueta ────────────────────────────────
    precio_etiqueta = empresa["precios"][prenda_key]
    brecha = precio_etiqueta - p_justo_final
    
    def _veredicto(etiqueta, justo):
        ratio = etiqueta / max(justo, 1)
        if ratio < 0.60:    return "externaliza"
        elif ratio < 0.90:  return "subestimado"
        elif ratio <= 1.15: return "alineado"
        elif ratio <= 1.50: return "margen_alto"
        else:               return "sobreprecio"
    
    return {
        # Identidad
        "empresa": empresa["nombre"],
        "material": material["label"],
        "prenda": prenda["label"],
        "transparencia_pct": round(empresa["transparencia"] * 100),
        
        # Precio etiqueta vs justo
        "precio_etiqueta_mxn": precio_etiqueta,
        "p_justo_mxn": round(p_justo_final),
        "brecha_mxn": round(brecha),
        "veredicto": _veredicto(precio_etiqueta, p_justo_final),
        
        # Desglose de costos (NUEVA INFORMACIÓN)
        "landed_cost_usd": round(landed_ponderado, 2),
        "landed_cost_mxn": round(landed_mxn),
        "desglose_fob": desglose_fob,
        "desglose_landed": desglose_landed,
        
        # Externalidades
        "c_laboral_digno_mxn": round(c_lab_digno * TC_MXN),
        "c_ambiental_mxn": round(c_ambiental_mxn),
        "c_agua_mxn": round(c_agua),
        "c_co2_mxn": round(c_co2),
        "c_social_mxn": round(c_social_mxn),
        
        # Penalizaciones y márgenes
        "alpha_opacidad": round(alpha, 4),
        "penalizacion_opacidad_mxn": round(penalizacion_opacidad_mxn),
        "margen_reinversion_mxn": round(margen_reinversion),
        "factor_markup_retail": markup_retail,
        
        # Metadata
        "vida_util_meses": vida_util,
        "factor_riesgo_prom": factor_prom,
        "desglose_paises": desglose_paises,
    }


def run_all(
    material_key: str,
    prenda_key: str,
    mercado_destino: str = "USA",
    margen: float = MARGEN_REINVERSION_DEFAULT,
) -> list[dict]:
    """Corre cálculo para todas las empresas."""
    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]
    
    resultados = [
        calcular_precio_justo(e, mat, pre, prenda_key, mercado_destino, margen)
        for e in EMPRESAS
    ]
    
    # Ordenar por brecha (mayores externalizadores primero)
    return sorted(resultados, key=lambda x: x["brecha_mxn"])