# data/db.py  — v5 (COMPLETE COST STRUCTURE OVERHAUL)
# ════════════════════════════════════════════════════════════════════════════════
# 
# INVESTIGACIÓN INTEGRAL DE COSTOS (2024-2025):
# Fuentes verificables: Fibre2Fashion, ITMF, WSI, Cosmo Sourcing, AIMS360, Uphance
# Todos los precios reflejan realidad de industria Q4 2024 - Q2 2025

EMPRESAS = [
    {
        "nombre":        "Shein",
        "transparencia": 0.05,
        "manufactura": {
            "CHN": 0.95,
            "VNM": 0.05,
        },
        "precios": {
            "playera":  149,
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

MATERIALES = {
    "poliester": {
        "key": "poliester",
        "label": "Poliéster",
        
        # Costo de fibra virgen PSF (polyester staple fiber) por kg
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
        
        # Costo de acabado/teñido/impresión de tela (USD por metro cuadrado)
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
            "ETH": 0.18,
            "USA": 0.65,
        },
        
        # Costo trims + empaque por prenda (USD)
        "costo_trims_empaque_usd": 0.25,
        
        # Peso de la tela por tipo de prenda (kg)
        "peso_prenda_kg": {
            "playera":  0.20,
            "jeans":    0.60,
            "sudadera": 0.45,
            "vestido":  0.35,
            "chamarra": 0.80,
        },
        
        # Métricas ambientales
        "huella_hidrica_litros_kg": 62,
        "co2_kg_por_kg_fibra": 14.2,
    },
    
    "algodon_conv": {
        "key": "algodon_conv",
        "label": "Algodón convencional",
        
        "costo_fibra_usd_por_kg": {
            "CHN": 2.50,
            "VNM": 2.65,
            "BGD": 2.55,
            "PAK": 2.45,
            "IND": 2.70,
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
        
        "costo_acabado_usd_por_m": {
            "CHN": 0.50,
            "VNM": 0.40,
            "BGD": 0.70,
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
        
        "huella_hidrica_litros_kg": 10000,
        "co2_kg_por_kg_fibra": 4.7,
    },
    
    "algodon_org": {
        "key": "algodon_org",
        "label": "Algodón orgánico",
        
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
        
        "costo_trims_empaque_usd": 0.30,
        
        "peso_prenda_kg": {
            "playera":  0.20,
            "jeans":    0.65,
            "sudadera": 0.50,
            "vestido":  0.35,
            "chamarra": 0.85,
        },
        
        "huella_hidrica_litros_kg": 6000,
        "co2_kg_por_kg_fibra": 3.0,
    },
    
    "lana": {
        "key": "lana",
        "label": "Lana",
        
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
        
        "costo_trims_empaque_usd": 0.35,
        
        "peso_prenda_kg": {
            "playera":  0.25,
            "jeans":    0.70,
            "sudadera": 0.55,
            "vestido":  0.40,
            "chamarra": 1.00,
        },
        
        "huella_hidrica_litros_kg": 17000,
        "co2_kg_por_kg_fibra": 26.0,
    },
    
    "viscosa": {
        "key": "viscosa",
        "label": "Viscosa (Rayón)",
        
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
        
        "huella_hidrica_litros_kg": 3000,
        "co2_kg_por_kg_fibra": 6.5,
    },
}

# ────────────────────────────────────────────────────────────────────────────
# COSTOS DE MANUFACTURA (LABOR + OVERHEAD) POR PAÍS
# ────────────────────────────────────────────────────────────────────────────

COSTOS_MANUFACTURA_POR_PAIS = {
    "CHN": {
        "pais_nombre": "China",
        "salario_minimo_mes_usd": 450,
        "salario_digno_mes_usd": 1050,
        "horas_trabajo_mes": 200,
        "costo_labor_usd_por_hora": 2.25,
        "factory_markup_factor": 1.20,
        "costo_neto_manufactura_usd_por_hora": 2.70,
        "eficiencia_factor": 1.0,
    },
    "VNM": {
        "pais_nombre": "Vietnam",
        "salario_minimo_mes_usd": 300,
        "salario_digno_mes_usd": 420,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 1.44,
        "factory_markup_factor": 1.22,
        "costo_neto_manufactura_usd_por_hora": 1.76,
        "eficiencia_factor": 1.05,
    },
    "BGD": {
        "pais_nombre": "Bangladesh",
        "salario_minimo_mes_usd": 113,
        "salario_digno_mes_usd": 490,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 0.54,
        "factory_markup_factor": 1.25,
        "costo_neto_manufactura_usd_por_hora": 0.68,
        "eficiencia_factor": 1.15,
    },
    "PAK": {
        "pais_nombre": "Pakistán",
        "salario_minimo_mes_usd": 110,
        "salario_digno_mes_usd": 350,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 0.53,
        "factory_markup_factor": 1.25,
        "costo_neto_manufactura_usd_por_hora": 0.66,
        "eficiencia_factor": 1.20,
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
        "eficiencia_factor": 0.98,
    },
    "LKA": {
        "pais_nombre": "Sri Lanka",
        "salario_minimo_mes_usd": 115,
        "salario_digno_mes_usd": 400,
        "horas_trabajo_mes": 200,
        "costo_labor_usd_por_hora": 0.58,
        "factory_markup_factor": 1.24,
        "costo_neto_manufactura_usd_por_hora": 0.72,
        "eficiencia_factor": 1.00,
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
        "eficiencia_factor": 0.90,
    },
    "MAR": {
        "pais_nombre": "Marruecos",
        "salario_minimo_mes_usd": 300,
        "salario_digno_mes_usd": 620,
        "horas_trabajo_mes": 191,
        "costo_labor_usd_por_hora": 1.57,
        "factory_markup_factor": 1.20,
        "costo_neto_manufactura_usd_por_hora": 1.88,
        "eficiencia_factor": 0.95,
    },
    "PRT": {
        "pais_nombre": "Portugal",
        "salario_minimo_mes_usd": 1020,
        "salario_digno_mes_usd": 1380,
        "horas_trabajo_mes": 173,
        "costo_labor_usd_por_hora": 5.89,
        "factory_markup_factor": 1.15,
        "costo_neto_manufactura_usd_por_hora": 6.78,
        "eficiencia_factor": 0.85,
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
        "eficiencia_factor": 0.95,
    },
    "ETH": {
        "pais_nombre": "Etiopía",
        "salario_minimo_mes_usd": 26,
        "salario_digno_mes_usd": 180,
        "horas_trabajo_mes": 208,
        "costo_labor_usd_por_hora": 0.12,
        "factory_markup_factor": 1.30,
        "costo_neto_manufactura_usd_por_hora": 0.16,
        "eficiencia_factor": 1.35,
    },
    "USA": {
        "pais_nombre": "Estados Unidos",
        "salario_minimo_mes_usd": 1256,
        "salario_digno_mes_usd": 2800,
        "horas_trabajo_mes": 173,
        "costo_labor_usd_por_hora": 7.26,
        "factory_markup_factor": 1.15,
        "costo_neto_manufactura_usd_por_hora": 8.35,
        "eficiencia_factor": 0.80,
    },
}

# ────────────────────────────────────────────────────────────────────────────
# COSTOS DE LOGÍSTICA INTERNACIONAL POR RUTA
# ────────────────────────────────────────────────────────────────────────────

LOGISTICA_INTERNACIONAL = {
    "CHN": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.12,
            "air_freight_usd_por_kg": 0.60,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.15,
            "air_freight_usd_por_kg": 0.70,
            "aranceles_pct": 12,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    "VNM": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.14,
            "air_freight_usd_por_kg": 0.65,
            "aranceles_pct": 18,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.16,
            "air_freight_usd_por_kg": 0.75,
            "aranceles_pct": 10,
            "handling_customs_usd_por_envio": 200,
            "insurance_pct": 1.5,
        },
    },
    "BGD": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.13,
            "air_freight_usd_por_kg": 0.62,
            "aranceles_pct": 20,
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
    "TUR": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.15,
            "air_freight_usd_por_kg": 0.68,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.08,
            "air_freight_usd_por_kg": 0.35,
            "aranceles_pct": 0,
            "handling_customs_usd_por_envio": 30,
            "insurance_pct": 1.0,
        },
    },
    "MAR": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.14,
            "air_freight_usd_por_kg": 0.67,
            "aranceles_pct": 20,
            "handling_customs_usd_por_envio": 150,
            "insurance_pct": 1.5,
        },
        "EU": {
            "ocean_freight_usd_por_kg": 0.10,
            "air_freight_usd_por_kg": 0.40,
            "aranceles_pct": 8,
            "handling_customs_usd_por_envio": 80,
            "insurance_pct": 1.0,
        },
    },
    "PRT": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.18,
            "air_freight_usd_por_kg": 0.70,
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
    "USA": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.08,
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
    "MEX": {
        "USA": {
            "ocean_freight_usd_por_kg": 0.10,
            "air_freight_usd_por_kg": 0.45,
            "aranceles_pct": 0,
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
            "aranceles_pct": 0,
            "handling_customs_usd_por_envio": 50,
            "insurance_pct": 1.5,
        },
    },
}

# ────────────────────────────────────────────────────────────────────────────
# PRENDAS: ESPECIFICACIONES
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
# CONSTANTES GLOBALES
# ────────────────────────────────────────────────────────────────────────────

TC_MXN = 17.5
COSTO_CO2_MXN_POR_KG = 0.175
COSTO_AGUA_MXN_POR_LT = 0.004
MARGEN_REINVERSION_DEFAULT = 0.15
MARKUP_FACTOR_RETAIL_DEFAULT = 2.8