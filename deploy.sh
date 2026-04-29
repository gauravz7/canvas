#!/bin/bash
set -e

SERVICE_NAME="vibe-studio-refactor"
REGION="us-central1"
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:?"Error: GOOGLE_CLOUD_PROJECT env var must be set"}

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
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,FIREBASE_PROJECT_ID=$PROJECT_ID,CORS_ORIGINS=*"

echo "✅ Deployment completed successfully!"
