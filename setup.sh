#!/bin/bash

# 1. Create dbconn.env if it doesn't exist
if [ ! -f dbconn.env ]; then
    echo "Creating dbconn.env from dbconn.env.example..."
    cp dbconn.env.example dbconn.env
fi

# 2. Generate random keys if they are default or empty
generate_key() {
    openssl rand -hex 32
}

# Replace default/empty keys in dbconn.env
# We check if the key is 'supersecretapikey', 'supersecretflaskkey', or 'supersecretprometheuskey'
# which are the defaults in dbconn.env.example

if grep -q "APP_API_KEY=supersecretapikey" dbconn.env; then
    NEW_KEY=$(generate_key)
    echo "Generating new APP_API_KEY..."
    sed -i '' "s/APP_API_KEY=supersecretapikey/APP_API_KEY=$NEW_KEY/" dbconn.env
fi

if grep -q "FLASK_SECRET_KEY=supersecretflaskkey" dbconn.env; then
    NEW_KEY=$(generate_key)
    echo "Generating new FLASK_SECRET_KEY..."
    sed -i '' "s/FLASK_SECRET_KEY=supersecretflaskkey/FLASK_SECRET_KEY=$NEW_KEY/" dbconn.env
fi

if grep -q "PROMETHEUS_API_KEY=supersecretprometheuskey" dbconn.env; then
    NEW_KEY=$(generate_key)
    echo "Generating new PROMETHEUS_API_KEY..."
    sed -i '' "s/PROMETHEUS_API_KEY=supersecretprometheuskey/PROMETHEUS_API_KEY=$NEW_KEY/" dbconn.env
fi

# 3. Run upgrade script to build and initialize the database
echo "Running upgrade.sh to build and initialize the database..."
chmod +x upgrade.sh
./upgrade.sh

echo "------------------------------------------------"
echo "Setup complete!"
echo "Your APP_API_KEY is: $(grep APP_API_KEY dbconn.env | cut -d'=' -f2)"
echo "You can now access the dashboard at http://localhost:45000"
echo "------------------------------------------------"
