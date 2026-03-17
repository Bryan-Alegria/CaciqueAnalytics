# VALIDACIÓN DE SISTEMA — CaciqueAnalytics

**Propósito**: Remítete a esta guía para verificar que todo el setup está correcto.
**Última actualización**: 17 de Marzo de 2026

**IMPORTANTE**: Este archivo es un template. Las credenciales deben cargarse desde `.env`.

---

## Configuración Previa

```bash
# Cargar credenciales desde .env
source .env  # Linux/Mac
# O manualmente en PowerShell:
$env:PGPASSWORD = (Get-Content .env | Select-String "DB_PASSWORD").ToString().Split("=")[1]
```

---

## Checklist Rápido

### Paso 1: PostgreSQL Activo

```bash
# Desde PowerShell (cualquier usuario)
sc query postgresql-x64-18 | findstr RUNNING
```

**Resultado esperado**: `RUNNING`

**Si no está activo**:
```powershell
# Abrir PowerShell como ADMIN
.\scripts\postgres-start.ps1
```

---

### Paso 2: Base de Datos Existe

```bash
# Credenciales desde .env
psql -U cacique_app -d cacique_analytics -c "SELECT datname FROM pg_database WHERE datname='cacique_analytics';"
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
psql -U cacique_app -d cacique_analytics -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
```

**Resultado esperado**: `12`

**Ver lista completa**:
```bash
psql -U cacique_app -d cacique_analytics -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"
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
psql -U cacique_app -d cacique_analytics -c "SELECT COUNT(*) FROM positions;"
```

**Resultado esperado**: `19`

```bash
# Competencias
psql -U cacique_app -d cacique_analytics -c "SELECT COUNT(*) FROM competitions;"
```

**Resultado esperado**: `4`

**Ver detalles de posiciones**:
```bash
psql -U cacique_app -d cacique_analytics -c "SELECT code, name_es, position_group FROM positions ORDER BY position_group, code;"
```

---

### Paso 5: Permisos de Usuario Correctos

```bash
# Should work: SELECT
psql -U cacique_app -d cacique_analytics -c "SELECT 1;"
```

**Resultado esperado**: `1`

```bash
# Should work: INSERT (test en tabla temporal)
psql -U cacique_app -d cacique_analytics -c "INSERT INTO nationalities (name, code) VALUES ('TEST', 'ZZ'); DELETE FROM nationalities WHERE code='ZZ';"
```

**Resultado esperado**: No error

```bash
# Should FAIL: DROP
psql -U cacique_app -d cacique_analytics -c "DROP TABLE positions;"
```

**Resultado esperado**: `ERROR: permission denied for table positions`

---

### Paso 6: Integridad del Schema

```bash
# Verificar constraints
psql -U cacique_app -d cacique_analytics -c "
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
psql -U cacique_app -d cacique_analytics -c "
SELECT COUNT(*) as cantidad_indices FROM pg_indexes WHERE schemaname='public';
"
```

**Resultado esperado**: `15` (inicial) o `24+` (después de migration 002)

**Ver lista de índices**:
```bash
psql -U cacique_app -d cacique_analytics -c "
SELECT indexname FROM pg_indexes WHERE schemaname='public' ORDER BY indexname;
"
```

---

## Auditoría Adicional

### Verificar Secretos en Repositorio

```bash
cd C:\Users\PC\Projects\CaciqueAnalytics

# Buscar palabras como "password", "secret", etc.
git grep -i "password" -- ':!.env' ':!.env.example' ':!memory' ':!VALIDACION_SISTEMA.md'
```

**Resultado esperado**: Sin matches (ningún archivo debería tener contraseña)

**Verificar .gitignore Efectivo**:

```bash
# .env NO debería estar en git
git check-ignore .env
```

**Resultado esperado**: `.env` (confirmando que está ignorado)

```bash
# VALIDACION_SISTEMA.md NO debería estar en git
git check-ignore VALIDACION_SISTEMA.md
```

**Resultado esperado**: `VALIDACION_SISTEMA.md`

---

## Test de Integridad Referencial

```bash
# Verificar que las posiciones seeded funcionan
psql -U cacique_app -d cacique_analytics -c "
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
cat .env | grep DB_PASSWORD
```

### Problema: `database "cacique_analytics" does not exist`

```bash
# Verificar que se creó la BD (requiere credenciales de postgres desde .env)
psql -U postgres -c "SELECT datname FROM pg_database WHERE datname LIKE '%cacique%';"

# Si no existe, usar migration 001
```

### Problema: `ERROR: relation "positions" does not exist`

```bash
# Migration 001 no se ejecutó correctamente

# Reimplementar migrations:
cd C:\Users\PC\Projects\CaciqueAnalytics

# Como postgres (credenciales desde .env):
psql -U postgres -d cacique_analytics -f src/migrations/001_initial_schema.sql
psql -U postgres -d cacique_analytics -f src/migrations/002_optimize_indexes.sql
```

---

## Resumen Final

| Componente | Esperado | Verificar | Estado |
|-----------|----------|-----------|--------|
| PostgreSQL | 18.3 | `sc query postgresql-x64-18` | OK |
| BD | `cacique_analytics` | Paso 2 | OK |
| Tablas | 12 | Paso 3 | OK |
| Posiciones | 19 | Paso 4 | OK |
| Competencias | 4 | Paso 4 | OK |
| Permisos | cacique_app (SELECT, INSERT, UPDATE, DELETE) | Paso 5 | OK |
| Constraints | FKs, PKs, UCs, CHECKs | Paso 6 | OK |
| Índices | 15+ (24+ con optimization) | Paso 7 | OK |
| Secretos | Ninguno en git | Auditoría | OK |

---

## Una Vez Validado

Proceder a:
1. **Sprint 1 Fase 1C**: ETL implementation con LanusStats
2. **Ejecución**: Descargar datos temporada 2026
3. **Análisis**: Generar rankings y visualizaciones

Próxima revisión: 20 de Marzo de 2026 (post-ETL)
