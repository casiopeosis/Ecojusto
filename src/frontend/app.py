# frontend/app.py  — v4 (Corregido)
import sys
import os

# Forzar que la raíz del proyecto (donde vive la carpeta 'src') esté en el sys.path
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

from src.data.db import (
    MATERIALES,
    PRENDAS,
    SALARIOS_PAIS,
    TC_MXN,
    MARGEN_REINVERSION_DEFAULT,
    EMPRESAS,
)
from src.data.world_bank import get_datos_pais
from src.algoritmo.ensamblaje import run_all
from src.llm.narrativa import generar_narrativa

load_dotenv()

st.set_page_config(page_title="EcoJusto AI 🌿", page_icon="🌿", layout="wide")
st.title("🌿 EcoJusto AI")
st.caption(
    "Auditor algorítmico de externalidades socioambientales — industria de la moda"
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Parámetros")
    material_key = st.selectbox(
        "Material",
        list(MATERIALES.keys()),
        format_func=lambda k: MATERIALES[k]["label"],
    )
    prenda_key = st.selectbox(
        "Tipo de prenda",
        list(PRENDAS.keys()),
        format_func=lambda k: PRENDAS[k]["label"],
    )
    margen_pct = st.slider(
        "Margen de reinversión empresarial (%)",
        5,
        35,
        int(MARGEN_REINVERSION_DEFAULT * 100),
        5,
        help="Muévelo en presentación para mostrar sensibilidad del modelo.",
    )
    margen = margen_pct / 100
    usar_llm = st.toggle("📰 Narrativa IA (requiere API key)", value=False)
    st.divider()
    st.markdown(
        "**Fuentes:** \n"
        "· Fashion Transparency Index 2023  \n"
        "· Adidas AR 2024 · Nike 10-K 2024  \n"
        "· Inditex AR 2023 · FTM/Patagonia 2023  \n"
        "· API Banco Mundial  \n"
        "· WageIndicator Living Wage Oct 2024  \n"
        "· Water Footprint Network / LCA 2024"
    )

# ── Cálculo ───────────────────────────────────────────────────────────────────
with st.spinner("🌐 Consultando datos laborales del Banco Mundial..."):
    # Nota: Pasamos margen_pct o margen según requiera tu función original.
    # Mantenemos 'margen' (float) de acuerdo a la firma de run_all.
    resultados = run_all(material_key, prenda_key, margen)

df = pd.DataFrame(resultados)
mat_label = MATERIALES[material_key]["label"]
prenda_label = PRENDAS[prenda_key]["label"]

# ── Métricas ──────────────────────────────────────────────────────────────────
peor = df.iloc[0]
mejor = df.iloc[-1]
# Ajustado a las llaves reales retornadas por calcular_precio_justo ('brecha_mxn')
n_externalizan = (df["brecha_mxn"] < 0).sum()
ahorro_prom = (
    abs(round(df[df["brecha_mxn"] < 0]["brecha_mxn"].mean()))
    if n_externalizan > 0
    else 0
)

c1, c2, c3 = st.columns(3)
c1.metric(
    "Mayor externalización",
    peor["empresa"],
    f"cobra ${peor['precio_etiqueta_mxn']:,} · justo ${peor['p_justo_mxn']:,} MXN",
    delta_color="inverse",
)
c2.metric(
    "Más alineada",
    mejor["empresa"],
    f"${mejor['precio_etiqueta_mxn']:,} etiqueta · ${mejor['p_justo_mxn']:,} justo",
)
c3.metric(
    "Empresas que externalizan",
    f"{n_externalizan} de {len(df)}",
    f"~${ahorro_prom:,} MXN/prenda no pagados" if ahorro_prom else "ninguna",
    delta_color="inverse",
)

st.divider()

# ── Gráfica 1: Etiqueta vs P_justo ────────────────────────────────────────────
st.subheader(
    f"💰 Precio etiqueta real vs. Precio justo — {prenda_label} de {mat_label}"
)
st.caption(
    "🔴 cobra menos de lo justo (externaliza) · 🟢 cobra más (posible internalización o margen alto)"
)

df_s = df.sort_values("brecha_mxn")
orden = df_s["empresa"].tolist()

fig1 = go.Figure()
fig1.add_trace(
    go.Bar(
        name="Precio de etiqueta",
        x=df_s["empresa"],
        y=df_s["precio_etiqueta_mxn"],
        marker_color="#4A90D9",
        text=df_s["precio_etiqueta_mxn"].apply(lambda v: f"${v:,}"),
        textposition="outside",
        customdata=df_s["n_paises_manufactura"],
        hovertemplate="<b>%{x}</b><br>Etiqueta: $%{y:,} MXN<br>Países de manufactura: %{customdata}<extra></extra>",
    )
)
fig1.add_trace(
    go.Scatter(
        name="Precio justo (P_justo)",
        x=df_s["empresa"],
        y=df_s["p_justo_mxn"],
        mode="markers+lines",
        marker=dict(size=12, color="#E67E22", symbol="diamond"),
        line=dict(color="#E67E22", width=2, dash="dot"),
        text=df_s["p_justo_mxn"].apply(lambda v: f"${v:,}"),
        textposition="top center",
    )
)
fig1.update_layout(
    barmode="group",
    height=420,
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="rgba(200,200,200,0.2)", title="MXN"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    xaxis=dict(categoryorder="array", categoryarray=orden),
)
st.plotly_chart(fig1, use_container_width=True)

# ── Gráfica 2: Desglose del P_justo ──────────────────────────────────────────
st.subheader("🔍 Desglose del Precio Justo por componente")
st.caption("El punto ✕ naranja es el precio de etiqueta real de cada empresa.")

df_long = df_s.melt(
    id_vars="empresa",
    value_vars=[
        "c_laboral_digno_mxn",
        "c_ambiental_mxn",
        "c_social_mxn",
        "penalizacion_opacidad_mxn",
        "margen_reinversion_mxn",
    ],
    var_name="componente",
    value_name="mxn",
)
etiquetas = {
    "c_laboral_digno_mxn": "Salario digno manufactura",
    "c_ambiental_mxn": "Impacto ambiental (agua + CO₂)",
    "c_social_mxn": "Brecha salarial (deuda social)",
    "penalizacion_opacidad_mxn": "Penalización opacidad (KL)",
    "margen_reinversion_mxn": f"Margen reinversión ({margen_pct}%)",
}
colores_comp = {
    "Salario digno manufactura": "#2ECC71",
    "Impacto ambiental (agua + CO₂)": "#3498DB",
    "Brecha salarial (deuda social)": "#E74C3C",
    "Penalización opacidad (KL)": "#9B59B6",
    f"Margen reinversión ({margen_pct}%)": "#95A5A6",
}
df_long["componente"] = df_long["componente"].map(etiquetas)
fig2 = px.bar(
    df_long,
    x="empresa",
    y="mxn",
    color="componente",
    color_discrete_map=colores_comp,
    category_orders={"empresa": orden, "componente": list(etiquetas.values())},
    labels={"mxn": "MXN", "empresa": "Empresa", "componente": "Componente"},
)
fig2.add_trace(
    go.Scatter(
        name="Precio etiqueta real",
        x=df_s["empresa"],
        y=df_s["precio_etiqueta_mxn"],
        mode="markers",
        marker=dict(size=14, color="#E67E22", symbol="x", line=dict(width=2)),
    )
)
fig2.update_layout(
    barmode="stack",
    height=430,
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="rgba(200,200,200,0.2)"),
    xaxis=dict(categoryorder="array", categoryarray=orden),
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Panel: Cadena de suministro por empresa ───────────────────────────────────
st.subheader("🗺️ Cadena de suministro por empresa")
st.caption(
    "Distribución real de manufactura por país. "
    "Fuentes: reportes anuales Adidas 2024, Nike 10-K 2024, Inditex 2023, "
    "FTM/Patagonia 2023, FASH455/Shein 2023, Statista/Primark 2024."
)

filas_cadena = []
for r in resultados:
    empresa_nombre = r["empresa"]
    for iso, datos in r["desglose_paises_social"].items():
        filas_cadena.append(
            {
                "Empresa": empresa_nombre,
                "País": datos["pais_nombre"],
                "ISO3": iso,
                "% producción": f"{datos['fraccion_pct']}%",
                "Sal. mínimo (USD/mes)": f"${datos['sal_minimo_usd']:,}",
                "Sal. digno (USD/mes)": f"${datos['sal_digno_usd']:,}",
                "Brecha (USD/mes)": f"${datos['sal_digno_usd'] - datos['sal_minimo_usd'] if isinstance(datos['sal_digno_usd'], (int,float)) and isinstance(datos['sal_minimo_usd'], (int,float)) else '?':,}",
                "Factor riesgo (BM)": datos["factor_riesgo"],
                "C_social este país ($)": f"${datos['c_social']:,}",
            }
        )

df_cadena = pd.DataFrame(filas_cadena)
st.dataframe(df_cadena, use_container_width=True, hide_index=True)

# Mapa de calor: empresa × país → fracción de producción
st.caption("Mapa de calor: intensidad = % de producción en ese país")
pivot_data = []
for r in resultados:
    for iso, datos in r["desglose_paises_social"].items():
        pivot_data.append(
            {
                "Empresa": r["empresa"],
                "País": datos["pais_nombre"],
                "Fracción": datos["fraccion_pct"],
            }
        )

df_pivot = pd.DataFrame(pivot_data).pivot_table(
    index="Empresa", columns="País", values="Fracción", fill_value=0
)
fig_heat = px.imshow(
    df_pivot,
    labels=dict(x="País de manufactura", y="Empresa", color="% producción"),
    color_continuous_scale="Reds",
    text_auto=True,
    aspect="auto",
)
fig_heat.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# ── Panel: Impacto ambiental ──────────────────────────────────────────────────
st.subheader(f"🌊 Impacto ambiental — {mat_label}")
mat = MATERIALES[material_key]
peso_ref = mat["peso_prenda_kg"].get(prenda_key, 0.30)
ca, cb, cc = st.columns(3)
ca.metric(
    "Huella hídrica por prenda",
    f"{round(mat['huella_hidrica_litros_kg']*peso_ref):,} litros",
    f"{mat['huella_hidrica_litros_kg']:,} L/kg fibra",
)
cb.metric(
    "Emisiones CO₂ por prenda",
    f"{round(mat['co2_kg_por_kg_fibra']*peso_ref,2)} kg CO₂",
    f"{mat['co2_kg_por_kg_fibra']} kg CO₂/kg fibra",
)
cc.metric("Peso estimado", f"{peso_ref*1000:.0f} g", mat_label)

st.divider()

# ── Tabla resumen ─────────────────────────────────────────────────────────────
st.subheader("📋 Resumen por empresa")
VEREDICTO_LABEL = {
    "externaliza": "🔴 Externaliza",
    "subestimado": "🟠 Subestimado",
    "alineado": "🟢 Alineado",
    "margen_alto": "🟡 Margen alto",
    "sobreprecio": "⚪ Sobreprecio",
}
df_tab = df_s[
    [
        "empresa",
        "n_paises_manufactura",
        "precio_etiqueta_mxn",
        "p_justo_mxn",
        "brecha_mxn",
        "c_laboral_digno_mxn",
        "c_ambiental_mxn",
        "c_social_mxn",
        "vida_util_meses",
        "transparencia_pct",
        "alpha_opacidad",
        "veredicto",
    ]
].copy()
df_tab["veredicto"] = df_tab["veredicto"].map(VEREDICTO_LABEL)
df_tab["brecha_mxn"] = df_tab["brecha_mxn"].apply(
    lambda b: f"+${b:,.0f}" if b >= 0 else f"-${abs(b):,.0f}"
)
df_tab.columns = [
    "Empresa",
    "# Países mfg.",
    "Etiqueta ($)",
    "P_justo ($)",
    "Brecha ($)",
    "C. laboral ($)",
    "C. ambiental ($)",
    "C. social ($)",
    "Vida útil (m)",
    "Transparencia (%)",
    "α",
    "Veredicto",
]
st.dataframe(df_tab, use_container_width=True, hide_index=True)

st.divider()

# ── Scatter: transparencia vs brecha ─────────────────────────────────────────
st.subheader("🔎 Transparencia vs. brecha")
df["brecha_val"] = df["brecha_mxn"]
fig3 = px.scatter(
    df,
    x="transparencia_pct",
    y="brecha_val",
    text="empresa",
    size="factor_riesgo_prom",
    size_max=40,
    color="veredicto",
    color_discrete_map={
        "externaliza": "#C0392B",
        "subestimado": "#E67E22",
        "alineado": "#27AE60",
        "margen_alto": "#F1C40F",
        "sobreprecio": "#95A5A6",
    },
    labels={
        "transparencia_pct": "FTI (%)",
        "brecha_val": "Brecha (MXN)",
        "veredicto": "Veredicto",
        "factor_riesgo_prom": "Riesgo país prom.",
    },
)
fig3.add_hline(
    y=0,
    line_dash="dash",
    line_color="gray",
    annotation_text="Equilibrio: etiqueta = precio justo",
)
fig3.update_traces(textposition="top center")
fig3.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    height=430,
    yaxis=dict(gridcolor="rgba(200,200,200,0.2)"),
    xaxis=dict(gridcolor="rgba(200,200,200,0.2)"),
)
st.plotly_chart(fig3, use_container_width=True)

