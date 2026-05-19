# data/db.py  — v5 (COMPLETE COST STRUCTURE OVERHAUL)
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
        "nombre":        "Shein",
        "transparencia": 0.05,
        "manufactura": {
            "CHN": 0.95,
            "VNM": 0.05,
        },
        # Precios al minorista (MSRP/retail)
        "precios": {
            "playera":  149,   # Ultra fast-fashion
            "jeans":    299,
            "sudadera": 249,
            "vestido":  199,
            "chamarra": 449,
        },
    },
    {
        "nombre":        "Primark",
        "transparencia": 0.22,
        "manufactura": {
            "CHN": 0.35,
            "BGD": 0.25,
            "IND": 0.20,
            "VNM": 0.10,
            "PAK": 0.10,
        },
        "precios": {
            "playera":  199,
            "jeans":    399,
            "sudadera": 349,
            "vestido":  299,
            "chamarra": 699,
        },
    },
    {
        "nombre":        "H&M",
        "transparencia": 0.62,
        "manufactura": {
            "BGD": 0.30,
            "CHN": 0.25,
            "IND": 0.15,
            "VNM": 0.15,
            "TUR": 0.15,
        },
        "precios": {
            "playera":  349,
            "jeans":    699,
            "sudadera": 599,
            "vestido":  549,
            "chamarra": 1299,
        },
    },
    {
        "nombre":        "Zara (Inditex)",
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
            "playera":  499,
            "jeans":    999,
            "sudadera": 849,
            "vestido":  799,
            "chamarra": 2199,
        },
    },
    {
        "nombre":        "Nike",
        "transparencia": 0.68,
        "manufactura": {
            "VNM": 0.50,
            "IDN": 0.20,
            "CHN": 0.18,
            "THA": 0.07,
            "IND": 0.05,
        },
        "precios": {
            "playera":  699,
            "jeans":    1299,
            "sudadera": 1099,
            "vestido":  899,
            "chamarra": 2499,
        },
    },
    {
        "nombre":        "Adidas",
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
            "playera":  749,
            "jeans":    1499,
            "sudadera": 1199,
            "vestido":  999,
            "chamarra": 2799,
        },
    },
    {
        "nombre":        "Levi's",
        "transparencia": 0.70,
        "manufactura": {
            "BGD": 0.30,
            "MEX": 0.20,
            "PAK": 0.20,
            "ETH": 0.15,
            "IND": 0.15,
        },
        "precios": {
            "playera":  599,
            "jeans":    1299,
            "sudadera": 999,
            "vestido":  899,
            "chamarra": 2299,
        },
    },
    {
        "nombre":        "Patagonia",
        "transparencia": 0.92,
        "manufactura": {
            "LKA": 0.40,
            "VNM": 0.30,
            "BGD": 0.20,
            "USA": 0.10,
        },
        "precios": {
            "playera":  1299,
            "jeans":    3499,
            "sudadera": 2999,
            "vestido":  2499,
            "chamarra": 8999,
        },
    },
]

# ────────────────────────────────────────────────────────────────────────────
# COSTOS DE MATERIA PRIMA POR PAÍS Y MATERIAL
# ────────────────────────────────────────────────────────────────────────────
# 
# Estructura:
#   "material_key": {
#       "nombre": "...",
#       "materiales_costo_usd_por_kg_fibra": {
#           "CHN": precio,  # China tiene acceso local, costo menor
#           "VNM": precio,  # Vietnam importa más, precio intermedio
#           "BGD": precio,  # Bangladesh costo menor por volumen
#           ...
#       },
#       "fabric_finishing_usd_por_m": {...},  # Costo de teñido/impresión
#       "peso_prenda_kg": {...},  # Peso del garment finished
#   }
#
# FUENTE: Fibre2Fashion weekly prices Nov 2024, EmergingTextiles 2024-2025,
#         ITMF fabric finishing costs 2023, LCA data Textile Exchange

