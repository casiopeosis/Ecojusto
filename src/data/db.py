# data/db.py  — v4
# CAMBIO PRINCIPAL:
# - 'iso_pais' reemplazado por 'manufactura': dict {ISO3: fracción} con la
#   distribución real de producción por país de cada empresa.
#   Fuentes por empresa documentadas abajo.
# - Se agrega "LKA" (Sri Lanka) a SALARIOS_PAIS para Patagonia.
# - Se agrega "TUR" (Turquía) para H&M y Zara.
#
# FUENTES DE DISTRIBUCIÓN:
#   Shein:    ~95% China (FASH455 / US-China Economic Security Review 2023)
#   H&M:      China+Bangladesh dominan; India, Vietnam, Turquía secundarios
#             (Wikipedia H&M; NewAsiaGarment supplier breakdown 2024)
#   Zara:     Portugal/España ~40%, Marruecos+Turquía ~25%, Asia ~35%
#             (Inditex Annual Report 2023)
#   Nike:     Vietnam ~50%, Indonesia ~20%, China ~18% (Nike FY2024 10-K)
#   Patagonia: Sri Lanka ~40%, Vietnam ~30%, Bangladesh ~20% (FTM investigation 2023)
#   Levi's:   Bangladesh ~30%, México ~20%, Pakistan ~20%, otros (Levi's SR 2023)
#   Primark:  China ~35%, Bangladesh ~25%, India ~20%, otros (Statista Oct 2024)
#   Adidas:   Vietnam 27%, Indonesia 19%, China 16%, otros Asia (Adidas AR 2024)

EMPRESAS = [
    {
        "nombre":        "Shein",
        "transparencia": 0.05,
        "manufactura": {
            "CHN": 0.95,
            "VNM": 0.05,
        },
        "precios": {
            "playera":  149, "jeans": 299, "sudadera": 249,
            "vestido":  199, "chamarra": 449,
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
            "playera":  199, "jeans": 399, "sudadera": 349,
            "vestido":  299, "chamarra": 699,
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
            "playera":  349, "jeans": 699, "sudadera": 599,
            "vestido":  549, "chamarra": 1299,
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
            "playera":  499, "jeans": 999, "sudadera": 849,
            "vestido":  799, "chamarra": 2199,
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
            "playera":  699, "jeans": 1299, "sudadera": 1099,
            "vestido":  899, "chamarra": 2499,
        },
    },
    {
        "nombre":        "Adidas",
        "transparencia": 0.74,
        "manufactura": {
            "VNM": 0.27,
            "IDN": 0.19,
            "CHN": 0.16,
            "KHM": 0.15,   # Cambodia
            "PAK": 0.13,
            "IND": 0.10,
        },
        "precios": {
            "playera":  749, "jeans": 1499, "sudadera": 1199,
            "vestido":  999, "chamarra": 2799,
        },
    },
    {
        "nombre":        "Levi's",
        "transparencia": 0.70,
        "manufactura": {
            "BGD": 0.30,
            "MEX": 0.20,
            "PAK": 0.20,
            "ETH": 0.15,   # Ethiopia — nueva base de manufactura
            "IND": 0.15,
        },
        "precios": {
            "playera":  599, "jeans": 1299, "sudadera": 999,
            "vestido":  899, "chamarra": 2299,
        },
    },
    {
        "nombre":        "Patagonia",
        "transparencia": 0.92,
        "manufactura": {
            "LKA": 0.40,   # Sri Lanka — 14 fábricas (FTM 2023)
            "VNM": 0.30,
            "BGD": 0.20,
            "USA": 0.10,
        },
        "precios": {
            "playera":  1299, "jeans": 3499, "sudadera": 2999,
            "vestido":  2499, "chamarra": 8999,
        },
    },
]

# ── Salarios por país de manufactura ─────────────────────────────────────────
TC_MXN = 17.5  # USD → MXN, Mayo 2025

