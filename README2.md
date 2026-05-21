# EcoJusto AI 🌿

> **Auditor algorítmico de externalidades socioambientales en la industria de la moda**

EcoJusto AI es una herramienta de periodismo de datos que calcula el **precio justo real** de una prenda de ropa, revelando los costos ocultos que las marcas de moda trasladan a la sociedad y al medio ambiente. El sistema combina Teoría de la Información, Procesos de Decisión de Markov y Teoría de Juegos para producir un dashboard comparativo interactivo entre empresas para un material y prenda específicos.

---

## Screenshot del output

![Dashboard comparativo EcoJusto AI](https://placehold.co/900x480/1a1a2e/ffffff?text=EcoJusto+AI+%E2%80%94+Dashboard+Comparativo)

> El dashboard muestra, para cada empresa: precio de etiqueta, costo ambiental (C_ambiental), costo social (C_social) y penalización por opacidad (α_e), apilados en una barra comparativa. La tabla inferior incluye vida útil estimada por Markov, índice de transparencia y semáforo de nivel ético.

---

## Tabla de contenidos

1. [Visión general](#visión-general)
2. [Input y output del sistema](#input-y-output-del-sistema)
3. [Arquitectura general](#arquitectura-general)
4. [Módulo 1 — Opacidad (Teoría de la Información)](#módulo-1--opacidad-teoría-de-la-información)
5. [Módulo 2 — Ciclo de vida (Cadenas de Markov)](#módulo-2--ciclo-de-vida-cadenas-de-markov)
6. [Módulo 3 — Impacto social (Teoría de Juegos)](#módulo-3--impacto-social-teoría-de-juegos)
7. [Ensamblaje: Precio Justo](#ensamblaje-precio-justo)
8. [Bases de datos y fuentes](#bases-de-datos-y-fuentes)
9. [Stack tecnológico](#stack-tecnológico)
10. [Complejidad algorítmica](#complejidad-algorítmica)
11. [Estructura del proyecto](#estructura-del-proyecto)
12. [Instrucciones de instalación](#instrucciones-de-instalación)
13. [Supuestos y limitaciones](#supuestos-y-limitaciones)

---

## Visión general

La industria de la moda es la segunda más contaminante del mundo. Una playera de poliéster vendida en $299 MXN puede representar externamente entre $600 y $1,400 MXN en costos ambientales y sociales no pagados: contaminación hídrica, emisiones de microplásticos, salarios por debajo del mínimo vital y cadenas de suministro opacas.

EcoJusto AI cuantifica esos costos mediante tres módulos matemáticos independientes y los presenta en un dashboard comparativo que permite al usuario elegir un material y tipo de prenda, y ver cómo se comportan distintas empresas frente al mismo producto.

---

## Input y output del sistema

### Input

El sistema recibe tres parámetros del usuario a través del frontend:

| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `material` | `str` (enum) | `"poliester"` | Material principal de la prenda |
| `prenda` | `str` (enum) | `"playera"` | Tipo de prenda |
| *(empresas)* | interno | — | Se evalúan todas las empresas de la base de datos simultáneamente |

**Materiales disponibles:** poliéster, algodón convencional, algodón orgánico, lana, viscosa.

**Prendas disponibles:** playera, jeans, sudadera, vestido, chamarra.

### Output

Para cada empresa en la base de datos, el sistema devuelve un objeto con:

```json
{
  "empresa": "H&M",
  "precio_etiqueta": 280,
  "alpha_e": 1.41,
  "c_ambiental": 32,
  "c_social": 74,
  "p_justo": 543,
  "vida_util_meses": 8.7,
  "transparencia_pct": 62,
  "nivel": "media"
}
```

El frontend consume este JSON para renderizar:

- **Gráfica de barras apiladas** (precio etiqueta + C_ambiental + C_social + penalización opacidad) por empresa
- **Tarjetas de métricas** (empresa más cara real, más transparente, brecha promedio)
- **Tabla detallada** con semáforo de nivel ético por empresa

---

## Arquitectura general

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                 │
│   Select: material × prenda  →  Dashboard comparativo   │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP / función directa
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend Python / Docker                 │
│                                                         │
│  Input: (material_m, prenda_p)                          │
│                        │                               │
│         ┌──────────────▼──────────────┐                │
│         │  Para cada empresa e en DB  │                │
│         └──────────────┬──────────────┘                │
│                        │                               │
│    ┌───────────────────▼──────────────────────────┐    │
│    │  Módulo 1: Opacidad — D_KL → α_e             │    │
│    └───────────────────┬──────────────────────────┘    │
│                        │                               │
│    ┌───────────────────▼──────────────────────────┐    │
│    │  Módulo 2: Markov — F=(I-Q)⁻¹ → C_ambiental │    │
│    └───────────────────┬──────────────────────────┘    │
│                        │                               │
│    ┌───────────────────▼──────────────────────────┐    │
│    │  Módulo 3: Juegos — Nash → C_social          │    │
│    └───────────────────┬──────────────────────────┘    │
│                        │                               │
│    ┌───────────────────▼──────────────────────────┐    │
│    │  P_justo = α_e · (P_com + C_amb + C_soc)     │    │
│    └───────────────────┬──────────────────────────┘    │
│                        │                               │
│         Output: List[ResultadoEmpresa]                  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
              JSON → Plotly / Streamlit
```

---

## Módulo 1 — Opacidad (Teoría de la Información)

### Objetivo

Medir qué tan lejos está la empresa de reportar lo que debería reportar sobre su cadena de suministro, y castigar esa opacidad con un multiplicador de penalización.

### Fundamento matemático

Se utiliza la **Divergencia de Kullback-Leibler (D_KL)**, también llamada entropía relativa. Esta métrica de la Teoría de la Información cuantifica cuánta información se "pierde" al aproximar una distribución real Q con una distribución ideal P.

$$D_{KL}(P \| Q_e) = \sum_{x \in X} P(x) \log\left(\frac{P(x)}{Q_e(x)}\right)$$

**Definición de distribuciones:**

- `P(x)`: distribución ideal de reporte. Se define como la distribución uniforme sobre el conjunto de dimensiones que el Fashion Transparency Index evalúa: trazabilidad de fábricas, política salarial, huella hídrica, auditorías de terceros, política de género, etc. La empresa con mayor puntaje en el FTI actúa como proxy de P.
- `Q_e(x)`: distribución real de la empresa `e`, derivada de su puntaje en el FTI (0–100%). Una empresa con 20% de transparencia concentra su masa de probabilidad en pocas dimensiones.

**Factor de penalización:**

$$\alpha_e = 1 + \gamma \cdot D_{KL}(P \| Q_e)$$

donde `γ = 0.3` es el parámetro de ajuste (calibrable). Si la empresa es totalmente transparente, `D_KL = 0` → `α_e = 1` (sin penalización).

### Implementación

```python
import numpy as np

def calcular_alpha(transparencia: float, gamma: float = 0.3) -> float:
    """
    transparencia: float en [0, 1], índice FTI normalizado de la empresa
    Retorna el factor multiplicador alpha_e
    """
    p = 1.0
    q = max(transparencia, 1e-9)  # evitar log(0)
    dkl = p * np.log(p / q)
    return 1 + gamma * dkl
```

### Complejidad

- **Temporal:** O(|X|) donde |X| es el número de dimensiones evaluadas por el FTI (~10). Constante en la práctica.
- **Espacial:** O(1)

---

## Módulo 2 — Ciclo de vida (Cadenas de Markov)

### Objetivo

Estimar cuánto tiempo durará la prenda antes de terminar en un vertedero, y traducir ese tiempo en un costo ambiental por ciclo de uso acortado.

### Fundamento matemático

Se modela la vida útil de la prenda como una **Cadena de Markov Absorbente** con el siguiente espacio de estados:

$$S = \{ \text{Activo},\ \text{Segunda Mano},\ \text{Basurero} \}$$

donde `Basurero` es el único estado absorbente. La dinámica está definida por la matriz de transición `T`, que depende de dos factores:

1. **Material `m`:** durabilidad intrínseca (poliéster se degrada rápido; algodón orgánico dura más)
2. **Empresa `e`:** calidad de manufactura, proxy del índice de transparencia

**Ejemplo de matriz de transición para poliéster fast-fashion:**

```
             Activo   2a Mano   Basurero
Activo      [ 0.20,    0.10,     0.70  ]
2a Mano     [ 0.00,    0.30,     0.70  ]
Basurero    [ 0.00,    0.00,     1.00  ]
```

**Cálculo del tiempo esperado hasta absorción** usando la **Matriz Fundamental de Kemeny**:

$$F = (I - Q)^{-1}$$

donde `Q` es la submatriz de estados transitorios (Activo y Segunda Mano). El vector de tiempos esperados es:

$$\mathbf{t} = F \cdot \mathbf{1}$$

El primer componente `t[0]` da el número esperado de ciclos antes de que una prenda en estado Activo llegue al Basurero.

**Costo ambiental:**

$$C_{\text{ambiental}} = \frac{\text{Costo de Remediación Estándar}(m)}{E[T]}$$

A menor vida útil esperada `E[T]`, mayor frecuencia de reposición y mayor huella ecológica acumulada.

### Implementación

```python
import numpy as np

def calcular_c_ambiental(transparencia: float, material: dict) -> tuple[float, float]:
    """
    Retorna (vida_util_meses, c_ambiental_mxn)
    material: dict con keys 'vida_base' (meses) y 'costo_remediacion' (MXN)
    """
    calidad = 0.5 + transparencia * 0.5  # [0.5, 1.0]
    vida_esperada = material['vida_base'] * calidad

    # Matriz Q (estados transitorios: Activo, Segunda Mano)
    p_activo_a_basurero = max(0.05, 0.95 - calidad * 0.8)
    Q = np.array([
        [0.20 * calidad, 0.10],
        [0.00,           0.30 * calidad]
    ])
    I = np.eye(2)
    F = np.linalg.inv(I - Q)
    t = F @ np.ones(2)
    vida_markov = round(t[0], 1)

    c_ambiental = round(material['costo_remediacion'] / vida_markov)
    return vida_markov, c_ambiental
```

### Complejidad

- **Temporal:** O(n³) por la inversión de matriz, donde n=2 (estados transitorios). Constante en la práctica.
- **Espacial:** O(n²) para almacenar Q y F.

---

## Módulo 3 — Impacto social (Teoría de Juegos)

### Objetivo

Estimar el costo financiero necesario para resarcir las condiciones laborales en la cadena de suministro, modelando la relación empresa–maquiladora como un juego estratégico.

### Fundamento matemático

La relación entre la corporación y sus proveedores en países en desarrollo se modela como un **Dilema del Prisionero Repetido**:

| | Maquiladora coopera | Maquiladora defecciona |
|---|---|---|
| **Empresa coopera** | (salario digno, estabilidad) | (empresa pierde, maquiladora gana) |
| **Empresa defecciona** | (empresa gana, maquiladora pierde) | (equilibrio de explotación) |

En el equilibrio de Nash estático, la estrategia dominante para empresas de moda masiva es **defeccionar** (explotar vacíos legales para reducir costos laborales), dado que el mercado premia el precio bajo.

**Costo de Estabilización Social:**

Equivale a la penalización financiera teórica requerida para alterar la matriz de pagos del juego, haciendo que la cooperación sea la estrategia dominante:

$$C_{\text{social}} = P_{\text{base}} \times \text{FactorRiesgoPaís} \times \text{BrechaSalarialOIT}$$

donde:
- `P_base`: precio base de la prenda (valor fijo por tipo, no el precio de etiqueta — evita circularidad)
- `FactorRiesgoPaís`: índice de riesgo laboral del país principal de manufactura (fuente: CSI Global Rights Index)
- `BrechaSalarialOIT`: brecha porcentual entre salario pagado y salario digno estimado por la OIT para ese país

### Implementación

```python
def calcular_c_social(empresa: dict, prenda: dict) -> float:
    """
    empresa: dict con 'pais_riesgo' (factor 0.0–2.0)
    prenda: dict con 'precio_base' y 'brecha_oit'
    """
    c_social = prenda['precio_base'] * empresa['pais_riesgo'] * prenda['brecha_oit']
    return round(c_social)
```

### Complejidad

- **Temporal:** O(1)
- **Espacial:** O(1)

---

## Ensamblaje: Precio Justo

Una vez calculados los tres módulos, el precio justo final se obtiene con:

$$P_{\text{justo}} = \alpha_e \cdot (P_{\text{comercial}} + C_{\text{ambiental}} + C_{\text{social}})$$

El resultado se calcula para **todas las empresas en paralelo** (via `list comprehension` o `pandas.apply`) y se devuelve como una lista ordenada de mayor a menor `P_justo`.

```python
def calcular_precio_justo(empresa: dict, material: dict, prenda: dict) -> dict:
    alpha = calcular_alpha(empresa['transparencia'])
    vida, c_amb = calcular_c_ambiental(empresa['transparencia'], material)
    c_soc = calcular_c_social(empresa, prenda)
    p_justo = round(alpha * (prenda['precio_base'] + c_amb + c_soc))

    return {
        "empresa": empresa['nombre'],
        "precio_etiqueta": prenda['precio_base'],
        "alpha_e": round(alpha, 2),
        "c_ambiental": c_amb,
        "c_social": c_soc,
        "p_justo": p_justo,
        "vida_util_meses": vida,
        "transparencia_pct": round(empresa['transparencia'] * 100),
        "nivel": badge(empresa['transparencia'])
    }

def run_all(material_key: str, prenda_key: str) -> list[dict]:
    mat = MATERIALES[material_key]
    pre = PRENDAS[prenda_key]
    results = [calcular_precio_justo(e, mat, pre) for e in EMPRESAS]
    return sorted(results, key=lambda x: x['p_justo'], reverse=True)
```

---

## Bases de datos y fuentes

El sistema utiliza una base de datos estática en Python (diccionario hardcodeado) para la versión inicial, con los siguientes datos reales preprocesados:

### Empresas (8 empresas hardcodeadas)

| Empresa | Índice FTI (%) | País mfg. | Factor riesgo CSI |
|---|---|---|---|
| Shein | 5 | China | 1.8 |
| H&M | 62 | Bangladesh | 1.2 |
| Zara (Inditex) | 55 | Portugal | 1.1 |
| Nike | 68 | Vietnam | 1.0 |
| Patagonia | 92 | USA | 0.3 |
| Levi's | 70 | México | 0.8 |
| Primark | 22 | India | 1.5 |
| Adidas | 74 | Indonesia | 1.0 |

### Materiales (5 materiales)

| Material | Vida base (meses) | Costo remediación (MXN) |
|---|---|---|
| Poliéster | 6 | 280 |
| Algodón convencional | 14 | 180 |
| Algodón orgánico | 20 | 120 |
| Lana | 30 | 100 |
| Viscosa | 8 | 220 |

### Fuentes de referencia

| Fuente | Uso | URL |
|---|---|---|
| Fashion Transparency Index | Índice de transparencia por empresa | fashionrevolution.org/fti |
| CSI Global Rights Index | Factor de riesgo laboral por país | globalrightsindex.org |
| OIT — Salario mínimo vital | Brecha salarial por país de manufactura | ilo.org/travail |
| Ellen MacArthur Foundation | Tasas de transición Markov (vida útil de prendas) | ellenmacarthurfoundation.org |

---

## Stack tecnológico

| Capa | Tecnología | Justificación |
|---|---|---|
| Backend | Python 3.11 | Ecosistema científico, numpy para álgebra lineal |
| Álgebra lineal | NumPy | Inversión de matriz F=(I-Q)⁻¹ |
| Frontend | Streamlit | Despliegue rápido de dashboards de datos |
| Visualización | Plotly Express | Gráficas de barras apiladas interactivas |
| Contenedorización | Docker | Reproducibilidad del entorno |
| LLM (opcional) | Anthropic Claude API | Narrativa explicativa de resultados |
| Datos | Diccionario Python (JSON estático) | Simplicidad para prototipo académico |

### APIs externas

| API | Uso | Autenticación |
|---|---|---|
| Anthropic Claude API (`claude-sonnet-4-20250514`) | Generación de narrativa explicativa opcional | API Key en `.env` |

El resto del sistema **no requiere llamadas a APIs externas** en tiempo de ejecución. Todos los índices (FTI, CSI, OIT) están preprocesados y almacenados en el diccionario de datos.

---

## Complejidad algorítmica

| Módulo | Complejidad temporal | Complejidad espacial | Cuello de botella |
|---|---|---|---|
| Módulo 1 — KL divergence | O(&#124;X&#124;) ≈ O(1) | O(1) | Ninguno |
| Módulo 2 — Markov (inversión) | O(n³), n=2 → O(1) | O(n²) → O(1) | Ninguno |
| Módulo 3 — Nash payoff | O(1) | O(1) | Ninguno |
| Ensamblaje P_justo | O(1) por empresa | O(1) | Ninguno |
| Pipeline completo (E empresas) | O(E) | O(E) | Lineal en # empresas |
| Ordenamiento del output | O(E log E) | O(E) | Dominante total |

**Complejidad total del sistema:** O(E log E) donde E = número de empresas (actualmente 8).

El sistema es computacionalmente trivial. El verdadero cuello de botella es la latencia de red si se activa el módulo LLM opcional (~1–3s por llamada a la API de Claude).

---

## Estructura del proyecto

```
ecojusto-ai/
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
│
├── data/
│   └── db.py                  # Diccionario de empresas, materiales y prendas
│
├── algoritmo/
│   ├── __init__.py
│   ├── opacidad.py            # Módulo 1: D_KL → alpha_e
│   ├── markov.py              # Módulo 2: Cadena absorbente → C_ambiental
│   ├── social.py              # Módulo 3: Nash payoff → C_social
│   └── ensamblaje.py          # P_justo = alpha * (P + C_amb + C_soc)
│
├── llm/
│   └── narrativa.py           # Prompt a Claude API (opcional)
│
└── frontend/
    └── app.py                 # Streamlit: inputs + Plotly dashboard
```

---

## Instrucciones de instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/ecojusto-ai.git
cd ecojusto-ai

# Opción A: Docker (recomendado)
docker-compose up --build

# Opción B: Local
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Agregar API key de Anthropic si se usa el módulo LLM
streamlit run frontend/app.py
```

**requirements.txt:**
```
streamlit==1.35.0
numpy==1.26.4
plotly==5.22.0
anthropic==0.28.0
python-dotenv==1.0.1
```

---

## Supuestos y limitaciones

1. **Datos estáticos:** los índices FTI, CSI y OIT están fijados a la edición 2023–2024. El sistema no hace scraping en tiempo real.

2. **Granularidad empresa:** el índice FTI cubre ~250 marcas. Empresas no cubiertas recibirán un valor de transparencia por defecto (20%).

3. **Matriz de Markov calibrada manualmente:** las probabilidades de transición entre estados (Activo → Segunda Mano → Basurero) se estimaron con base en literatura de la Ellen MacArthur Foundation. No son resultado de un modelo estadístico entrenado.

4. **C_social usa precio base fijo:** se utiliza el precio base de la prenda (no el precio de etiqueta) para evitar circularidad — una empresa que vende más barato no debería tener menor costo social.

5. **γ = 0.3 es un hiperparámetro:** el parámetro de escala de la penalización KL no ha sido optimizado empíricamente. Es un valor de diseño justificable pero arbitrario.

6. **Alcance académico:** este sistema es un prototipo demostrativo para un proyecto de clase de Inteligencia Artificial. No debe usarse como fuente de verdad para decisiones de consumo reales sin validación adicional de los datos subyacentes.

---

*EcoJusto AI — Proyecto académico de IA, 2025.*
