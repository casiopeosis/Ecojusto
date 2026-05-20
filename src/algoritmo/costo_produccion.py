# algoritmo/costo_produccion.py — v1
# Calcula FOB y Landed cost basado en costos REALES por país

from data.db import (
    MATERIALES,
    COSTOS_MANUFACTURA_POR_PAIS,
    LOGISTICA_INTERNACIONAL,
    TC_MXN,
)

def calcular_costo_materiales_usd(material_key: str, pais_iso: str, prenda_key: str) -> dict:
    """
    Calcula costo de fibra bruta + acabado + trims para una prenda en un país.
    
    Returns: {
        "fibra": float,
        "acabado": float,
        "trims": float,
        "total": float,
    }
    """
    mat = MATERIALES.get(material_key)
    if not mat:
        raise ValueError(f"Material {material_key} not found")
    
    peso_kg = mat["peso_prenda_kg"].get(prenda_key, 0.30)
    
    # Costo fibra bruta (variable por país)
    precio_fibra = mat["costo_fibra_usd_por_kg"].get(pais_iso, mat["costo_fibra_usd_por_kg"]["CHN"])
    costo_fibra = precio_fibra * peso_kg
    
    # Costo acabado (variable por país, depende superficie aproximada)
    # Estimamos ~1.5 m² de tela para cualquier garment (aproximado)
    precio_acabado_por_m2 = mat["costo_acabado_usd_por_m"].get(pais_iso, mat["costo_acabado_usd_por_m"]["VNM"])
    area_tela_m2 = peso_kg * 1.3  # Densidad promedio ~0.77 kg/m² → 1.3 m²/kg
    costo_acabado = precio_acabado_por_m2 * area_tela_m2
    
    # Trims (global, no varía por país significativamente)
    costo_trims = mat["costo_trims_empaque_usd"]
    
    return {
        "fibra": round(costo_fibra, 3),
        "acabado": round(costo_acabado, 3),
        "trims": round(costo_trims, 3),
        "total": round(costo_fibra + costo_acabado + costo_trims, 3),
    }


def calcular_costo_manufactura_usd(pais_iso: str, horas_manufactura: float) -> dict:
    """
    Calcula costo de labor + overhead factory (no incluye markup).
    
    Returns: {
        "salario_minimo": float,
        "costo_labor": float,
        "factory_markup_mxn": float,  # En pesos
        "costo_total_manufactura": float,
    }
    """
    fab = COSTOS_MANUFACTURA_POR_PAIS.get(pais_iso)
    if not fab:
        raise ValueError(f"País {pais_iso} not found in manufacturing costs")
    
    costo_hora = fab["costo_neto_manufactura_usd_por_hora"]  # Ya incluye markup
    costo_labor = costo_hora * horas_manufactura
    
    return {
        "salario_minimo_mes": fab["salario_minimo_mes_usd"],
        "costo_hora": round(costo_hora, 2),
        "costo_labor": round(costo_labor, 2),
        "horas_trabajadas": horas_manufactura,
    }


def calcular_fob(
    material_key: str,
    prenda_key: str,
    pais_manufactura: str,
) -> dict:
    """
    Calcula FOB = materiales + labor + factory margin.
    
    Nota: factory_markup_factor ya está en costo_neto_manufactura,
    no necesitamos aplicarlo dos veces.
    """
    mat_cost = calcular_costo_materiales_usd(material_key, pais_manufactura, prenda_key)
    fab_cost = calcular_costo_manufactura_usd(pais_manufactura, PRENDAS[prenda_key]["horas_manufactura"])
    
    fob = mat_cost["total"] + fab_cost["costo_labor"]
    
    return {
        "materiales_usd": mat_cost["total"],
        "manufactura_usd": fab_cost["costo_labor"],
        "fob_usd": round(fob, 2),
        "desglose": {
            "fibra": mat_cost["fibra"],
            "acabado": mat_cost["acabado"],
            "trims": mat_cost["trims"],
            "labor": fab_cost["costo_labor"],
        },
    }


def calcular_landed_cost(
    fob_usd: float,
    pais_origen_iso: str,
    mercado_destino: str = "USA",  # "USA" o "EU"
    peso_kg: float = 0.30,
) -> dict:
    """
    Calcula costo total hasta warehouse destino (landed cost).
    
    Args:
        fob_usd: Precio FOB factory
        pais_origen_iso: País donde se fabrica
        mercado_destino: Mercado principal (USA o EU)
        peso_kg: Peso garment para cálculo flete
    
    Returns: {
        "fob": float,
        "ocean_freight": float,
        "aranceles": float,
        "handling": float,
        "insurance": float,
        "inland_freight": float,
        "landed_cost": float,
    }
    """
    logistica = LOGISTICA_INTERNACIONAL.get(pais_origen_iso, {}).get(mercado_destino)
    if not logistica:
        raise ValueError(f"Logística {pais_origen_iso} → {mercado_destino} no encontrada")
    
    ocean_freight = logistica["ocean_freight_usd_por_kg"] * peso_kg
    aranceles = fob_usd * (logistica["aranceles_pct"] / 100)
    handling = logistica["handling_customs_usd_por_envio"] / 1000  # Amortizado por prenda
    insurance = fob_usd * (logistica["insurance_pct"] / 100)
    inland_freight = (fob_usd + ocean_freight + aranceles) * 0.05  # 5% adicional
    
    landed = fob_usd + ocean_freight + aranceles + handling + insurance + inland_freight
    
    return {
        "fob": round(fob_usd, 2),
        "ocean_freight": round(ocean_freight, 2),
        "aranceles": round(aranceles, 2),
        "handling_customs": round(handling, 2),
        "insurance": round(insurance, 2),
        "inland_freight": round(inland_freight, 2),
        "landed_cost_usd": round(landed, 2),
        "ratio_vs_fob": round((landed / fob_usd - 1) * 100, 1),  # % sobrecoste
    }