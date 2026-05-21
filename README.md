---
title: "EcoJusto AI 🌿"
subtitle: "Auditor Algorítmico de Externalidades Socioambientales en la Industria de la Moda"
author: "Karol Josafat Cisneros Suárez"
date: "`r Sys.Date()`"
output:
  pdf_document:
    toc: true
    toc_depth: 3
    number_sections: true
    highlight: tango
header-includes:
  - \usepackage{amsmath}
  - \usepackage{amsfonts}
  - \usepackage{graphicx}
  - \usepackage{booktabs}
  - \usepackage{geometry}
  - \geometry{margin=1in}
---

\pagebreak

# Estructura General del Proyecto

El sistema está desarrollado con una arquitectura desacoplada que separa la persistencia de datos calibrados, el motor de inferencia matemática, las simulaciones estadísticas y la interfaz de usuario:

- **data/**
    - `db.py`: Base de datos calibrada de costos, salarios y huellas LCA.
    - `world_bank.py`: Cliente de la API del Banco Mundial con caché y fallbacks.
- **algoritmo/**
    - `costo_produccion.py`: Capa 1: Modelado de costos industriales (FOB y Landed Cost).
    - `opacidad.py`: Capa 2: Penalización informacional por Divergencia KL.
    - `markov.py`: Capa 3: Ciclo de uso de prendas mediante Cadenas de Markov.
    - `social.py`: Capa 4: Extracción de brechas salariales y factores de riesgo.
    - `ensamblaje.py`: Capa 5: Orquestación, markups minoristas y cálculo final de $P_{\text{justo}}$.
    - `monte_carlo.py`: Simulación estocástica de estrés por bonos de carbono (v2).
    - `monte_carlo_hidrico.py`: Simulación estocástica de agotamiento de acuíferos (v3).
    - `monte_carlo_deuda_social.py`: Reloj acumulativo de brecha salarial ética.
- **frontend/**
    - `app.py`: Interfaz interactiva y tableros analíticos en Streamlit.

---

# Arquitectura de la Base de Datos (`db.py`)

La base de datos centraliza parámetros técnicos recopilados a partir de auditorías de la cadena de suministro e informes sectoriales internacionales (Fibre2Fashion, EmergingTextiles, ITMF, Cosmo Sourcing, FASH455 y WageIndicator 2024-2025).

## Estructura del Modelo de Datos
- **`EMPRESAS`**: Almacena el vector de transparencia informacional ($\tau \in [0, 1]$) basado en el *Fashion Transparency Index*, la matriz de distribución productiva fraccionada por país exportador, y los precios de etiqueta reales en pesos mexicanos ($MXN$) para 5 prendas tipo: *playera, jeans, sudadera, vestido y chamarra*.
- **`SALARIOS_PAIS`**: Almacena las variables macroeconómicas de manufactura para 16 economías globales, mapeando el salario mínimo legal frente al salario digno (*Living Wage*) estimado por la Organización Internacional del Trabajo (OIT) y WageIndicator.
- **`MATERIALES`**: Centraliza las métricas de Análisis de Ciclo de Vida (LCA) para cinco fibras matrices: *Poliéster, Algodón Convencional, Algodón Orgánico, Lana y Viscosa*. Mapea de forma dinámica los costos de fibra bruta y acabados textiles según el país manufacturero, junto a constantes ecológicas críticas:

| Fibra | Vida Útil Base | Huella Hídrica ($L/kg$) | Emisiones $CO_2$ ($kg/kg$) |
| :--- | :---: | :---: | :---: |
| Poliéster | 6 meses | 62 | 14.2 |
| Algodón Convencional | 14 meses | 10,000 | 4.7 |
| Algodón Orgánico | 20 meses | 6,000 | 3.0 |
| Lana | 30 meses | 17,000 | 26.0 |
| Viscosa | 8 meses | 3,000 | 6.5 |

## Mecanismos de Calibración Económica
Para homogeneizar y anclar el modelo a la economía real, el sistema fija un tipo de cambio base ($TC_{\text{MXN}} = 17.5$) y define los valores de remediación marginal de las externalidades:
- **Costo Social del Carbono:** Valorizado en $\delta_{\text{CO}_2} = 3.50\text{ MXN/kg}$ (bonos de carbono base voluntaria México).
- **Costo de Remediación Hídrica:** Fijado en $\delta_{\text{agua}} = 0.25\text{ MXN/L}$, reflejando costos reales de purificación y remoción de químicos pesados de escorrentías industriales.

---

# Capas de Cálculo del Costo Justo ($P_{\text{justo}}$)

El algoritmo ejecuta un ensamblaje lineal distribuido en 5 capas secuenciales dentro de `ensamblaje.py`.

## Capa 1: Costo de Producción Comercial Tradicional
Calcula el costo base industrial de la prenda libre a bordo (FOB) y el costo final en almacén de destino (Landed Cost).

1. **Costo de Materiales ($C_{\text{mat}}$):**
   $$C_{\text{mat}} = (\text{PrecioFibra}_{\text{ISO}} \times \text{PesoPrenda}) + (\text{PrecioAcabado}_{\text{ISO}} \times (\text{PesoPrenda} \times 1.3)) + \text{Trims}$$
2. **Costo de Manufactura ($C_{\text{man}}$):**
   $$C_{\text{man}} = \left( \frac{\text{SalarioMínimo}_{\text{ISO}}}{\text{HorasMes}_{\text{ISO}}} \right) \times \text{HorasManufacturaPrenda}$$
3. **FOB & Landed Cost Ponderado:** Se calcula el valor FOB como $FOB = C_{\text{mat}} + C_{\text{man}}$. Posteriormente, se integra la logística internacional en `costo_produccion.py` agregando flete marítimo diferenciado por región de origen, seguros, aranceles de importación (18%-20%) y flete terrestre local. La capa de ensamblaje pondera este costo según el mix de manufactura de la empresa:
   $$\text{Landed}_{\text{ponderado}} = \sum (\text{Landed}_{\text{ISO}} \times \text{FracciónManufactura}_{\text{ISO}})$$
   Para emular la estructura de retail tradicional sin inflar las externalidades, el costo landed se multiplica de forma exclusiva por el factor comercial base:
   $$\text{PrecioRetailBase} = \text{Landed}_{\text{ponderado}} \times 2.8$$

## Capa 2: Penalización por Opacidad Informacional
Cuando una corporación bloquea la trazabilidad de su cadena de suministro, introduce un riesgo sistémico. EcoJusto AI penaliza la opacidad utilizando la **Divergencia de Kullback-Leibler (KL)** en `opacidad.py`.

Se modela la transparencia observada como una distribución de Bernoulli $Q(\tau)$ frente a un estándar ético ideal $P(\tau_{\text{ideal}} = 1)$. La divergencia mide la pérdida de información:
$$D_{\text{KL}}(P \parallel Q) = \sum_{x \in \{0,1\}} P(x) \log \left( \frac{P(x)}{Q(x)} \right) = 1 \cdot \log\left(\frac{1}{\tau}\right) + 0 = -\log(\tau)$$

Para evitar asíntotas en empresas con transparencia nula, el sistema mapea el multiplicador de opacidad $\alpha$ mediante un suavizado acotado:
$$\alpha = 1.0 + \gamma \cdot \min\left(-\log(\tau + \epsilon), \text{MAX\_PENALIZATION}\right)$$
Donde $\epsilon = 0.05$ previene la división por cero y $\gamma = 0.15$ calibra el impacto.

## Capa 3: Ciclo de Uso mediante Cadenas de Markov
Modelamos la durabilidad de la prenda mediante una **Cadena de Markov Absorbente** con tres estados de transición: *Activo*, *Segunda Mano*, y *Basurero* (Estado Absorbente).

La probabilidad de transición al basurero desde el estado activo ($p_{\text{basurero}}$) se calcula dinámicamente según la fibra y se refina inversamente a la calidad de manufactura de la marca (derivada linealmente de su transparencia):
$$\text{Calidad} = 0.5 + (\tau \times 0.5)$$
$$\text{FactorCalidad} = \frac{\text{Calidad} - 0.5}{0.5}$$
$$p_{\text{basurero}} = \text{clip}\left( p_{\text{base}} \times (1 - \text{FactorCalidad} \times 0.40), 0.05, 0.95 \right)$$

Con esto se construye la submatriz transitoria $Q$:
$$Q = \begin{pmatrix} p_{\text{activo}} & p_{\text{segunda}} \\ 0 & 1 - p_{\text{2a\_mano}} \end{pmatrix}$$

La vida útil esperada en meses ($V_u$) corresponde a la suma de la primera fila de la Matriz Fundamental $F = (I - Q)^{-1}$:
$$V_u = \sum_{j} F_{1,j}$$

### El Factor de Reposición
Si una prenda no cumple con el estándar de durabilidad óptimo ($V_{\text{referencia}} = 24\text{ meses}$), se calcula un **Factor de Reposición ($\mathcal{F}_R$)**:
$$\mathcal{F}_R = \max \left(1.0, \frac{24.0}{V_u}\right)$$

Este factor actúa como un multiplicador directo sobre el costo base de remediación ambiental inicial ($Huella_{\text{LCA}} \times \delta$):
$$C_{\text{ambiental}} = \left[ (\text{HuellaHídrica}_{\text{Prenda}} \times \delta_{\text{agua}}) + (\text{HuellaCO}_2\text{}_{\text{Prenda}} \times \delta_{\text{CO}_2}) \right] \times \mathcal{F}_R$$

## Capa 4: Deuda Social y Riesgo País
La externalidad social ($C_{\text{social}}$) representa la brecha económica no pagada a la fuerza laboral en los países maquiladores, incorporando el **Factor de Riesgo Laboral ($FR_{\text{ISO}}$)** calculado desde el Banco Mundial.
$$C_{\text{social}} = \sum_{ \text{ISO} } \left( C_{\text{social}_{\text{ISO}}} \times \text{FracciónManufactura}_{\text{ISO}} \right)$$

## Capa 5: Ensamblaje Estructural del $P_{\text{justo}}$
$$\text{BloqueÉtico} = \text{PrecioRetailBase} + C_{\text{ambiental}} + C_{\text{social}}$$
$$P_{\text{justo}} = (\text{BloqueÉtico} \times \alpha) \times (1 + \mu)$$
Donde $\mu = 15\%$ representa el margen de reinversión ética.

---

# Motor de Inferencia Laboral de la API del Banco Mundial

Para evitar indicadores estáticos, `world_bank.py` consume en tiempo real dos indicadores del Banco Mundial:
1. **Vulnerabilidad del Empleo (`SL.EMP.VULN.ZS`)**
2. **Tasa de Desempleo Total (`SL.UEM.TOTL.ZS`)**

El **Factor de Riesgo Laboral ($FR$)** se computa mediante una combinación lineal ponderada, acotada en el rango $[0.3, 2.0]$:
$$FR = \text{clip}\left( 0.7 \times \left(\frac{\text{Vulnerabilidad}}{50.0}\right) + 0.3 \times \left(\frac{\text{Desempleo}}{5.0}\right), 0.3, 2.0 \right)$$

---

# Módulos de Simulación Avanzada (Monte Carlo)

El sistema incorpora tres motores de simulación estocástica que ejecutan $N = 2,000$ iteraciones por corrida en el backend:

## Estrés Climático por Bonos de Carbono (`monte_carlo.py`)
Evalúa la resiliencia financiera de cada empresa ante incrementos regulatorios. El precio del $CO_2$ se modela como una distribución uniforme $\sim \mathcal{U}(3.5, 200)\text{ MXN/kg}$.

## Agotamiento Hídrico Acumulado (`monte_carlo_hidrico.py`)
Estima el impacto hídrico a largo plazo generado por el consumo colectivo de un grupo de personas en un horizonte de hasta 30 años. La huella se simula como $\sim \mathcal{N}(\mu_{\text{LCA}}, 0.30 \cdot \mu_{\text{LCA}})$ y el consumo personal como $\sim \mathcal{N}(\mu_{\text{input}}, 0.25 \cdot \mu_{\text{input}})$.

## Reloj de Deuda Social Acumulada (`monte_carlo_deuda_social.py`)
Mide el tiempo requerido para que el consumo ordinario de un grupo acumule una brecha salarial equivalente al sueldo anual íntegro de un trabajador textil en el hemisferio sur.