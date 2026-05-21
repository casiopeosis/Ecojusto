# algoritmo/costo_produccion.py — v1 (Corregido)
from src.data.db import (
    MATERIALES,
    SALARIOS_PAIS,  # Reemplazado de COSTOS_MANUFACTURA_POR_PAIS que no existía en db.py
    PRENDAS,
)


def calcular_costo_materiales_usd(
    material_key: str, pais_iso: str, prenda_key: str
) -> dict:
    """
    Calcula costo de fibra bruta + acabado + trims para una prenda en un país.
    """
    mat = MATERIALES.get(material_key)
    if not mat:
        raise ValueError(f"Material {material_key} not found")

    peso_kg = mat["peso_prenda_kg"].get(prenda_key, 0.30)

    # Costo fibra bruta (variable por país)
    precio_fibra = mat["costo_fibra_usd_por_kg"].get(
        pais_iso, mat["costo_fibra_usd_por_kg"].get("CHN", 1.0)
    )
    costo_fibra = precio_fibra * peso_kg

    # Costo acabado
    precio_acabado_por_m2 = mat["costo_acabado_usd_por_m"].get(
        pais_iso, mat["costo_acabado_usd_por_m"].get("VNM", 0.3)
    )
    area_tela_m2 = peso_kg * 1.3  # Densidad promedio ~0.77 kg/m² → 1.3 m²/kg
    costo_acabado = precio_acabado_por_m2 * area_tela_m2

    # Trims fijos por el momento (0.50 USD de fallback si no está definido en db)
    costo_trims = mat.get("costo_trims_empaque_usd", 0.50)

    return {
        "fibra": round(costo_fibra, 3),
        "acabado": round(costo_acabado, 3),
        "trims": round(costo_trims, 3),
        "total": round(costo_fibra + costo_acabado + costo_trims, 3),
    }


def calcular_costo_manufactura_usd(pais_iso: str, horas_manufactura: float) -> dict:
    """
    Calcula costo de labor basándose en los salarios de SALARIOS_PAIS.
    """
    fab = SALARIOS_PAIS.get(pais_iso)
    if not fab:
        raise ValueError(f"País {pais_iso} not found in manufacturing costs")

    # Estimamos costo por hora: salario_minimo / horas_mes
    horas_mes = fab.get("horas_mes", 200)
    costo_hora = fab["salario_minimo_usd"] / horas_mes
    costo_labor = costo_hora * horas_manufactura

    return {
        "salario_minimo_mes": fab["salario_minimo_usd"],
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
    Calcula FOB = materiales + labor.
    """
    mat_cost = calcular_costo_materiales_usd(material_key, pais_manufactura, prenda_key)
    fab_cost = calcular_costo_manufactura_usd(
        pais_manufactura, PRENDAS[prenda_key]["horas_manufactura"]
    )

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
    mercado_destino: str = "USA",
    peso_kg: float = 0.30,
) -> dict:
    """
    Calcula costo total hasta warehouse destino (landed cost) con logísticas base por región.
    """
    # Mapeo básico de logística simulada ya que db.py no contiene la constante completa de logística.
    # Ajustado a los rangos descritos en tu cabecera de db.py (WSI 2025)
    logistica_default = {
        "ocean_freight_usd_por_kg": (
            11.5
            if pais_origen_iso
            in ["CHN", "VNM", "BGD", "IND", "IDN", "PAK", "LKA", "KHM", "THA"]
            else 4.0
        ),
        "aranceles_pct": 20.0 if mercado_destino == "EU" else 18.0,
        "handling_customs_usd_por_envio": 50.0,  # amortizado / 1000 prendas = 0.05
        "insurance_pct": 1.5,
    }

    ocean_freight = logistica_default["ocean_freight_usd_por_kg"] * peso_kg
    aranceles = fob_usd * (logistica_default["aranceles_pct"] / 100)
    handling = logistica_default["handling_customs_usd_por_envio"] / 1000
    insurance = fob_usd * (logistica_default["insurance_pct"] / 100)
    inland_freight = (fob_usd + ocean_freight + aranceles) * 0.05

    landed = fob_usd + ocean_freight + aranceles + handling + insurance + inland_freight

    return {
        "fob": round(fob_usd, 2),
        "ocean_freight": round(ocean_freight, 2),
        "aranceles": round(aranceles, 2),
        "handling_customs": round(handling, 2),
        "insurance": round(insurance, 2),
        "inland_freight": round(inland_freight, 2),
        "landed_cost_usd": round(landed, 2),
        "ratio_vs_fob": round((landed / max(fob_usd, 1) - 1) * 100, 1),
    }
