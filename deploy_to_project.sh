#!/usr/bin/env bash
# ==============================================================================
# Automated Turnkey Deployment & Teardown Script for AI Marketing Studio
#
# Usage:
#   ./deploy_to_project.sh [TARGET_GCP_PROJECT_ID] [REGION] [OPTIONS]
#
# Options:
#   --destroy, -d     Tear down and delete the Cloud Run service from the project
#   --skip-tests      Deploy without executing the 10 holistic E2E user journeys
#   --service-name    Override Cloud Run service name (default: ai-marketing-studio)
#   -h, --help        Show usage help
# ==============================================================================
set -euo pipefail

# Default Parameters
RAW_TARGET_PROJECT="secondtestproject"
REGION="us-east1"
SERVICE_NAME="ai-marketing-studio"
MODE="deploy"
RUN_TESTS="true"

# Parse CLI Arguments & Flags
POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --destroy|--teardown|-d)
            MODE="destroy"
            shift
            ;;
        --skip-tests|--no-tests)
            RUN_TESTS="false"
            shift
            ;;
        --service-name)
            SERVICE_NAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "=================================================================="
            echo "🚀 AI Marketing Studio Turnkey Deployment CLI"
            echo "=================================================================="
            echo "Usage: $0 [TARGET_GCP_PROJECT_ID] [REGION] [OPTIONS]"
            echo ""
            echo "Arguments:"
            echo "  TARGET_GCP_PROJECT_ID  GCP Project ID or alias (default: second-test-project-393510 / secondtestproject)"
            echo "  REGION                 GCP Region (default: us-east1)"
            echo ""
            echo "Options:"
            echo "  --destroy, -d          Destroy and delete Cloud Run service from the project"
            echo "  --skip-tests           Skip automated Playwright E2E verification test suite"
            echo "  --service-name <NAME>  Override service name (default: ai-marketing-studio)"
            echo "  -h, --help             Display this help message"
            echo "=================================================================="
            exit 0
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

