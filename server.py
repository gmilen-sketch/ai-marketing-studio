import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from app.studio_api import router as studio_router

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="CloudHost AI Marketing Studio")
app.include_router(studio_router)

@app.get("/")
@app.get("/studio")
@app.get("/index.html")
async def serve_index():
    return FileResponse(os.path.join(PROJECT_DIR, "index.html"))

@app.get("/media/{filename}")
async def serve_media(filename: str):
    file_path = os.path.join(PROJECT_DIR, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(PROJECT_DIR, "media", filename)
    if not os.path.exists(file_path):
        if filename.startswith("asset_") or filename in ("slide.png", "sg_logo_badge.png", "gcp_cloud_badge.png"):
            from app.image_studio import generate_campaign_asset
            asset_type = "speed"
            if "error" in filename:
                asset_type = "error"
            elif "support" in filename or "trustpilot" in filename:
                asset_type = "support"
            elif "discount" in filename or "promo" in filename:
                asset_type = "discount"
            generate_campaign_asset(asset_type, "")
            file_path = os.path.join(PROJECT_DIR, filename)
            if not os.path.exists(file_path):
                file_path = os.path.join(PROJECT_DIR, "media", filename)
        elif filename.endswith(".mp4"):
            try:
                from app.video_renderer import render_marketing_video
                render_marketing_video(variant_id="variant_1", aspect_ratio="16:9", target_path=file_path)
            except Exception as e:
                print(f"Fallback video rendering: {e}")
        elif filename.endswith(".mp3"):
            try:
                from gtts import gTTS
                tts = gTTS(text="SiteGround Ultra-Fast Managed WordPress Hosting with Google Cloud Infrastructure.", lang="en")
                tts.save(file_path)
            except Exception as e:
                print(f"Fallback audio rendering: {e}")

    if os.path.exists(file_path):
        media_type = "video/mp4" if filename.endswith(".mp4") else ("audio/mpeg" if filename.endswith(".mp3") else "image/png")
        return FileResponse(
            file_path,
            media_type=media_type,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/uploads/{filename}")
async def serve_upload(filename: str):
    upload_path = os.path.join(PROJECT_DIR, "uploads", filename)
    if os.path.exists(upload_path):
        media_type = "image/png" if filename.endswith(".png") else ("image/jpeg" if filename.endswith((".jpg", ".jpeg")) else "application/octet-stream")
        return FileResponse(
            upload_path,
            media_type=media_type,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    raise HTTPException(status_code=404, detail="Uploaded asset not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
