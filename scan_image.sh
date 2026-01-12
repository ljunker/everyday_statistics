#!/bin/bash

# Configuration
IMAGE_NAME="everyday_statistics"
IMAGE_TAG="local-scan"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building Docker image ${FULL_IMAGE_NAME}..."
docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed."
    exit 1
fi

echo "------------------------------------------------"
echo "Running Trivy vulnerability scanner..."
echo "Scanning for HIGH and CRITICAL vulnerabilities..."

# Check if trivy is installed
if ! command -v trivy &> /dev/null; then
    echo "Trivy is not installed locally. Running via Docker..."
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v $HOME/Library/Caches:/root/.cache/ \
        aquasec/trivy:latest image \
        --severity HIGH,CRITICAL \
        --exit-code 1 \
        --ignore-unfixed \
        "${FULL_IMAGE_NAME}"
else
    trivy image \
        --severity HIGH,CRITICAL \
        --exit-code 1 \
        --ignore-unfixed \
        "${FULL_IMAGE_NAME}"
fi

SCAN_EXIT_CODE=$?

if [ $SCAN_EXIT_CODE -eq 0 ]; then
    echo "------------------------------------------------"
    echo "Scan passed! No HIGH or CRITICAL vulnerabilities found."
else
    echo "------------------------------------------------"
    echo "Scan failed! HIGH or CRITICAL vulnerabilities detected."
fi

exit $SCAN_EXIT_CODE
