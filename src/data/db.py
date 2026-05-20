# data/db.py  — v6 (CALIBRADO Y COMPLETADO)
# ════════════════════════════════════════════════════════════════════════════════
#
# INVESTIGACIÓN INTEGRAL DE COSTOS (2024-2025):
#
# • Materias primas: Precios reales por fibra y país (Fibre2Fashion, EmergingTextiles 2024-2025)
#   - Polyester staple fiber (PSF) virgin: $0.85-1.05/kg global, +10-15% en EU/USA por tarifa
#   - Cotton yarn: $3.12/kg Nov 2024 (premium sobre polyester)
#   - Fabric printed/dyed: +$0.30-0.70/m sobre fibra bruta
#   - Variación por país fabricante: Bangladesh -15%, Vietnam baseline, China -5%, EU +20-30%
#
# • Mano de obra REAL por país (ITMF 2023, Cosmo Sourcing 2026, FASH455):
#   - China coastal: $600-800/mes → $3-4/hora (HIGHEST)
#   - Vietnam: $250-350/mes → $1.50/hora  ($2.99/hora es dato outlier alto)
#   - Bangladesh: $113-115/mes → $0.55/hora (LOWEST)
#   - Manufacturing hours: 0.5h (playera) a 3h (chamarra)
#   - Factory markup: 15-25% sobre labor + materials
#
# • Logística diferenciada (WSI 2025, Mordor Intelligence, Grand View 2024-2030):
#   - Ocean freight FOB to warehouse: $8-15/kg typical Asia origin
#   - Tariffs & duties: 15-20% EU (includes 2025 carbon tax), 15-25% USA (tariff uncertainty 2025)
#   - Air freight: 3-5× ocean cost, usado solo premium/rush
#   - Inland freight + customs handling: 5-8% FOB adicional
#   - Insurance: 1-2% FOB
#
# • Retail structure (AIMS360, Uphance, TrueProfit, Opensend 2025):
#   - Gross margin DTC: 60-75% (retail minus landed cost)
#   - Gross margin wholesale: 40-50% (wholesale price minus landed cost)
#   - Net margin overall: 2-10% (después OPEX, returns, markdowns)
#   - Markup factor retail: 2.5-3.5× landed cost (varía por posicionamiento)
#   - Returns processing: 20.8% rate apparel, costo reverso 66% de COGS

EMPRESAS = [
    {
        "nombre": "Shein",
        "transparencia": 0.05,
        "manufactura": {
            "CHN": 0.95,
            "VNM": 0.05,
        },
        "precios": {
            "playera": 149,
            "jeans": 299,
            "sudadera": 249,
            "vestido": 199,
            "chamarra": 449,
        },
    },
    {
        "nombre": "Primark",
        "transparencia": 0.22,
        "manufactura": {
            "CHN": 0.35,
            "BGD": 0.25,
            "IND": 0.20,
            "VNM": 0.10,
            "PAK": 0.10,
        },
        "precios": {
            "playera": 199,
            "jeans": 399,
            "sudadera": 349,
            "vestido": 299,
            "chamarra": 699,
        },
    },
    {
        "nombre": "H&M",
        "transparencia": 0.62,
        "manufactura": {
            "BGD": 0.30,
            "CHN": 0.25,
            "IND": 0.15,
            "VNM": 0.15,
            "TUR": 0.15,
        },
        "precios": {
            "playera": 349,
            "jeans": 699,
            "sudadera": 599,
            "vestido": 549,
            "chamarra": 1299,
        },
    },
    {
        "nombre": "Zara (Inditex)",
        "transparencia": 0.55,
        "manufactura": {
            "PRT": 0.25,
            "ESP": 0.15,
            "MAR": 0.20,
            "TUR": 0.15,
            "BGD": 0.15,
            "CHN": 0.10,
        },
        "precios": {
            "playera": 499,
            "jeans": 999,
            "sudadera": 849,
            "vestido": 799,
            "chamarra": 2199,
        },
    },
    {
        "nombre": "Nike",
        "transparencia": 0.68,
        "manufactura": {
            "VNM": 0.50,
            "IDN": 0.20,
            "CHN": 0.18,
            "THA": 0.07,
            "IND": 0.05,
        },
        "precios": {
            "playera": 699,
            "jeans": 1299,
            "sudadera": 1099,
            "vestido": 899,
            "chamarra": 2499,
        },
    },
    {
        "nombre": "Adidas",
        "transparencia": 0.74,
        "manufactura": {
            "VNM": 0.27,
            "IDN": 0.19,
            "CHN": 0.16,
            "KHM": 0.15,
            "PAK": 0.13,
            "IND": 0.10,
        },
        "precios": {
            "playera": 749,
            "jeans": 1499,
            "sudadera": 1199,
            "vestido": 999,
            "chamarra": 2799,
        },
    },
    {
        "nombre": "Levi's",
        "transparencia": 0.70,
        "manufactura": {
            "BGD": 0.30,
            "MEX": 0.20,
            "PAK": 0.20,
            "ETH": 0.15,
            "IND": 0.15,
        },
        "precios": {
            "playera": 599,
            "jeans": 1299,
            "sudadera": 999,
            "vestido": 899,
            "chamarra": 2299,
        },
    },
    {
        "nombre": "Patagonia",
        "transparencia": 0.92,
        "manufactura": {
            "LKA": 0.40,
            "VNM": 0.30,
            "BGD": 0.20,
            "USA": 0.10,
        },
        "precios": {
            "playera": 1299,
            "jeans": 3499,
            "sudadera": 2999,
            "vestido": 2499,
            "chamarra": 8999,
        },
    },
]

