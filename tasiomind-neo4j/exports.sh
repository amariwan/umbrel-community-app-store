export APP_TASIOMIND_NEO4J_PASSWORD="$(derive_entropy "env-${app_entropy_identifier}-NEO4J_PASSWORD" | tr -cd 'A-Za-z0-9' | head -c32)"
