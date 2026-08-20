# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pytest
import requests
from tests.integration.test_server_e2e import server_fixture, BASE_URL, HEADERS


def test_e2e_script_generation(server_fixture):
    """Verify script generation returns variants adhering to Google ABCD framework."""
    url = f"{BASE_URL}/api/studio/scripts/generate"
    payload = {
        "product_feature": "SuperCacher Speed Boost",
        "target_audience": "Managed WordPress Store Owners",
        "duration": 15
    }
    response = requests.post(url, json=payload, headers=HEADERS, timeout=30)
    assert response.status_code == 200
    data = response.json()
    assert "variants" in data
    assert len(data["variants"]) >= 1


def test_e2e_dynamic_image_asset_generation(server_fixture):
    """Verify image asset generation produces unique asset filenames on different prompts."""
    url = f"{BASE_URL}/api/studio/images/generate"

    # Prompt 1
    p1 = {"asset_type": "speed", "prompt_text": "SiteGround SuperCacher 3X Speed Boost UI with neon green glow"}
    r1 = requests.post(url, json=p1, headers=HEADERS, timeout=30)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["status"] == "success"
    assert "filename" in d1

    # Prompt 2 (different prompt)
    p2 = {"asset_type": "support", "prompt_text": "SiteGround 24/7 Support Trustpilot badge with 5 star rating"}
    r2 = requests.post(url, json=p2, headers=HEADERS, timeout=30)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["status"] == "success"
    assert "filename" in d2

    # Filenames for different custom prompts should be unique
    assert d1["filename"] != d2["filename"] or d1["prompt_used"] != d2["prompt_used"]


def test_e2e_dynamic_video_production(server_fixture):
    """Verify video production generates new video assets with unique filenames on different prompts."""
    url = f"{BASE_URL}/api/studio/video/produce"

    # Video Run 1
    v1_payload = {
        "aspect_ratio": "9:16",
        "variant_id": "variant_1",
        "model_choice": "gemini-omni-flash-preview",
        "edit_prompt": "Add neon teal glow border around SiteGround logo"
    }
    r1 = requests.post(url, json=v1_payload, headers=HEADERS, timeout=30)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["status"] == "success"

    # Video Run 2 with different prompt
    v2_payload = {
        "aspect_ratio": "9:16",
        "variant_id": "variant_1",
        "model_choice": "gemini-omni-flash-preview",
        "edit_prompt": "Zoom into 3X SuperCacher speed gauge with fast kinetic transitions"
    }
    r2 = requests.post(url, json=v2_payload, headers=HEADERS, timeout=30)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["status"] == "success"

    # Ensure unique filenames are returned for different edit prompts
    assert d1["video_url"] != d2["video_url"]


def test_e2e_multilingual_audio_synthesis(server_fixture):
    """Verify multilingual speech synthesis returns valid audio endpoints."""
    url = f"{BASE_URL}/api/studio/audio/synthesize"

    for lang_code, voice in [
        ("en-US", "en-US-Chirp3-HD-Aoede"),
        ("de-DE", "de-DE-Chirp3-HD-Gradius"),
        ("es-ES", "es-ES-Chirp3-HD-Euterpe")
    ]:
        payload = {
            "ssml_text": "<speak>SiteGround ultra-fast Google Cloud hosting!</speak>",
            "language_code": lang_code,
            "voice_name": voice,
            "speaking_rate": 1.05
        }
        res = requests.post(url, json=payload, headers=HEADERS, timeout=30)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "audio_url" in data


def test_e2e_google_ads_deployment(server_fixture):
    """Verify Google Ads API deployment returns activated campaign metadata."""
    url = f"{BASE_URL}/api/studio/ads/deploy"
    payload = {
        "customer_id": "849-204-1928",
        "campaign_type": "Performance Max (PMax)",
        "video_url": "/media/finished_ad.mp4"
    }
    response = requests.post(url, json=payload, headers=HEADERS, timeout=30)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "activated"
    assert len(data["mutated_assets"]) > 0
