# Wrapper para consultar estado de PostgreSQL reutilizando el script central.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$scriptDir\postgres-service.ps1" -Action status