if [[ ${#POSITIONAL_ARGS[@]} -ge 1 ]]; then
    RAW_TARGET_PROJECT="${POSITIONAL_ARGS[0]}"
fi
if [[ ${#POSITIONAL_ARGS[@]} -ge 2 ]]; then
    REGION="${POSITIONAL_ARGS[1]}"
fi
if [[ ${#POSITIONAL_ARGS[@]} -ge 3 ]]; then
    SERVICE_NAME="${POSITIONAL_ARGS[2]}"
fi

# ------------------------------------------------------------------------------
# 1. Project Resolution & Validation
# ------------------------------------------------------------------------------
echo "=================================================================="
echo "⚙️ Resolving and validating GCP Project: ${RAW_TARGET_PROJECT}..."
echo "=================================================================="

# Check if RAW_TARGET_PROJECT is directly accessible
TARGET_PROJECT="${RAW_TARGET_PROJECT}"
if ! gcloud projects describe "${TARGET_PROJECT}" --format="value(projectId)" &>/dev/null; then
    echo "🔍 Looking up canonical Project ID for '${RAW_TARGET_PROJECT}'..."
    RESOLVED_ID=$(python3 -c '
import subprocess, json, sys
target = "'"${RAW_TARGET_PROJECT}"'".lower().replace("-", "").replace("_", "").replace(" ", "")
try:
    out = subprocess.check_output(["gcloud", "projects", "list", "--format=json"], stderr=subprocess.DEVNULL)
    data = json.loads(out)
    for p in data:
        pid = p.get("projectId", "").lower()
        pname = p.get("name", "").lower()
        p_clean_id = pid.replace("-", "").replace("_", "").replace(" ", "")
        p_clean_name = pname.replace("-", "").replace("_", "").replace(" ", "")
        if target == p_clean_id or target == p_clean_name or target in p_clean_id or target in p_clean_name:
            print(p.get("projectId"))
            sys.exit(0)
except Exception:
    pass
' 2>/dev/null || true)
    if [[ -n "${RESOLVED_ID}" ]]; then
        echo "✅ Resolved '${RAW_TARGET_PROJECT}' -> '${RESOLVED_ID}'"
        TARGET_PROJECT="${RESOLVED_ID}"
    else
        echo "❌ ERROR: Could not resolve or access project '${RAW_TARGET_PROJECT}'."
        echo "Please check available projects with 'gcloud projects list'."
        exit 1
    fi
else
    # Confirm exact project ID
    TARGET_PROJECT=$(gcloud projects describe "${TARGET_PROJECT}" --format="value(projectId)")
fi

# Set active gcloud project
gcloud config set project "${TARGET_PROJECT}" --quiet

# ------------------------------------------------------------------------------
# DESTROY MODE
# ------------------------------------------------------------------------------
if [[ "${MODE}" == "destroy" ]]; then
    echo "=================================================================="
    echo "🗑️ DESTROYING AI MARKETING STUDIO IN PROJECT: ${TARGET_PROJECT}"
    echo "📍 Region: ${REGION}"
    echo "📦 Service: ${SERVICE_NAME}"
    echo "=================================================================="

    if gcloud run services describe "${SERVICE_NAME}" --project="${TARGET_PROJECT}" --region="${REGION}" &>/dev/null; then
        echo "⏳ Deleting Cloud Run service '${SERVICE_NAME}'..."
        gcloud run services delete "${SERVICE_NAME}" \
            --project="${TARGET_PROJECT}" \
            --region="${REGION}" \
            --quiet
        echo "✅ Cloud Run service '${SERVICE_NAME}' deleted successfully."
    else
        echo "ℹ️ Cloud Run service '${SERVICE_NAME}' does not exist in region '${REGION}'. Nothing to delete."
    fi

    echo "=================================================================="
    echo "🎉 TEARDOWN COMPLETE FOR ${TARGET_PROJECT} (${REGION})"
    echo "=================================================================="
    exit 0
fi

# ------------------------------------------------------------------------------
# DEPLOY MODE
# ------------------------------------------------------------------------------
echo "=================================================================="
echo "🚀 DEPLOYING AI MARKETING STUDIO TO GCP PROJECT: ${TARGET_PROJECT}"
echo "📍 Region: ${REGION}"
echo "📦 Service: ${SERVICE_NAME}"
echo "=================================================================="

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
    --project="${TARGET_PROJECT}" \
    --quiet || true

# 3. Ensure Service Account IAM Permissions for Vertex AI & Logging
echo "🔐 Verifying Service Account IAM bindings..."
PROJECT_NUMBER=$(gcloud projects describe "${TARGET_PROJECT}" --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

if [[ -n "${PROJECT_NUMBER}" ]]; then
    gcloud projects add-iam-policy-binding "${TARGET_PROJECT}" \
        --member="serviceAccount:${COMPUTE_SA}" \
        --role="roles/aiplatform.user" \
        --condition=None \
        --quiet &>/dev/null || true

    gcloud projects add-iam-policy-binding "${TARGET_PROJECT}" \
        --member="serviceAccount:${COMPUTE_SA}" \
        --role="roles/logging.logWriter" \
        --condition=None \
        --quiet &>/dev/null || true
fi

# 4. Deploy container directly to Cloud Run
echo "📦 Building container and deploying to Cloud Run (memory: 2Gi, cpu: 2)..."
gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --project="${TARGET_PROJECT}" \
    --region="${REGION}" \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${TARGET_PROJECT},GOOGLE_CLOUD_LOCATION=${REGION}" \
    --memory=2Gi \
    --cpu=2 \
    --concurrency=80 \
    --timeout=300 \
    --quiet

# 5. Retrieve Service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${TARGET_PROJECT}" --region="${REGION}" --format="value(status.url)")
echo "=================================================================="
echo "✅ SERVICE DEPLOYED SUCCESSFULLY!"
echo "🌐 Live URL: ${SERVICE_URL}"
echo "=================================================================="

# 6. Service Health Check Readiness Probe
echo "🩺 Verifying endpoint readiness..."
for i in {1..30}; do
    if curl -s -f -o /dev/null "${SERVICE_URL}/" 2>/dev/null; then
        echo "✅ Health check passed: ${SERVICE_URL} is live and responding (200 OK)."
        break
    fi
    echo "⏳ Waiting for service warmup... (${i}/30)"
    sleep 2
done

# 7. Run Automated 10 Holistic E2E User Journeys Verification
if [[ "${RUN_TESTS}" == "true" ]]; then
    echo "🧪 Running 10 Holistic E2E Verification Journeys on new deployment..."
    if command -v uv &>/dev/null; then
        echo "📦 Ensuring dependencies and Playwright browser are synced..."
        uv sync --quiet 2>/dev/null || true
        uv run playwright install chromium 2>/dev/null || true
        STUDIO_APP_URL="${SERVICE_URL}" uv run python run_10_journeys.py
    else
        if ! python3 -c "import playwright" &>/dev/null; then
            echo "📦 Installing playwright for E2E verification..."
            pip install --quiet playwright 2>/dev/null || true
            python3 -m playwright install chromium 2>/dev/null || true
        fi
        STUDIO_APP_URL="${SERVICE_URL}" python3 run_10_journeys.py
    fi
    echo "🎉 ALL CHECKS PASSED ON ${SERVICE_URL}!"
else
    echo "⏩ Skipping E2E test verification (--skip-tests specified)."
fi

echo "=================================================================="
echo "🎉 DEPLOYMENT READY: ${SERVICE_URL}"
echo "=================================================================="
