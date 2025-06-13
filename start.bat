@echo off
echo Starting Docker infrastructure...

docker compose -f deploy/caddy.compose.yaml up -d
docker compose -f admin/compose.yaml up -d
docker compose -f store/compose.yaml up -d

echo All services started successfully.
pause
