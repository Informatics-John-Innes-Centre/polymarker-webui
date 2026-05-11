```bash
cp .env.example .env
sudo docker compose -f dev-compose.yaml up -d

# initialise database
sudo docker compose -f dev-compose.yaml exec polymarker uv run flask --app pmwui init

# import genome
sudo docker compose -f dev-compose.yaml exec polymarker uv run flask --app pmwui import genome.toml
```