# ────────────────────────────────────────────────────────────────────────────
# SALARIOS POR PAÍS DE MANUFACTURA
# ────────────────────────────────────────────────────────────────────────────
# Fuentes: ITMF 2023, Cosmo Sourcing 2026, WageIndicator Oct 2024, OIT ILOSTAT

TC_MXN = 17.5  # USD → MXN conversion (May 2025)

SALARIOS_PAIS = {
    "CHN": {
        "pais_nombre": "China",
        "salario_minimo_usd": 600,
        "salario_digno_usd": 1200,
        "horas_mes": 200,
    },
    "BGD": {
        "pais_nombre": "Bangladesh",
        "salario_minimo_usd": 113,
        "salario_digno_usd": 490,
        "horas_mes": 208,
    },
    "PRT": {
        "pais_nombre": "Portugal",
        "salario_minimo_usd": 1020,
        "salario_digno_usd": 1380,
        "horas_mes": 173,
    },
    "ESP": {
        "pais_nombre": "España",
        "salario_minimo_usd": 1134,
        "salario_digno_usd": 1500,
        "horas_mes": 173,
    },
    "VNM": {
        "pais_nombre": "Vietnam",
        "salario_minimo_usd": 250,
        "salario_digno_usd": 420,
        "horas_mes": 208,
    },
    "USA": {
        "pais_nombre": "Estados Unidos",
        "salario_minimo_usd": 1256,
        "salario_digno_usd": 2800,
        "horas_mes": 173,
    },
    "MEX": {
        "pais_nombre": "México",
        "salario_minimo_usd": 260,
        "salario_digno_usd": 680,
        "horas_mes": 192,
    },
    "IND": {
        "pais_nombre": "India",
        "salario_minimo_usd": 130,
        "salario_digno_usd": 380,
        "horas_mes": 208,
    },
    "IDN": {
        "pais_nombre": "Indonesia",
        "salario_minimo_usd": 220,
        "salario_digno_usd": 510,
        "horas_mes": 200,
    },
    "PAK": {
        "pais_nombre": "Pakistán",
        "salario_minimo_usd": 110,
        "salario_digno_usd": 350,
        "horas_mes": 208,
    },
    "TUR": {
        "pais_nombre": "Turquía",
        "salario_minimo_usd": 530,
        "salario_digno_usd": 900,
        "horas_mes": 180,
    },
    "MAR": {
        "pais_nombre": "Marruecos",
        "salario_minimo_usd": 300,
        "salario_digno_usd": 620,
        "horas_mes": 191,
    },
    "LKA": {
        "pais_nombre": "Sri Lanka",
        "salario_minimo_usd": 115,
        "salario_digno_usd": 400,
        "horas_mes": 200,
    },
    "KHM": {
        "pais_nombre": "Cambodia",
        "salario_minimo_usd": 200,
        "salario_digno_usd": 450,
        "horas_mes": 208,
    },
    "THA": {
        "pais_nombre": "Tailandia",
        "salario_minimo_usd": 310,
        "salario_digno_usd": 620,
        "horas_mes": 200,
    },
    "ETH": {
        "pais_nombre": "Etiopía",
        "salario_minimo_usd": 26,
        "salario_digno_usd": 180,
        "horas_mes": 208,
    },
}

# ────────────────────────────────────────────────────────────────────────────
# COSTOS DE MATERIA PRIMA POR PAÍS Y MATERIAL
# ────────────────────────────────────────────────────────────────────────────

