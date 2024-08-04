#!/bin/bash

# Build the frontend
cd frontend
npm install
npm run build

# Go back to the root directory
cd ..

# Install backend dependencies
cd backend
pip install -r requirements.txt
