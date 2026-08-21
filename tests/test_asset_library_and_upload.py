import pytest
import io
import os
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_upload_and_list_image_asset():
    # 1. Upload a test image asset
    img_bytes = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
    files = {"file": ("banner_sample.png", img_bytes, "image/png")}
    data = {"project_id": "proj_wp_speed", "title": "Summer WordPress Promo Banner"}

    res = client.post("/api/studio/assets/upload", files=files, data=data)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["status"] == "success"
    assert res_data["asset_type"] == "image"
    assert "banner_sample" in res_data["file_url"]
    asset_id = res_data["asset"]["id"]

    # 2. Upload a test audio asset
    audio_bytes = io.BytesIO(b"ID3\x03\x00\x00\x00\x00\x00#TIT2\x00\x00\x00\x13\x00\x00\x00\x00Test Voiceover Track")
    files_aud = {"file": ("voiceover_promo.mp3", audio_bytes, "audio/mpeg")}
    res_aud = client.post("/api/studio/assets/upload", files=files_aud, data={"project_id": "proj_wp_speed", "title": "German Voiceover Hook"})
    assert res_aud.status_code == 200
    assert res_aud.json()["asset_type"] == "audio"

    # 3. Retrieve assets library
    list_res = client.get("/api/studio/assets?project_id=proj_wp_speed")
    assert list_res.status_code == 200
    lib_data = list_res.json()
    assert lib_data["status"] == "success"
    assert len(lib_data["assets"]["images"]) >= 1
    assert len(lib_data["assets"]["audios"]) >= 1

    # 4. Delete asset
    del_res = client.delete(f"/api/studio/assets/{asset_id}?project_id=proj_wp_speed")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"
