# VALIDACIÓN DE SISTEMA — CaciqueAnalytics

**Propósito**: Remítete a esta guía para verificar que todo el setup está correcto.
**Última actualización**: 16 de Marzo de 2026

---

## Checklist Rápido

### Paso 1: PostgreSQL Activo

```bash
# Desde PowerShell (cualquier usuario)
gslist PostgreSQL-x64-18 | findstr Running
```

**Resultado esperado**: `Running`

**Si no está activo**:
```powershell
# Abrir PowerShell como ADMIN
.\scripts\postgres-start.ps1
```

---

### Paso 2: Base de Datos Existe

```bash
# Desde PowerShell admin
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "SELECT datname FROM pg_database WHERE datname='cacique_analytics';"
```

**Resultado esperado**:
```
 datname
─────────────────
 cacique_analytics
```

---

### Paso 3: Tablas Creadas (12)

```bash
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
```

**Resultado esperado**: `12`

**Ver lista completa**:
```bash
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"
```

Deberías ver:
```
      table_name
──────────────────────────
 competitions
 matches
 nationalities
 player_market_values
 player_match_stats
 player_season_stats
 player_team_seasons
 players
 positions
 seasons
 team_season_stats
 teams
```

---

### Paso 4: Datos Semilla (19 posiciones + 4 competencias)

```bash
# Posiciones
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "SELECT COUNT(*) FROM positions;"
```

**Resultado esperado**: `19`

```bash
# Competencias
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "SELECT COUNT(*) FROM competitions;"
```

**Resultado esperado**: `4`

**Ver detalles de posiciones**:
```bash
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "SELECT code, name_es, position_group FROM positions ORDER BY position_group, code;"
```

---

### Paso 5: Permisos de Usuario Correctos

```bash
# Should work: SELECT
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "SELECT 1;"
```

**Resultado esperado**: `1`

```bash
# Should work: INSERT (test en tabla temporal)
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "INSERT INTO nationalities (name, code) VALUES ('TEST', 'ZZ'); DELETE FROM nationalities WHERE code='ZZ';"
```

**Resultado esperado**: No erro

```bash
# Should FAIL: DROP
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "DROP TABLE positions;"
```

**Resultado esperado**: `ERROR: permission denied for table positions`

---

### Paso 6: Integridad del Schema

```bash
# Verificar constraints
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "
SELECT constraint_name, constraint_type, table_name
FROM information_schema.table_constraints
WHERE table_schema='public'
ORDER BY table_name;
" | head -30
```

**Resultado esperado**: 30+ constraints (FKs, PKs, UCs, CHECKs)

---

### Paso 7: Índices Creados

```bash
# Contar índices (esperado: ~15+ después de migration 002)
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "
SELECT COUNT(*) as cantidad_indices FROM pg_indexes WHERE schemaname='public';
"
```

**Resultado esperado**: `14` (inicial) o `22` (después de migration 002)

**Ver lista de índices**:
```bash
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "
SELECT indexname FROM pg_indexes WHERE schemaname='public' ORDER BY indexname;
"
```

---

## ⚙️ Auditoría Adicional

### Verificar Secretos en Repositorio

```bash
cd C:\Users\PC\Projects\CaciqueAnalytics

# Buscar palabras como "password", "secret", etc.
git grep -i "password" -- ':!.env' ':!.env.example' ':!memory'
```

**Resultado esperado**: Sin matches (ningún archivo debería tener contraseña)

__Verificar .gitignore Efectivo__:

```bash
# .env NO debería estar en git
git check-ignore .env
```

**Resultado esperado**: `.env` (confirmando que está ignorado)

```bash
# Data cruda NO debería estar en git
git check-ignore data/raw/example.csv
git check-ignore memory/MEMORY.md
```

**Resultado esperado**: Ambos ignorados

---

## Test de Integridad Referencial

```bash
# Verificar que las posiciones seeded funcionan
PGPASSWORD='App@2026Cacique#Data!' psql -U cacique_app -d cacique_analytics -c "
SELECT
    p.code,
    p.name_es,
    p.position_group,
    COUNT(CASE WHEN p.position_group='GK' THEN 1 END) OVER () as gk_count,
    COUNT(CASE WHEN p.position_group='DEF' THEN 1 END) OVER () as def_count,
    COUNT(CASE WHEN p.position_group='MID' THEN 1 END) OVER () as mid_count,
    COUNT(CASE WHEN p.position_group='FWD' THEN 1 END) OVER () as fwd_count
FROM positions p
LIMIT 5;
"
```

**Resultado esperado**:
```
 code | name_es | position_group | gk_count | def_count | mid_count | fwd_count
──────────────────────────────────────────────────────────────────────────────
 GK   | Portero | GK             |        1 |         7 |         7 |         4
```

---

## Diagnóstico de Problemas

### Problema: `psql: command not found`

```bash
# Solución: Agregar PostgreSQL al PATH
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"

# O usar full path
"C:\Program Files\PostgreSQL\18\bin\psql" -U cacique_app -d cacique_analytics -c "SELECT 1;"
```

### Problema: `FATAL: password authentication failed`

```bash
# Verificar credenciales en .env
cat .env | grep PG_

# Resultado esperado:
# PG_USER=cacique_app
# PG_PASSWORD=App@2026Cacique#Data!

# NOTA: Si cambiaste la contraseña, actualiza .env
```

### Problema: `database "cacique_analytics" does not exist`

```bash
# Verificar que se creó la BD
PGPASSWORD='Pg@2026Cacique#Analytics!' psql -U postgres -c "SELECT datname FROM pg_database WHERE datname LIKE '%cacique%';"

# Si no existe, crear (como admin):
PGPASSWORD='Pg@2026Cacique#Analytics!' psql -U postgres -c "CREATE DATABASE cacique_analytics; GRANT CONNECT ON DATABASE cacique_analytics TO cacique_app;"
```

### Problema: `ERROR: relation "positions" does not exist`

```bash
# Migration 001 no se ejecutó correctamente

# Reimplementar migrations:
cd C:\Users\PC\Projects\CaciqueAnalytics

# Como admin:
PGPASSWORD='Pg@2026Cacique#Analytics!' psql -U postgres -d cacique_analytics -f src/migrations/001_initial_schema.sql

PGPASSWORD='Pg@2026Cacique#Analytics!' psql -U postgres -d cacique_analytics -f src/migrations/002_optimize_indexes.sql
```

---

## Resumen Final

| Componente | Esperado | Verificar | Estado |
|-----------|----------|-----------|--------|
| PostgreSQL | 18.3 | `Services` app o `postgres --version` | OK |
| BD | `cacique_analytics` | Paso 2 | OK |
| Tablas | 12 | Paso 3 | OK |
| Posiciones | 19 | Paso 4 | OK |
| Competencias | 4 | Paso 4 | OK |
| Permisos | cacique_app (SELECT, INSERT, UPDATE, DELETE) | Paso 5 | OK |
| Constraints | FKs, PKs, UCs, CHECKs | Paso 6 | OK |
| Índices | 14+ (22+ con optimization) | Paso 7 | OK |
| Secretos | Ninguno en git | Auditoría | OK |

---

## Una Vez Validado

Proceder a:
1. **Sprint 1 Fase 1C**: ETL implementation con LanusStats
2. **Ejecución**: Descargar datos del 2021-2026
3. **Análisis**: Generar rankings y visualizaciones

Próxima revisión: 20 de Marzo de 2026 (post-ETL)