MATERIALES = {
    "poliester": {
        "key": "poliester",
        "label": "Poliéster",
        
        # Costo de fibra virgen PSF (polyester staple fiber) por kg
        # Fuente: Fibre2Fashion, EmergingTextiles 2024-2025
        # Nota: Precios en factory gate; incluye conversión a fibra para hilado
        "costo_fibra_usd_por_kg": {
            "CHN": 0.85,    # China tiene acceso a materia prima barata + producción vertical
            "VNM": 0.92,    # Vietnam importa PTA/MEG, cost intermedio
            "BGD": 0.88,    # Bangladesh importa pero compra en volumen
            "PAK": 0.87,
            "IND": 0.90,
            "TUR": 0.95,    # Turquía importa más, sobrecoste transporte
            "MAR": 0.93,
            "PRT": 1.05,    # Portugal: UE tarifa carbono + logística
            "ESP": 1.03,
            "IDN": 0.89,
            "LKA": 0.91,
            "KHM": 0.89,
            "THA": 0.90,
            "MEX": 1.00,    # México: acceso USMCA pero costo base mayor
            "ETH": 0.86,    # Etiopía: costo muy bajo
            "USA": 1.08,    # USA: importa o produce local (premium)
        },
        
        # Costo de acabado/teñido/impresión de tela (USD por metro cuadrado)
        # Varía drásticamente por país (energía, regulación, escala)
        # Fuente: ITMF 2023, Bangladesh leads cotton finishing $0.30/m
        "costo_acabado_usd_por_m": {
            "CHN": 0.35,    # Cheap energy, scale economies
            "VNM": 0.28,    # Lower electricity rates in Vietnam
            "BGD": 0.22,    # Bangladesh dominates: $0.70/m for full cotton, $0.22 for polyester
            "PAK": 0.30,
            "IND": 0.32,
            "TUR": 0.42,    # EU regulations push cost up
            "MAR": 0.35,
            "PRT": 0.55,    # EU environmental compliance premium
            "ESP": 0.53,
            "IDN": 0.26,    # Emerging market advantage
            "LKA": 0.24,
            "KHM": 0.23,
            "THA": 0.28,
            "MEX": 0.45,    # Clean production standards (USMCA)
            "ETH": 0.18,    # Lowest cost base
            "USA": 0.65,    # Domestic finishing premium
        },
        
        # Costo trims + empaque por prenda (USD, estimado)
        "costo_trims_empaque_usd": 0.25,  # Global average: botones, zipper, label, etiqueta, empaque
        
        # Peso de la tela por tipo de prenda (kg)
        # Para cálculo de huella ambiental y costo de materia prima
        "peso_prenda_kg": {
            "playera":  0.20,
            "jeans":    0.60,
            "sudadera": 0.45,
            "vestido":  0.35,
            "chamarra": 0.80,
        },
        
        # Métricas ambientales (para módulo Markov + impacto)
        "huella_hidrica_litros_kg": 62,   # Polyester: bajo uso agua
        "co2_kg_por_kg_fibra": 14.2,      # De producción + transporte
    },
    
    "algodon_conv": {
        "key": "algodon_conv",
        "label": "Algodón convencional",
        
        # Cotton está más volatile, precios Nov 2024: $3.12/kg yarn
        # Convertimos a fibra bruta (~15% menos que yarn):
        "costo_fibra_usd_por_kg": {
            "CHN": 2.50,
            "VNM": 2.65,
            "BGD": 2.55,    # Bangladesh spins domestic + imported
            "PAK": 2.45,    # Pakistan: 20% of spinning capacity, cheaper
            "IND": 2.70,    # India holds 20% world capacity, but prices higher
            "TUR": 2.85,
            "MAR": 2.75,
            "PRT": 3.10,
            "ESP": 3.05,
            "IDN": 2.62,
            "LKA": 2.60,
            "KHM": 2.58,
            "THA": 2.64,
            "MEX": 2.90,
            "ETH": 2.40,
            "USA": 2.95,
        },
        
        # Cotton finishing: más costoso que polyester (water intensive, chemistry)
        "costo_acabado_usd_por_m": {
            "CHN": 0.50,
            "VNM": 0.40,
            "BGD": 0.70,    # Bangladesh: $0.70/m cotton complete process (ITMF 2023)
            "PAK": 0.45,
            "IND": 0.48,
            "TUR": 0.65,
            "MAR": 0.55,
            "PRT": 0.80,
            "ESP": 0.75,
            "IDN": 0.42,
            "LKA": 0.38,
            "KHM": 0.37,
            "THA": 0.44,
            "MEX": 0.68,
            "ETH": 0.30,
            "USA": 0.95,
        },
        
        "costo_trims_empaque_usd": 0.25,
        
        "peso_prenda_kg": {
            "playera":  0.20,
            "jeans":    0.65,
            "sudadera": 0.50,
            "vestido":  0.35,
            "chamarra": 0.85,
        },
        
        # Cotton es high-water, pesticides
        "huella_hidrica_litros_kg": 10000,  # HUGE water footprint
        "co2_kg_por_kg_fibra": 4.7,
    },
    
    "algodon_org": {
        "key": "algodon_org",
        "label": "Algodón orgánico",
        
        # Organic cotton: +25-40% premium sobre conventional (Textile Exchange data)
        "costo_fibra_usd_por_kg": {
            "CHN": 3.25,
            "VNM": 3.45,
            "BGD": 3.35,
            "PAK": 3.20,
            "IND": 3.55,
            "TUR": 3.75,
            "MAR": 3.60,
            "PRT": 4.05,
            "ESP": 3.95,
            "IDN": 3.40,
            "LKA": 3.38,
            "KHM": 3.35,
            "THA": 3.45,
            "MEX": 3.80,
            "ETH": 3.12,
            "USA": 3.85,
        },
        
        # Organic finishing: similar costs but certification overhead +10%
        "costo_acabado_usd_por_m": {
            "CHN": 0.55,
            "VNM": 0.44,
            "BGD": 0.77,
            "PAK": 0.50,
            "IND": 0.53,
            "TUR": 0.72,
            "MAR": 0.60,
            "PRT": 0.88,
            "ESP": 0.82,
            "IDN": 0.46,
            "LKA": 0.42,
            "KHM": 0.41,
            "THA": 0.48,
            "MEX": 0.75,
            "ETH": 0.33,
            "USA": 1.04,
        },
        
        "costo_trims_empaque_usd": 0.30,  # Organic labels cost more
        
        "peso_prenda_kg": {
            "playera":  0.20,
            "jeans":    0.65,
            "sudadera": 0.50,
            "vestido":  0.35,
            "chamarra": 0.85,
        },
        
        "huella_hidrica_litros_kg": 6000,  # Still high but lower chemicals
        "co2_kg_por_kg_fibra": 3.0,
    },
    
    "lana": {
        "key": "lana",
        "label": "Lana",
        
        # Wool prices highly dependent on sourcing region (Aus/NZ premium)
        "costo_fibra_usd_por_kg": {
            "CHN": 8.50,
            "VNM": 9.20,
            "BGD": 8.80,
            "PAK": 8.40,
            "IND": 9.00,
            "TUR": 9.50,
            "MAR": 9.30,
            "PRT": 10.50,
            "ESP": 10.20,
            "IDN": 8.95,
            "LKA": 8.75,
            "KHM": 8.70,
            "THA": 9.10,
            "MEX": 10.00,
            "ETH": 8.30,
            "USA": 11.00,
        },
        
        # Wool finishing: complex (scouring, carding, dyeing)
        "costo_acabado_usd_por_m": {
            "CHN": 0.75,
            "VNM": 0.65,
            "BGD": 0.70,
            "PAK": 0.72,
            "IND": 0.80,
            "TUR": 1.10,
            "MAR": 0.95,
            "PRT": 1.40,
            "ESP": 1.35,
            "IDN": 0.68,
            "LKA": 0.62,
            "KHM": 0.60,
            "THA": 0.72,
            "MEX": 1.05,
            "ETH": 0.55,
            "USA": 1.60,
        },
        
        "costo_trims_empaque_usd": 0.35,  # Premium trims for wool
        
        "peso_prenda_kg": {
            "playera":  0.25,
            "jeans":    0.70,
            "sudadera": 0.55,
            "vestido":  0.40,
            "chamarra": 1.00,
        },
        
        "huella_hidrica_litros_kg": 17000,  # Livestock: very high water
        "co2_kg_por_kg_fibra": 26.0,        # Methane emissions from sheep
    },
    
    "viscosa": {
        "key": "viscosa",
        "label": "Viscosa (Rayón)",
        
        # Viscosa/rayon: wood pulp sourced, processing intensive
        "costo_fibra_usd_por_kg": {
            "CHN": 1.85,
            "VNM": 1.95,
            "BGD": 1.88,
            "PAK": 1.82,
            "IND": 1.92,
            "TUR": 2.15,
            "MAR": 2.05,
            "PRT": 2.45,
            "ESP": 2.35,
            "IDN": 1.90,
            "LKA": 1.86,
            "KHM": 1.84,
            "THA": 1.93,
            "MEX": 2.20,
            "ETH": 1.75,
            "USA": 2.60,
        },
        
        # Viscosa finishing: chemical-intensive
        "costo_acabado_usd_por_m": {
            "CHN": 0.42,
            "VNM": 0.35,
            "BGD": 0.38,
            "PAK": 0.40,
            "IND": 0.44,
            "TUR": 0.58,
            "MAR": 0.48,
            "PRT": 0.72,
            "ESP": 0.68,
            "IDN": 0.36,
            "LKA": 0.32,
            "KHM": 0.31,
            "THA": 0.38,
            "MEX": 0.56,
            "ETH": 0.25,
            "USA": 0.85,
        },
        
        "costo_trims_empaque_usd": 0.25,
        
        "peso_prenda_kg": {
            "playera":  0.18,
            "jeans":    0.55,
            "sudadera": 0.42,
            "vestido":  0.30,
            "chamarra": 0.75,
        },
        
        "huella_hidrica_litros_kg": 3000,   # Lower than cotton
        "co2_kg_por_kg_fibra": 6.5,
    },
}

