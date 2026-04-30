#!/bin/bash
set -e

SERVICE_NAME="vibe-studio-refactor"
REGION="us-central1"
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:?"Error: GOOGLE_CLOUD_PROJECT env var must be set"}
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "🏗️  Building frontend..."
(cd frontend && rm -rf dist && npm run build)

echo "🐳 Building Docker image (explicit Dockerfile, not buildpacks)..."
gcloud builds submit \
    --tag "$IMAGE" \
    --project "$PROJECT_ID" \
    --timeout 1200s

echo "🚀 Deploying $SERVICE_NAME to $REGION..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE" \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 3600 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,FIREBASE_PROJECT_ID=$PROJECT_ID,CORS_ORIGINS=*"

echo "✅ Deployment completed successfully!"
