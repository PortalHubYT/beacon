#!/bin/bash

# Deactivate the virtual environment
deactivate

# Switch back to the main branch
git checkout main

echo "Virtual environment deactivated, and switched back to the 'main' branch."

# Update the repository to reflect the state of the main branch
echo "Updating the repository to reflect the state of the 'main' branch..."
git pull origin main