MATERIALES = {
    "poliester": {
        "key": "poliester",
        "label": "Poliéster",
        "costo_fibra_usd_por_kg": {
            "CHN": 0.85,
            "VNM": 0.92,
            "BGD": 0.88,
            "PAK": 0.87,
            "IND": 0.90,
            "TUR": 0.95,
            "MAR": 0.93,
            "PRT": 1.05,
            "ESP": 1.03,
            "IDN": 0.89,
            "LKA": 0.91,
            "KHM": 0.89,
            "THA": 0.90,
            "MEX": 1.00,
            "ETH": 0.86,
            "USA": 1.08,
        },
        "costo_acabado_usd_por_m": {
            "CHN": 0.35,
            "VNM": 0.28,
            "BGD": 0.22,
            "PAK": 0.30,
            "IND": 0.32,
            "TUR": 0.42,
            "MAR": 0.35,
            "PRT": 0.55,
            "ESP": 0.53,
            "IDN": 0.26,
            "LKA": 0.24,
            "KHM": 0.23,
            "THA": 0.28,
            "MEX": 0.45,
            "ETH": 0.20,
            "USA": 0.50,
        },
        "peso_prenda_kg": {
            "playera": 0.20,
            "jeans": 0.60,
            "sudadera": 0.45,
            "vestido": 0.35,
            "chamarra": 0.80,
        },
        "vida_base": 6,
        "huella_hidrica_litros_kg": 62,
        "co2_kg_por_kg_fibra": 14.2,
    },
    "algodon_conv": {
        "key": "algodon_conv",
        "label": "Algodón convencional",
        "costo_fibra_usd_por_kg": {
            "CHN": 2.80,
            "VNM": 3.12,
            "BGD": 2.95,
            "PAK": 2.98,
            "IND": 3.05,
            "TUR": 3.25,
            "MAR": 3.15,
            "PRT": 3.40,
            "ESP": 3.35,
            "IDN": 3.08,
            "LKA": 3.10,
            "KHM": 3.00,
            "THA": 3.08,
            "MEX": 3.20,
            "ETH": 2.75,
            "USA": 3.45,
        },
        "costo_acabado_usd_por_m": {
            "CHN": 0.45,
            "VNM": 0.38,
            "BGD": 0.30,
            "PAK": 0.40,
            "IND": 0.42,
            "TUR": 0.55,
            "MAR": 0.48,
            "PRT": 0.70,
            "ESP": 0.68,
            "IDN": 0.35,
            "LKA": 0.32,
            "KHM": 0.31,
            "THA": 0.37,
            "MEX": 0.60,
            "ETH": 0.28,
            "USA": 0.65,
        },
        "peso_prenda_kg": {
            "playera": 0.20,
            "jeans": 0.65,
            "sudadera": 0.50,
            "vestido": 0.35,
            "chamarra": 0.85,
        },
        "vida_base": 14,
        "huella_hidrica_litros_kg": 10000,
        "co2_kg_por_kg_fibra": 4.7,
    },
    "algodon_org": {
        "key": "algodon_org",
        "label": "Algodón orgánico",
        "costo_fibra_usd_por_kg": {
            "CHN": 4.20,
            "VNM": 4.50,
            "BGD": 4.35,
            "PAK": 4.40,
            "IND": 4.50,
            "TUR": 4.80,
            "MAR": 4.60,
            "PRT": 5.00,
            "ESP": 4.95,
            "IDN": 4.50,
            "LKA": 4.55,
            "KHM": 4.40,
            "THA": 4.50,
            "MEX": 4.70,
            "ETH": 4.15,
            "USA": 5.10,
        },
        "costo_acabado_usd_por_m": {
            "CHN": 0.45,
            "VNM": 0.38,
            "BGD": 0.30,
            "PAK": 0.40,
            "IND": 0.42,
            "TUR": 0.55,
            "MAR": 0.48,
            "PRT": 0.70,
            "ESP": 0.68,
            "IDN": 0.35,
            "LKA": 0.32,
            "KHM": 0.31,
            "THA": 0.37,
            "MEX": 0.60,
            "ETH": 0.28,
            "USA": 0.65,
        },
        "peso_prenda_kg": {
            "playera": 0.20,
            "jeans": 0.65,
            "sudadera": 0.50,
            "vestido": 0.35,
            "chamarra": 0.85,
        },
        "vida_base": 20,
        "huella_hidrica_litros_kg": 6000,
        "co2_kg_por_kg_fibra": 3.0,
    },
    "lana": {
        "key": "lana",
        "label": "Lana",
        "costo_fibra_usd_por_kg": {
            "CHN": 5.50,
            "VNM": 6.00,
            "BGD": 5.80,
            "PAK": 5.90,
            "IND": 6.05,
            "TUR": 6.50,
            "MAR": 6.20,
            "PRT": 7.00,
            "ESP": 6.90,
            "IDN": 6.05,
            "LKA": 6.10,
            "KHM": 5.95,
            "THA": 6.05,
            "MEX": 6.30,
            "ETH": 5.45,
            "USA": 7.20,
        },
        "costo_acabado_usd_por_m": {
            "CHN": 0.55,
            "VNM": 0.48,
            "BGD": 0.40,
            "PAK": 0.50,
            "IND": 0.52,
            "TUR": 0.70,
            "MAR": 0.60,
            "PRT": 0.90,
            "ESP": 0.88,
            "IDN": 0.48,
            "LKA": 0.45,
            "KHM": 0.42,
            "THA": 0.48,
            "MEX": 0.75,
            "ETH": 0.38,
            "USA": 0.85,
        },
        "peso_prenda_kg": {
            "playera": 0.25,
            "jeans": 0.70,
            "sudadera": 0.55,
            "vestido": 0.40,
            "chamarra": 1.00,
        },
        "vida_base": 30,
        "huella_hidrica_litros_kg": 17000,
        "co2_kg_por_kg_fibra": 26.0,
    },
    "viscosa": {
        "key": "viscosa",
        "label": "Viscosa",
        "costo_fibra_usd_por_kg": {
            "CHN": 1.20,
            "VNM": 1.35,
            "BGD": 1.25,
            "PAK": 1.28,
            "IND": 1.32,
            "TUR": 1.45,
            "MAR": 1.38,
            "PRT": 1.55,
            "ESP": 1.52,
            "IDN": 1.30,
            "LKA": 1.32,
            "KHM": 1.28,
            "THA": 1.32,
            "MEX": 1.40,
            "ETH": 1.18,
            "USA": 1.60,
        },
        "costo_acabado_usd_por_m": {
            "CHN": 0.32,
            "VNM": 0.26,
            "BGD": 0.20,
            "PAK": 0.28,
            "IND": 0.30,
            "TUR": 0.40,
            "MAR": 0.33,
            "PRT": 0.52,
            "ESP": 0.50,
            "IDN": 0.24,
            "LKA": 0.22,
            "KHM": 0.21,
            "THA": 0.26,
            "MEX": 0.42,
            "ETH": 0.18,
            "USA": 0.48,
        },
        "peso_prenda_kg": {
            "playera": 0.18,
            "jeans": 0.55,
            "sudadera": 0.42,
            "vestido": 0.30,
            "chamarra": 0.75,
        },
        "vida_base": 8,
        "huella_hidrica_litros_kg": 3000,
        "co2_kg_por_kg_fibra": 6.5,
    },
}

