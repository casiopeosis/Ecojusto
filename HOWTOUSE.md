# EcoJusto AI 🌿

> **Auditor algorítmico de externalidades socioambientales en la industria de la moda**

Calcula el **precio justo real** de una prenda de ropa revelando los costos ocultos que las marcas trasladan a la sociedad y al medio ambiente. Combina Divergencia KL (opacidad informacional), Cadenas de Markov absorbentes (ciclo de vida) y Teoría de Juegos (impacto laboral) para producir un dashboard comparativo interactivo.

---

## Cómo usar

### Requisitos previos

- Python 3.10 o superior
- `pip` disponible en tu terminal

Verifica con:

```bash
python --version
pip --version
```

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/ecojusto-ai.git
cd ecojusto-ai
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Levantar el dashboard

```bash
streamlit run frontend/app.py
```

Abre tu navegador en `http://localhost:8501`. Streamlit lo hace automáticamente.

Selecciona material y tipo de prenda en el sidebar. El dashboard se actualiza en tiempo real.

### 4. (Opcional) Activar la narrativa generada por IA

Si quieres que el dashboard genere un párrafo periodístico interpretando los resultados, necesitas una API key de Anthropic:

```bash
cp .env.example .env
# Edita .env y reemplaza sk-ant-... con tu key real
```

Luego activa el toggle **"Narrativa IA"** en el sidebar. Sin este paso el dashboard funciona igual, solo sin esa sección.

### 5. Correr solo el backend (sin UI)

Si quieres ver los resultados en JSON directo desde la terminal, sin levantar Streamlit:

```bash
python - <<'EOF'
from algoritmo.ensamblaje import run_all
import json

resultados = run_all("poliester", "playera")
print(json.dumps(resultados, indent=2, ensure_ascii=False))
EOF
```

Opciones de material: `poliester`, `algodon_conv`, `algodon_org`, `lana`, `viscosa`

Opciones de prenda: `playera`, `jeans`, `sudadera`, `vestido`, `chamarra`

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
12. [Supuestos y limitaciones](#supuestos-y-limitaciones)

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

---

## Arquitectura general

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                 │
│   Select: material × prenda  →  Dashboard comparativo   │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend Python                          │
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

Se utiliza la **Divergencia de Kullback-Leibler (D_KL)**. Esta métrica cuantifica cuánta información se "pierde" al aproximar una distribución real Q con una distribución ideal P.

$$D_{KL}(P \| Q_e) = \sum_{x \in X} P(x) \log\left(\frac{P(x)}{Q_e(x)}\right)$$

**Factor de penalización:**

$$\alpha_e = 1 + \gamma \cdot D_{KL}(P \| Q_e)$$

donde `γ = 0.3`. Si la empresa es totalmente transparente, `D_KL = 0` → `α_e = 1` (sin penalización).

---

## Módulo 2 — Ciclo de vida (Cadenas de Markov)

### Objetivo

Estimar cuánto tiempo durará la prenda antes de terminar en un vertedero, y traducir ese tiempo en un costo ambiental por ciclo de uso acortado.

### Fundamento matemático

Cadena de Markov Absorbente con estados `{Activo, Segunda Mano, Basurero}`. Tiempo esperado hasta absorción via Matriz Fundamental de Kemeny:

$$F = (I - Q)^{-1}, \quad \mathbf{t} = F \cdot \mathbf{1}$$

$$C_{\text{ambiental}} = \frac{\text{Costo de Remediación}(m)}{E[T]}$$

---

## Módulo 3 — Impacto social (Teoría de Juegos)

### Objetivo

Estimar el costo de resarcir las condiciones laborales en la cadena de suministro, modelando la relación empresa–maquiladora como un Dilema del Prisionero Repetido.

$$C_{\text{social}} = P_{\text{base}} \times \text{FactorRiesgoPaís} \times \text{BrechaSalarialOIT}$$

---

## Ensamblaje: Precio Justo

$$P_{\text{justo}} = \alpha_e \cdot (P_{\text{comercial}} + C_{\text{ambiental}} + C_{\text{social}})$$

---

## Bases de datos y fuentes

### Empresas

| Empresa | Índice FTI (%) | Factor riesgo CSI |
|---|---|---|
| Shein | 5 | 1.8 |
| H&M | 62 | 1.2 |
| Zara (Inditex) | 55 | 1.1 |
| Nike | 68 | 1.0 |
| Patagonia | 92 | 0.3 |
| Levi's | 70 | 0.8 |
| Primark | 22 | 1.5 |
| Adidas | 74 | 1.0 |

### Fuentes

| Fuente | Uso |
|---|---|
| Fashion Transparency Index | Índice de transparencia por empresa |
| CSI Global Rights Index | Factor de riesgo laboral por país |
| OIT — Salario mínimo vital | Brecha salarial por país de manufactura |
| Ellen MacArthur Foundation | Tasas de transición Markov (vida útil de prendas) |

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.10+ |
| Álgebra lineal | NumPy |
| Frontend | Streamlit |
| Visualización | Plotly Express |
| LLM (opcional) | Anthropic Claude API |

---

## Complejidad algorítmica

| Módulo | Complejidad temporal | Complejidad espacial |
|---|---|---|
| Módulo 1 — KL divergence | O(1) | O(1) |
| Módulo 2 — Markov (inversión 2×2) | O(1) | O(1) |
| Módulo 3 — Nash payoff | O(1) | O(1) |
| Pipeline completo (E empresas) | O(E) | O(E) |
| Ordenamiento del output | O(E log E) | O(E) |

**Complejidad total:** O(E log E), E = 8 empresas. El cuello de botella real es la latencia de red del módulo LLM opcional (~1–3s).

---

## Estructura del proyecto

```
ecojusto-ai/
├── README.md
├── requirements.txt
├── .env.example
│
├── data/
│   └── db.py                  # Empresas, materiales y prendas
│
├── algoritmo/
│   ├── opacidad.py            # Módulo 1: D_KL → alpha_e
│   ├── markov.py              # Módulo 2: (I-Q)⁻¹ → C_ambiental
│   ├── social.py              # Módulo 3: Nash payoff → C_social
│   └── ensamblaje.py          # P_justo = alpha * (P + C_amb + C_soc)
│
├── llm/
│   └── narrativa.py           # Narrativa periodística via Claude API (opcional)
│
└── frontend/
    └── app.py                 # Streamlit + Plotly dashboard
```

---

## Supuestos y limitaciones

1. **Datos estáticos:** los índices FTI, CSI y OIT están fijados a la edición 2023–2024. El sistema no hace scraping en tiempo real.

2. **Matriz de Markov calibrada manualmente:** las probabilidades de transición se estimaron con base en literatura de la Ellen MacArthur Foundation, no entrenadas estadísticamente.

3. **C_social usa precio base fijo:** para evitar circularidad — una empresa que vende más barato no debería tener menor costo social.

4. **γ = 0.3 es un hiperparámetro de diseño:** justificable pero no optimizado empíricamente.

5. **Alcance académico:** prototipo demostrativo. No debe usarse como fuente de verdad para decisiones de consumo sin validación adicional.

---

*EcoJusto AI — Proyecto académico de IA, 2025.*
