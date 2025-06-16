@echo off
echo Starting Docker infrastructure...

docker compose -f deploy/caddy.compose.yaml up -d
docker compose -f admin/compose.yaml up -d
docker compose -f store/compose.yaml up -d

docker compose -f store/compose.yaml exec store python manage.py migrate

    set /p createadmin=Would you like to create a superuser? (y/n): 
    IF "%createadmin%"=="y" (
        docker compose -f store/compose.yaml exec store python manage.py createsuperuser
    ) ELSE (
        echo Skipping superuser creation.
    )

echo All services started successfully.
pause
