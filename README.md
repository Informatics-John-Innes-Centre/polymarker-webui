```bash
cp .env.example .env
sudo docker compose -f dev-compose.yaml up -d
sudo docker compose -f dev-compose.yaml exec polymarker uv run flask --app pmwui init
```