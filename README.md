<div align="center">
  <img src="assets/logo.png" alt="CaciqueAnalytics" width="160"/>

  # CaciqueAnalytics
</div>

**Análisis estadístico e inteligencia competitiva para el fútbol chileno.**

Plataforma ETL + analytics para recolectar, procesar y analizar estadísticas de jugadores
de la Primera División de Chile y competencias CONMEBOL. Generadora de contenido visual
y rankings por posición para publicación en redes sociales.

---

## Objetivos del Proyecto

1. **Analítica avanzada**: Construir rankings dinámicos por posición granular (19 roles distintos)
2. **Comparativas inteligentes**: Perfiles 1v1 entre jugadores con contexto de percentiles de liga
3. **Contenido viral**: Generar visualizaciones publication-ready para X, Instagram, TikTok
4. **Histórico**: Comparación de evolución de jugadores a través de temporadas (2021-2026)
5. **Portafolio profesional**: Demostración de ingeniería ETL, análisis de datos y visualización

---

## Arquitectura de Datos

### 12 Tablas Principales

| Tabla | Propósito | Registros esperados |
|-------|-----------|-------------------|
| **nationalities** | Países/códigos ISO | ~250 |
| **positions** | Taxonomía de 19 posiciones granulares | 19 (seeded) |
| **competitions** | Ligas, copas, CONMEBOL | ~4 (seeded) |
| **teams** | Equipos chilenos y regionales | ~200 |
| **players** | Jugadores con IDs de todas las fuentes | ~15k |
| **seasons** | Temporadas por competencia (2021-2026) | ~20 |
| **matches** | Partidos con scores y estado | ~2k |
| **player_team_seasons** | Historial de equipos por temporada | ~15k |
| **player_season_stats** | Stats por temporada (multi-source: SofaScore, FBref, FotMob) | ~150k |
| **player_match_stats** | Stats granulares por partido (SofaScore) | ~500k |
| **player_market_values** | Historial de valor de mercado (Transfermarkt) | ~50k |
| **team_season_stats** | Stats agregadas de equipos por temporada | ~60 |

### 19 Posiciones Granulares

```
PORTERO (1)      → GK
DEFENSA (7)      → CB, STP, SW, RB, LB, RWB, LWB
MEDIOCAMPO (7)   → CDM, CM_B2B, Mezzala, Regista, CAM, RM, LM
ATAQUE (4)       → RW, LW, CF, SS
```

**Beneficio**: Cada posición tiene métricas relevantes distintas. Comparar un Regista (distribuidor)
con un CDM (defensivo) ahora tiene sentido analítico.

---

## Estado del Proyecto

### Sprint 0 — Infraestructura COMPLETADO

- PostgreSQL 18.3 instalado y operativo en Windows
- Base de datos `cacique_analytics` creada
- Usuario `cacique_app` con permisos mínimos (SELECT, INSERT, UPDATE, DELETE)
- Scripts de control: start/stop/status/manual startup
- VS Code tasks configuradas (11 tareas operativas)
- `.env` seguro en `.gitignore` con credenciales
- Documentación de PostgreSQL para Windows

### Sprint 1 Fase 1A — Modelo de Dominio COMPLETADO

- Análisis de datos de infografías X (posts iniciales)
- Taxonomía de posiciones validada (19 roles)
- Métricas por posición documentadas (GK, DEF, MID, FWD)
- Fuentes de datos verificadas en LanusStats 2.0.1
- docs/domain_model.md con ERD conceptual completo

### Sprint 1 Fase 1B — Schema SQL COMPLETADO

- src/migrations/001_initial_schema.sql con 12 tablas
- 19 posiciones + 4 competencias como datos semilla
- Constraints completos: FKs, PKs, UCs, CHECKs
- Índices fundamentales para queries frecuentes
- GRANTs configurados para usuario de aplicación
- Migración ejecutada exitosamente en PostgreSQL 18.3 local

### Sprint 1 Fase 1C — ETL PRÓXIMO

- Conectar LanusStats a scrapers
- Poblar historiales desde 2021
- Idempotencia y validación de datos

---

## Fuentes de Datos

| Fuente | ID Liga | Temporadas | Cobertura | Acceso |
|--------|---------|-----------|-----------|--------|
| **SofaScore** | `11653` | 2023 → 2026 | Ratings, stats por partido, heatmaps, eventos | LanusStats |
| **FBref** | `35` | 2021 → 2025 | Stats avanzadas (xG, xA, carries progresivos) | LanusStats |
| **FotMob** | `273` | 2021 → 2025 | Shotmaps, percentiles de liga, stats de temporada | LanusStats |
| **Transfermarkt** | `CLPD` | Sin límite | Valores de mercado, historial de transferencias | LanusStats |

**Temporalidad**: Combinando FBref + FotMob (2021-2025) con SofaScore (2023-2026) y Transfermarkt
(histórico), podemos hacer **comparaciones temporales de 5+ años**.

---

