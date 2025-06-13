@echo off
echo Stopping Docker infrastructure...

docker compose -f store/compose.yaml down
docker compose -f admin/compose.yaml down
docker compose -f deploy/caddy.compose.yaml down

echo All services stopped successfully.
pause
