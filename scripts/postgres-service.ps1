# Script central para administrar el servicio de PostgreSQL en Windows.
# Acciones soportadas: iniciar, detener, reiniciar, estado y tipo de inicio (manual/automatico).
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("start", "stop", "restart", "status", "manual", "auto")]
    [string]$Action,

    [Parameter(Mandatory = $false)]
    [string]$ServiceName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Verifica si la sesion actual tiene permisos de administrador.
# Es obligatorio para acciones que cambian estado/configuracion del servicio.
function Test-IsAdministrator {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Resuelve el nombre del servicio PostgreSQL a utilizar.
# Si se provee PreferredName, valida que exista y lo retorna.
# Si no, detecta automaticamente por patron 'postgresql*':
#   - Un solo servicio encontrado: lo usa directamente.
#   - Varios servicios: prefiere el unico en estado Running; si hay empate, toma el ultimo alfabetico (version mayor).
#   - FailIfMissing controla si lanza error o retorna null cuando no hay ningun servicio instalado.
function Resolve-PostgresServiceName {
    param(
        [string]$PreferredName,
        [bool]$FailIfMissing = $true
    )

    if ($PreferredName) {
        $svc = Get-Service -Name $PreferredName -ErrorAction SilentlyContinue
        if (-not $svc) {
            throw "No existe el servicio '$PreferredName'. Revisa el nombre con: Get-Service postgresql*"
        }
        return $svc.Name
    }

    $services = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Sort-Object Name
    if (-not $services) {
        if ($FailIfMissing) {
            throw "No se encontro ningun servicio PostgreSQL. Instala PostgreSQL primero."
        }
        return $null
    }

    if ($services.Count -eq 1) {
        return $services[0].Name
    }

    $running = $services | Where-Object { $_.Status -eq "Running" }
    if ($running.Count -eq 1) {
        return $running[0].Name
    }

    # Si hay varios, toma el ultimo alfabetico (normalmente mayor version)
    return $services[-1].Name
}

# Imprime estado operativo y modo de inicio del servicio.
function Print-ServiceState {
    param([string]$Name)

    $svc = Get-Service -Name $Name
    $wmi = Get-CimInstance Win32_Service -Filter "Name='$Name'"

    Write-Host "Servicio      : $($svc.Name)"
    Write-Host "Estado        : $($svc.Status)"
    Write-Host "Inicio        : $($wmi.StartMode)"
    Write-Host "Display Name  : $($svc.DisplayName)"
}

if ($Action -eq "status") {
    # Para estado permitimos ejecucion sin admin y sin error duro si PostgreSQL no esta instalado.
    $resolvedService = Resolve-PostgresServiceName -PreferredName $ServiceName -FailIfMissing $false
    if (-not $resolvedService) {
        Write-Host "Estado: PostgreSQL no instalado o servicio no registrado."
        Write-Host "Siguiente paso: instala PostgreSQL y vuelve a ejecutar este script."
        exit 0
    }
}
else {
    # Cualquier accion mutante requiere elevacion para evitar fallos silenciosos.
    if (-not (Test-IsAdministrator)) {
        throw "Se requieren permisos de administrador para la accion '$Action'. Ejecuta PowerShell/VS Code como administrador."
    }
    $resolvedService = Resolve-PostgresServiceName -PreferredName $ServiceName
}

# Ejecuta la accion solicitada y muestra el estado final para confirmacion operativa.
switch ($Action) {
    "start" {
        Start-Service -Name $resolvedService
        Start-Sleep -Seconds 1
        Print-ServiceState -Name $resolvedService
    }
    "stop" {
        Stop-Service -Name $resolvedService
        Start-Sleep -Seconds 1
        Print-ServiceState -Name $resolvedService
    }
    "restart" {
        Restart-Service -Name $resolvedService
        Start-Sleep -Seconds 1
        Print-ServiceState -Name $resolvedService
    }
    "status" {
        Print-ServiceState -Name $resolvedService
    }
    "manual" {
        Set-Service -Name $resolvedService -StartupType Manual
        Print-ServiceState -Name $resolvedService
    }
    "auto" {
        Set-Service -Name $resolvedService -StartupType Automatic
        Print-ServiceState -Name $resolvedService
    }
    default {
        throw "Accion no soportada: $Action"
    }
}
