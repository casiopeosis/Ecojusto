# frontend/app.py
# Dashboard interactivo — EcoJusto AI
# Streamlit + Plotly Express
#
# CAMBIOS v2:
# - Bug corregido: penalizacion_opacidad ahora viene directo del backend
#   (antes se calculaba en el frontend y siempre daba 0).
# - Nueva sección: "Datos laborales por país" con fuente del Banco Mundial.
# - Scatter plot mejorado: tamaño de burbuja = factor_riesgo_pais.
# - Spinner mientras se consulta la API del Banco Mundial al arrancar.

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

from data.db import MATERIALES, PRENDAS
from data.world_bank import get_datos_pais
from algoritmo.ensamblaje import run_all
from llm.narrativa import generar_narrativa

load_dotenv()

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoJusto AI",
    page_icon="🌿",
    layout="wide",
)

st.title("🌿 EcoJusto AI")
st.caption(
    "Auditor algorítmico de externalidades socioambientales en la industria de la moda"
)

# ── Sidebar: inputs ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parámetros")

    material_key = st.selectbox(
        "Material",
        options=list(MATERIALES.keys()),
        format_func=lambda k: MATERIALES[k]["label"],
    )
    prenda_key = st.selectbox(
        "Tipo de prenda",
        options=list(PRENDAS.keys()),
        format_func=lambda k: PRENDAS[k]["label"],
    )
    usar_llm = st.toggle("Narrativa IA (requiere API key)", value=False)

    st.divider()
    st.markdown(
        "**Fuentes:**  \n"
        "Fashion Transparency Index 2023  \n"
        "API Banco Mundial (SL.EMP.VULN.ZS · SL.UEM.TOTL.ZS)  \n"
        "OIT Global Wage Report  \n"
        "Ellen MacArthur Foundation 2017"
    )

# ── Cálculo ───────────────────────────────────────────────────────────────────
with st.spinner("Consultando datos laborales del Banco Mundial..."):
    resultados = run_all(material_key, prenda_key)

df = pd.DataFrame(resultados)

material_label = MATERIALES[material_key]["label"]
prenda_label   = PRENDAS[prenda_key]["label"]

# ── Métricas resumen ──────────────────────────────────────────────────────────
peor  = df.iloc[0]    # mayor P_justo
mejor = df.iloc[-1]   # menor P_justo
brecha_promedio = round((df["p_justo"] - df["precio_etiqueta"]).mean())

col1, col2, col3 = st.columns(3)
col1.metric(
    "Empresa con mayor costo real",
    peor["empresa"],
    f"${peor['p_justo']:,} MXN (etiqueta ${peor['precio_etiqueta']:,})",
    delta_color="inverse",
)
col2.metric(
    "Empresa más responsable",
    mejor["empresa"],
    f"${mejor['p_justo']:,} MXN · {mejor['transparencia_pct']}% transparencia",
)
col3.metric(
    "Brecha promedio oculta",
    f"${brecha_promedio:,} MXN",
    "por encima del precio de etiqueta",
    delta_color="inverse",
)

st.divider()

# ── Gráfica de barras apiladas ────────────────────────────────────────────────
st.subheader(f"Dashboard comparativo — {prenda_label} de {material_label}")

# Construir df largo para barras apiladas
# penalizacion_opacidad ya viene calculada correctamente desde ensamblaje.py
df_long = df.melt(
    id_vars="empresa",
    value_vars=["precio_etiqueta", "c_ambiental", "c_social", "penalizacion_opacidad"],
    var_name="componente",
    value_name="mxn",
)

etiquetas = {
    "precio_etiqueta":       "Precio de etiqueta",
    "c_ambiental":           "Costo ambiental",
    "c_social":              "Costo social",
    "penalizacion_opacidad": "Penalización por opacidad",
}
colores = {
    "Precio de etiqueta":        "#4A90D9",
    "Costo ambiental":           "#27AE60",
    "Costo social":              "#E67E22",
    "Penalización por opacidad": "#C0392B",
}

df_long["componente"] = df_long["componente"].map(etiquetas)
orden_empresas = df.sort_values("p_justo", ascending=False)["empresa"].tolist()

