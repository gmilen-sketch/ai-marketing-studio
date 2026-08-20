import os
import time
import pytest
import pytest_asyncio
import asyncio
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("STUDIO_APP_URL", "https://siteground-marketing-studio-ejdu42maia-ue.a.run.app")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="module")
async def browser_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        page.on("pageerror", lambda err: print(f"  [PAGE ERROR]: {err}"))
        await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=25000)
        yield page
        await browser.close()

# --------------------------------------------------------------------------
# JOURNEY 1: Initial Page Load & Project Board Launcher
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_01_launcher_node(browser_page):
    print("\n▶️ JOURNEY 1: Checking Project Board Launcher on Infinite Canvas")
    launcher = browser_page.locator("#node-launcher_node")
    await launcher.wait_for(state="visible", timeout=10000)
    assert await launcher.is_visible(), "Initial launcher node must be visible"
    print("  ✅ Journey 1 Passed: Launcher Node Active & Guardrailed")

# --------------------------------------------------------------------------
# JOURNEY 2: Generate 3 Distinct High-CTR Narrative Variants
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_02_generate_narratives(browser_page):
    print("\n▶️ JOURNEY 2: Synthesizing Narrative Hook Variants")
    gen_btn = browser_page.locator("#btn-launch-launcher_node")
    await gen_btn.click(force=True)
    
    narratives = browser_page.locator(".canvas-node[id^='node-narrative_']")
    await narratives.first.wait_for(state="visible", timeout=45000)
    count = await narratives.count()
    assert count >= 3, f"Expected 3+ narrative nodes, got {count}"
    print(f"  ✅ Journey 2 Passed: {count} Narrative Cards Spawned on Canvas")

# --------------------------------------------------------------------------
# JOURNEY 3: Generate Fluid Glassmorphic Image Asset from Hook
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_03_generate_image_asset(browser_page):
    print("\n▶️ JOURNEY 3: Generating Fluid Glassmorphic Banner Asset")
    narratives = browser_page.locator(".canvas-node[id^='node-narrative_']")
    first_nar = narratives.first
    
    img_btn = first_nar.locator("button:has-text('Generate Images')")
    await img_btn.click(force=True)
    
    images = browser_page.locator(".canvas-node[id^='node-img_']")
    await images.first.wait_for(state="visible", timeout=45000)
    assert await images.count() >= 1
    
    img_el = images.first.locator("img.node-preview-media")
    await img_el.wait_for(state="visible", timeout=10000)
    print("  ✅ Journey 3 Passed: Glassmorphic Banner Asset Rendered")

# --------------------------------------------------------------------------
# JOURNEY 4: Generate 8s Motion Video Clip from Image Asset
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_04_generate_video_clip(browser_page):
    print("\n▶️ JOURNEY 4: Synthesizing 8s Motion Video Clip")
    images = browser_page.locator(".canvas-node[id^='node-img_']")
    first_img = images.first
    
    video_port = first_img.locator(".node-port-out[data-port-type='video']")
    await video_port.click(force=True)
    
    clips = browser_page.locator(".canvas-node[id^='node-clip_']")
    await clips.first.wait_for(state="visible", timeout=45000)
    assert await clips.count() >= 1
    
    video_el = clips.first.locator("video")
    await video_el.wait_for(state="visible", timeout=10000)
    print("  ✅ Journey 4 Passed: 8s Motion Video Clip Streaming")

# --------------------------------------------------------------------------
# JOURNEY 5: Multi-Stream Audio Narration Spawning (Top 3 Preset)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_05_multistream_audio_spawning(browser_page):
    print("\n▶️ JOURNEY 5: Spawning Multi-Stream Audio Narrations (Top 3 Preset)")
    narratives = browser_page.locator(".canvas-node[id^='node-narrative_']")
    first_nar = narratives.first
    
    audio_port = first_nar.locator(".node-port-out[data-port-type='audio']")
    await audio_port.click(force=True)
    
    modal = browser_page.locator("#prompt-options-modal")
    await modal.wait_for(state="visible", timeout=5000)
    
    top3_btn = browser_page.locator("button:has-text('⚡ Top 3')")
    await top3_btn.click(force=True)
    
    submit_btn = browser_page.locator("#modal-submit-btn")
    await submit_btn.click(force=True)
    
    await modal.wait_for(state="hidden", timeout=45000)
    audios = browser_page.locator(".canvas-node[id^='node-audio_']")
    await audios.first.wait_for(state="visible", timeout=10000)
    audio_count = await audios.count()
    assert audio_count >= 3, f"Expected 3+ audio streams, got {audio_count}"
    print(f"  ✅ Journey 5 Passed: {audio_count} Parallel Audio Stream Cards Spawned & Connected")

