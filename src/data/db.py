# data/db.py
# Base de datos estática — EcoJusto AI
# Fuentes: Fashion Transparency Index 2023, CSI Global Rights Index, OIT
#
# CAMBIOS v2:
# - 'pais_riesgo' eliminado; reemplazado por 'iso_pais' (ISO3)
#   El factor de riesgo ahora se consulta en tiempo real desde la API
#   del Banco Mundial (data/world_bank.py). Si la API no responde,
#   world_bank.py tiene un fallback hardcodeado por iso_pais.
# - Materiales ahora incluyen 'key' para que markov.py acceda a las
#   probabilidades de desecho base por material.

EMPRESAS = [
    {"nombre": "Shein",          "transparencia": 0.05, "iso_pais": "CHN"},
    {"nombre": "H&M",            "transparencia": 0.62, "iso_pais": "BGD"},
    {"nombre": "Zara (Inditex)", "transparencia": 0.55, "iso_pais": "PRT"},
    {"nombre": "Nike",           "transparencia": 0.68, "iso_pais": "VNM"},
    {"nombre": "Patagonia",      "transparencia": 0.92, "iso_pais": "USA"},
    {"nombre": "Levi's",         "transparencia": 0.70, "iso_pais": "MEX"},
    {"nombre": "Primark",        "transparencia": 0.22, "iso_pais": "IND"},
    {"nombre": "Adidas",         "transparencia": 0.74, "iso_pais": "IDN"},
]

MATERIALES = {
    "poliester": {
        "key":               "poliester",
        "label":             "Poliéster",
        "vida_base":         6,
        "costo_remediacion": 280,
    },
    "algodon_conv": {
        "key":               "algodon_conv",
        "label":             "Algodón convencional",
        "vida_base":         14,
        "costo_remediacion": 180,
    },
    "algodon_org": {
        "key":               "algodon_org",
        "label":             "Algodón orgánico",
        "vida_base":         20,
        "costo_remediacion": 120,
    },
    "lana": {
        "key":               "lana",
        "label":             "Lana",
        "vida_base":         30,
        "costo_remediacion": 100,
    },
    "viscosa": {
        "key":               "viscosa",
        "label":             "Viscosa",
        "vida_base":         8,
        "costo_remediacion": 220,
    },
}

PRENDAS = {
    "playera": {
        "label":       "Playera",
        "precio_base": 280,
        "brecha_oit":  0.45,
    },
    "jeans": {
        "label":       "Jeans",
        "precio_base": 650,
        "brecha_oit":  0.50,
    },
    "sudadera": {
        "label":       "Sudadera",
        "precio_base": 480,
        "brecha_oit":  0.48,
    },
    "vestido": {
        "label":       "Vestido",
        "precio_base": 520,
        "brecha_oit":  0.42,
    },
    "chamarra": {
        "label":       "Chamarra",
        "precio_base": 1100,
        "brecha_oit":  0.55,
    },
}