fig = px.bar(
    df_long,
    x="empresa",
    y="mxn",
    color="componente",
    color_discrete_map=colores,
    category_orders={
        "empresa":     orden_empresas,
        "componente":  list(etiquetas.values()),
    },
    labels={"mxn": "MXN", "empresa": "Empresa", "componente": "Componente"},
    title=f"Precio justo real por empresa — {prenda_label} de {material_label}",
)
fig.update_layout(
    barmode="stack",
    legend_title_text="Componente del precio",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="rgba(200,200,200,0.3)"),
    height=450,
)
st.plotly_chart(fig, use_container_width=True)

# ── Tabla detallada ────────────────────────────────────────────────────────────
st.subheader("Detalle por empresa")

NIVEL_EMOJI = {"alta": "🟢", "media": "🟡", "baja": "🔴"}

df_tabla = df[[
    "empresa", "iso_pais", "precio_etiqueta", "c_ambiental", "c_social",
    "penalizacion_opacidad", "alpha_e", "p_justo",
    "vida_util_meses", "transparencia_pct", "factor_riesgo_pais", "nivel",
]].copy()
df_tabla["nivel"] = df_tabla["nivel"].map(
    lambda n: f"{NIVEL_EMOJI.get(n, '⚪')} {n.capitalize()}"
)
df_tabla.columns = [
    "Empresa", "País mfg.", "Etiqueta ($)", "C. ambiental ($)", "C. social ($)",
    "Penaliz. opacidad ($)", "α", "Precio justo ($)",
    "Vida útil (m)", "Transparencia (%)", "Riesgo país", "Nivel ético",
]
st.dataframe(df_tabla, use_container_width=True, hide_index=True)

st.divider()

# ── Scatter: transparencia vs brecha ─────────────────────────────────────────
st.subheader("Transparencia vs. brecha con precio justo")

df["brecha"] = df["p_justo"] - df["precio_etiqueta"]

fig2 = px.scatter(
    df,
    x="transparencia_pct",
    y="brecha",
    text="empresa",
    size="factor_riesgo_pais",      # burbuja = riesgo laboral del país
    size_max=40,
    color="nivel",
    color_discrete_map={
        "alta":  "#27AE60",
        "media": "#E67E22",
        "baja":  "#C0392B",
    },
    labels={
        "transparencia_pct":  "Índice de transparencia FTI (%)",
        "brecha":             "Brecha oculta (P_justo − etiqueta, MXN)",
        "nivel":              "Nivel ético",
        "factor_riesgo_pais": "Riesgo país (Banco Mundial)",
    },
    title="A menor transparencia y mayor riesgo país → mayor brecha oculta",
)
fig2.update_traces(textposition="top center")
fig2.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="rgba(200,200,200,0.3)"),
    xaxis=dict(gridcolor="rgba(200,200,200,0.3)"),
    height=420,
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Panel de datos laborales por país (Banco Mundial) ────────────────────────
st.subheader("Datos laborales por país de manufactura (Banco Mundial)")
st.caption(
    "Factor de riesgo calculado desde SL.EMP.VULN.ZS (trabajadores vulnerables) "
    "y SL.UEM.TOTL.ZS (desempleo total). "
    "Fuente: API del Banco Mundial, sin API key."
)

paises_unicos = df[["iso_pais", "empresa"]].drop_duplicates("iso_pais")
filas_pais = []
for _, row in paises_unicos.iterrows():
    datos = get_datos_pais(row["iso_pais"])
    filas_pais.append({
        "País (ISO3)":              datos["iso"],
        "% Trabajadores vulnerables": (
            f"{datos['vulnerabilidad_pct']}%" if datos["vulnerabilidad_pct"] else "N/D"
        ),
        "% Desempleo":              (
            f"{datos['desempleo_pct']}%" if datos["desempleo_pct"] else "N/D"
        ),
        "Factor riesgo calculado":  datos["factor_riesgo"],
        "Fuente":                   datos["fuente"],
    })

st.dataframe(
    pd.DataFrame(filas_pais),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ── Narrativa LLM (opcional) ──────────────────────────────────────────────────
if usar_llm:
    with st.spinner("Generando narrativa con Claude..."):
        narrativa = generar_narrativa(resultados, material_label, prenda_label)
    if narrativa:
        st.subheader("📰 Narrativa periodística")
        st.info(narrativa)
    else:
        st.warning(
            "No se encontró ANTHROPIC_API_KEY en el entorno. "
            "Agrega tu key en el archivo .env"
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "EcoJusto AI — Proyecto académico de IA, 2025. "
    "Los datos son un prototipo demostrativo; no constituyen asesoría de consumo."
)
