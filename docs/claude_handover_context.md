# CaciqueAnalytics - Handover Maestro para Nuevo Chat (Claude)

## 1. Objetivo del proyecto

CaciqueAnalytics es un proyecto ETL orientado al analisis de Colo-Colo y la Primera Division de Chile para construir un portafolio profesional de ingenieria de datos.

Objetivos inmediatos:

1. Refinar scraping para obtener y validar IDs de liga/equipo (temporada 2026).
2. Definir arquitectura de datos antes de SQL final (tablas base: matches, player_stats, league_standings).
3. Implementar flujo idempotente para deteccion de partidos finalizados sin duplicidad.
4. Preparar base de visualizaciones profesionales (heatmaps y pass networks).

## 2. Reglas y convenciones obligatorias

1. Codigo, variables y funciones en ingles.
2. Comentarios y documentacion en espanol.
3. Nunca hardcodear secretos.
4. Credenciales siempre por .env (ya ignorado por git).
5. Principio de minimo privilegio para usuarios de base de datos.
6. Respuestas tecnicas, sobrias, concisas y objetivas.
7. No implementar codigo masivo sin validar arquitectura de base de datos con el usuario.

## 3. Estado actual del repositorio

Se agrego infraestructura operativa para PostgreSQL local en Windows y estandar de enrutamiento de modelos para Copilot.

Archivos clave incorporados:

- scripts/postgres-service.ps1
- scripts/postgres-start.ps1
- scripts/postgres-stop.ps1
- scripts/postgres-status.ps1
- scripts/copilot-model-advisor.ps1
- .vscode/tasks.json
- docs/postgresql_windows_guide.md
- docs/copilot_model_routing.md
- .github/copilot-instructions.md

Notas de estado:

1. PostgreSQL aun no esta instalado en esta maquina.
2. El script de status maneja correctamente el caso sin instalacion (sin error critico).
3. Las acciones mutantes del servicio (start/stop/manual/auto/restart) requieren modo administrador.

## 4. Operacion PostgreSQL local (resumen)

Tareas de VS Code disponibles:

- PostgreSQL: Start
- PostgreSQL: Stop
- PostgreSQL: Status
- PostgreSQL: Startup Manual

Politica recomendada:

1. Dejar startup en Manual.
2. Iniciar solo al trabajar.
3. Detener al terminar para evitar proceso residente en segundo plano.

## 5. Enrutamiento de modelos (costo vs calidad)

Limitacion tecnica:

No existe enrutamiento automatico por prompt a nivel de repositorio en Copilot.

Limitacion de flujo actual del usuario:

Para usar modelos Anthropic (Claude), se debe abrir un chat nuevo.

Regla operativa actual:

- quick_question: Claude Haiku 4.5 (preferido) o Grok Code Fast 1
- docs: Claude Haiku 4.5 o Claude Sonnet 4
- refactor_simple: Claude Sonnet 4.5 o GPT-5 mini
- architecture: GPT-5.3-Codex
- etl_critical: GPT-5.3-Codex
- debug_complex: GPT-5.3-Codex o Claude Sonnet 4.6
- code_review: GPT-5.3-Codex o Claude Sonnet 4.6

## 6. Mandato para el agent en nuevo chat

El agent debe ejecutar, como minimo, este protocolo antes de avanzar en nuevas features:

1. Auditoria de seguridad:
- Revisar que no existan secretos hardcodeados.
- Verificar uso exclusivo de .env para credenciales.
- Confirmar principio de minimo privilegio para usuarios de BD.
- Verificar que scripts operativos no expongan informacion sensible en logs.

2. Auditoria funcional:
- Ejecutar scripts de control PostgreSQL y validar salidas esperadas.
- Verificar tareas de VS Code asociadas.
- Confirmar que los flujos fallen con mensajes claros cuando falten prerequisitos.

3. Auditoria de calidad de codigo:
- Revisar consistencia con convenciones (ingles en codigo, espanol en comentarios/docs).
- Detectar deuda tecnica temprana y proponer mitigacion.
- Evitar cambios grandes sin validacion previa de arquitectura.

4. Auditoria de regresion:
- Confirmar que cambios nuevos no rompan scripts existentes.
- Revalidar rutas, nombres de tareas y comandos documentados.

## 7. Checklist de aceptacion para Sprint 0

1. PostgreSQL instalado y operativo localmente.
2. Startup configurado en Manual.
3. Scripts start/stop/status/manual validados end-to-end.
4. Arquitectura de tablas validada con el usuario antes de DDL.
5. Definidas reglas de idempotencia para ingestiones.
6. IDs de liga/equipo 2026 obtenidos y verificados.

## 8. Riesgos actuales y mitigacion

1. Riesgo: avanzar a SQL sin definicion de modelado.
- Mitigacion: mantener puerta de aprobacion de arquitectura.

2. Riesgo: costo elevado por usar modelo avanzado en tareas simples.
- Mitigacion: aplicar siempre model advisor previo a cada tarea.

3. Riesgo: configuraciones locales inconsistentes al instalar PostgreSQL.
- Mitigacion: seguir docs/postgresql_windows_guide.md paso a paso y validar con tasks.

## 9. Proximo paso recomendado

Instalar PostgreSQL local en Windows y ejecutar validacion operativa completa (Start -> Status -> Stop -> Startup Manual) antes de iniciar modelado de base de datos o ETL productivo.
