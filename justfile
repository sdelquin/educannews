# Run program
run:
    uv run python main.py notify -v

# Sync uv
[macos]
sync:
    uv sync --no-group prod

# Sync uv
[linux]
sync:
    uv sync --no-dev --group prod

# Deploy
deploy: && sync
    git pull