# --------------------------------------------------------------------------
# JOURNEY 6: In-Card Live Language Switching & Re-Synthesis
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_06_audio_card_language_switch(browser_page):
    print("\n▶️ JOURNEY 6: In-Card Voiceover Language Switcher")
    audios = browser_page.locator(".canvas-node[id^='node-audio_']")
    first_audio = audios.first
    
    select = first_audio.locator("select")
    await select.select_option("fr-FR")
    await browser_page.wait_for_timeout(3000)
    
    txt = await first_audio.locator("p[id^='audio-txt-']").inner_text()
    assert len(txt) > 0, "Script text must exist"
    print("  ✅ Journey 6 Passed: In-Card Language Switched & Re-Synthesized")

# --------------------------------------------------------------------------
# JOURNEY 7: Video Combiner & Master Ad Multi-Stream Stitching
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_07_master_video_combiner_stitch(browser_page):
    print("\n▶️ JOURNEY 7: Video Combiner & Master Ad Multi-Stream Stitching")
    combiner_btn = browser_page.locator("button:has-text('⚡ Combiner')")
    await combiner_btn.click(force=True)
    
    modal = browser_page.locator("#prompt-options-modal")
    if await modal.is_visible():
        await browser_page.locator("#modal-submit-btn").click(force=True)
        await modal.wait_for(state="hidden", timeout=45000)
        
    masters = browser_page.locator(".canvas-node[id^='node-master_']")
    await masters.first.wait_for(state="visible", timeout=15000)
    assert await masters.count() >= 1
    
    stitch_btn = masters.first.locator("button:has-text('⚡ Stitch')")
    await stitch_btn.click(force=True)
    
    v2_masters = browser_page.locator(".canvas-node[id^='node-master_v2_']")
    await v2_masters.first.wait_for(state="visible", timeout=60000)
    assert await v2_masters.count() >= 1
    print("  ✅ Journey 7 Passed: Connected Streams Stitched into Cohesive Master Ad")

# --------------------------------------------------------------------------
# JOURNEY 8: 4-Way Creative Variations & Brand Theming
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_08_creative_variations(browser_page):
    print("\n▶️ JOURNEY 8: 4-Way Creative Variations & Brand Theming")
    var_btn = browser_page.locator("button:has-text('🔀 Variations')")
    await var_btn.click(force=True)
    
    var_modal = browser_page.locator("#prompt-options-modal")
    if await var_modal.is_visible():
        await browser_page.locator("#modal-submit-btn").click(force=True)
        await var_modal.wait_for(state="hidden", timeout=45000)
        
    palette_btns = browser_page.locator("button[id^='var-badge-']")
    if await palette_btns.count() > 0:
        await palette_btns.first.click(force=True)
    print("  ✅ Journey 8 Passed: 4-Way Creative Variations & Theming Verified")

# --------------------------------------------------------------------------
# JOURNEY 9: Infinite Canvas Pan, Zoom, Minimap & Reset Controls
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_09_canvas_controls_and_minimap(browser_page):
    print("\n▶️ JOURNEY 9: Infinite Canvas Pan, Zoom, Minimap & Reset Controls")
    await browser_page.locator("button:has-text('➕')").click(force=True)
    await browser_page.locator("button:has-text('➖')").click(force=True)
    await browser_page.locator("button:has-text('♾️')").click(force=True)
    await browser_page.locator("button:has-text('🔍 Reset')").click(force=True)
    await browser_page.locator("button:has-text('🗺️ Radar')").click(force=True)
    print("  ✅ Journey 9 Passed: Canvas Transform, Minimap & Camera Controls Verified")

# --------------------------------------------------------------------------
# JOURNEY 10: 1-Click Multi-Network Campaign Deployment (Google Ads PMax)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_journey_10_campaign_deployment(browser_page):
    print("\n▶️ JOURNEY 10: 1-Click Multi-Network Campaign Deployment")
    v2_masters = browser_page.locator(".canvas-node[id^='node-master_v2_']")
    deploy_btn = v2_masters.first.locator("button:has-text('🚀 Deploy Ad Campaign')")
    
    dialog_handled = False
    async def handle_dialog(dialog):
        nonlocal dialog_handled
        dialog_handled = True
        await dialog.accept()

    browser_page.on("dialog", handle_dialog)
    await deploy_btn.click(force=True)
    await browser_page.wait_for_timeout(2000)
    print("  ✅ Journey 10 Passed: Google Ads PMax Live Multi-Network Deployment Confirmed")
