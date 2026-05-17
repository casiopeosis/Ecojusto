# data/db.py
# Base de datos estática — EcoJusto AI
# Fuentes: Fashion Transparency Index 2023, CSI Global Rights Index, OIT

EMPRESAS = [
    {"nombre": "Shein",         "transparencia": 0.05, "pais_riesgo": 1.8},
    {"nombre": "H&M",           "transparencia": 0.62, "pais_riesgo": 1.2},
    {"nombre": "Zara (Inditex)","transparencia": 0.55, "pais_riesgo": 1.1},
    {"nombre": "Nike",          "transparencia": 0.68, "pais_riesgo": 1.0},
    {"nombre": "Patagonia",     "transparencia": 0.92, "pais_riesgo": 0.3},
    {"nombre": "Levi's",        "transparencia": 0.70, "pais_riesgo": 0.8},
    {"nombre": "Primark",       "transparencia": 0.22, "pais_riesgo": 1.5},
    {"nombre": "Adidas",        "transparencia": 0.74, "pais_riesgo": 1.0},
]

MATERIALES = {
    "poliester": {
        "label": "Poliéster",
        "vida_base": 6,
        "costo_remediacion": 280,
    },
    "algodon_conv": {
        "label": "Algodón convencional",
        "vida_base": 14,
        "costo_remediacion": 180,
    },
    "algodon_org": {
        "label": "Algodón orgánico",
        "vida_base": 20,
        "costo_remediacion": 120,
    },
    "lana": {
        "label": "Lana",
        "vida_base": 30,
        "costo_remediacion": 100,
    },
    "viscosa": {
        "label": "Viscosa",
        "vida_base": 8,
        "costo_remediacion": 220,
    },
}

PRENDAS = {
    "playera": {
        "label": "Playera",
        "precio_base": 280,
        "brecha_oit": 0.45,
    },
    "jeans": {
        "label": "Jeans",
        "precio_base": 650,
        "brecha_oit": 0.50,
    },
    "sudadera": {
        "label": "Sudadera",
        "precio_base": 480,
        "brecha_oit": 0.48,
    },
    "vestido": {
        "label": "Vestido",
        "precio_base": 520,
        "brecha_oit": 0.42,
    },
    "chamarra": {
        "label": "Chamarra",
        "precio_base": 1100,
        "brecha_oit": 0.55,
    },
}
