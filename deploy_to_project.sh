#!/usr/bin/env bash
# ==============================================================================
# Automated Turnkey Deployment Script for AI Marketing Studio
# Usage: ./deploy_to_project.sh <TARGET_GCP_PROJECT_ID> [REGION]
# ==============================================================================
set -euo pipefail

TARGET_PROJECT="${1:-secondtestproject}"
REGION="${2:-us-east1}"
SERVICE_NAME="ai-marketing-studio"

echo "=================================================================="
echo "🚀 DEPLOYING AI MARKETING STUDIO TO GCP PROJECT: ${TARGET_PROJECT}"
echo "📍 Region: ${REGION}"
echo "=================================================================="

# 1. Configure gcloud project
echo "⚙️ Setting gcloud active project..."
gcloud config set project "${TARGET_PROJECT}"

# 2. Enable Required Google Cloud APIs
echo "🔌 Enabling required GCP Services & APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    texttospeech.googleapis.com \
    compute.googleapis.com \
    logging.googleapis.com \
    --quiet || true

# 3. Deploy container directly to Cloud Run
echo "📦 Building container and deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region "${REGION}" \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${TARGET_PROJECT},GOOGLE_CLOUD_LOCATION=${REGION}" \
    --memory=2Gi \
    --cpu=2 \
    --concurrency=80 \
    --timeout=300 \
    --quiet

# 4. Retrieve Service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format="value(status.url)")
echo "=================================================================="
echo "✅ SERVICE DEPLOYED SUCCESSFULLY!"
echo "🌐 Live URL: ${SERVICE_URL}"
echo "=================================================================="

# 5. Run Automated 10 Holistic E2E User Journeys Verification
echo "🧪 Running 10 Holistic E2E Verification Journeys on new deployment..."
STUDIO_APP_URL="${SERVICE_URL}" python3 run_10_journeys.py

echo "🎉 ALL CHECKS PASSED ON ${SERVICE_URL}!"