# ────────────────────────────────────────────────────────────────────────────
# COSTOS DE MANUFACTURA (LABOR + OVERHEAD) POR PAÍS
# ────────────────────────────────────────────────────────────────────────────
#
# Estructura:
#   "ISO3": {
#       "pais_nombre": "...",
#       "salario_minimo_mes_usd": X,
#       "salario_digno_mes_usd": Y,
#       "horas_trabajo_mes": Z,  # ~200 standard
#       "costo_manufactura_usd_por_hora": X,  # includes factory markup 15-25%
#       "eficiencia_factor": 1.0,  # 1.0 = baseline; >1.0 más lento
#   }
#
# FUENTE: ITMF 2023, Cosmo Sourcing 2026, FASH455, multiple guides 2024-2025
# NOTA: Costo manufactura = (salario + overhead) / horas, × factory margin

COSTOS_MANUFACTURA_POR_PAIS = {
    "CHN": {
        "pais_nombre": "China",
        "salario_minimo_mes_usd": 450,      # Coastal regions $600-800, inland $350-400 → avg $450
        "salario_digno_mes_usd": 1050,
        "horas_trabajo_mes": 200,
        "costo_labor_usd_por_hora": 2.25,   # $450/200h = $2.25/h, before factory markup
        "factory_markup_factor": 1.20,      # 20% overhead
        "costo_neto_manufactura_usd_por_hora": 2.70,  # 2.25 × 1.20
        "eficiencia_factor": 1.0,           # Baseline
    },
    "VNM": {
        "pais_nombre": "Vietnam",
        "salario_minimo_mes_usd": 300,      # $250-350 range
        "salario_digno_mes_usd": 420,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 1.44,   # $300/208h
        "factory_markup_factor": 1.22,      # 22% (slightly higher than China)
        "costo_neto_manufactura_usd_por_hora": 1.76,
        "eficiencia_factor": 1.05,          # Slightly less efficient than China
    },
    "BGD": {
        "pais_nombre": "Bangladesh",
        "salario_minimo_mes_usd": 113,
        "salario_digno_mes_usd": 490,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 0.54,   # CHEAPEST
        "factory_markup_factor": 1.25,      # 25% (emerging market risk margin)
        "costo_neto_manufactura_usd_por_hora": 0.68,
        "eficiencia_factor": 1.15,          # Slower, quality issues if rushed
    },
    "PAK": {
        "pais_nombre": "Pakistán",
        "salario_minimo_mes_usd": 110,
        "salario_digno_mes_usd": 350,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 0.53,
        "factory_markup_factor": 1.25,
        "costo_neto_manufactura_usd_por_hora": 0.66,
        "eficiencia_factor": 1.20,          # Weaving/specialty operations faster
    },
    "IND": {
        "pais_nombre": "India",
        "salario_minimo_mes_usd": 130,
        "salario_digno_mes_usd": 380,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 0.62,
        "factory_markup_factor": 1.23,
        "costo_neto_manufactura_usd_por_hora": 0.76,
        "eficiencia_factor": 1.08,
    },
    "IDN": {
        "pais_nombre": "Indonesia",
        "salario_minimo_mes_usd": 220,
        "salario_digno_mes_usd": 510,
        "horas_trabajo_mes": 200,
        "costo_labor_usd_por_hora": 1.10,
        "factory_markup_factor": 1.22,
        "costo_neto_manufactura_usd_por_hora": 1.34,
        "eficiencia_factor": 1.02,
    },
    "THA": {
        "pais_nombre": "Tailandia",
        "salario_minimo_mes_usd": 310,
        "salario_digno_mes_usd": 620,
        "horas_trabajo_mes": 200,
        "costo_labor_usd_por_hora": 1.55,
        "factory_markup_factor": 1.20,
        "costo_neto_manufactura_usd_por_hora": 1.86,
        "eficiencia_factor": 0.98,          # Skilled workforce
    },
    "LKA": {
        "pais_nombre": "Sri Lanka",
        "salario_minimo_mes_usd": 115,
        "salario_digno_mes_usd": 400,
        "horas_trabajo_mes": 200,
        "costo_labor_usd_por_hora": 0.58,
        "factory_markup_factor": 1.24,
        "costo_neto_manufactura_usd_por_hora": 0.72,
        "eficiencia_factor": 1.00,          # High-quality garments
    },
    "KHM": {
        "pais_nombre": "Cambodia",
        "salario_minimo_mes_usd": 200,
        "salario_digno_mes_usd": 450,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 0.96,
        "factory_markup_factor": 1.25,
        "costo_neto_manufactura_usd_por_hora": 1.20,
        "eficiencia_factor": 1.12,
    },
    "TUR": {
        "pais_nombre": "Turquía",
        "salario_minimo_mes_usd": 530,
        "salario_digno_mes_usd": 900,
        "horas_trabajo_mes": 180,
        "costo_labor_usd_por_hora": 2.94,
        "factory_markup_factor": 1.18,
        "costo_neto_manufactura_usd_por_hora": 3.47,
        "eficiencia_factor": 0.90,          # Very fast turnarounds
    },
    "MAR": {
        "pais_nombre": "Marruecos",
        "salario_minimo_mes_usd": 300,
        "salario_digno_mes_usd": 620,
        "horas_trabajo_mes": 191,
        "costo_labor_usd_por_hora": 1.57,
        "factory_markup_factor": 1.20,
        "costo_neto_manufactura_usd_por_hora": 1.88,
        "eficiencia_factor": 0.95,          # Nearshoring advantage (EU)
    },
    "PRT": {
        "pais_nombre": "Portugal",
        "salario_minimo_mes_usd": 1020,
        "salario_digno_mes_usd": 1380,
        "horas_trabajo_mes": 173,
        "costo_labor_usd_por_hora": 5.89,
        "factory_markup_factor": 1.15,
        "costo_neto_manufactura_usd_por_hora": 6.78,
        "eficiencia_factor": 0.85,          # EU automation + skilled labor
    },
    "ESP": {
        "pais_nombre": "España",
        "salario_minimo_mes_usd": 1134,
        "salario_digno_mes_usd": 1500,
        "horas_trabajo_mes": 173,
        "costo_labor_usd_por_hora": 6.56,
        "factory_markup_factor": 1.15,
        "costo_neto_manufactura_usd_por_hora": 7.55,
        "eficiencia_factor": 0.85,
    },
    "MEX": {
        "pais_nombre": "México",
        "salario_minimo_mes_usd": 260,
        "salario_digno_mes_usd": 680,
        "horas_trabajo_mes": 192,
        "costo_labor_usd_por_hora": 1.35,
        "factory_markup_factor": 1.20,
        "costo_neto_manufactura_usd_por_hora": 1.62,
        "eficiencia_factor": 0.95,          # Nearshoring to USA
    },
    "ETH": {
        "pais_nombre": "Etiopía",
        "salario_minimo_mes_usd": 26,
        "salario_digno_mes_usd": 180,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 0.12,
        "factory_markup_factor": 1.30,      # 30% (emerging market risk)
        "costo_neto_manufactura_usd_por_hora": 0.16,
        "eficiencia_factor": 1.35,          # Least efficient
    },
    "USA": {
        "pais_nombre": "Estados Unidos",
        "salario_minimo_mes_usd": 1256,
        "salario_digno_mes_usd": 2800,
        "horas_trabajo_mes": 173,
        "costo_labor_usd_por_hora": 7.26,
        "factory_markup_factor": 1.15,
        "costo_neto_manufactura_usd_por_hora": 8.35,
        "eficiencia_factor": 0.80,          # Most automated/efficient
    },
}

