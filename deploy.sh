#!/bin/bash
set -e

SERVICE_NAME="vibe-studio-refactor"
REGION="us-central1"
# Ensure PROJECT_ID is set, otherwise default to vital-octagon-19612
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"vital-octagon-19612"}

echo "🏗️ Building frontend..."
cd frontend && npm run build
cd ..

echo "🚀 Deploying $SERVICE_NAME to $REGION (Project: $PROJECT_ID)..."

# Deploy to Cloud Run using source (builds with Dockerfile in current dir)
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 3600 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

echo "✅ Deployment completed successfully!"
