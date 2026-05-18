# data/world_bank.py
# Módulo de datos laborales en tiempo real — API del Banco Mundial
#
# No requiere API key. Gratuita y pública.
# Documentación: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581
#
# Indicadores usados:
#   SL.EMP.VULN.ZS  — Trabajadores vulnerables (% del empleo total)
#                     Incluye trabajadores por cuenta propia y familiares
#                     no remunerados. Alta correlación con precariedad laboral.
#   SL.UEM.TOTL.ZS  — Desempleo total (% de la fuerza laboral, estimación OIT)
#
# Lógica de fallback:
#   Si la API no responde (timeout, sin internet, país sin datos),
#   se usa el diccionario FALLBACK_RIESGO con valores precalculados.

import requests
from functools import lru_cache

WB_BASE = (
    "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}"
    "?format=json&mrv=5&gapfill=Y"
)

# Indicadores del Banco Mundial
IND_VULNERABILIDAD = "SL.EMP.VULN.ZS"
IND_DESEMPLEO      = "SL.UEM.TOTL.ZS"

# Fallback si la API no responde.
# Fuente: Banco Mundial 2022-2023 (preprocesado manualmente).
FALLBACK_RIESGO = {
    "CHN": 1.75,  # China — alta vulnerabilidad laboral, restricciones sindicales
    "BGD": 1.80,  # Bangladesh — industria textil con condiciones críticas
    "PRT": 0.65,  # Portugal — dentro de la UE, protección laboral media-alta
    "VNM": 1.40,  # Vietnam — creciente manufactura, protección laboral limitada
    "USA": 0.30,  # EE.UU. — alta protección, salarios dignos
    "MEX": 1.00,  # México — manufactura mixta, reformas laborales recientes
    "IND": 1.70,  # India — alta vulnerabilidad, informalidad elevada
    "IDN": 1.30,  # Indonesia — manufactura en expansión, protección media
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

    Fórmula:
        factor = 0.7 × (vulnerabilidad / 50) + 0.3 × (desempleo / 5)

    Donde:
      - vulnerabilidad: % trabajadores vulnerables (referencia: 50% = promedio mundial)
      - desempleo:      % desempleo total         (referencia:  5% = promedio mundial)

    El resultado se normaliza al rango [0.3, 2.0]:
      - 0.3 = condiciones laborales excelentes (Países Nórdicos, USA)
      - 1.0 = condiciones promedio
      - 2.0 = condiciones muy precarias (Bangladesh, Myanmar)

    Si la API no responde, usa FALLBACK_RIESGO.

    Args:
        iso_pais: código ISO3 del país (e.g. "CHN", "BGD")

    Returns:
        float en [0.3, 2.0]
    """
    vuln   = _fetch_indicador(iso_pais, IND_VULNERABILIDAD)
    desemp = _fetch_indicador(iso_pais, IND_DESEMPLEO)

    if vuln is None and desemp is None:
        return FALLBACK_RIESGO.get(iso_pais, 1.0)

    factor_vuln  = (vuln   or 50.0) / 50.0
    factor_desemp = (desemp or 5.0) / 5.0
    raw = 0.7 * factor_vuln + 0.3 * factor_desemp
    return round(min(max(raw, 0.3), 2.0), 2)


def get_datos_pais(iso_pais: str) -> dict:
    """
    Retorna un dict con los datos laborales crudos del país para mostrar
    en el dashboard (transparencia al usuario sobre la fuente).

    Returns:
        {
          "iso": str,
          "vulnerabilidad_pct": float | None,
          "desempleo_pct":      float | None,
          "factor_riesgo":      float,
          "fuente":             "API Banco Mundial" | "Fallback"
        }
    """
    vuln   = _fetch_indicador(iso_pais, IND_VULNERABILIDAD)
    desemp = _fetch_indicador(iso_pais, IND_DESEMPLEO)
    fuente = "API Banco Mundial" if (vuln is not None or desemp is not None) else "Fallback"
    factor = get_factor_riesgo_pais(iso_pais)

    return {
        "iso":                 iso_pais,
        "vulnerabilidad_pct":  round(vuln,   1) if vuln   is not None else None,
        "desempleo_pct":       round(desemp, 1) if desemp is not None else None,
        "factor_riesgo":       factor,
        "fuente":              fuente,
    }