# ────────────────────────────────────────────────────────────────────────────
# COSTOS DE LOGÍSTICA INTERNACIONAL
# ────────────────────────────────────────────────────────────────────────────
#
# Estructura: Costos diferenciados para rutas reales manufacturing → principales mercados
#   "ISO_ORIGEN": {
#       "ISO_DESTINO": {
#           "ocean_freight_usd_por_kg": X,
#           "aranceles_pct": Y,
#           "handling_customs_usd": Z,
#       }
#   }
#
# MERCADOS DESTINO PRINCIPALES:
#   - USA: Principal mercado para Shein, Nike, Adidas, Patagonia
#   - EU: Zara, H&M, Patagonia, luxury
#   - Global e-commerce: Shein, Amazon, TikTok Shop
#
# FUENTE: WSI 2025, Mordor Intelligence 2024-2030, actual shipping quotes 2025

LOGISTICA_INTERNACIONAL = {
    # China → USA/EU (cheapest, most mature route)
    "CHN": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.12,   # Shanghai-LA, very competitive
            "air_freight_usd_por_kg": 0.60,
            "aranceles_pct": 20,                 # Trump 2025: 25% base + phase-in, we use conservative 20%
            "handling_customs_usd_por_envio": 150,  # Per shipment, ~40ft container
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.15,   # Longer route, Rotterdam/Hamburg
            "air_freight_usd_por_kg": 0.70,
            "aranceles_pct": 12,                 # EU post-2025 tariff: ~12% average
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Vietnam → USA/EU (growing route, competitive)
    "VNM": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.14,   # Slightly slower than China, competitive pricing
            "air_freight_usd_por_kg": 0.65,
            "aranceles_pct": 18,                 # Vietnam benefits from CPTPP, lower tariffs
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.16,
            "air_freight_usd_por_kg": 0.75,
            "aranceles_pct": 10,                 # Vietnam-EU trade agreement benefits
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Bangladesh → USA/EU (volume player)
    "BGD": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.13,
            "air_freight_usd_por_kg": 0.62,
            "aranceles_pct": 20,                 # Standard MFN rates
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.15,
            "air_freight_usd_por_kg": 0.72,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Pakistan (textiles hub)
    "PAK": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.13,
            "air_freight_usd_por_kg": 0.63,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.16,
            "air_freight_usd_por_kg": 0.73,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # India
    "IND": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.13,
            "air_freight_usd_por_kg": 0.64,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.16,
            "air_freight_usd_por_kg": 0.74,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Indonesia
    "IDN": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.14,
            "air_freight_usd_por_kg": 0.66,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.17,
            "air_freight_usd_por_kg": 0.76,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Thailand
    "THA": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.13,
            "air_freight_usd_por_kg": 0.65,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.16,
            "air_freight_usd_por_kg": 0.75,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Sri Lanka
    "LKA": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.13,
            "air_freight_usd_por_kg": 0.64,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.15,
            "air_freight_usd_por_kg": 0.73,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Cambodia
    "KHM": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.14,
            "air_freight_usd_por_kg": 0.65,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.17,
            "air_freight_usd_por_kg": 0.75,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # EUROPA
    # Turkey
    "TUR": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.15,   # Longer route
            "air_freight_usd_por_kg": 0.68,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.08,   # Customs union, very cheap (trucking mostly)
            "air_freight_usd_por_kg": 0.35,
            "aranceles_pct": 0,                  # EU customs union
            "handling_customs_usd_por_envio": 30,  # Minimal
            "insurance_pct": 1.0,
        },
    },
    
    # Morocco
    "MAR": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.14,
            "air_freight_usd_por_kg": 0.67,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.10,   # Nearshoring advantage
            "air_freight_usd_por_kg": 0.40,
            "aranceles_pct": 8,                  # Association Agreement benefits
            "handling_customs_usd_por_envio": 80,
            "insurance_pct": 1.0,
        },
    },
    
    # Portugal
    "PRT": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.18,
            "air_freight_usd_por_kg": 0.70,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.02,   # Direct truck/rail within EU
            "air_freight_usd_por_kg": 0.20,
            "aranceles_pct": 0,
            "handling_customs_usd_por_envio": 0,
            "insurance_pct": 0.5,
        },
    },
    
    # Spain
    "ESP": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.17,
            "air_freight_usd_por_kg": 0.69,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.02,
            "air_freight_usd_por_kg": 0.20,
            "aranceles_pct": 0,
            "handling_customs_usd_por_envio": 0,
            "insurance_pct": 0.5,
        },
    },
    
    # USA (domestic)
    "USA": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.08,   # Domestic trucking, much cheaper
            "air_freight_usd_por_kg": 0.35,
            "aranceles_pct": 0,
            "handling_customs_usd_por_envio": 0,
            "insurance_pct": 0.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.20,
            "air_freight_usd_por_kg": 0.80,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Mexico
    "MEX": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.10,   # Nearshoring: trucking cheaper
            "air_freight_usd_por_kg": 0.45,
            "aranceles_pct": 0,                  # USMCA duty-free on qualifying origin
            "handling_customs_usd_por_envio": 50,
            "insurance_pct": 1.0,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.18,
            "air_freight_usd_por_kg": 0.75,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    
    # Ethiopia
    "ETH": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.13,
            "air_freight_usd_por_kg": 0.63,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.16,
            "air_freight_usd_por_kg": 0.73,
            "aranceles_pct": 0,                  # EBA (Everything But Arms) preferences
            "handling_customs_usd_por_envio": 50,
            "insurance_pct": 1.5,
        },
    },
}

