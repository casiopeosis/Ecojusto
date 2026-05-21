# EcoJusto AI

**Auditor algorítmico de externalidades socioambientales en la industria de la moda**

EcoJusto AI es un sistema de análisis cuantitativo que calcula el precio justo real de una prenda de ropa, revelando los costos externos que las marcas transfieren a la sociedad y al medio ambiente. El sistema integra Teoría de la Información, Procesos de Decisión de Markov, Teoría de Juegos, datos en tiempo real del Banco Mundial y simulaciones Monte Carlo para producir un dashboard interactivo comparativo entre empresas, parametrizado por material y tipo de prenda.

---

## Tabla de contenidos

1. [Propósito y contexto](#1-propósito-y-contexto)
2. [Input y output del sistema](#2-input-y-output-del-sistema)
3. [Arquitectura del sistema](#3-arquitectura-del-sistema)
4. [Base de datos y fuentes](#4-base-de-datos-y-fuentes)
5. [Módulo 1 — Costo de producción real (FOB + Landed Cost)](#5-módulo-1--costo-de-producción-real-fob--landed-cost)
6. [Módulo 2 — Penalización por opacidad informacional (KL Divergence)](#6-módulo-2--penalización-por-opacidad-informacional-kl-divergence)
7. [Módulo 3 — Costo ambiental por ciclo de vida (Cadenas de Markov)](#7-módulo-3--costo-ambiental-por-ciclo-de-vida-cadenas-de-markov)
8. [Módulo 4 — Costo social y brecha salarial (Teoría de Juegos)](#8-módulo-4--costo-social-y-brecha-salarial-teoría-de-juegos)
9. [Ensamblaje: cálculo del precio justo](#9-ensamblaje-cálculo-del-precio-justo)
10. [Módulo 5 — Simulación Monte Carlo: sensibilidad al precio de carbono](#10-módulo-5--simulación-monte-carlo-sensibilidad-al-precio-de-carbono)
11. [Módulo 6 — Simulación Monte Carlo: agotamiento hídrico acumulado](#11-módulo-6--simulación-monte-carlo-agotamiento-hídrico-acumulado)
12. [Módulo 7 — Simulación Monte Carlo: reloj de deuda social](#12-módulo-7--simulación-monte-carlo-reloj-de-deuda-social)
13. [Módulo LLM — Narrativa interpretativa](#13-módulo-llm--narrativa-interpretativa)
14. [Complejidad algorítmica](#14-complejidad-algorítmica)
15. [Stack tecnológico](#15-stack-tecnológico)
16. [Estructura del proyecto](#16-estructura-del-proyecto)
17. [Instrucciones de instalación](#17-instrucciones-de-instalación)
18. [Supuestos, limitaciones y trabajo futuro](#18-supuestos-limitaciones-y-trabajo-futuro)

---

## 1. Propósito y contexto

La industria de la moda genera entre 4% y 8% de las emisiones globales de gases de efecto invernadero, consume aproximadamente 93,000 millones de metros cúbicos de agua al año y es responsable de una cadena de suministro donde los salarios pagados en países de manufactura se sitúan consistentemente por debajo del umbral de subsistencia definido por la Organización Internacional del Trabajo. Estos costos no aparecen en el precio de etiqueta: son externalizados hacia trabajadores, comunidades locales y el sistema climático global.

EcoJusto AI cuantifica esas externalidades de forma sistemática y las traduce a la unidad de análisis más directa: el precio adicional que una prenda debería costar si la empresa que la produce internalizara el daño real que genera. El sistema no es un ejercicio de opinión; cada componente del precio justo se deriva de una metodología matemática con sustento en literatura académica y datos públicos verificables.

El proyecto fue desarrollado como prototipo académico avanzado en el contexto de un curso de Inteligencia Artificial, con énfasis en la aplicación de técnicas formales de ML, matemáticas discretas y simulación estocástica a problemas de impacto social medible.

---

## 2. Input y output del sistema

### Input

El sistema recibe dos parámetros del usuario a través del frontend Streamlit:

| Parámetro | Tipo | Valores disponibles |
|---|---|---|
| `material_key` | `str` | `poliester`, `algodon_conv`, `algodon_org`, `lana`, `viscosa` |
| `prenda_key` | `str` | `playera`, `jeans`, `sudadera`, `vestido`, `chamarra` |

Las ocho empresas de la base de datos se evalúan simultáneamente con los mismos parámetros.

Los módulos Monte Carlo (Módulos 5, 6 y 7) aceptan parámetros adicionales a través del frontend: número de personas, prendas por persona por año y horizonte temporal en años.

### Output principal por empresa

```json
{
  "empresa": "H&M",
  "transparencia_pct": 62,
  "nivel": "media",
  "alpha_opacidad": 1.147,
  "precio_etiqueta_mxn": 349,
  "p_justo_mxn": 7838,
  "brecha_mxn": -7489,
  "veredicto": "externaliza",
  "fob_ponderado_usd": 4.21,
  "landed_cost_usd": 9.18,
  "landed_cost_mxn": 175,
  "c_ambiental_mxn": 1240,
  "c_social_mxn": 388,
  "vida_util_meses": 5.8,
  "huella_hidrica_litros": 620,
  "co2_kg": 0.94
}
```

El veredicto categórico sigue la escala:

| Ratio etiqueta / P_justo | Veredicto |
|---|---|
| < 0.60 | `externaliza` |
| 0.60 – 0.90 | `subestimado` |
| 0.90 – 1.15 | `alineado` |
| 1.15 – 1.50 | `margen_alto` |
| > 1.50 | `sobreprecio` |

---

## 3. Arquitectura del sistema

```
src/
├── data/
│   ├── db.py                        # Base de datos estática: EMPRESAS, MATERIALES, PRENDAS
│   └── world_bank.py                # API Banco Mundial: indicadores laborales en tiempo real
│
└── algoritmo/
    ├── opacidad.py                  # Módulo 2: D_KL → alpha_e
    ├── markov.py                    # Módulo 3: Cadena absorbente + factor de reposición
    ├── social.py                    # Módulo 4: brecha salarial ponderada por país
    ├── costo_produccion.py          # Módulo 1: FOB + Landed Cost por país de manufactura
    ├── ensamblaje.py                # Orquestación: P_justo para todas las empresas
    ├── monte_carlo.py               # Módulo 5: sensibilidad al precio del bono CO2
    ├── monte_carlo_hidrico.py       # Módulo 6: agotamiento hídrico acumulado
    └── monte_carlo_deuda_social.py  # Módulo 7: reloj de deuda social

frontend/
└── app.py                           # Streamlit: sidebar, gráficas, tabs de simulación
```

El flujo de ejecución para cada empresa es secuencial y estrictamente acíclico:

```
db.py
  └── costo_produccion.py   → FOB_ponderado, Landed_ponderado
  └── opacidad.py           → alpha_e
  └── markov.py             → vida_util, c_ambiental
  └── social.py             ←── world_bank.py (API o fallback)
                            → c_social
  └── ensamblaje.py         → P_justo, veredicto, desglose completo
```

---

## 4. Base de datos y fuentes

### 4.1 Empresas

Ocho empresas con distribución real de manufactura por país:

| Empresa | FTI (%) | Distribución de manufactura (ISO3 : fracción) |
|---|---|---|
| Shein | 5 | CHN:0.95, VNM:0.05 |
| Primark | 22 | BGD:0.45, IND:0.30, CHN:0.15, PAK:0.10 |
| H&M | 62 | BGD:0.27, CHN:0.21, TUR:0.12, IND:0.10, otros |
| Zara (Inditex) | 55 | PRT:0.20, ESP:0.15, MAR:0.18, TUR:0.14, otros |
| Nike | 68 | VNM:0.50, IDN:0.25, CHN:0.14, THA:0.11 |
| Adidas | 74 | VNM:0.27, IDN:0.19, CHN:0.16, otros |
| Levi's | 70 | MEX:0.25, BGD:0.20, LKA:0.15, KHM:0.12, otros |
| Patagonia | 92 | VNM:0.35, MEX:0.20, USA:0.15, LKA:0.15, otros |

La distribución de manufactura es un promedio ponderado de fuentes públicas: informes de sostenibilidad de cada empresa (2023–2024), Fashion Transparency Index 2024 y análisis de la base de datos de importaciones de EE.UU. (USITC).

### 4.2 Materiales

| Material | Huella hídrica (L/kg) | CO2 (kg/kg fibra) | Peso playera (kg) |
|---|---|---|---|
| Poliéster | 62 | 14.2 | 0.20 |
| Algodón convencional | 10,000 | 4.7 | 0.20 |
| Algodón orgánico | 6,000 | 2.5 | 0.20 |
| Lana | 17,000 | 18.5 | 0.40 |
| Viscosa | 3,000 | 5.2 | 0.18 |

Fuentes: Textile Exchange Preferred Fiber & Materials Report 2023; Quantis, Life Cycle Assessment of Apparel (2018); Common Objective, Fibre Briefing Series (2022).

### 4.3 Salarios y datos laborales

Datos de salario mínimo y salario digno para 16 países de manufactura, con fuente en:

- OIT — ILOSTAT, módulo de salarios mínimos (edición 2023)
- WageIndicator Foundation, Global Wage Database (2023–2024)
- SEDLAC / CEPAL para países de América Latina

Los datos de salario digno (*living wage*) siguen la metodología Anker de la Global Living Wage Coalition, que estima el salario necesario para cubrir alimentación, vivienda, atención médica, educación y un margen de ahorro modesto en cada contexto geográfico.

### 4.4 Indicadores laborales en tiempo real

El módulo `world_bank.py` consulta la API del Banco Mundial para dos indicadores:

- `SL.EMP.VULN.ZS` — Empleo vulnerable como porcentaje del total (OIT)
- `SL.UEM.TOTL.ZS` — Tasa de desempleo total

El factor de riesgo laboral se calcula como:

```
factor = 0.7 × (vulnerabilidad / 50) + 0.3 × (desempleo / 5)
```

normalizado al rango [0.3, 2.0]. Si la API falla o no devuelve datos para el período solicitado, el sistema utiliza un diccionario de fallback calibrado manualmente con base en informes de la OIT y el Global Rights Index de la ITUC (2023).

### 4.5 Fuentes de referencia completas

| Fuente | Uso en el sistema |
|---|---|
| Fashion Transparency Index 2024 — Fashion Revolution | Índice de transparencia por empresa (0–100%) |
| OIT — ILOSTAT, Wage Statistics | Salarios mínimos por país |
| WageIndicator Foundation | Salarios dignos (metodología Anker) |
| World Bank Open Data API | Vulnerabilidad laboral y desempleo en tiempo real |
| ITUC Global Rights Index 2023 | Fallback del factor de riesgo laboral |
| Textile Exchange — Preferred Fiber Report 2023 | Huellas hídricas y CO2 por fibra |
| Quantis LCA of Apparel 2018 | Análisis de ciclo de vida por material |
| Ellen MacArthur Foundation — A New Textiles Economy (2017) | Tasas de transición Markov y vida útil de prendas |
| SACMEX / CONAGUA — Reporte Anual 2023 | Consumo anual de agua CDMX (referencia hídrica) |
| FINA Technical Regulations 2022 | Volumen de alberca olímpica (referencia hídrica) |
| CONAGUA — Informe Sistema Cutzamala 2023 | Capacidad útil Presa Cutzamala (referencia hídrica) |
| IPCC AR6 — Working Group III (2022) | Rango de escenarios de precio de carbono |
| Acuerdo de París — NDC Registry | Precio de carbono objetivo 2030 |
| USITC — Import Statistics | Distribución de manufactura por país por empresa |
| Informes de sostenibilidad corporativa 2023–2024 | Validación de distribución de manufactura |

---

## 5. Módulo 1 — Costo de producción real (FOB + Landed Cost)

### Objetivo

Calcular el costo real de fabricar una prenda, considerando fibra, acabado, mano de obra y logística internacional, ponderado por la distribución de manufactura de cada empresa entre múltiples países.

### FOB (Free On Board)

El FOB por país se descompone en tres componentes:

**Costo de materiales:**

```
costo_fibra = precio_fibra[pais] × peso_kg
costo_acabado = precio_acabado[pais] × (peso_kg × 1.3)  # factor densidad ~0.77 kg/m²
costo_trims = constante por material
costo_materiales = costo_fibra + costo_acabado + costo_trims
```

**Costo de manufactura (labor):**

```
costo_hora = salario_minimo_usd[pais] / horas_mes[pais]
costo_labor = costo_hora × horas_manufactura[prenda]
```

**FOB total:**

```
FOB[pais] = costo_materiales + costo_labor
```

### Landed Cost

El landed cost incorpora los costos de llevar la prenda desde la fábrica hasta el almacén del mercado destino:

```
ocean_freight = tarifa_por_kg[origen] × peso_kg
aranceles     = FOB × arancel_pct[destino]     # 18% USA, 20% EU (promedio textil)
handling      = costo_fijo / 1000               # amortizado por prenda
insurance     = FOB × 1.5%
inland        = (FOB + ocean + aranceles) × 5%

landed_cost = FOB + ocean_freight + aranceles + handling + insurance + inland
```

### Ponderación por distribución de manufactura

Dado que cada empresa fabrica en múltiples países con distintas fracciones:

```
FOB_ponderado   = Σ (FOB[pais_i] × fraccion_i)
landed_ponderado = Σ (landed[pais_i] × fraccion_i)
```

Este promedio ponderado refleja que una empresa que produce 45% en Bangladesh y 30% en India tiene un costo de producción diferente a otra que produce 95% en China.

---

## 6. Módulo 2 — Penalización por opacidad informacional (KL Divergence)

### Fundamento matemático

El módulo cuantifica la brecha entre el nivel ideal de divulgación corporativa y el nivel real de cada empresa, utilizando la **Divergencia de Kullback-Leibler**, métrica central de la Teoría de la Información (Shannon, 1948; Kullback y Leibler, 1951).

La divergencia KL mide la información adicional necesaria para describir la distribución real Q a partir de la distribución de referencia P:

$$D_{KL}(P \| Q_e) = \sum_{x \in \mathcal{X}} P(x) \log\left(\frac{P(x)}{Q_e(x)}\right)$$

**Definición de distribuciones:**

- $P$: distribución ideal de reporte, modelada como distribución puntual en el máximo de transparencia (P = 1.0), representando a la empresa con mayor puntaje del Fashion Transparency Index como referencia normativa.
- $Q_e$: distribución real de la empresa $e$, derivada de su puntaje FTI normalizado al rango (0, 1]. Una empresa con transparencia $\tau = 0.05$ como Shein asigna casi toda su masa de probabilidad a una fracción mínima de las dimensiones evaluadas.

Bajo esta modelización escalar, la divergencia se reduce a:

$$D_{KL}(P \| Q_e) = \log\left(\frac{1}{\tau_e}\right) = -\log(\tau_e)$$

**Factor de penalización:**

$$\alpha_e = 1 + \gamma \cdot D_{KL}(P \| Q_e) = 1 + \gamma \cdot (-\log(\tau_e))$$

con $\gamma = 0.3$ como parámetro de escala (hiperparámetro calibrable).

**Propiedades:**
- Si $\tau_e = 1.0$: $D_{KL} = 0 \Rightarrow \alpha_e = 1.0$ (sin penalización)
- Si $\tau_e = 0.05$ (Shein): $D_{KL} \approx 3.0 \Rightarrow \alpha_e \approx 1.90$
- Si $\tau_e = 0.92$ (Patagonia): $D_{KL} \approx 0.083 \Rightarrow \alpha_e \approx 1.025$

```python
def calcular_alpha(transparencia: float, gamma: float = 0.3) -> float:
    p = 1.0
    q = max(transparencia, 1e-9)
    dkl = p * np.log(p / q)
    return round(1 + gamma * dkl, 4)
```

**Complejidad:** O(1) temporal y espacial.

---

## 7. Módulo 3 — Costo ambiental por ciclo de vida (Cadenas de Markov)

### Objetivo

Estimar la vida útil esperada de una prenda mediante una cadena de Markov absorbente, y traducir esa duración en un costo de remediación ambiental escalado por el ritmo de reposición que el mercado impone.

### Espacio de estados y matriz de transición

El ciclo de vida de una prenda se modela con tres estados:

$$\mathcal{S} = \{\text{Activo},\ \text{Segunda Mano},\ \text{Basurero}\}$$

donde `Basurero` es el único estado absorbente. La dinámica está definida por:

```
Q = submatriz de estados transitorios (Activo y Segunda Mano):
    [ p_activo    p_segunda ]
    [ 0.0         p_2a_activo ]
```

Las probabilidades de transición base $p_{\text{basurero}}$ se calibran por material:

| Material | $p_{\text{basurero}}$ base |
|---|---|
| Poliéster | 0.73 |
| Algodón convencional | 0.57 |
| Algodón orgánico | 0.40 |
| Lana | 0.25 |
| Viscosa | 0.65 |

El factor de calidad ajusta la probabilidad de descarte según la transparencia de la empresa (proxy de calidad de manufactura):

```
calidad = 0.5 + transparencia × 0.5
factor_calidad = (calidad - 0.5) / 0.5
p_basurero = p_base × (1 - factor_calidad × 0.40)
```

### Vida útil esperada mediante la Matriz Fundamental de Kemeny

La vida útil esperada en estados transitorios se calcula mediante la inversa de $(I - Q)$:

$$F = (I - Q)^{-1}$$

El vector de tiempos esperados hasta absorción es $\mathbf{t} = F \cdot \mathbf{1}$. La vida útil de la prenda es el primer elemento de $\mathbf{t}$ (tiempo esperado desde el estado Activo):

```python
F = np.linalg.inv(np.eye(2) - Q)
vida_util = float((F @ np.ones(2))[0])
```

**Complejidad:** O(n³) para la inversión matricial, con n = 2 (constante en la práctica → O(1)).

### Factor de reposición y costo ambiental

Una vida útil corta implica que el consumidor repone la prenda con mayor frecuencia, multiplicando el impacto ambiental real del ciclo de producción. Se define una vida útil de referencia de 24 meses como estándar de durabilidad:

```
factor_reposicion = max(1.0, 24 / vida_util)
```

Los costos de remediación por prenda se calculan como:

```
c_agua = (huella_hidrica_L_kg × peso_kg) × COSTO_AGUA_MXN_POR_LT × factor_reposicion
c_co2  = (co2_kg_por_kg × peso_kg)       × COSTO_CO2_MXN_POR_KG  × factor_reposicion
c_ambiental = c_agua + c_co2
```

Los precios de remediación actuales ($COSTO\_CO2 = 3.50$ MXN/kg, $COSTO\_AGUA = 0.25$ MXN/L) son la base deterministadel módulo. Los Módulos 5 y 6 exploran el espacio de incertidumbre alrededor de estos valores.

---

## 8. Módulo 4 — Costo social y brecha salarial (Teoría de Juegos)

### Fundamento

El módulo cuantifica la externalidad laboral como la brecha entre el costo real de producción (salario mínimo pagado) y el costo de producción socialmente justo (salario digno), ponderada por el riesgo institucional del país de manufactura. Conceptualmente, esto formaliza el problema de la cadena de suministro como un juego asimétrico de información donde la empresa captura el excedente de la brecha salarial a expensas del trabajador.

### Cálculo por país

Para cada país de manufactura:

```
costo_hora_real  = salario_minimo_usd[pais] / horas_mes[pais]
costo_hora_digno = salario_digno_usd[pais] / horas_mes[pais]

costo_real_usd  = costo_hora_real  × horas_manufactura[prenda]
costo_digno_usd = costo_hora_digno × horas_manufactura[prenda]

brecha_usd        = max(0, costo_digno_usd - costo_real_usd)
factor_riesgo     = get_factor_riesgo_pais(iso)   # API Banco Mundial
c_social_pais_mxn = brecha_usd × factor_riesgo × TC_MXN
```

El factor de riesgo amplifica la brecha para países con mayor informalidad, represión sindical o vulnerabilidad laboral, y la reduce para países con instituciones laborales sólidas (factor mínimo: 0.30 para economías de alta protección).

### Ponderación por distribución de manufactura

```
c_social_total = Σ (c_social[pais_i] × fraccion_i)
```

Esta ponderación diferencia matemáticamente a empresas con distintas geografías de manufactura. Shein (95% China, factor_riesgo = 1.75) tiene un costo social diferente a Patagonia (15% USA, factor_riesgo = 0.30; 35% Vietnam, 1.40; etc.).

---

## 9. Ensamblaje: cálculo del precio justo

### Estructura de costos

El precio justo se construye en capas:

**Capa 1 — Base comercial (manufactura + logística + margen retail):**

```
precio_retail_base_mxn = landed_ponderado_usd × TC_MXN × markup_retail
```

El `markup_retail` (por defecto 2.8×) representa el margen acumulado de intermediación entre el costo de manufactura y el precio al consumidor, calibrado con base en datos de la industria del fast fashion.

**Capa 2 — Externalidades:**

```
c_ambiental_mxn  (del Módulo 3)
c_social_mxn     (del Módulo 4, convertido a MXN)
```

**Capa 3 — Penalización por opacidad:**

```
costo_base_etico = precio_retail_base + c_ambiental + c_social
costo_con_opacidad = costo_base_etico × alpha_e
```

**Capa 4 — Margen de reinversión para sustentabilidad:**

```
margen_reinversion = costo_con_opacidad × margen   # default 15%
P_justo = costo_con_opacidad + margen_reinversion
```

### Fórmula completa

$$P_{\text{justo}} = \alpha_e \cdot \left( P_{\text{retail}} + C_{\text{ambiental}} + C_{\text{social}} \right) \cdot (1 + m)$$

donde:
- $\alpha_e = 1 + 0.3 \cdot (-\log(\tau_e))$
- $P_{\text{retail}} = \text{landed\_usd} \times TC \times \mu_{\text{retail}}$
- $C_{\text{ambiental}} = (c_{\text{agua}} + c_{\text{co2}}) \times f_{\text{repos}}$
- $C_{\text{social}} = \sum_i \text{brecha}_i \times f_{\text{riesgo},i} \times w_i \times TC$
- $m = 0.15$ (margen de reinversión por defecto)

### Pipeline de ejecución

```python
def run_all(material_key, prenda_key, margen, markup_retail, mercado_destino):
    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]
    resultados = [
        calcular_precio_justo(e, mat, pre, prenda_key, mercado_destino, margen, markup_retail)
        for e in EMPRESAS
    ]
    return sorted(resultados, key=lambda x: x["brecha_mxn"])
```

**Complejidad total:** O(E log E) donde E = 8 empresas. El ordenamiento final domina.

---

## 10. Módulo 5 — Simulación Monte Carlo: sensibilidad al precio de carbono

### Problema y diagnóstico de la versión anterior

La implementación inicial calculaba el "umbral de quiebre CO2" como el percentil 90 de los precios de CO2 del vector de simulación ordenado por P_justo. Esto equivale algebraicamente al percentil 90 de Uniform(3.5, 25) ≈ 22.85 MXN/kg, una constante de distribución independiente de la empresa. El resultado era idéntico para todas las marcas porque el método no medía una propiedad de la empresa, sino una propiedad de la distribución de entrada.

### Rediseño

El módulo v2 reformula la pregunta: dado que el costo de remediación CO2 por prenda es lineal en el precio del bono, la sensibilidad real de cada empresa es:

$$\text{sensibilidad}_e = \frac{\partial c_{\text{CO}_2,e}}{\partial p_{\text{CO}_2}} = \frac{c_{\text{CO}_2,e}^{\text{base}}}{p_{\text{CO}_2}^{\text{base}}}$$

Esta sensibilidad **sí varía por empresa** porque $c_{\text{CO}_2}$ depende de $f_{\text{repos}}$, que a su vez depende de la vida útil esperada calculada por Markov, que depende de la transparencia de la empresa.

### Variables estocásticas

| Variable | Distribución | Rango | Justificación |
|---|---|---|---|
| Precio CO2 | Uniform(3.5, 200) MXN/kg | 3.5 = mercado voluntario México; 200 = límite IPCC AR6 escenario 1.5°C | Cubre todo el espectro de política climática conocido |
| Precio agua | Normal(0.25, σ=0.075) MXN/L | clip [0.05, 1.20] | Incertidumbre metodológica en valoración de agua |

### Métricas diferenciadas por empresa

**Sensibilidad analítica:** MXN adicionales en el costo ambiental por cada MXN/kg de aumento en el precio del bono de carbono.

**Precio de breakeven:**

$$p_{\text{CO}_2}^{\text{breakeven}} = \frac{\theta \cdot P_{\text{etiqueta}}}{\text{sensibilidad}_e}$$

donde $\theta$ es el umbral de materialidad (10%, 25% o 50% del precio de etiqueta). Este precio sí es específico de cada empresa.

**Ejemplo (algodón convencional, playera):**
- Shein: sensibilidad = 12.53 MXN/prenda por MXN/kg·CO2; breakeven 25% etiqueta = $2.97 MXN/kg
- Patagonia: sensibilidad = 8.68 MXN/prenda por MXN/kg·CO2; breakeven 25% etiqueta = $37.43 MXN/kg

La diferencia se explica porque Shein (transparencia = 5%) produce prendas con vida útil de ~1.5 meses → factor de reposición ≈ 16×, que amplifica el costo ambiental por unidad de tiempo de uso.

---

## 11. Módulo 6 — Simulación Monte Carlo: agotamiento hídrico acumulado

### Pregunta central

Si un grupo de N personas compra X prendas de un material determinado por año, ¿en cuántos años el agua embebida en su producción equivale a referencias hídricas concretas y localmente reconocibles?

### Variables estocásticas

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| Huella hídrica por kg fibra | Normal(μ, σ=0.30μ) | μ = base de db.py | Variabilidad metodológica LCA y variaciones de cultivo interanual |
| Prendas por persona por año | Normal(μ, σ=0.25μ) | μ = input del usuario | Heterogeneidad de comportamiento de consumo dentro del grupo |

### Modelo

Para cada simulación $s$ y año $t$:

$$L_{s,t} = N \times \tilde{X}_{s,t} \times w_{\text{prenda}} \times \tilde{h}_{s,t}$$

donde $\tilde{X}_{s,t} \sim \mathcal{N}(\mu_X, 0.25\mu_X)$ son las prendas por persona y $\tilde{h}_{s,t} \sim \mathcal{N}(\mu_h, 0.30\mu_h)$ es la huella hídrica en L/kg.

El consumo acumulado es $A_{s,T} = \sum_{t=1}^{T} L_{s,t}$.

El sistema genera 2,000 trayectorias y calcula percentiles P10, P25, P50, P75, P90 y P99 para cada año del horizonte.

### Referencias adaptativas

El problema central de las implementaciones de este tipo es seleccionar referencias de comparación que sean a la vez informativas y alcanzables. Si la referencia está 700,000 veces por encima del fenómeno que se modela, la gráfica pierde todo valor comunicacional.

El módulo selecciona referencias adaptativamente según el material:

```python
def _seleccionar_referencias(litros_por_ano_mediana, anos):
    litros_total = litros_por_ano_mediana * anos
    dentro = {k: v for k, v in REFERENCIAS.items() if v["litros"] <= litros_total}
    fuera  = {k: v for k, v in REFERENCIAS.items() if litros_total < v["litros"] <= litros_total * 10}
    # Tomar las 3 más grandes dentro del horizonte + 1 aspiracional fuera
```

Catálogo de referencias (de menor a mayor):

| Referencia | Volumen | Fuente |
|---|---|---|
| Persona/año (2 L/día) | 730 L | OMS |
| Piscina privada residencial | 30,000 L | NOM-127 |
| Alberca olímpica FINA | 2,500,000 L | FINA Technical Regulations 2022 |
| Lago de Chapultepec | 1,700,000 L | SEDEMA CDMX |
| Presa Cutzamala (cap. útil) | 960,000,000 L | CONAGUA 2023 |
| CDMX anual | 1,100,000,000,000 L | SACMEX / CONAGUA 2023 |

Para poliéster (62 L/kg), la referencia alcanzable en un horizonte de 15 años con configuración estándar es la piscina privada. Para algodón convencional (10,000 L/kg), el sistema selecciona alberca olímpica, Lago de Chapultepec y piscina privada.

---

## 12. Módulo 7 — Simulación Monte Carlo: reloj de deuda social

### Pregunta central

Si un grupo de N personas consume X prendas de una marca determinada por año, ¿en cuántos años la deuda salarial acumulada (brecha entre salario mínimo pagado y salario digno) equivale al salario anual completo de un trabajador textil?

### Variables estocásticas

| Variable | Distribución | σ relativo | Justificación |
|---|---|---|---|
| Tipo de cambio USD → MXN | Normal(TC_MXN, σ=8%) | 8% | Volatilidad histórica anualizada del peso mexicano |
| Brecha salarial (salario digno - mínimo) | Normal(μ, σ=20%) | 20% | Variación inter-fábrica y temporal en datos WageIndicator |
| Factor de riesgo laboral | Normal(μ, σ=15%) | 15% | Incertidumbre en indicadores del Banco Mundial |
| Prendas por persona/año | Normal(μ, σ=20%) | 20% | Heterogeneidad de consumo |

### Modelo

La brecha salarial por prenda para una simulación $s$ se calcula ponderando por la distribución de manufactura:

$$B_{s,e} = \sum_{i} \left[ \frac{\tilde{\delta}_{i,s}}{h_{\text{mes},i}} \times h_{\text{prenda}} \times \tilde{f}_{i,s} \times w_{i,e} \right]$$

donde $\tilde{\delta}_{i,s}$ es la brecha salarial estocástica en el país $i$, $h_{\text{prenda}}$ son las horas de manufactura de la prenda, $\tilde{f}_{i,s}$ es el factor de riesgo estocástico y $w_{i,e}$ es la fracción de producción de la empresa $e$ en el país $i$.

El tipo de cambio estocástico $\tilde{TC}_s$ convierte el total acumulado en MXN.

La deuda acumulada en MXN al año $T$ para la simulación $s$:

$$D_{s,T}^{\text{MXN}} = \tilde{TC}_s \times \sum_{t=1}^{T} \left( N \times \tilde{X}_{s,t} \times B_{s,e} \right)$$

### Umbrales de referencia

La deuda acumulada se compara contra el salario anual total de un trabajador textil en distintos contextos:

| Referencia | Umbral (USD/año) |
|---|---|
| Salario mínimo Bangladesh | $1,356 |
| Salario mínimo Vietnam | $3,000 |
| Salario mínimo México | $3,120 |
| Salario digno Bangladesh (metodología Anker) | $5,880 |

La gráfica muestra las 500 trayectorias del haz, las bandas de incertidumbre P25–P75 y las líneas horizontales de umbral para cada referencia salarial.

---

## 13. Módulo LLM — Narrativa interpretativa

El frontend invoca opcionalmente la API de Anthropic Claude (`claude-sonnet-4-20250514`) para generar un párrafo de narrativa interpretativa a partir del JSON de resultados del ensamblaje. El prompt incluye el veredicto, la brecha entre precio etiqueta y P_justo, el porcentaje ambiental y social, y la empresa con mayor opacidad del conjunto.

El módulo es completamente opcional y no afecta los cálculos cuantitativos. Su función es pedagógica: traducir los resultados numéricos a lenguaje accesible para audiencias no especializadas.

```python
def generar_narrativa(resultados: list[dict]) -> str:
    client = anthropic.Anthropic()
    mensaje = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return mensaje.content[0].text
```

---

## 14. Complejidad algorítmica

| Módulo | Complejidad temporal | Complejidad espacial | Nota |
|---|---|---|---|
| Costo de producción (FOB + Landed) | O(P) — P países por empresa | O(P) | P ≤ 8 en la DB actual |
| KL Divergence (opacidad) | O(1) | O(1) | Fórmula escalar cerrada |
| Markov (inversión matricial) | O(n³), n=2 | O(n²) | Constante en la práctica |
| Costo social (brecha salarial) | O(P) | O(P) | Ponderación por país |
| API Banco Mundial | O(P) red | O(P) | Con caché LRU en memoria |
| Ensamblaje P_justo (una empresa) | O(P) | O(P) | P países de manufactura |
| Pipeline completo (E empresas) | O(E × P) | O(E) | E=8, P≤8 → O(1) práctica |
| Ordenamiento output | O(E log E) | O(E) | Dominante del pipeline |
| Monte Carlo CO2 (2000 sim.) | O(N) | O(N × E) | N sim., E empresas |
| Monte Carlo hídrico (2000 sim.) | O(N × T) | O(N × T) | T = años del horizonte |
| Monte Carlo deuda social (2000 sim.) | O(N × T × P) | O(N × T) | P países por empresa |

El sistema completo (sin Monte Carlo) tiene complejidad O(E log E) ≈ O(1) para el tamaño actual de datos. La latencia dominante en producción es la llamada a la API del Banco Mundial (~300–600 ms por país, con caché LRU que elimina llamadas repetidas en la misma sesión) y la API de Claude (~1–3 s por narrativa).

---

## 15. Stack tecnológico

| Capa | Tecnología | Versión | Justificación |
|---|---|---|---|
| Backend | Python | 3.11 | Ecosistema científico maduro |
| Álgebra lineal | NumPy | 1.26.4 | Inversión matricial Markov, operaciones vectorizadas MC |
| Frontend / Dashboard | Streamlit | 1.35.0 | Despliegue rápido de dashboards interactivos |
| Visualización | Plotly | 5.22.0 | Gráficas interactivas: barras apiladas, haz de líneas, histogramas |
| DataFrames | Pandas | 2.2 | Tablas de resultados y exportación |
| LLM | Anthropic Claude API | `claude-sonnet-4-20250514` | Narrativa interpretativa opcional |
| API externa | World Bank Open Data API v2 | — | Indicadores laborales en tiempo real |
| HTTP | `requests` | 2.31 | Llamadas a World Bank API con timeout y fallback |
| Contenedorización | Docker + Docker Compose | — | Reproducibilidad del entorno |
| Variables de entorno | python-dotenv | 1.0.1 | Gestión de API keys |

---

## 16. Estructura del proyecto

```
ecojusto-ai/
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
│
├── src/
│   ├── data/
│   │   ├── db.py                        # EMPRESAS, MATERIALES, PRENDAS, SALARIOS_PAIS, constantes
│   │   └── world_bank.py                # API Banco Mundial: get_factor_riesgo_pais(), get_datos_pais()
│   │
│   └── algoritmo/
│       ├── __init__.py
│       ├── opacidad.py                  # calcular_alpha(transparencia) → alpha_e
│       ├── markov.py                    # calcular_c_ambiental() → (vida_util, c_ambiental, c_agua, c_co2)
│       ├── social.py                    # calcular_c_social() → (c_social, c_real, c_digno, factor_prom, desglose)
│       ├── costo_produccion.py          # calcular_fob(), calcular_landed_cost()
│       ├── ensamblaje.py                # calcular_precio_justo(), run_all()
│       ├── monte_carlo.py               # simular_sensibilidad_co2(), comparar_sensibilidad_todas()
│       ├── monte_carlo_hidrico.py       # simular_huella_hidrica()
│       └── monte_carlo_deuda_social.py  # simular_deuda_social(), comparar_empresas_deuda()
│
└── frontend/
    └── app.py                           # Streamlit: sidebar, gráficas, 3 tabs Monte Carlo, LLM
```

---

## 17. Instrucciones de instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/ecojusto-ai.git
cd ecojusto-ai

# Opción A: Docker (recomendado para reproducibilidad)
docker-compose up --build
# La aplicación estará disponible en http://localhost:8501

# Opción B: entorno local
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Agregar ANTHROPIC_API_KEY si se usa el módulo LLM
streamlit run frontend/app.py
```

**requirements.txt:**

```
streamlit==1.35.0
numpy==1.26.4
plotly==5.22.0
pandas==2.2.2
anthropic==0.28.0
requests==2.31.0
python-dotenv==1.0.1
```

**Variables de entorno (.env):**

```
ANTHROPIC_API_KEY=sk-ant-...    # Requerida solo para el módulo LLM
```

La API del Banco Mundial no requiere autenticación. El resto del sistema funciona sin conexión a internet, utilizando los datos preprocesados en `db.py` y el diccionario de fallback en `world_bank.py`.

---

## 18. Supuestos, limitaciones y trabajo futuro

### Supuestos del modelo

**Datos estáticos en `db.py`:** Los índices FTI, salarios mínimos y huellas hídricas están fijados a las ediciones 2023–2024 de cada fuente. El sistema no actualiza estos valores automáticamente.

**Distribución de manufactura hardcodeada:** Las fracciones de producción por país se estimaron con base en informes públicos disponibles y pueden diferir de la distribución real interna de cada empresa.

**Markup retail constante:** El multiplicador 2.8× sobre el landed cost es un promedio de la industria. Empresas con modelos de negocio muy distintos (venta directa al consumidor vs. distribución por terceros) tendrían multiplicadores diferentes.

**Vida útil como proxy de calidad:** Se asume que la transparencia del índice FTI correlaciona con la calidad de manufactura y, por extensión, con la vida útil de las prendas. Esta correlación es plausible pero no está empíricamente validada en la literatura.

**Factor de reposición lineal:** El modelo asume que una prenda con vida útil de 12 meses (en lugar de 24) generará el doble de impacto ambiental a lo largo del tiempo. Esto es correcto bajo el supuesto de que el consumidor efectivamente repone la prenda, lo cual depende de factores de demanda fuera del modelo.

**Parámetro γ = 0.3:** El parámetro de escala de la penalización KL no fue optimizado con datos empíricos. Es un valor de diseño que produce penalizaciones en el rango [1.0, 1.9] para el rango observado de transparencias FTI.

### Limitaciones

Los precios calculados por el sistema son órdenes de magnitud superiores a los precios de etiqueta para todas las empresas en el dataset actual. Esto es un resultado del modelo, no un error: refleja que el costo de internalizar completamente las externalidades ambientales y sociales supera con creces el precio de mercado. Sin embargo, la magnitud exacta depende críticamente de los valores del markup retail, el factor de reposición y los precios de remediación ambiental, todos los cuales tienen incertidumbre significativa. Los módulos Monte Carlo cuantifican parte de esa incertidumbre.

### Trabajo futuro

- Integración con la base de datos USITC de importaciones para actualización automática de distribuciones de manufactura
- Calibración empírica del parámetro γ usando datos de litigios ambientales y sociales como variable de resultado
- Extensión del espacio de estados Markov para incluir estados de reciclaje y compostaje
- Modelo de demanda para estimar el efecto de la internalización de costos sobre el volumen de consumo
- API REST desacoplada del frontend para permitir integración con otros sistemas

---

*EcoJusto AI — Proyecto académico de Inteligencia Artificial, 2025.*
