# frontend/app.py
# Dashboard interactivo — EcoJusto AI
# Streamlit + Plotly Express

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

from data.db import MATERIALES, PRENDAS
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
st.caption("Auditor algorítmico de externalidades socioambientales en la industria de la moda")

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
        "**Fuentes:** Fashion Transparency Index 2023 · "
        "CSI Global Rights Index · OIT · Ellen MacArthur Foundation"
    )

# ── Cálculo ───────────────────────────────────────────────────────────────────
resultados = run_all(material_key, prenda_key)
df = pd.DataFrame(resultados)

material_label = MATERIALES[material_key]["label"]
prenda_label   = PRENDAS[prenda_key]["label"]

# ── Métricas resumen ──────────────────────────────────────────────────────────
peor  = df.iloc[0]   # mayor P_justo (más cara externamente)
mejor = df.iloc[-1]  # menor P_justo
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

# ── Gráfica de barras apiladas ─────────────────────────────────────────────────
st.subheader(f"Dashboard comparativo — {prenda_label} de {material_label}")

# Construir df largo para barras apiladas
df_plot = df[["empresa", "precio_etiqueta", "c_ambiental", "c_social"]].copy()
df_plot["penalizacion_opacidad"] = df["p_justo"] - (
    df["alpha_e"] * (df["precio_etiqueta"] + df["c_ambiental"] + df["c_social"]) / df["alpha_e"]
    # Nota: la penalización no es aditiva sino multiplicativa; la representamos como
    # la diferencia entre P_justo y la suma sin multiplicador para visualización.
)
# Recalcular correctamente la porción del multiplicador
df_plot["base_sin_alpha"] = df["precio_etiqueta"] + df["c_ambiental"] + df["c_social"]
df_plot["penalizacion_opacidad"] = df["p_justo"] - df_plot["base_sin_alpha"]

df_long = df_plot.melt(
    id_vars="empresa",
    value_vars=["precio_etiqueta", "c_ambiental", "c_social", "penalizacion_opacidad"],
    var_name="componente",
    value_name="mxn",
)

etiquetas = {
    "precio_etiqueta":      "Precio de etiqueta",
    "c_ambiental":          "Costo ambiental",
    "c_social":             "Costo social",
    "penalizacion_opacidad":"Penalización por opacidad",
}
colores = {
    "Precio de etiqueta":        "#4A90D9",
    "Costo ambiental":           "#27AE60",
    "Costo social":              "#E67E22",
    "Penalización por opacidad": "#C0392B",
}

df_long["componente"] = df_long["componente"].map(etiquetas)

# Ordenar empresas por P_justo descendente
orden = df.sort_values("p_justo", ascending=False)["empresa"].tolist()

fig = px.bar(
    df_long,
    x="empresa",
    y="mxn",
    color="componente",
    color_discrete_map=colores,
    category_orders={"empresa": orden, "componente": list(etiquetas.values())},
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
    "empresa", "precio_etiqueta", "c_ambiental", "c_social",
    "alpha_e", "p_justo", "vida_util_meses", "transparencia_pct", "nivel"
]].copy()
df_tabla["nivel"] = df_tabla["nivel"].map(lambda n: f"{NIVEL_EMOJI[n]} {n.capitalize()}")
df_tabla.columns = [
    "Empresa", "Precio etiqueta ($)", "C. ambiental ($)", "C. social ($)",
    "α (opacidad)", "Precio justo ($)", "Vida útil (meses)", "Transparencia (%)", "Nivel ético"
]

st.dataframe(df_tabla, use_container_width=True, hide_index=True)

# ── Gráfica de dispersión: transparencia vs brecha ────────────────────────────
st.subheader("Transparencia vs. brecha con precio justo")

df["brecha"] = df["p_justo"] - df["precio_etiqueta"]
fig2 = px.scatter(
    df,
    x="transparencia_pct",
    y="brecha",
    text="empresa",
    size="p_justo",
    color="nivel",
    color_discrete_map={"alta": "#27AE60", "media": "#E67E22", "baja": "#C0392B"},
    labels={
        "transparencia_pct": "Índice de transparencia FTI (%)",
        "brecha": "Brecha oculta (P_justo − etiqueta, MXN)",
        "nivel": "Nivel ético",
    },
)
fig2.update_traces(textposition="top center")
fig2.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="rgba(200,200,200,0.3)"),
    xaxis=dict(gridcolor="rgba(200,200,200,0.3)"),
    height=400,
)
st.plotly_chart(fig2, use_container_width=True)

# ── Narrativa LLM (opcional) ──────────────────────────────────────────────────
if usar_llm:
    with st.spinner("Generando narrativa..."):
        narrativa = generar_narrativa(resultados, material_label, prenda_label)
    if narrativa:
        st.divider()
        st.subheader("📰 Narrativa periodística")
        st.info(narrativa)
    else:
        st.warning("No se encontró ANTHROPIC_API_KEY en el entorno. Agrega tu key en el archivo .env")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "EcoJusto AI — Proyecto académico de IA, 2025. "
    "Los datos son un prototipo demostrativo; no constituyen asesoría de consumo."
)