# ────────────────────────────────────────────────────────────────────────────
# PRENDAS: ESPECIFICACIONES Y HORAS DE MANUFACTURA
# ────────────────────────────────────────────────────────────────────────────

PRENDAS = {
    "playera":  {
        "label": "Playera",
        "horas_manufactura": 0.5,           # Simple garment, quick assembly
        "complejidad_relativa": 1.0,        # Baseline
    },
    "jeans":    {
        "label": "Jeans",
        "horas_manufactura": 1.5,           # Multiple operations: cutting, riveting, hemming
        "complejidad_relativa": 2.0,        # 2× baseline complexity
    },
    "sudadera": {
        "label": "Sudadera",
        "horas_manufactura": 1.2,
        "complejidad_relativa": 1.5,        # Hood, drawstring, etc.
    },
    "vestido":  {
        "label": "Vestido",
        "horas_manufactura": 2.0,
        "complejidad_relativa": 2.5,        # Seams, darts, potential pattern matching
    },
    "chamarra": {
        "label": "Chamarra",
        "horas_manufactura": 3.0,           # Lining, zipper, collar, patches
        "complejidad_relativa": 3.5,        # Most complex
    },
}

# ────────────────────────────────────────────────────────────────────────────
# CONSTANTES GLOBALES
# ────────────────────────────────────────────────────────────────────────────

TC_MXN = 17.5                               # USD → MXN conversion (May 2025)

# Environmental remediation costs (from Markov module)
COSTO_CO2_MXN_POR_KG = 0.175                # $10 USD/ton CO₂ → MXN/kg
COSTO_AGUA_MXN_POR_LT = 0.004               # Wastewater treatment MX

# Retail structure
MARGEN_MINORISTA_DTC_PCT = 0.65             # DTC gross margin: 65% (60-75% range)
MARGEN_MINORISTA_WHOLESALE_PCT = 0.45       # Wholesale markup: 45% (40-50% range)
MARKUP_FACTOR_RETAIL = 2.8                  # Typical fashion: 2.5-3.5× landed cost

# Global defaults
MARGEN_REINVERSION_DEFAULT = 0.15           # 15% margin for "ethical" reinvestment

# Average returns & discounting impact (reduces realized margin)
TASA_DEVOLUCIONES_ECOMMERCE = 0.208         # 20.8% apparel returns rate
COSTO_PROCESAMIENTO_DEVOLUCIONES_PCT = 0.66  # 66% of original COGS to process return