SALARIOS_PAIS = {
    "CHN": {"pais_nombre": "China",         "salario_minimo_usd": 290,  "salario_digno_usd": 650,  "horas_mes": 200},
    "BGD": {"pais_nombre": "Bangladesh",    "salario_minimo_usd": 113,  "salario_digno_usd": 490,  "horas_mes": 208},
    "PRT": {"pais_nombre": "Portugal",      "salario_minimo_usd": 1020, "salario_digno_usd": 1380, "horas_mes": 173},
    "ESP": {"pais_nombre": "España",        "salario_minimo_usd": 1134, "salario_digno_usd": 1500, "horas_mes": 173},
    "VNM": {"pais_nombre": "Vietnam",       "salario_minimo_usd": 180,  "salario_digno_usd": 420,  "horas_mes": 208},
    "USA": {"pais_nombre": "Estados Unidos","salario_minimo_usd": 1256, "salario_digno_usd": 2800, "horas_mes": 173},
    "MEX": {"pais_nombre": "México",        "salario_minimo_usd": 260,  "salario_digno_usd": 680,  "horas_mes": 192},
    "IND": {"pais_nombre": "India",         "salario_minimo_usd": 130,  "salario_digno_usd": 380,  "horas_mes": 208},
    "IDN": {"pais_nombre": "Indonesia",     "salario_minimo_usd": 220,  "salario_digno_usd": 510,  "horas_mes": 200},
    "PAK": {"pais_nombre": "Pakistán",      "salario_minimo_usd": 110,  "salario_digno_usd": 350,  "horas_mes": 208},
    "TUR": {"pais_nombre": "Turquía",       "salario_minimo_usd": 530,  "salario_digno_usd": 900,  "horas_mes": 180},
    "MAR": {"pais_nombre": "Marruecos",     "salario_minimo_usd": 300,  "salario_digno_usd": 620,  "horas_mes": 191},
    "LKA": {"pais_nombre": "Sri Lanka",     "salario_minimo_usd": 115,  "salario_digno_usd": 400,  "horas_mes": 200},
    "KHM": {"pais_nombre": "Cambodia",      "salario_minimo_usd": 200,  "salario_digno_usd": 450,  "horas_mes": 208},
    "THA": {"pais_nombre": "Tailandia",     "salario_minimo_usd": 310,  "salario_digno_usd": 620,  "horas_mes": 200},
    "ETH": {"pais_nombre": "Etiopía",       "salario_minimo_usd":  26,  "salario_digno_usd": 180,  "horas_mes": 208},
}

# ── Materiales ────────────────────────────────────────────────────────────────
MATERIALES = {
    "poliester": {
        "key": "poliester", "label": "Poliéster", "vida_base": 6,
        "huella_hidrica_litros_kg": 62, "co2_kg_por_kg_fibra": 14.2,
        "peso_prenda_kg": {"playera": 0.20, "jeans": 0.60, "sudadera": 0.45, "vestido": 0.35, "chamarra": 0.80},
    },
    "algodon_conv": {
        "key": "algodon_conv", "label": "Algodón convencional", "vida_base": 14,
        "huella_hidrica_litros_kg": 10000, "co2_kg_por_kg_fibra": 4.7,
        "peso_prenda_kg": {"playera": 0.20, "jeans": 0.65, "sudadera": 0.50, "vestido": 0.35, "chamarra": 0.85},
    },
    "algodon_org": {
        "key": "algodon_org", "label": "Algodón orgánico", "vida_base": 20,
        "huella_hidrica_litros_kg": 6000, "co2_kg_por_kg_fibra": 3.0,
        "peso_prenda_kg": {"playera": 0.20, "jeans": 0.65, "sudadera": 0.50, "vestido": 0.35, "chamarra": 0.85},
    },
    "lana": {
        "key": "lana", "label": "Lana", "vida_base": 30,
        "huella_hidrica_litros_kg": 17000, "co2_kg_por_kg_fibra": 26.0,
        "peso_prenda_kg": {"playera": 0.25, "jeans": 0.70, "sudadera": 0.55, "vestido": 0.40, "chamarra": 1.00},
    },
    "viscosa": {
        "key": "viscosa", "label": "Viscosa", "vida_base": 8,
        "huella_hidrica_litros_kg": 3000, "co2_kg_por_kg_fibra": 6.5,
        "peso_prenda_kg": {"playera": 0.18, "jeans": 0.55, "sudadera": 0.42, "vestido": 0.30, "chamarra": 0.75},
    },
}

# ── Prendas ───────────────────────────────────────────────────────────────────
PRENDAS = {
    "playera":  {"label": "Playera",  "horas_manufactura": 0.5},
    "jeans":    {"label": "Jeans",    "horas_manufactura": 1.5},
    "sudadera": {"label": "Sudadera", "horas_manufactura": 1.2},
    "vestido":  {"label": "Vestido",  "horas_manufactura": 2.0},
    "chamarra": {"label": "Chamarra", "horas_manufactura": 3.0},
}

# ── Constantes globales ───────────────────────────────────────────────────────
COSTO_CO2_MXN_POR_KG   = 0.175   # ~$10 USD/ton CO₂ → MXN/kg
COSTO_AGUA_MXN_POR_LT  = 0.004   # tratamiento agua residual MX
MARGEN_REINVERSION_DEFAULT = 0.15