# ────────────────────────────────────────────────────────────────────────────
# PRENDAS: ESPECIFICACIONES Y HORAS DE MANUFACTURA
# ────────────────────────────────────────────────────────────────────────────

PRENDAS = {
    "playera": {
        "label": "Playera",
        "horas_manufactura": 0.5,
        "complejidad_relativa": 1.0,
    },
    "jeans": {
        "label": "Jeans",
        "horas_manufactura": 1.5,
        "complejidad_relativa": 2.0,
    },
    "sudadera": {
        "label": "Sudadera",
        "horas_manufactura": 1.2,
        "complejidad_relativa": 1.5,
    },
    "vestido": {
        "label": "Vestido",
        "horas_manufactura": 2.0,
        "complejidad_relativa": 2.5,
    },
    "chamarra": {
        "label": "Chamarra",
        "horas_manufactura": 3.0,
        "complejidad_relativa": 3.5,
    },
}

# ────────────────────────────────────────────────────────────────────────────
# CONSTANTES GLOBALES DE EXTERNALIDADES RECALIBRADAS (REPARACIÓN DE ESCALA)
# ────────────────────────────────────────────────────────────────────────────

# Refleja el Costo Social Real del Carbono (EPA ~200 USD por tonelada)
COSTO_CO2_MXN_POR_KG = 3.50

# Refleja el costo real de remediación y purificación de agua con químicos pesados
COSTO_AGUA_MXN_POR_LT = 0.25

# Coeficientes comerciales minoristas y margen de sustentabilidad
MARGEN_REINVERSION_DEFAULT = 0.15
MARKUP_FACTOR_RETAIL_DEFAULT = 2.8
