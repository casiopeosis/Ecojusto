# frontend/app.py  — v5 (Rediseño visual EcoJusto AI - Corregido)
import sys
import os

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

# ── Paleta de color ──────────────────────────────────────────────────────────
CARBON   = "#1E1E1E"
MINT     = "#F1FFFA"
ORANGE   = "#F98948"
GREEN    = "#57A773"
BERRY    = "#D90368"
MUTED    = "#6B7280"  # texto secundario

st.set_page_config(
    page_title="EcoJusto AI",
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Global ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght=300;400;500;600&family=DM+Mono:wght=400;500&display=swap');

  html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {CARBON};
    color: {MINT};
  }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
    background-color: #141414 !important;
    border-right: 1px solid #2a2a2a;
  }}
  [data-testid="stSidebar"] * {{
    color: {MINT} !important;
  }}
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stSlider label {{
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: {MUTED} !important;
  }}

  /* ── Main background ── */
  .main .block-container {{
    background-color: {CARBON};
    padding-top: 2rem;
    padding-bottom: 4rem;
  }}

  /* ── Headings ── */
  h1 {{
    font-size: 2rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: {MINT} !important;
  }}
  h2, h3 {{
    font-family: ui-sans-serif, system-ui, BlinkMacSystemFont, sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    color: {MINT} !important;
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: 0.4rem;
    margin-top: 1.8rem !important;
  }}

  /* ── Caption / muted text ── */
  [data-testid="stCaptionContainer"] p {{
    color: {MUTED} !important;
    font-size: 0.82rem !important;
  }}

  /* ── Metric cards ── */
  [data-testid="stMetric"] {{
    background: #252525;
    border: 1px solid #2e2e2e;
    border-radius: 10px;
    padding: 1rem 1.2rem !important;
  }}
  [data-testid="stMetricLabel"] {{
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
  }}
  [data-testid="stMetricValue"] {{
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: {MINT} !important;
    font-family: 'DM Mono', monospace !important;
  }}
  [data-testid="stMetricDelta"] {{
    font-size: 0.78rem !important;
    font-family: 'DM Mono', monospace !important;
  }}

  /* ── Dataframes ── */
  [data-testid="stDataFrame"] {{
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #2a2a2a;
  }}

  /* ── Divider ── */
  hr {{
    border: none;
    border-top: 1px solid #2a2a2a !important;
    margin: 2rem 0 !important;
  }}

  /* ── Info / warning boxes ── */
  [data-testid="stAlert"] {{
    background: #1c2620 !important;
    border: 1px solid #2e4a38 !important;
    border-left: 3px solid {GREEN} !important;
    border-radius: 8px !important;
    color: {MINT} !important;
    font-size: 0.85rem !important;
  }}

  /* ── Tabs ── */
  [data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 1px solid #2a2a2a;
    gap: 0.25rem;
  }}
  [data-testid="stTabs"] button[role="tab"] {{
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    color: {MUTED} !important;
    padding: 0.5rem 1.2rem;
    border-radius: 6px 6px 0 0;
    transition: color 0.2s;
  }}
  [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    color: {MINT} !important;
    border-bottom: 2px solid {ORANGE} !important;
    background: #252525 !important;
  }}

  /* ── Toggle ── */
  [data-testid="stToggle"] label {{
    font-size: 0.82rem !important;
    color: {MUTED} !important;
  }}

  /* ── Selectbox / slider ── */
  .stSelectbox > div > div,
  .stSlider > div {{
    background: #252525 !important;
  }}

  /* ── Footer ── */
  .ecojusto-footer {{
    font-size: 0.72rem;
    color: {MUTED};
    text-align: center;
    padding-top: 2rem;
    border-top: 1px solid #2a2a2a;
    letter-spacing: 0.04em;
  }}
    /* ── Ocultar barra superior nativa (Deploy, Menú y espacio) ── */
  [data-testid="stHeader"] {{
    background-color: rgba(0, 0, 0, 0) !important; /* Hace transparente el contenedor */
    display: none !important; /* Desaparece por completo la barra superior */
  }}

  /* Eliminar el espacio en blanco (padding) superior que deja la barra al irse */
  .main .block-container {{
    padding-top: 1.5rem !important; /* Ajusta este valor si quieres más o menos margen inicial */
  }}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme base ─────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color=MINT, size=12),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=50, b=30),
)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex; align-items:baseline; gap:0.75rem; margin-bottom:0.25rem;">
  <span style="font-family:DM Sans; font-size:1.75rem; font-weight:1000; letter-spacing:-0.02em; color:{MINT};">ECOJUSTO</span>
  <span style="font-size:0.75rem; font-weight:500; letter-spacing:0.1em; text-transform:uppercase;

  </span>
