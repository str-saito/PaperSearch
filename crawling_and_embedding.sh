#!/bin/bash

CONTAINER_ID=$(sudo docker ps --filter "ancestor=papersearch_saito_satoru-web" --format "{{.ID}}")

if [ -z "$CONTAINER_ID" ]; then
  echo "Error: Not found container."
  exit 1
fi

echo "Fount container ID: $CONTAINER_ID"

sudo docker exec -it $CONTAINER_ID /bin/bash -c "
  python util/crawling_script.py && \
  python util/embedding_script.py
"