# ── Narrativa LLM ─────────────────────────────────────────────────────────────
if usar_llm:
    with st.spinner("✍️ Generando narrativa con Claude..."):
        narrativa = generar_narrativa(resultados, mat_label, prenda_label)
    if narrativa:
        st.divider()
        st.subheader("📰 Narrativa periodística")
        st.info(narrativa)
    else:
        st.warning("Agrega tu ANTHROPIC_API_KEY en .env para activar este módulo.")

st.divider()
st.caption(
    "EcoJusto AI — Proyecto académico de IA, 2025. Prototipo demostrativo con fuentes citadas."
)


# ── NUEVA SECCIÓN COMPLETA: SIMULACIONES AVANZADAS E INTELIGENCIA ARTIFICIAL ──
st.markdown("---")
st.header("🧠 Módulos Avanzados de Simulación e Inteligencia Artificial")

tab_montecarlo, tab_genetico = st.tabs(
    [
        "🎲 Simulación Monte Carlo (Bono Carbono)",
        "🧬 Algoritmo Genético (Frente de Pareto)",
    ]
)

# ── PANE 1: MONTE CARLO ───────────────────────────────────────────────────────
with tab_montecarlo:
    st.subheader("🎲 Análisis de Estrés Industrial vía Monte Carlo")
    st.caption(
        "Simula 2,000 escenarios estocásticos variando los precios internacionales de CO₂ y remediación de agua para proyectar el punto de quiebre financiero del Fast Fashion."
    )

    col_mc1, col_mc2 = st.columns([1, 3])

    with col_mc1:
        empresa_mc = st.selectbox(
            "Selecciona Marca a Auditar", [e["nombre"] for e in EMPRESAS]
        )
        st.info(
            "Pregunta clave: ¿Cuánto tendría que subir el bono de carbono para que esta empresa no pueda seguir rentabilizando sus externalidades?"
        )

    # Correr la simulación al vuelo usando el nuevo módulo modular
    from src.algoritmo.monte_carlo import simular_umbrales_co2

    res_mc = simular_umbrales_co2(empresa_mc, material_key, prenda_key)

    with col_mc2:
        st.metric(
            f"Punto de Quiebre de CO₂ (Percentil 90) para {empresa_mc}",
            f"${res_mc['umbral_co2_percentil_90']} MXN/kg",
            f"Inviable en el {res_mc['pct_escenarios_insostenible']}% de los escenarios futuros",
        )

        # Histograma de precios justos simulados
        fig_hist = px.histogram(
            x=res_mc["historico_precios_justos"],
            nbins=30,
            labels={
                "x": "Precio Justo Simulado (MXN)",
                "y": "Frecuencia de Escenarios",
            },
            title=f"Distribución del Precio Justo Calculado bajo Estrés Climático ({prenda_label} de {mat_label})",
            color_discrete_sequence=["#8E44AD"],
        )
        fig_hist.add_vline(
            x=res_mc["precio_etiqueta"],
            line_dash="dash",
            line_color="red",
            annotation_text=f"Precio Etiqueta Real (${res_mc['precio_etiqueta']} MXN)",
        )
        fig_hist.update_layout(plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)
