# ⚡ Cloud & Web Hosting AI Marketing Studio (v1.0.0)

> **Customer-Agnostic Enterprise Autonomous Marketing Production Suite** built on an Infinite Node Workbench Canvas powered by **Gemini Omni Multimodal Reasoning**, **Google Veo 3.1 Video Generation**, and **Google Chirp 3 HD Multilingual Speech Synthesis**.

---

## 🌟 Key Capabilities

### 1. ♾️ Infinite Visual Node Canvas (ComfyUI / Magnific AI Style)
- **Fluid Drag-and-Drop Wires**: Connect narrative hooks ➔ visual banners ➔ motion video clips ➔ voiceover audio ➔ stitched master ads.
- **Dedicated Port Color Sockets**:
  - `[🚀]` Prompt & Initial Launcher Port
  - `[🖼️]` Visual / Image Asset Port (Emerald `#10b981`)
  - `[📹]` Motion Video Stream Port (Teal `#06b6d4`)
  - `[🎙️]` Multilingual Audio Stream Port (Violet `#a855f7`)
- **Interactive Workbench Tools**: Smooth camera panning, zooming, 1-click **Fit View** (`♾️`), **Reset Canvas** (`🔍`), **Radar Minimap** (`🗺️`), and card minimization/expansion (`⤢`).

### 2. 💡 High-CTR Narrative Generation (Gemini 2.5 Flash)
- Synthesizes 3 distinct narrative angles (Shock-Factor, Data/Speed Benchmark, Discount/Promo Blitz) with live CTR predictions (`8.8%`, `8.4%`, `8.0%`).

### 3. 🖼️ Fluid Glassmorphic Image Asset Synthesis
- Generates high-resolution brand posters with dark-mode glassmorphism, dynamic glowing neon gradients, ABCD validation score pills (`9.6/10`), and 4-way palette switching (`#96CB4C` Green, `#00A88F` Navy, Emerald, White).

### 4. 🎙️ Multilingual Multi-Stream Audio Narration (Google Chirp 3 HD)
- Spawns parallel audio streams across 8 languages (🇺🇸 English, 🇪🇸 Spanish, 🇩🇪 German, 🇫🇷 French, 🇮🇹 Italian, 🇧🇷 Portuguese, 🇧🇬 Bulgarian, 🇯🇵 Japanese).
- 1-click presets: `[⚡ Top 3 (US/ES/DE)]`, `[🌍 EU Pack]`, `[Toggle All]`.
- In-card real-time language switcher with live translation and re-synthesis.

### 5. 🎬 Connected Multi-Stream Video Combiner & Stitcher
- Gathers connected video clips and voiceover tracks, normalizes frame rates/dimensions, and stitches them with **Gemini Omni Visual Cohesion** (`98.8%`).
- Direct aspect ratio transformation (`16:9`, `9:16`, `1:1`, `4:5`).

### 6. 🚀 1-Click Multi-Network Campaign Deployment
- Instant live push to **Google Ads Performance Max (PMax)**, **YouTube Shorts**, and **Instagram Reels** with tracking ID assignment.

---

## 🏗️ Architecture & Project Structure

```
ai-marketing-studio/
├── app/
│   ├── agent.py               # ADK agent reasoning loop & tool declarations
│   ├── fast_api_app.py        # Production FastAPI server & SSE streaming routes
│   ├── studio_api.py          # REST endpoints for scripts, images, audio & stitching
│   ├── image_studio.py        # Branded image synthesis & typography rendering
│   ├── video_renderer.py      # Video clip compositor & frame animation engine
│   ├── script_engine.py       # Narrative generation & CTR estimation
│   ├── compositor.py          # Video concat & audio muxing pipeline
│   └── app_utils/             # A2A protocol and reasoning engine adapters
├── index.html                 # Modern glassmorphic Web App UI & canvas frontend
├── tests/
│   ├── test_holistic_10_user_journeys.py  # Playwright 10-journey automated suite
│   ├── test_agent_node.py                 # Agent node interruption & resume tests
│   ├── test_compositor.py                 # Media stitching unit tests
│   ├── test_script_engine.py              # Script engine fallback tests
│   └── integration/                       # Server and ADK streaming integration tests
├── run_10_journeys.py         # Standalone 10-journey automated browser runner
├── Dockerfile                 # Cloud Run deployment container
├── pyproject.toml             # Python 3.11+ dependencies & metadata
└── README.md                  # Comprehensive documentation
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- `uv` package manager (`pip install uv`)
- Google Cloud SDK (`gcloud`)

### 2. Local Development
```bash
# Install dependencies
uv sync

# Run local development server
uv run uvicorn server:app --host 0.0.0.0 --port 8080 --reload
```
Open **`http://localhost:8080/`** in your browser.

---

## 🧪 Testing

Run the unit and integration test suite:
```bash
uv run pytest tests/unit tests/integration -v
```

Run the **10 Holistic E2E User Journeys**:
```bash
python3 run_10_journeys.py
```

---

## 🌐 Production Deployment (Cloud Run)

```bash
gcloud config set project <YOUR-GCP-PROJECT-ID>
gcloud run deploy ai-marketing-studio \
  --source . \
  --region us-east1 \
  --allow-unauthenticated
```
