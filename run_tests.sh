#!/bin/bash

# Run tests and collect coverage
echo "Running tests with coverage..."
COVERAGE_OUTPUT=$(python3 -m pytest --cov=src --cov-report=term-missing)
echo "$COVERAGE_OUTPUT"

# Extract total coverage percentage
# Look for the TOTAL line and extract the percentage value
COVERAGE_PCT=$(echo "$COVERAGE_OUTPUT" | grep 'TOTAL' | awk '{print $NF}' | sed 's/%//')

if [ -z "$COVERAGE_PCT" ]; then
    echo "Failed to extract coverage percentage."
    exit 1
fi

echo "Detected coverage: ${COVERAGE_PCT}%"

# Determine color based on coverage percentage
if [ "$COVERAGE_PCT" -ge 90 ]; then
    COLOR="brightgreen"
elif [ "$COVERAGE_PCT" -ge 75 ]; then
    COLOR="yellowgreen"
elif [ "$COVERAGE_PCT" -ge 60 ]; then
    COLOR="yellow"
elif [ "$COVERAGE_PCT" -ge 40 ]; then
    COLOR="orange"
else
    COLOR="red"
fi

# Update README.md
# Search for the coverage badge and replace it
# Example: ![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)
sed -i.bak "s/badge\/coverage-[0-9]\{1,3\}%25-[a-z]*/badge\/coverage-${COVERAGE_PCT}%25-${COLOR}/g" README.md

echo "Updated README.md with ${COVERAGE_PCT}% coverage badge."
rm README.md.bak
