#!/bin/bash

# Navigate to the frontend folder
cd "$(dirname "$0")"

# Install dependencies (if using npm/yarn)
if [ -f "package.json" ]; then
  echo "Installing dependencies..."
  npm install
else
  echo "No package.json found. Skipping dependency installation."
fi

# Start the server (if applicable)
echo "Starting the development server..."
npm start

# Display success message
echo "Frontend setup complete. Open your browser at http://localhost:3000"
