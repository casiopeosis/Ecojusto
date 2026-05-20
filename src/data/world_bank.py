# data/world_bank.py — v5 (Corregido y Completo)
# ════════════════════════════════════════════════════════════════════════════════
# Módulo de datos laborales en tiempo real — API del Banco Mundial

import requests
from functools import lru_cache

WB_BASE = (
    "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}"
    "?format=json&mrv=5&gapfill=Y"
)

# Indicadores del Banco Mundial
IND_VULNERABILIDAD = "SL.EMP.VULN.ZS"
IND_DESEMPLEO = "SL.UEM.TOTL.ZS"

# Fallback completo para TODOS los países presentes en db.py
# Escala normalizada en rango [0.3, 2.0] basada en la OIT y Banco Mundial
FALLBACK_RIESGO = {
    "CHN": 1.75,  # China — Alta vulnerabilidad, restricciones sindicales
    "BGD": 1.80,  # Bangladesh — Condiciones críticas en sector maquila
    "PRT": 0.65,  # Portugal — Protección laboral media-alta (UE)
    "ESP": 0.50,  # España — Alta protección laboral institucional
    "VNM": 1.40,  # Vietnam — Manufactura en expansión, libertades colectivas limitadas
    "USA": 0.30,  # EE.UU. — Estructura de salarios altos, bajo desempleo relativo
    "MEX": 1.00,  # México — Manufactura mixta, reformas recientes de outsourcing
    "IND": 1.70,  # India — Alta informalidad y vulnerabilidad laboral
    "IDN": 1.30,  # Indonesia — Protección laboral media, volatilidad sectorial
    "PAK": 1.65,  # Pakistán — Vulnerabilidad alta en cadena textil profunda
    "TUR": 1.10,  # Turquía — Protección media, alta inflación e informalidad refugiada
    "MAR": 1.20,  # Marruecos — Cercanía textil a Europa, sindicatos moderados
    "LKA": 1.45,  # Sri Lanka — Alta volatilidad económica reciente
    "KHM": 1.60,  # Cambodia — Dependencia absoluta de maquila, riesgos de seguridad
    "THA": 1.05,  # Tailandia — Desempleo muy bajo registrado, pero informalidad presente
    "ETH": 1.90,  # Etiopía — Salarios base extremadamente bajos, zonas económicas vulnerables
}


@lru_cache(maxsize=64)
def _fetch_indicador(iso_pais: str, indicador: str) -> float | None:
    """
    Consulta un indicador del Banco Mundial para un país ISO3.
    Cachea el resultado en memoria para no repetir llamadas en la misma sesión.
    Retorna el valor más reciente no nulo, o None si no hay datos.
    """
    url = WB_BASE.format(iso=iso_pais, ind=indicador)
    try:
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        payload = resp.json()
        # payload[0] = metadata, payload[1] = lista de registros
        registros = payload[1] if len(payload) > 1 else []
        if not registros:
            return None
        for reg in registros:
            if reg.get("value") is not None:
                return float(reg["value"])
    except Exception:
        pass
    return None


def get_factor_riesgo_pais(iso_pais: str) -> float:
    """
    Calcula un factor de riesgo laboral en el rango [0.3, 2.0] para un país.
    Fórmula: factor = 0.7 × (vulnerabilidad / 50) + 0.3 × (desempleo / 5)
    """
    vuln = _fetch_indicador(iso_pais, IND_VULNERABILIDAD)
    desemp = _fetch_indicador(iso_pais, IND_DESEMPLEO)

    # Si faltan ambos o la API falla por completo, jalar del diccionario extendido
    if vuln is None and desemp is None:
        return FALLBACK_RIESGO.get(iso_pais, 1.0)

    # Si solo falta uno, usar promedios globales como ancla segura para evitar desproporciones
    factor_vuln = (vuln if vuln is not None else 50.0) / 50.0
    factor_desemp = (desemp if desemp is not None else 5.0) / 5.0

    raw = 0.7 * factor_vuln + 0.3 * factor_desemp
    return round(min(max(raw, 0.3), 2.0), 2)


def get_datos_pais(iso_pais: str) -> dict:
    """
    Retorna un dict con los datos laborales crudos del país para mostrar en el dashboard.
    Garantiza valores por defecto si la API devuelve parciales o nulos.
    """
    vuln = _fetch_indicador(iso_pais, IND_VULNERABILIDAD)
    desemp = _fetch_indicador(iso_pais, IND_DESEMPLEO)

    # Determinar fuente de manera estricta
    fuente = (
        "API Banco Mundial" if (vuln is not None and desemp is not None) else "Fallback"
    )
    factor = get_factor_riesgo_pais(iso_pais)

    return {
        "iso": iso_pais,
        "vulnerabilidad_pct": round(vuln, 1) if vuln is not None else 50.0,
        "desempleo_pct": round(desemp, 1) if desemp is not None else 5.0,
        "factor_riesgo": factor,
        "fuente": fuente,
    }
