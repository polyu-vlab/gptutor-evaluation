#!/bin/bash

# Test request for embedding model api
curl  "$AZURE_OPENAI_EMBEDDING_BASE_URL"openai/deployments/"$AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"/embeddings?api-version="$AZURE_OPENAI_EMBEDDING_API_VERSION"\
  -H 'Content-Type: application/json' \
  -H "api-key: $AZURE_OPENAI_EMBEDDING_API_KEY" \
  -d '{"input": "Sample Document goes here"}'
