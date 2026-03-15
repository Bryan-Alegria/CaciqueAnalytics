# Copilot Model Routing (Costo vs Calidad)

## Limite tecnico actual

No existe un mecanismo oficial en el repositorio para forzar que Copilot cambie de modelo automaticamente por cada prompt.

Tambien, en tu flujo actual, para usar modelos de Anthropic debes abrir un chat nuevo.

Si existe estandarizacion operativa: puedes definir reglas y usar un selector rapido para decidir modelo antes de enviar cada tarea.

## Regla de enrutamiento recomendada

- quick_question -> Claude Haiku 4.5 (preferido) o Grok Code Fast 1
- docs -> Claude Haiku 4.5 o Claude Sonnet 4
- refactor_simple -> Claude Sonnet 4.5 o GPT-5 mini
- architecture -> GPT-5.3-Codex
- etl_critical -> GPT-5.3-Codex
- debug_complex -> GPT-5.3-Codex o Claude Sonnet 4.6
- code_review -> GPT-5.3-Codex o Claude Sonnet 4.6

## Script de apoyo

Ejemplo:

powershell -NoProfile -ExecutionPolicy RemoteSigned -File scripts/copilot-model-advisor.ps1 -TaskType architecture

TaskType validos:

- quick_question
- docs
- refactor_simple
- architecture
- etl_critical
- debug_complex
- code_review

## Politica operativa sugerida

- 70% a 85% de tareas en modelos economicos.
- 15% a 30% en modelos Codex para decisiones y cambios criticos.
- Si una tarea economica entra en iteraciones repetidas, escalar temprano a Codex para reducir costo total.

## Flujo recomendado cuando quieras usar Claude

1. Ejecuta el advisor para elegir modelo por tipo de tarea.
2. Si el advisor recomienda Claude, abre chat nuevo y selecciona el modelo Claude.
3. Pega un prompt corto con contexto y objetivo cerrado para ahorrar tokens.
4. Si la tarea escala en complejidad ETL/arquitectura, vuelve a GPT-5.3-Codex.
