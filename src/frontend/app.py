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
st.header("🧠 Módulos Avanzados de Simulación")

from src.algoritmo.monte_carlo import simular_umbrales_co2
from src.algoritmo.monte_carlo_hidrico import simular_huella_hidrica
from src.algoritmo.monte_carlo_deuda_social import simular_deuda_social, comparar_empresas_deuda

tab_co2, tab_hidrico, tab_deuda = st.tabs(
    [
        "🎲 Estrés Climático (Bono CO₂)",
        "💧 Agotamiento Hídrico Acumulado",
        "⚖️ Reloj de Deuda Social",
    ]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Monte Carlo: Sensibilidad al Precio del Bono de Carbono (v2)
# ══════════════════════════════════════════════════════════════════════════════
with tab_co2:
    from src.algoritmo.monte_carlo import simular_sensibilidad_co2, comparar_sensibilidad_todas

    st.subheader("🎲 Sensibilidad al Precio del Bono de Carbono")
    st.caption(
        "Simula 2,000 escenarios de precios de CO₂ (rango 3.5–200 MXN/kg, cubriendo desde el "
        "mercado voluntario actual hasta escenarios IPCC 2°C). "
        "**KPI central:** ¿A qué precio de carbono el costo de remediación CO₂ se vuelve "
        "materialmente significativo para cada marca? Esto **sí varía por empresa** porque "
        "depende de la vida útil de las prendas (transparencia → factor de reposición)."
    )

    col_mc1, col_mc2 = st.columns([1, 3])
    with col_mc1:
        empresa_mc = st.selectbox(
            "Marca a auditar", [e["nombre"] for e in EMPRESAS], key="empresa_co2"
        )
        st.markdown("**Escenarios de referencia (MXN/kg CO₂):**")
        st.markdown("- Actual México: **$3.50**")
        st.markdown("- Objetivo París 2030: **$35**")
        st.markdown("- IPCC 1.5°C (2050): **$100–200**")

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
            "Escenarios c_ambiental > etiqueta",
            f"{res_co2['pct_c_ambiental_supera_etiqueta']:.0f}%",
            "de 2,000 simulaciones",
            delta_color="inverse",
        )

    # ── Gráfica 1: Curva de sensibilidad — c_co2(precio) por empresa ─────────
    with st.spinner("Comparando todas las marcas..."):
        todas_co2 = comparar_sensibilidad_todas(material_key, prenda_key, n_simulaciones=500)

    fig_curva = go.Figure()
    colores_curva = ["#e63946","#f4a261","#e9c46a","#2a9d8f","#264653","#a8dadc","#457b9d","#1d3557"]
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

    # Líneas verticales de escenarios de política
    for precio_ref, etiqueta_ref, color_ref in [
        (3.5,  "Actual MX",     "rgba(200,200,200,0.5)"),
        (35.0, "Objetivo París","rgba(100,200,150,0.7)"),
        (100.0,"IPCC 1.5°C",   "rgba(255,150,50,0.7)"),
    ]:
        fig_curva.add_vline(
            x=precio_ref, line_dash="dash", line_color=color_ref,
            annotation_text=etiqueta_ref, annotation_font_size=10,
        )

    # Línea horizontal: precio de etiqueta de la empresa seleccionada
    fig_curva.add_hline(
        y=res_co2["precio_etiqueta"],
        line_dash="longdash", line_color="red",
        annotation_text=f"Etiqueta {empresa_mc} (${res_co2['precio_etiqueta']} MXN)",
        annotation_font_size=10,
    )

    fig_curva.update_layout(
        height=420,
        title=f"Curva de Sensibilidad: Costo CO₂ por prenda vs Precio del Bono — {mat_label}",
        xaxis=dict(title="Precio del bono de carbono (MXN/kg CO₂)", gridcolor="rgba(200,200,200,0.15)"),
        yaxis=dict(title="Costo remediación CO₂ por prenda (MXN)", gridcolor="rgba(200,200,200,0.15)"),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
    )
    st.plotly_chart(fig_curva, use_container_width=True)

    # ── Gráfica 2: Histograma del costo ambiental bajo incertidumbre ─────────
    fig_hist_co2 = px.histogram(
        x=res_co2["sim_c_ambiental"],
        nbins=50,
        labels={"x": "Costo ambiental total simulado (MXN/prenda)", "y": "Escenarios"},
        title=f"Distribución del Costo Ambiental bajo 2,000 escenarios de precio CO₂ — {empresa_mc}",
        color_discrete_sequence=["#8E44AD"],
    )
    fig_hist_co2.add_vline(
        x=res_co2["c_ambiental_base"], line_dash="dash", line_color="cyan",
        annotation_text=f"Base actual (${res_co2['c_ambiental_base']:,.0f} MXN)",
        annotation_font_size=10,
    )
    fig_hist_co2.add_vline(
        x=res_co2["precio_etiqueta"], line_dash="dash", line_color="red",
        annotation_text=f"Etiqueta (${res_co2['precio_etiqueta']} MXN)",
        annotation_font_size=10,
    )
    fig_hist_co2.update_layout(plot_bgcolor="rgba(0,0,0,0)", height=350)
    st.plotly_chart(fig_hist_co2, use_container_width=True)

    # ── Tabla comparativa de sensibilidad por empresa ─────────────────────────
    st.subheader("📊 Comparativa de sensibilidad por empresa")
    st.caption(
        "Empresas con vida útil baja (baja transparencia → alta frecuencia de reposición) "
        "tienen mayor sensibilidad al precio del carbono. "
        "El breakeven es el precio de bono donde el costo de remediación CO₂ supera el 25% del precio de etiqueta."
    )
    df_sens = pd.DataFrame([
        {
            "Empresa": r["empresa"],
            "Transparencia": f"{r['transparencia_pct']}%",
            "Vida útil (meses)": r["vida_util_meses"],
            "Sensibilidad (MXN/prenda\npor MXN/kg CO₂)": r["sensibilidad_co2_mxn_por_mxn_kg"],
            "Breakeven 25% etiqueta\n(MXN/kg CO₂)": r["co2_breakeven_25pct_etiqueta"],
            "c_ambiental base (MXN)": f"${r['c_ambiental_base']:,.0f}",
            "% c_amb vs etiqueta": f"{r['pct_ambiental_vs_etiqueta']:.0f}%",
        }
        for r in todas_co2
    ])
    st.dataframe(df_sens, use_container_width=True, hide_index=True)

    st.info(
        f"📌 **Interpretación:** Con el precio actual del bono de carbono ($3.50 MXN/kg), "
        f"**{empresa_mc}** genera un costo de remediación CO₂ de **${res_co2['c_co2_base']:.2f} MXN** "
        f"por prenda de {mat_label}. Si el precio subiera al nivel del Acuerdo de París ($35 MXN/kg), "
        f"ese costo subiría a **${res_co2['sensibilidad_co2_mxn_por_mxn_kg']*35:.2f} MXN** por prenda. "
        f"La empresa con mayor sensibilidad es **{todas_co2[0]['empresa']}** "
        f"({todas_co2[0]['sensibilidad_co2_mxn_por_mxn_kg']:.2f} MXN/prenda por MXN/kg CO₂) "
        f"porque sus prendas duran solo {todas_co2[0]['vida_util_meses']} meses en promedio, "
        f"amplificando el impacto de cada producción."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Monte Carlo: Agotamiento Hídrico Acumulado (v3 — referencias adaptativas)
# ══════════════════════════════════════════════════════════════════════════════
with tab_hidrico:
    st.subheader("💧 Simulación de Agotamiento Hídrico Acumulado")
    st.caption(
        "¿Cuántos años tarda el consumo del salón en equivaler a una alberca olímpica, "
        "al Lago de Chapultepec o a la Presa Cutzamala? "
        "Las referencias son **adaptativas al material**: siempre hay al menos un cruce "
        "visible en el horizonte. Poliéster (62 L/kg) y algodón (10,000 L/kg) "
        "tienen escalas muy distintas — la gráfica lo refleja correctamente."
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
        st.markdown("**Material seleccionado:**")
        st.markdown(f"**{mat_label}**")
        litros_kg = MATERIALES[material_key]['huella_hidrica_litros_kg']
        st.caption(f"{litros_kg:,} L/kg fibra")

    with st.spinner("🌊 Simulando 2,000 trayectorias hídricas..."):
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

    # ── Métricas resumen ──────────────────────────────────────────────────────
    mh1, mh2, mh3, mh4 = st.columns(4)
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
    mh4.metric(
        "Litros por prenda",
        fmt_litros(res_h["litros_por_prenda_base"]),
        f"base sin incertidumbre",
    )

    # ── Gráfica: haz + bandas + referencias adaptativas ──────────────────────
    anos_labels = [f"Año {i}" for i in range(anos_h + 1)]
    anos_labels[0] = "Hoy"

    fig_h = go.Figure()

    # Haz de trayectorias (muestra, alpha muy bajo)
    for tray in res_h["trayectorias_muestra"][:300]:
        fig_h.add_trace(go.Scatter(
            x=anos_labels, y=tray, mode="lines",
            line=dict(color="rgba(55,120,200,0.04)", width=1),
            showlegend=False, hoverinfo="skip",
        ))

    # Banda P25–P75
    fig_h.add_trace(go.Scatter(
        x=anos_labels + anos_labels[::-1],
        y=res_h["p75"] + res_h["p25"][::-1],
        fill="toself", fillcolor="rgba(55,120,200,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Banda P25–P75", hoverinfo="skip",
    ))

    # Percentiles principales
    for pct_key, nombre, color, ancho in [
        ("p50", "Mediana (P50)", "#3a85d4", 2.5),
        ("p90", "Escenario adverso (P90)", "#d4703a", 2),
        ("p99", "Worst case (P99)", "#7a3010", 1.5),
    ]:
        fig_h.add_trace(go.Scatter(
            x=anos_labels, y=res_h[pct_key], mode="lines",
            name=nombre, line=dict(color=color, width=ancho),
        ))

    # Referencias adaptativas (líneas horizontales al nivel del volumen)
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
        )

    fig_h.update_layout(
        height=500,
        title=(
            f"Haz Monte Carlo — Huella Hídrica Acumulada · "
            f"{n_personas_h} personas × {prendas_h} prendas/año · {mat_label}"
        ),
        yaxis=dict(
            title="Litros acumulados",
            tickformat=".3s",
            gridcolor="rgba(200,200,200,0.15)",
        ),
        xaxis=dict(gridcolor="rgba(200,200,200,0.15)"),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
    )
    st.plotly_chart(fig_h, use_container_width=True)

    # ── Tabla de equivalencias ────────────────────────────────────────────────
    st.subheader("🏊 Equivalencias de referencia")
    st.caption(
        "Referencias seleccionadas adaptativamente según el material. "
        "Cada cruce representa el año en que el consumo acumulado del salón "
        "iguala el volumen de esa referencia."
    )
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

    # ── Nota interpretativa contextualizada al material actual ────────────────
    # Encontrar la primera referencia con cruce visible
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
            f"Esto es solo el agua embebida en la **producción de la fibra** "
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
    st.info(f"📌 **Interpretación:** {interp}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Monte Carlo: Reloj de Deuda Social
# ══════════════════════════════════════════════════════════════════════════════
with tab_deuda:
    st.subheader("⚖️ Reloj de Deuda Social Acumulada")
    st.caption(
        "¿Cuántos años tarda el consumo del salón en acumular una deuda salarial equivalente al "
        "sueldo anual completo de un trabajador textil? "
        "Variables estocásticas: brecha salarial (±20%), tipo de cambio (±8%), "
        "factor de riesgo laboral (±15%), prendas consumidas (±20%)."
    )

    # ── Controles ─────────────────────────────────────────────────────────────
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

    # ── Simulación empresa seleccionada ───────────────────────────────────────
    with st.spinner("⚖️ Simulando 2,000 trayectorias de deuda social..."):
        res_d = simular_deuda_social(
            empresa_nombre=empresa_d,
            prenda_key=prenda_key,
            n_personas=n_personas_d,
            prendas_por_persona=prendas_d,
            anos=anos_d,
            n_sim=2000,
        )

    # ── Métricas resumen ──────────────────────────────────────────────────────
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
    # Cruce con Bangladesh mínimo
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

    # ── Gráfica principal: haz de trayectorias ────────────────────────────────
    anos_labels_d = [f"Año {i}" for i in range(anos_d + 1)]
    anos_labels_d[0] = "Hoy"

    fig_d = go.Figure()

    muestra_d = res_d["trayectorias_mxn"][:300]
    for tray in muestra_d:
        fig_d.add_trace(go.Scatter(
            x=anos_labels_d, y=tray,
            mode="lines",
            line=dict(color="rgba(180,30,30,0.04)", width=1),
            showlegend=False, hoverinfo="skip",
        ))

    # Banda de incertidumbre
    p25_mxn = [v * TC_MXN for v in res_d["p25_usd"]]
    p75_mxn = [v * TC_MXN for v in res_d["p75_usd"]]
    fig_d.add_trace(go.Scatter(
        x=anos_labels_d + anos_labels_d[::-1],
        y=p75_mxn + p25_mxn[::-1],
        fill="toself",
        fillcolor="rgba(180,30,30,0.10)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Banda P25–P75",
        hoverinfo="skip",
    ))

    # Percentiles clave (convertidos a MXN para el eje)
    for pct_key, nombre, color, ancho in [
        ("p50_usd", "Mediana (P50)", "#a32d2d", 2.5),
        ("p90_usd", "Escenario adverso (P90)", "#501313", 2),
    ]:
        fig_d.add_trace(go.Scatter(
            x=anos_labels_d,
            y=[v * TC_MXN for v in res_d[pct_key]],
            mode="lines", name=nombre,
            line=dict(color=color, width=ancho),
        ))

    # Líneas de umbrales de referencia
    colores_umbrales = ["#0f6e56", "#1d9e75", "#5dcaa5", "#9fe1cb"]
    for (etiqueta, datos), color_u in zip(res_d["años_cruce_umbrales"].items(), colores_umbrales):
        umbral_mxn = datos["umbral_usd"] * TC_MXN
        fig_d.add_hline(
            y=umbral_mxn,
            line_dash="dot",
            line_color=color_u,
            annotation_text=etiqueta.replace("\n", " ") + f" (${umbral_mxn:,.0f} MXN)",
            annotation_font_size=10,
        )

    fig_d.update_layout(
        height=500,
        title=(
            f"Deuda Social Acumulada — {empresa_d} · {n_personas_d} personas × "
            f"{prendas_d} prendas/año · {prenda_label}"
        ),
        yaxis=dict(
            title="Deuda social acumulada (MXN)",
            tickformat="$,.0f",
            gridcolor="rgba(200,200,200,0.15)",
        ),
        xaxis=dict(gridcolor="rgba(200,200,200,0.15)"),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
    )
    st.plotly_chart(fig_d, use_container_width=True)

    # ── Tabla: años hasta cruce con cada umbral salarial ─────────────────────
    st.subheader("🧮 ¿Cuándo se equipara a un salario anual real?")
    st.caption(
        "Las líneas de puntos en la gráfica corresponden a estos umbrales. "
        "'Cruce P50' = en el escenario mediano, 'Cruce P90' = en el escenario adverso."
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

    # ── Comparativa entre empresas ────────────────────────────────────────────
    st.subheader("🏭 Comparativa de Deuda Social por Empresa")
    st.caption(
        "Mismo salón, misma prenda — ¿cuánta deuda social genera cada marca "
        "según dónde produce y cuánto paga?"
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

    # Gráfica de barras comparativa (P50 final en MXN)
    empresas_comp = [r["empresa"] for r in comparativa]
    p50_comp_mxn = [r["p50_final_mxn"] for r in comparativa]
    p90_comp_mxn = [r["p90_final_mxn"] for r in comparativa]

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name=f"Deuda P50 (año {anos_d})",
        x=empresas_comp, y=p50_comp_mxn,
        marker_color="#a32d2d",
        text=[f"${v:,.0f}" for v in p50_comp_mxn],
        textposition="outside",
    ))
    fig_comp.add_trace(go.Bar(
        name=f"Deuda P90 (año {anos_d})",
        x=empresas_comp, y=p90_comp_mxn,
        marker_color="#f09595",
        text=[f"${v:,.0f}" for v in p90_comp_mxn],
        textposition="outside",
    ))
    fig_comp.update_layout(
        barmode="group",
        height=380,
        title=f"Deuda Social Acumulada por Empresa — {prenda_label} · {anos_d} años",
        yaxis=dict(title="MXN", tickformat="$,.0f", gridcolor="rgba(200,200,200,0.15)"),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.info(
        f"📌 **Interpretación:** Cada prenda de {empresa_d} genera en promedio "
        f"**${res_d['brecha_prom_usd_por_prenda']:.3f} USD** de deuda salarial no compensada "
        f"(diferencia entre salario mínimo pagado y salario digno requerido, ponderada por riesgo país). "
        f"Con {n_personas_d} personas × {prendas_d} prendas/año, en {anos_d} años "
        f"la deuda acumulada mediana es **{fmt_usd(res_d['p50_final_usd'])}**."
    )