# PostgreSQL Local en Windows 11 (pgAdmin)

**Estado actual:** PostgreSQL 18.3 instalado y operativo (2026-03-15)

Esta guia deja PostgreSQL instalado en local y configurado para apagarse cuando no se use.

## 1) Instalacion

1. Descarga PostgreSQL para Windows desde el sitio oficial.
2. Ejecuta el instalador de EnterpriseDB.
3. Componentes recomendados:
   - PostgreSQL Server
   - pgAdmin 4
   - Command Line Tools
4. Puerto: 5432.
5. Crea una password robusta para el usuario postgres.
6. Finaliza la instalacion.

## 2) Verificacion inicial

Abre PowerShell y ejecuta:

psql --version

Si el comando no existe, agrega al PATH (reemplazar 18 con la version instalada — verificar en C:\Program Files\PostgreSQL\):

C:\Program Files\PostgreSQL\18\bin

## 3) Operacion diaria desde este repo

Se incluyeron scripts en scripts/ para controlar el servicio:

- Start: powershell -NoProfile -ExecutionPolicy RemoteSigned -File scripts/postgres-start.ps1
- Stop: powershell -NoProfile -ExecutionPolicy RemoteSigned -File scripts/postgres-stop.ps1
- Status: powershell -NoProfile -ExecutionPolicy RemoteSigned -File scripts/postgres-status.ps1

Tambien tienes tareas de VS Code en .vscode/tasks.json:

- PostgreSQL: Start
- PostgreSQL: Stop
- PostgreSQL: Status
- PostgreSQL: Startup Manual

## 4) Dejar PostgreSQL apagado por defecto

Para evitar un proceso activo en segundo plano cuando no lo uses:

1. Ejecuta la tarea PostgreSQL: Startup Manual una sola vez.
2. Usa PostgreSQL: Start solo cuando vayas a trabajar.
3. Al terminar, ejecuta PostgreSQL: Stop.

## 5) Conectar pgAdmin

1. Abre pgAdmin.
2. Register -> Server.
3. En General, define un nombre local (ejemplo: local-postgres).
4. En Connection:
   - Host: localhost
   - Port: 5432
   - Username: postgres
   - Password: la que definiste en la instalacion

## 6) Seguridad minima recomendada

- No hardcodear credenciales en codigo.
- Guardar secretos en .env (ya ignorado por git).
- Usar usuario de aplicacion con privilegios minimos, no postgres para pipelines.
- Mantener el servicio en Manual para no exponer superficie innecesaria.

## 7) Crear base de datos y usuario de aplicacion

Este paso aplica el principio de minimo privilegio: el pipeline ETL nunca usa el superusuario postgres.

Abre PowerShell como administrador, inicia el servicio y conéctate con psql:

    psql -U postgres -h localhost

Ejecuta los siguientes comandos dentro de psql:

    -- Crear la base de datos del proyecto
    CREATE DATABASE cacique_analytics;

    -- Crear el usuario de aplicacion con password robusta
    CREATE USER cacique_app WITH PASSWORD 'reemplazar_con_password_robusta';

    -- Conectar a la base de datos recien creada
    \c cacique_analytics

    -- Otorgar permiso de conexion
    GRANT CONNECT ON DATABASE cacique_analytics TO cacique_app;

    -- Otorgar uso del schema public
    GRANT USAGE ON SCHEMA public TO cacique_app;

    -- Las tablas futuras heredaran automaticamente estos privilegios al crearlas
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO cacique_app;

    -- Salir de psql
    \q

Nota: el usuario cacique_app NO tiene permisos para DROP ni CREATE TABLE.
Solo el superusuario postgres o un rol dedicado de migraciones los ejecutara.

## 8) Variables de entorno para conexion (.env)

Copia .env.example a .env y completa los valores:

    PG_HOST=localhost
    PG_PORT=5432
    PG_DB=cacique_analytics
    PG_USER=cacique_app
    PG_PASSWORD=tu_password_de_aplicacion_aqui

Nunca uses las credenciales del superusuario postgres en el .env del proyecto.
