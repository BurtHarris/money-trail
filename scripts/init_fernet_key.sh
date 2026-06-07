#!/bin/bash
# Initialize Airflow Fernet key on first container start
# Generates a cryptographically secure key and stores it in .env for persistence

set -euo pipefail

ENV_FILE="${WORKDIR:-/workspaces/money-trail}/.env"
EXAMPLE_ENV="${WORKDIR:-/workspaces/money-trail}/.env.example"

# If .env doesn't exist, copy from .env.example
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$EXAMPLE_ENV" ]; then
        cp "$EXAMPLE_ENV" "$ENV_FILE"
        echo "✓ Created .env from .env.example"
    else
        touch "$ENV_FILE"
        echo "✓ Created empty .env"
    fi
fi

# Check if AIRFLOW__CORE__FERNET_KEY is already set in .env
if grep -q "^AIRFLOW__CORE__FERNET_KEY=" "$ENV_FILE"; then
    EXISTING_KEY=$(grep "^AIRFLOW__CORE__FERNET_KEY=" "$ENV_FILE" | cut -d'=' -f2-)
    if [ -n "$EXISTING_KEY" ]; then
        echo "✓ Fernet key already configured in .env"
        export "AIRFLOW__CORE__FERNET_KEY=$EXISTING_KEY"
        exit 0
    fi
fi

# Generate a new Fernet key
echo "⚙ Generating new Airflow Fernet key..."
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

if [ -z "$FERNET_KEY" ]; then
    echo "✗ Failed to generate Fernet key"
    exit 1
fi

# Add or update AIRFLOW__CORE__FERNET_KEY in .env
if grep -q "^AIRFLOW__CORE__FERNET_KEY=" "$ENV_FILE"; then
    # Update existing line
    sed -i.bak "s|^AIRFLOW__CORE__FERNET_KEY=.*|AIRFLOW__CORE__FERNET_KEY=$FERNET_KEY|" "$ENV_FILE"
    rm -f "$ENV_FILE.bak"
else
    # Append new line
    echo "" >> "$ENV_FILE"
    echo "AIRFLOW__CORE__FERNET_KEY=$FERNET_KEY" >> "$ENV_FILE"
fi

echo "✓ Fernet key generated and saved to .env"