</div>
<p style="color:{MUTED}; font-size:0.85rem; margin:0 0 1.5rem 0; letter-spacing:0.01em;">
  Auditor de externalidades socioambientales
</p>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <p style="font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase;
       color:{MUTED}; margin-bottom:1rem;">Parámetros del modelo</p>
    """, unsafe_allow_html=True)

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
        "Margen de reinversión (%)",
        5, 35,
        int(MARGEN_REINVERSION_DEFAULT * 100),
        5,
        help="Sensibilidad al margen de reinversión empresarial.",
    )
    margen = margen_pct / 100
    usar_llm = st.toggle("Narrativa IA (requiere API key)", value=False)

    st.divider()

    st.markdown(f"""
    <p style="font-size:0.68rem; letter-spacing:0.08em; text-transform:uppercase; color:{MUTED}; margin-bottom:0.5rem;">
      Fuentes de datos
    </p>
    <p style="font-size:0.75rem; color:#4a5568; line-height:1.7;">
      Fashion Transparency Index 2023<br>
      Adidas AR 2024 · Nike 10-K 2024<br>
      Inditex AR 2023 · FTM/Patagonia 2023<br>
      API Banco Mundial<br>
      WageIndicator Living Wage Oct 2024<br>
      Water Footprint Network / LCA 2024
    </p>
    """, unsafe_allow_html=True)

# ── Cálculo ───────────────────────────────────────────────────────────────────
with st.spinner("Consultando datos laborales del Banco Mundial..."):
    resultados = run_all(material_key, prenda_key, margen)

df = pd.DataFrame(resultados)
mat_label = MATERIALES[material_key]["label"]
prenda_label = PRENDAS[prenda_key]["label"]

# ── Métricas ──────────────────────────────────────────────────────────────────
peor = df.iloc[0]
mejor = df.iloc[-1]
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

# ── Gráfica 1: Etiqueta vs P_justo ────────────────────────────────────────────
st.subheader(f"Precio etiqueta vs. precio justo.")

df_s = df.sort_values("brecha_mxn")
orden = df_s["empresa"].tolist()

fig1 = go.Figure()
fig1.add_trace(
    go.Bar(
        name="Precio de etiqueta",
        x=df_s["empresa"],
        y=df_s["precio_etiqueta_mxn"],
        marker_color=BERRY,
        marker_opacity=0.85,
        text=df_s["precio_etiqueta_mxn"].apply(lambda v: f"${v:,}"),
        textposition="outside",
        textfont=dict(size=11, color=MINT),
        customdata=df_s["n_paises_manufactura"],
        hovertemplate="<b>%{x}</b><br>Etiqueta: $%{y:,} MXN<br>Países de manufactura: %{customdata}<extra></extra>",
    )
)
fig1.add_trace(
    go.Scatter(
        name="Precio justo",
        x=df_s["empresa"],
        y=df_s["p_justo_mxn"],
        mode="markers+lines",
        marker=dict(size=10, color=GREEN, symbol="diamond"),
        line=dict(color=GREEN, width=2, dash="dot"),
        text=df_s["p_justo_mxn"].apply(lambda v: f"${v:,}"),
        textposition="top center",
        textfont=dict(size=10, color=GREEN),
    )
)
fig1.update_layout(
    **{
        **PLOTLY_LAYOUT,
        "barmode": "group",
        "height": 420,
        "yaxis": dict(**PLOTLY_LAYOUT["yaxis"], title="MXN"),
        "xaxis": dict(**PLOTLY_LAYOUT["xaxis"], categoryorder="array", categoryarray=orden),
    }
)
st.plotly_chart(fig1, use_container_width=True)

# ── Gráfica 2: Desglose del P_justo ──────────────────────────────────────────
st.subheader("Desglose del Precio Justo por componente")
st.caption("La marca × indica el precio de etiqueta real de cada empresa.")

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
    "Salario digno manufactura": GREEN,
    "Impacto ambiental (agua + CO₂)": "#3B82F6",
    "Brecha salarial (deuda social)": BERRY,
    "Penalización opacidad (KL)": "#8B5CF6",
    f"Margen reinversión ({margen_pct}%)": "#374151",
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
        marker=dict(size=14, color=ORANGE, symbol="x", line=dict(width=2, color=ORANGE)),
    )
)
fig2.update_layout(
    **{
        **PLOTLY_LAYOUT,
        "barmode": "stack",
        "height": 430,
        "xaxis": dict(**PLOTLY_LAYOUT["xaxis"], categoryorder="array", categoryarray=orden),
    }
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Panel: Cadena de suministro por empresa ───────────────────────────────────
st.subheader("Cadena de suministro por empresa")
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

st.caption("Mapa de calor — intensidad = % de producción en cada país")
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
    color_continuous_scale=[[0, "#1a1a1a"], [0.5, ORANGE], [1, BERRY]],
    text_auto=True,
    aspect="auto",
)
fig_heat.update_layout(**PLOTLY_LAYOUT, height=350)
st.plotly_chart(fig_heat, use_container_width=True)


# ── Panel: Impacto ambiental ──────────────────────────────────────────────────
st.subheader(f"Impacto ambiental — {mat_label}")
mat = MATERIALES[material_key]
peso_ref = mat["peso_prenda_kg"].get(prenda_key, 0.30)
ca, cb = st.columns(2)
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


# ── Tabla resumen ─────────────────────────────────────────────────────────────
st.subheader("Resumen por empresa")
VEREDICTO_LABEL = {
    "externaliza": "Externaliza",
    "subestimado": "Subestimado",
    "alineado": "Alineado",
    "margen_alto": "Margen alto",
    "sobreprecio": "Sobreprecio",
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
st.subheader("Transparencia vs. brecha")
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
        "externaliza": BERRY,
        "subestimado": ORANGE,
        "alineado": GREEN,
        "margen_alto": "#F59E0B",
        "sobreprecio": MUTED,
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
    line_color="rgba(255,255,255,0.2)",
    annotation_text="Equilibrio: etiqueta = precio justo",
    annotation_font_color=MUTED,
)
fig3.update_traces(textposition="top center")
fig3.update_layout(**PLOTLY_LAYOUT, height=430)
st.plotly_chart(fig3, use_container_width=True)

# ── Narrativa LLM ─────────────────────────────────────────────────────────────
if usar_llm:
    with st.spinner("Generando narrativa con Claude..."):
        narrativa = generar_narrativa(resultados, mat_label, prenda_label)
    if narrativa:
        st.divider()
        st.subheader("Narrativa periodística")
        st.info(narrativa)
    else:
        st.warning("Agrega tu ANTHROPIC_API_KEY en .env para activar este módulo.")

st.divider()




# ── Módulos Avanzados de Simulación ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Simulación con Monte Carlo")

from src.algoritmo.monte_carlo import simular_umbrales_co2
from src.algoritmo.monte_carlo_hidrico import simular_huella_hidrica
from src.algoritmo.monte_carlo_deuda_social import simular_deuda_social, comparar_empresas_deuda

tab_co2, tab_hidrico, tab_deuda = st.tabs(
    [
        "Estrés Climático — Bono CO₂",
        "Agotamiento Hídrico Acumulado",
        "Reloj de Deuda Social",
    ]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Monte Carlo: Sensibilidad al Precio del Bono de Carbono
# ══════════════════════════════════════════════════════════════════════════════
with tab_co2:
    from src.algoritmo.monte_carlo import simular_sensibilidad_co2, comparar_sensibilidad_todas

    st.subheader("Sensibilidad al Precio del Bono de Carbono")
    st.caption(
        "2,000 escenarios de precios de CO₂ (rango 3.5–200 MXN/kg). "
        "KPI central: ¿a qué precio de carbono el costo de remediación se vuelve materialmente significativo? "
        "Varía por empresa según la vida útil de las prendas."
    )

    col_mc1, col_mc2 = st.columns([1, 3])
    with col_mc1:
        empresa_mc = st.selectbox(
            "Marca a auditar", [e["nombre"] for e in EMPRESAS], key="empresa_co2"
        )
        st.markdown(f"""
        <p style="font-size:0.72rem; color:{MUTED}; text-transform:uppercase; letter-spacing:0.08em; margin-top:1rem;">
          Escenarios de referencia (MXN/kg CO₂)
        </p>
        <p style="font-size:0.82rem; color:{MINT}; font-family:'DM Mono',monospace; line-height:1.9;">
          Actual México: <b>$3.50</b><br>
          Objetivo París 2030: <b>$35</b><br>
          IPCC 1.5°C (2050): <b>$100–200</b>
        </p>
        """, unsafe_allow_html=True)

    with st.spinner("Calculando sensibilidad CO₂..."):
        res_co2 = simular_sensibilidad_co2(empresa_mc, material_key, prenda_key, n_simulaciones=2000)

    with col_mc2:
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric(
            "Sensibilidad CO₂",
            f"${res_co2['sensibilidad_co2_mxn_por_mxn_kg']:.2f} MXN/prenda",
            f"por cada MXN/kg de bono de carbono",
        )
        mc2.metric(
            "Breakeven 25% etiqueta",
            f"${res_co2['co2_breakeven_25pct_etiqueta']:.1f} MXN/kg",
            f"Vida útil: {res_co2['vida_util_meses']} meses",
        )
        mc3.metric(
            "c_ambiental > etiqueta",
            f"{res_co2['pct_c_ambiental_supera_etiqueta']:.0f}%",
            "de 2,000 simulaciones",
            delta_color="inverse",
        )

    with st.spinner("Comparando todas las marcas..."):
        todas_co2 = comparar_sensibilidad_todas(material_key, prenda_key, n_simulaciones=500)

    fig_curva = go.Figure()
    colores_curva = [ORANGE, GREEN, BERRY, "#3B82F6", "#8B5CF6", "#F59E0B", "#06B6D4", "#84CC16"]
    for i, r in enumerate(todas_co2):
        es_seleccionada = r["empresa"] == empresa_mc
        fig_curva.add_trace(go.Scatter(
            x=r["precios_curva"],
            y=r["c_co2_curva"],
            mode="lines",
            name=r["empresa"],
            line=dict(
                color=colores_curva[i % len(colores_curva)],
                width=3 if es_seleccionada else 1.5,
                dash="solid" if es_seleccionada else "dot",
            ),
        ))

    for precio_ref, etiqueta_ref, color_ref in [
        (3.5,  "Actual MX",     "rgba(255,255,255,0.2)"),
        (35.0, "Objetivo París","rgba(87,167,115,0.6)"),
        (100.0,"IPCC 1.5°C",   "rgba(249,137,72,0.6)"),
    ]:
        fig_curva.add_vline(
            x=precio_ref, line_dash="dash", line_color=color_ref,
            annotation_text=etiqueta_ref, annotation_font_size=10,
            annotation_font_color=MUTED,
        )

    fig_curva.add_hline(
        y=res_co2["precio_etiqueta"],
        line_dash="longdash", line_color=BERRY,
        annotation_text=f"Etiqueta {empresa_mc} (${res_co2['precio_etiqueta']} MXN)",
        annotation_font_size=10, annotation_font_color=BERRY,
    )

    fig_curva.update_layout(
        **{
            **PLOTLY_LAYOUT,
            "height": 420,
            "title": f"Curva de Sensibilidad: Costo CO₂/prenda vs Precio del Bono — {mat_label}",
            "xaxis": dict(**PLOTLY_LAYOUT["xaxis"], title="Precio del bono de carbono (MXN/kg CO₂)"),
            "yaxis": dict(**PLOTLY_LAYOUT["yaxis"], title="Costo remediación CO₂ por prenda (MXN)"),
        }
    )
    st.plotly_chart(fig_curva, use_container_width=True)

    fig_hist_co2 = px.histogram(
        x=res_co2["sim_c_ambiental"],
        nbins=50,
        labels={"x": "Costo ambiental total simulado (MXN/prenda)", "y": "Escenarios"},
        title=f"Distribución del Costo Ambiental — 2,000 escenarios · {empresa_mc}",
        color_discrete_sequence=["#8B5CF6"],
    )
    fig_hist_co2.add_vline(
        x=res_co2["c_ambiental_base"], line_dash="dash", line_color=GREEN,
        annotation_text=f"Base actual (${res_co2['c_ambiental_base']:,.0f} MXN)",
        annotation_font_size=10, annotation_font_color=GREEN,
    )
    fig_hist_co2.add_vline(
        x=res_co2["precio_etiqueta"], line_dash="dash", line_color=BERRY,
        annotation_text=f"Etiqueta (${res_co2['precio_etiqueta']} MXN)",
        annotation_font_size=10, annotation_font_color=BERRY,
    )
    fig_hist_co2.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig_hist_co2, use_container_width=True)

    st.subheader("Comparativa de sensibilidad por empresa")
    st.caption(
        "Empresas con menor vida útil (baja transparencia → mayor frecuencia de reposición) "
        "tienen mayor sensibilidad al precio del carbono."
    )
    df_sens = pd.DataFrame([
        {
            "Empresa": r["empresa"],
            "Transparencia": f"{r['transparencia_pct']}%",
            "Vida útil (meses)": r["vida_util_meses"],
            "Sensibilidad (MXN/prenda por MXN/kg CO₂)": r["sensibilidad_co2_mxn_por_mxn_kg"],
            "Breakeven 25% etiqueta (MXN/kg CO₂)": r["co2_breakeven_25pct_etiqueta"],
            "c_ambiental base (MXN)": f"${r['c_ambiental_base']:,.0f}",
            "% c_amb vs etiqueta": f"{r['pct_ambiental_vs_etiqueta']:.0f}%",
        }
        for r in todas_co2
    ])
    st.dataframe(df_sens, use_container_width=True, hide_index=True)

    st.info(
        f"**Interpretación:** Con el precio actual del bono de carbono ($3.50 MXN/kg), "
        f"**{empresa_mc}** genera un costo de remediación CO₂ de **${res_co2['c_co2_base']:.2f} MXN** "
        f"por prenda de {mat_label}. Si el precio subiera al nivel del Acuerdo de París ($35 MXN/kg), "
        f"ese costo subiría a **${res_co2['sensibilidad_co2_mxn_por_mxn_kg']*35:.2f} MXN** por prenda. "
        f"La empresa con mayor sensibilidad es **{todas_co2[0]['empresa']}** "
        f"({todas_co2[0]['sensibilidad_co2_mxn_por_mxn_kg']:.2f} MXN/prenda por MXN/kg CO₂) "
        f"porque sus prendas duran solo {todas_co2[0]['vida_util_meses']} meses en promedio."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Monte Carlo: Agotamiento Hídrico Acumulado
# ══════════════════════════════════════════════════════════════════════════════
with tab_hidrico:
    st.subheader("Simulación de Agotamiento Hídrico Acumulado")
    st.caption(
        "¿En cuántos años el consumo del salón equivale a una alberca olímpica, "
        "al Lago de Chapultepec o a la Presa Cutzamala? "
        "Las referencias son adaptativas al material seleccionado."
    )

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        n_personas_h = st.slider("Personas en el salón", 10, 80, 30, 5, key="h_personas")
    with col_h2:
        prendas_h = st.slider(
            "Prendas / persona / año", 5, 100, 25, 5, key="h_prendas",
            help="Promedio mundial fast fashion: ~60 prendas/año (McKinsey 2023).",
        )
    with col_h3:
        anos_h = st.slider("Horizonte (años)", 5, 30, 15, 1, key="h_anos")
    with col_h4:
        st.markdown(f"""
        <p style="font-size:0.72rem; color:{MUTED}; text-transform:uppercase; letter-spacing:0.08em;">Material</p>
        <p style="font-size:1rem; font-weight:600; color:{MINT};">{mat_label}</p>
        """, unsafe_allow_html=True)
        litros_kg = MATERIALES[material_key]['huella_hidrica_litros_kg']
        st.caption(f"{litros_kg:,} L/kg fibra")

    with st.spinner("Simulando 2,000 trayectorias hídricas..."):
        res_h = simular_huella_hidrica(
            material_key=material_key,
            prenda_key=prenda_key,
            n_personas=n_personas_h,
            prendas_por_persona=prendas_h,
            anos=anos_h,
            n_sim=2000,
        )

    def fmt_litros(n):
        if n >= 1e12: return f"{n/1e12:.2f} billones L"
        if n >= 1e9:  return f"{n/1e9:.1f} mil mill. L"
        if n >= 1e6:  return f"{n/1e6:.1f} M L"
        if n >= 1e3:  return f"{n/1e3:.1f} mil L"
        return f"{n:,.0f} L"

    mh1, mh2, mh3 = st.columns(3)
    mh1.metric(
        f"Consumo P50 (año {anos_h})",
        fmt_litros(res_h["p50_final"]),
        f"≈ {res_h['equiv_albercas_p50']} albercas olímpicas",
    )
    mh2.metric(
        "Escenario adverso P90",
        fmt_litros(res_h["p90_final"]),
        f"≈ {res_h['equiv_albercas_p90']} albercas olímpicas",
        delta_color="inverse",
    )
    mh3.metric(
        "Equivalente en personas",
        f"{res_h['equiv_personas_anos_p50']:,} años-persona",
        f"de agua potable (P50)",
        delta_color="inverse",
    )

    anos_labels = [f"Año {i}" for i in range(anos_h + 1)]
    anos_labels[0] = "Hoy"

    fig_h = go.Figure()

    for tray in res_h["trayectorias_muestra"][:300]:
        fig_h.add_trace(go.Scatter(
            x=anos_labels, y=tray, mode="lines",
            line=dict(color="rgba(59,130,246,0.04)", width=1),
            showlegend=False, hoverinfo="skip",
        ))

    fig_h.add_trace(go.Scatter(
        x=anos_labels + anos_labels[::-1],
        y=res_h["p75"] + res_h["p25"][::-1],
        fill="toself", fillcolor="rgba(59,130,246,0.10)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Banda P25–P75", hoverinfo="skip",
    ))

    for pct_key, nombre, color, ancho in [
        ("p50", "Mediana (P50)", "#3B82F6", 2.5),
        ("p90", "Escenario adverso (P90)", ORANGE, 2),
        ("p99", "Worst case (P99)", BERRY, 1.5),
    ]:
        fig_h.add_trace(go.Scatter(
            x=anos_labels, y=res_h[pct_key], mode="lines",
            name=nombre, line=dict(color=color, width=ancho),
        ))

    estilos_ref = ["dash", "dot", "dashdot", "longdash"]
    for idx_r, (nombre_r, datos_r) in enumerate(res_h["equivalencias"].items()):
        nombre_limpio = nombre_r.replace("\n", " ")
        vol = datos_r["vol_litros"]
        cruce = datos_r["años_p50"]
        cruce_str = f" — cruce P50: año {cruce}" if cruce else " — fuera del horizonte"
        fig_h.add_hline(
            y=vol,
            line_dash=estilos_ref[idx_r % len(estilos_ref)],
            line_color=datos_r["color"],
            annotation_text=f"{nombre_limpio} ({fmt_litros(vol)}){cruce_str}",
            annotation_font_size=9,
            annotation_font_color=MUTED,
        )

    fig_h.update_layout(
        **{
            **PLOTLY_LAYOUT,
            "height": 500,
            "title": (
                f"Haz Monte Carlo — Huella Hídrica · \n"
                f"{n_personas_h} personas × {prendas_h} prendas/año · {mat_label} \n"
            ),
            "yaxis": dict(**PLOTLY_LAYOUT["yaxis"], title="Litros acumulados", tickformat=".3s"),
        }
    )
    st.plotly_chart(fig_h, use_container_width=True)

    st.subheader("Equivalencias de referencia")
    filas_eq = []
    for nombre_r, datos_r in res_h["equivalencias"].items():
        filas_eq.append({
            "Referencia": nombre_r.replace("\n", " "),
            "Volumen": fmt_litros(datos_r["vol_litros"]),
            "Cruce P50": f"Año {datos_r['años_p50']}" if datos_r["años_p50"] else f">{anos_h} años",
            "Cruce P90": f"Año {datos_r['años_p90']}" if datos_r["años_p90"] else f">{anos_h} años",
            "% sim. que lo superan": f"{datos_r['pct_escenarios_supera']}%",
            "Fuente": datos_r["fuente"],
        })
    st.dataframe(pd.DataFrame(filas_eq), use_container_width=True, hide_index=True)

    primera_ref = next(
        ((n, d) for n, d in res_h["equivalencias"].items() if d["años_p50"] is not None),
        None
    )
    if primera_ref:
        n_ref, d_ref = primera_ref
        interp = (
            f"Con {n_personas_h} personas comprando {prendas_h} prendas de "
            f"**{mat_label}** al año, el consumo hídrico acumulado iguala "
            f"**{n_ref.replace(chr(10), ' ')}** ({fmt_litros(d_ref['vol_litros'])}) "
            f"en el año **{d_ref['años_p50']}** (escenario mediano). "
            f"Esto es solo el agua embebida en la producción de la fibra "
            f"— no incluye agua de lavado ni transporte."
        )
    else:
        interp = (
            f"Con {n_personas_h} personas comprando {prendas_h} prendas de "
            f"**{mat_label}** al año, el consumo acumulado en {anos_h} años es "
            f"**{fmt_litros(res_h['p50_final'])}** (P50). "
            f"Prueba con un material de mayor huella hídrica (ej. Algodón Conv. o Lana) "
            f"para ver cruces de referencia dentro del horizonte."
        )
    st.info(f"**Interpretación:** {interp}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Monte Carlo: Reloj de Deuda Social
# ══════════════════════════════════════════════════════════════════════════════
with tab_deuda:
    st.subheader("Reloj de Deuda Social Acumulada")
    st.caption(
        "¿Cuántos años tarda el consumo del salón en acumular una deuda salarial equivalente "
        "al sueldo anual de un trabajador textil? "
        "Variables estocásticas: brecha salarial (±20%), tipo de cambio (±8%), "
        "factor de riesgo laboral (±15%), prendas consumidas (±20%)."
    )

    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1:
        empresa_d = st.selectbox(
            "Marca de fast fashion",
            [e["nombre"] for e in EMPRESAS],
            key="d_empresa",
            index=0,
        )
    with col_d2:
        n_personas_d = st.slider(
            "Personas en el salón", 10, 80, 30, 5, key="d_personas"
        )
    with col_d3:
        prendas_d = st.slider(
            "Prendas / persona / año", 5, 100, 25, 5, key="d_prendas"
        )
    with col_d4:
        anos_d = st.slider("Horizonte (años)", 3, 20, 10, 1, key="d_anos")

    with st.spinner("Simulando 2,000 trayectorias de deuda social..."):
        res_d = simular_deuda_social(
            empresa_nombre=empresa_d,
            prenda_key=prenda_key,
            n_personas=n_personas_d,
            prendas_por_persona=prendas_d,
            anos=anos_d,
            n_sim=2000,
        )

    def fmt_usd(n):
        if n >= 1e6:
            return f"${n/1e6:.2f}M USD"
        if n >= 1e3:
            return f"${n/1e3:.1f}k USD"
        return f"${n:,.0f} USD"

    md1, md2, md3, md4 = st.columns(4)
    md1.metric(
        f"Deuda P50 (año {anos_d})",
        fmt_usd(res_d["p50_final_usd"]),
        f"≈ ${res_d['p50_final_mxn']:,.0f} MXN",
    )
    md2.metric(
        "Deuda adversa (P90)",
        fmt_usd(res_d["p90_final_usd"]),
        f"≈ ${res_d['p90_final_mxn']:,.0f} MXN",
        delta_color="inverse",
    )
    md3.metric(
        "Deuda por prenda (prom.)",
        f"${res_d['brecha_prom_usd_por_prenda']:.3f} USD",
        f"≈ ${res_d['brecha_prom_mxn_por_prenda']:.2f} MXN",
        delta_color="inverse",
    )
    clave_bgd = [k for k in res_d["años_cruce_umbrales"] if "Bangladesh" in k and "mínimo" in k]
    if clave_bgd:
        datos_bgd = res_d["años_cruce_umbrales"][clave_bgd[0]]
        cruce_bgd = datos_bgd["años_p50"]
        md4.metric(
            "Años hasta = salario anual BGD",
            f"{cruce_bgd} años" if cruce_bgd else f">{anos_d} años",
            f"({datos_bgd['pct_escenarios_supera']}% de simulaciones lo superan)",
            delta_color="inverse",
        )

    anos_labels_d = [f"Año {i}" for i in range(anos_d + 1)]
    anos_labels_d[0] = "Hoy"

    fig_d = go.Figure()

    muestra_d = res_d["trayectorias_mxn"][:300]
    for tray in muestra_d:
        fig_d.add_trace(go.Scatter(
            x=anos_labels_d, y=tray,
            mode="lines",
            line=dict(color="rgba(217,3,104,0.04)", width=1),
            showlegend=False, hoverinfo="skip",
        ))

    p25_mxn = [v * TC_MXN for v in res_d["p25_usd"]]
    p75_mxn = [v * TC_MXN for v in res_d["p75_usd"]]
    fig_d.add_trace(go.Scatter(
        x=anos_labels_d + anos_labels_d[::-1],
        y=p75_mxn + p25_mxn[::-1],
        fill="toself",
        fillcolor="rgba(217,3,104,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Banda P25–P75",
        hoverinfo="skip",
    ))

    for pct_key, nombre, color, ancho in [
        ("p50_usd", "Mediana (P50)", BERRY, 2.5),
        ("p90_usd", "Escenario adverso (P90)", "#7C0032", 2),
    ]:
        fig_d.add_trace(go.Scatter(
            x=anos_labels_d,
            y=[v * TC_MXN for v in res_d[pct_key]],
            mode="lines", name=nombre,
            line=dict(color=color, width=ancho),
        ))

    colores_umbrales = [GREEN, "#34D399", "#6EE7B7", "#A7F3D0"]
    for (etiqueta, datos), color_u in zip(res_d["años_cruce_umbrales"].items(), colores_umbrales):
        umbral_mxn = datos["umbral_usd"] * TC_MXN
        fig_d.add_hline(
            y=umbral_mxn,
            line_dash="dot",
            line_color=color_u,
            annotation_text=etiqueta.replace("\n", " ") + f" (${umbral_mxn:,.0f} MXN)",
            annotation_font_size=10,
            annotation_font_color=color_u,
        )

    fig_d.update_layout(
        **{
            **PLOTLY_LAYOUT,
            "height": 500,
            "title": (
                f"Deuda Social Acumulada — {empresa_d} · {n_personas_d} personas × "
                f"{prendas_d} prendas/año · {prenda_label}"
            ),
            "yaxis": dict(**PLOTLY_LAYOUT["yaxis"], title="Deuda social acumulada (MXN)", tickformat="$,.0f"),
        }
    )
    st.plotly_chart(fig_d, use_container_width=True)

    st.subheader("¿Cuándo se equipara a un salario anual real?")
    st.caption(
        "Las líneas de puntos en la gráfica corresponden a estos umbrales. "
        "'Cruce P50' = escenario mediano, 'Cruce P90' = escenario adverso."
    )
    filas_umbrales = []
    for etiqueta, datos in res_d["años_cruce_umbrales"].items():
        filas_umbrales.append({
            "Referencia salarial": etiqueta.replace("\n", " "),
            "Umbral (USD/año)": f"${datos['umbral_usd']:,}",
            "Umbral (MXN)": f"${datos['umbral_usd'] * TC_MXN:,.0f}",
            "Cruce P50": f"{datos['años_p50']} años" if datos["años_p50"] else f">{anos_d} años",
            "Cruce P90": f"{datos['años_p90']} años" if datos["años_p90"] else f">{anos_d} años",
            "% sim. que superan": f"{datos['pct_escenarios_supera']}%",
        })
    st.dataframe(pd.DataFrame(filas_umbrales), use_container_width=True, hide_index=True)

    st.subheader("Comparativa de Deuda Social por Empresa")
    st.caption(
        "Mismo salón, misma prenda — deuda social generada por cada marca "
        "según dónde produce y cuánto paga."
    )
    with st.spinner("Calculando deuda social de todas las empresas..."):
        comparativa = comparar_empresas_deuda(
            prenda_key=prenda_key,
            n_personas=n_personas_d,
            prendas_por_persona=prendas_d,
            anos=anos_d,
            n_sim=500,
        )

    df_comp = pd.DataFrame([
        {
            "Empresa": r["empresa"],
            "Transparencia (%)": r["transparencia_pct"],
            f"Deuda P50 año {anos_d} (USD)": f"${r['p50_final_usd']:,.0f}",
            f"Deuda P90 año {anos_d} (USD)": f"${r['p90_final_usd']:,.0f}",
            "Deuda/prenda prom. (USD)": f"${r['brecha_prom_usd_por_prenda']:.3f}",
            "Países manufactura": ", ".join(r["paises_manufactura"]),
        }
        for r in comparativa
    ])
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    empresas_comp = [r["empresa"] for r in comparativa]
    p50_comp_mxn = [r["p50_final_mxn"] for r in comparativa]
    p90_comp_mxn = [r["p90_final_mxn"] for r in comparativa]

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name=f"Deuda P50 (año {anos_d})",
        x=empresas_comp, y=p50_comp_mxn,
        marker_color=BERRY,
        text=[f"${v:,.0f}" for v in p50_comp_mxn],
        textposition="outside",
        textfont=dict(size=10, color=MINT),
    ))
    fig_comp.add_trace(go.Bar(
        name=f"Deuda P90 (año {anos_d})",
        x=empresas_comp, y=p90_comp_mxn,
        marker_color="#F472B6",
        text=[f"${v:,.0f}" for v in p90_comp_mxn],
        textposition="outside",
        textfont=dict(size=10, color=MINT),
    ))
    fig_comp.update_layout(
        **{
            **PLOTLY_LAYOUT,
            "barmode": "group",
            "height": 380,
            "title": f"Deuda Social Acumulada por Empresa — {prenda_label} · {anos_d} años",
            "yaxis": dict(**PLOTLY_LAYOUT["yaxis"], title="MXN", tickformat="$,.0f"),
        }
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.info(
        f"**Interpretación:** Cada prenda de {empresa_d} genera en promedio "
        f"**${res_d['brecha_prom_usd_por_prenda']:.3f} USD** de deuda salarial no compensada "
        f"(diferencia entre salario mínimo pagado y salario digno requerido, ponderada por riesgo país). "
        f"Con {n_personas_d} personas × {prendas_d} prendas/año, en {anos_d} años "
        f"la deuda acumulada mediana es **{fmt_usd(res_d['p50_final_usd'])}**."
    )