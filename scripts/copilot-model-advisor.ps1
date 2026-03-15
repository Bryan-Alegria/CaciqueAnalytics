# Selector operativo de modelo para Copilot segun tipo de tarea.
# No cambia el modelo automaticamente: solo recomienda para reducir costo y mejorar consistencia.
#
# Parametros:
#   -TaskType  Tipo de tarea a ejecutar. Determina el modelo y el canal de chat recomendados.
#              Valores validos: quick_question, docs, refactor_simple, architecture, etl_critical, debug_complex, code_review.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("quick_question", "docs", "refactor_simple", "architecture", "etl_critical", "debug_complex", "code_review")]
    [string]$TaskType
)

$routes = @{
    # Tareas de baja complejidad y bajo riesgo tecnico.
    quick_question = @{
        model = "Claude Haiku 4.5 (preferido) o Grok Code Fast 1"
        reason = "Costo bajo para respuestas cortas y no criticas"
        chat = "Si cambias a Claude, abre chat nuevo antes de enviar el prompt"
    }
    docs = @{
        model = "Claude Haiku 4.5 o Claude Sonnet 4"
        reason = "Buena redaccion con bajo costo"
        chat = "Si cambias a Claude, abre chat nuevo antes de enviar el prompt"
    }
    refactor_simple = @{
        model = "Claude Sonnet 4.5 o GPT-5 mini"
        reason = "Cambios mecanicos con buena calidad/precio"
        chat = "Si cambias a Claude, abre chat nuevo antes de enviar el prompt"
    }
    # Tareas criticas de arquitectura y calidad de datos.
    architecture = @{
        model = "GPT-5.3-Codex"
        reason = "Mayor precision en decisiones de alto impacto"
        chat = "Puedes continuar en este chat con GPT-5.3-Codex"
    }
    etl_critical = @{
        model = "GPT-5.3-Codex"
        reason = "Calidad de datos e idempotencia requieren maximo control"
        chat = "Puedes continuar en este chat con GPT-5.3-Codex"
    }
    # Tareas de analisis profundo donde conviene mayor capacidad de razonamiento.
    debug_complex = @{
        model = "GPT-5.3-Codex o Claude Sonnet 4.6"
        reason = "Analisis profundo en fallos no triviales"
        chat = "Si cambias a Claude, abre chat nuevo antes de enviar el prompt"
    }
    code_review = @{
        model = "GPT-5.3-Codex o Claude Sonnet 4.6"
        reason = "Mejor deteccion de riesgos y regresiones"
        chat = "Si cambias a Claude, abre chat nuevo antes de enviar el prompt"
    }
}

# Recupera la entrada de enrutamiento correspondiente al tipo de tarea recibido.
$route = $routes[$TaskType]

# Salida legible para usar antes de abrir/cambiar chat y ejecutar la tarea.
Write-Host "Task type : $TaskType"
Write-Host "Model     : $($route.model)"
Write-Host "Reason    : $($route.reason)"
Write-Host "Chat note : $($route.chat)"
Write-Host ""
Write-Host "Nota: Copilot no permite forzar cambio automatico de modelo por prompt desde este repo."
Write-Host "Usa este script como estandar operativo para elegir rapido el modelo antes de cada tarea."