## Tech Stack

| Área | Librerías |
|------|-----------|
| **Recolección de datos** | LanusStats, pydoll-python, nest-asyncio, beautifulsoup4 |
| **Procesamiento** | pandas, numpy, scipy |
| **Machine learning** | scikit-learn |
| **Visualización** | mplsoccer, matplotlib, pillow, Faker |
| **Notebooks** | jupyter, jupyterlab, ipykernel, ipywidgets |
| **Configuración** | python-dotenv |
| **Base de datos** | PostgreSQL 18.3 (local), Supabase (futuro) |

---

## Estructura del Proyecto

```
CaciqueAnalytics/
├── assets/                          # Logos e infografías
│   ├── logo.png
│   ├── 1.png - 4.png               # Infografías de X (referencia)
├── data/
│   ├── raw/                         # Datos crudos de APIs
│   ├── processed/                   # Datos limpios y transformados
│   └── external/                    # Archivos descargados manualmente
├── notebooks/                       # Análisis y visualización
│   ├── archive/                     # Exploración inicial
│   ├── 01_data_collection.ipynb
│   ├── 02_data_processing.ipynb
│   ├── 03_visualization.ipynb
│   ├── 04_jeyson_rojas_2026.ipynb
│   ├── 05_sosa_vs_zaldivia_2026.ipynb
│   ├── 06_victor_felipe_mendez_2026.ipynb
│   └── 07_superclasico_2026.ipynb
├── outputs/                         # Gráficos exportados para redes
│   ├── jeyson_rojas/
│   ├── sosa_vs_zaldivia/
│   ├── victor_felipe_mendez/
│   └── superclasico/
├── src/
│   ├── migrations/                  # Migraciones SQL
│   │   ├── 001_initial_schema.sql   # 12 tablas, datos semilla
│   │   └── 002_optimize_indexes.sql # Índices adicionales
│   ├── scripts/                     # Scripts utilitarios
│   │   ├── postgres-*.ps1           # Control del servicio PostgreSQL
│   │   └── audit_db_integrity.py    # Validación de BD
├── docs/                            # Documentación técnica
│   ├── domain_model.md              # ERD y especificación de datos
│   ├── security_audit_report.md     # Auditoría de seguridad e integridad
│   ├── postgresql_windows_guide.md  # Setup PostgreSQL en Windows
│   └── claude_handover_context.md   # Contexto para nuevos chats
├── .github/
│   └── copilot-instructions.md      # Política de project para Copilot
├── .vscode/
│   └── tasks.json                   # Tasks de VS Code (11 tareas)
├── .env.example                     # Template de variables de entorno
├── .gitignore                       # Exclusiones (secretos, datos)
├── requirements.txt                 # Dependencias Python
└── README.md                        # Este archivo
```

---

## Setup

### 1. Clonar repositorio

```bash
git clone https://github.com/Bryan-Alegria/CaciqueAnalytics.git
cd CaciqueAnalytics
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con credenciales reales (solo en desarrollo local)
```

### 5. PostgreSQL Local (Windows)

Abrir **VS Code como Administrador**:

```
Ctrl+Shift+P → "PostgreSQL: Start"
```

O desde PowerShell admin:

```powershell
.\scripts\postgres-start.ps1
```

Verificar que esté activo:

```powershell
.\scripts\postgres-status.ps1
```

Cuando termines, detener:

```
Ctrl+Shift+P → "PostgreSQL: Stop"
```

---

## Seguridad

- Cero secretos en código: Todas las credenciales en `.env` (no commiteado)
- Permisos mínimos: Usuario `cacique_app` sin DROP, CREATE, ALTER
- Git limpio: `.gitignore` protege `.env` y datos sensibles
- Auditoría: Script `audit_db_integrity.py` valida integridad

Ver `docs/security_audit_report.md` para detalles completos.

---

## Notas

- Archivos de fotos de jugadores (`assets/*.jpg`) están excluidos de git
- Datos crudos (`data/raw/`) y procesados (`data/processed/`) excluidos
- Scripts auxiliares: `_extract_colors.py`, `detect_red.py` → ejecutar independientemente
- Ejecutar notebooks en orden: `01` → `02` → `03` → `04/05/06/07`

---

## Referencias Rápidas

- **Guía PostgreSQL en Windows**: `docs/postgresql_windows_guide.md`
- **Especificación de datos**: `docs/domain_model.md`
- **Reporte de auditoría**: `docs/security_audit_report.md`
- **Validación de sistema**: `VALIDACION_SISTEMA.md`
- **Política del proyecto**: `.github/copilot-instructions.md`

---

## Autor

**Bryan Alegria** — [GitHub](https://github.com/Bryan-Alegria)

Proyecto de portfolio en ingeniería de datos (ETL, analytics, visualización).

---

**Última actualización**: 16 de Marzo de 2026
**Estado**: Sprint 1 Fase 1B Completado — Próximo: Sprint 1 Fase 1C (ETL)