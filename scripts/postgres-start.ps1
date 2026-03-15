# Wrapper para iniciar PostgreSQL reutilizando el script central de servicio.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$scriptDir\postgres-service.ps1" -Action start
