# llm/narrativa.py
# Módulo opcional — Narrativa explicativa via Claude API
#
# Genera un párrafo interpretativo del resultado para el dashboard.
# Requiere ANTHROPIC_API_KEY en .env. Si no está disponible, retorna None
# sin romper el flujo principal.

import os
import anthropic


def generar_narrativa(resultados: list[dict], material_label: str, prenda_label: str) -> str | None:
    """
    Genera una narrativa periodística breve (3-4 oraciones) que interpreta
    los resultados del dashboard comparativo.

    Args:
        resultados:     lista de dicts devuelta por run_all()
        material_label: nombre legible del material (e.g. "Poliéster")
        prenda_label:   nombre legible de la prenda  (e.g. "Playera")

    Returns:
        str con la narrativa, o None si no hay API key configurada.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    # Preparar resumen compacto para el prompt
    resumen = "\n".join(
        f"- {r['empresa']}: P_justo=${r['p_justo']} MXN "
        f"(etiqueta=${r['precio_etiqueta']}, α={r['alpha_e']}, "
        f"C_amb=${r['c_ambiental']}, C_soc=${r['c_social']}, "
        f"transparencia={r['transparencia_pct']}%)"
        for r in resultados
    )

    prompt = f"""Eres un periodista de datos especializado en sostenibilidad y moda.
Se calculó el precio justo real de una {prenda_label} de {material_label} para 8 marcas,
incluyendo costos ambientales y sociales ocultos. Aquí están los resultados:

{resumen}

Escribe exactamente 3-4 oraciones en español, en tono periodístico directo y sin tecnicismos,
que interpreten los hallazgos más llamativos: qué empresa sale peor, cuál mejor, y la brecha
entre precio de etiqueta y precio justo real. No uses listas ni encabezados."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        print(f"[llm/narrativa] Error al llamar a la API: {e}")
        return None
