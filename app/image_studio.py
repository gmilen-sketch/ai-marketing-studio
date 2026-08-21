import os
import json
import hashlib
import time
import re
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")

# Official SiteGround Brand Colors
SG_LOGO_GREEN = (150, 203, 76)      # Hex #96CB4C
SG_LOGO_BLACK = (51, 50, 48)        # Hex #333230
SG_GOLD_STARS = (255, 215, 0)       # Trustpilot Gold


def get_safe_font(size: int):
    """Safely resolves system truetype fonts across Linux/Cloud Run environments with graceful fallback."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def overlay_official_logo(img, x=60, y=45, logo_type="white", brand_name="CloudHost"):
    """Overlays official cloud hosting transparent PNG logo from brand-assets or dynamic brand typography."""
    logo_filename = "sg_logo_white.png" if logo_type == "white" else "sg_logo_black.png"
    logo_path = os.path.join(ASSETS_DIR, logo_filename)

    if os.path.exists(logo_path):
        try:
            logo_img = Image.open(logo_path).convert("RGBA")
            logo_img = logo_img.resize((230, 46), Image.Resampling.LANCZOS)
            img.paste(logo_img, (x, y), logo_img)
            return
        except Exception as e:
            print(f"Error pasting logo: {e}")

    draw = ImageDraw.Draw(img)
    f_logo = get_safe_font(38)
    draw.text((x, y), brand_name or "CloudHost", font=f_logo, fill=SG_LOGO_BLACK if logo_type == "black" else SG_LOGO_GREEN)


def draw_abcd_badge(draw, w, abcd_type="[A] ATTENTION & [B] BRANDING", is_white_bg=False):
    """Overlay badge signifying Google ABCD Framework alignment."""
    f_badge = get_safe_font(16)
    badge_w = 380
    rect_fill = (240, 244, 248) if is_white_bg else (30, 38, 52)
    draw.rounded_rectangle([w - badge_w - 60, 40, w - 60, 85], radius=10, fill=rect_fill, outline=SG_LOGO_GREEN, width=2)
    draw.text((w - badge_w - 40, 52), f"📐 GOOGLE ABCD: {abcd_type}", font=f_badge, fill=SG_LOGO_GREEN if not is_white_bg else SG_LOGO_BLACK)


def draw_wrapped_text(draw, text, font, x, y, max_width, fill, max_lines=2, line_spacing=6):
    """Draws text wrapped within max_width pixels. Truncates gracefully with ellipsis if max_lines exceeded."""
    if not text:
        return y
    words = str(text).split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines[-1] and (font.getbbox(lines[-1] + "...")[2] - font.getbbox(lines[-1] + "...")[0]) > max_width:
            lines[-1] = lines[-1][:-1].strip()
        if not lines[-1].endswith("..."):
            lines[-1] = lines[-1] + "..."

    curr_y = y
    line_height = (font.getbbox("Ay")[3] - font.getbbox("Ay")[1]) + line_spacing
    for line in lines:
        draw.text((x, curr_y), line, font=font, fill=fill)
        curr_y += line_height

    return curr_y


def get_gemini_campaign_copy(prompt_text: str) -> dict:
    """Uses Gemini 2.5 Flash to synthesize dynamic ad copy tailored specifically to the given prompt."""
    if not prompt_text or len(prompt_text.strip()) == 0 or os.environ.get("PYTEST_CURRENT_TEST"):
        return None

    try:
        from google import genai
        client = genai.Client()
        system_instruction = (
            "You are an expert Google Ads marketing copywriter for SiteGround Managed WordPress Hosting. "
            "Given a campaign narrative hook or prompt, return a JSON object with: "
            "\"badge\": (short uppercase badge 3-5 words), "
            "\"headline\": (catchy main headline 2-5 words), "
            "\"subtitle\": (engaging sub-headline 4-8 words), "
            "\"bullets\": (array of 3 benefit bullet points), "
            "\"cta\": (uppercase call to action button text 4-7 words), "
            "\"category\": ('staging', 'green', 'cdn', 'discount', 'speed', or 'clean_white')"
        )
        try:
            response = client.models.generate_content(
                model='gemini-3.7-flash',
                contents=f"Generate marketing ad banner copy for this prompt: '{prompt_text}'. Respect any color rules specified (such as 'no red' or 'white background').",
                config=dict(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
        except Exception:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=f"Generate marketing ad banner copy for this prompt: '{prompt_text}'. Respect any color rules specified (such as 'no red' or 'white background').",
                config=dict(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Gemini copy synthesis fallback: {e}")
        return None


def generate_campaign_asset(asset_type: str, prompt_text: str = "") -> str:
    """Generates authentic, multi-layered photographic SiteGround marketing banners matching real campaigns across siteground.com."""
    w, h = 1200, 800

    f_huge = get_safe_font(42)
    f_title = get_safe_font(26)
    f_sub = get_safe_font(20)
    f_badge = get_safe_font(16)

    prompt_clean = (prompt_text or "").strip()
    prompt_lower = prompt_clean.lower()

    # Detect explicit color & theme rules in prompt
    has_siteground_brand = any(k in prompt_lower for k in [
        "siteground", "branding", "official colours", "official colors", "brand colours", "brand colors"
    ])
    no_red = bool(re.search(r"\b(no|remove|without|avoid|strip|delete|zero|don't use|dont use|not|no)\b.*\bred", prompt_lower)) or has_siteground_brand

    # Explicit color requests in prompt
    explicit_blue = any(k in prompt_lower for k in ["blue background", "dark blue", "cobalt", "cyan", "sky blue", "azure", "blue", "navy"])
    explicit_green = any(k in prompt_lower for k in ["green background", "dark green", "emerald", "mint", "lime", "renewable", "sustainable", "eco"])
    explicit_white = any(k in prompt_lower for k in ["white background", "light background", "clean white", "white", "clean"])
    explicit_purple = any(k in prompt_lower for k in ["purple background", "violet background", "purple", "violet", "magenta"])
    explicit_amber = any(k in prompt_lower for k in ["amber background", "gold background", "orange background", "amber", "orange"])

    p_hash = hashlib.md5(((prompt_clean or asset_type) + str(time.time())).encode()).hexdigest()[:8]
    filename = f"asset_custom_{p_hash}.png"

    # Gemini 2.5 Flash Copy Synthesis
    copy = get_gemini_campaign_copy(prompt_clean)

    # Initial Category Selection from Copy / Keywords
    if explicit_blue:
        fallback_category = "staging"
    elif explicit_white:
        fallback_category = "clean_white"
    elif explicit_purple:
        fallback_category = "cdn"
    elif explicit_green:
        fallback_category = "green"
    elif any(k in prompt_lower for k in ["save", "80%", "discount", "savings", "promo", "cheap", "blitz", "price"]):
        fallback_category = "discount"
    elif any(k in prompt_lower for k in ["cdn", "edge", "global", "worldwide", "latency", "blazing"]):
        fallback_category = "cdn"
    else:
        fallback_category = "speed"

    if copy and isinstance(copy, dict):
        badge_text = copy.get("badge", "").upper()
        headline_text = copy.get("headline", "")
        subtitle_text = copy.get("subtitle", "")
        raw_bullets = copy.get("bullets", [])
        cta_text = copy.get("cta", "").upper()
        category = copy.get("category", fallback_category).lower()
    else:
        category = fallback_category
        badge_text = ""
        headline_text = ""
        subtitle_text = ""
        raw_bullets = []
        cta_text = ""

    # ABSOLUTE EXPLICIT COLOR OVERRIDES (Explicit prompt requests ALWAYS take top priority)
    if explicit_blue:
        category = "staging"
    elif explicit_white:
        category = "clean_white"
    elif explicit_purple:
        category = "cdn"
    elif explicit_green:
        category = "green"
    elif explicit_amber:
        category = "speed"
    elif no_red and category == "discount":
        category = "discount"  # Discount theme uses official green/slate zero red

    # Category Specific Fallback Overrides
    if category == "clean_white" or explicit_white:
        if not badge_text: badge_text = "🌿 OFFICIAL SITEGROUND MANAGED WORDPRESS"
        if not headline_text: headline_text = "Save 80% On Hosting"
        if not subtitle_text: subtitle_text = "Top-Rated Managed WordPress Hosting"
        if not raw_bullets: raw_bullets = ["3X Faster Page Loading Speeds", "Free 1-Click Site Migration", "30-Day Money-Back Guarantee"]
        if not cta_text: cta_text = "GET STARTED TODAY →"
    elif category == "staging":
        if not badge_text: badge_text = "🛠️ 1-CLICK STAGING & BACKUPS"
        if not headline_text: headline_text = "Deploy Updates Safely"
        if not subtitle_text: subtitle_text = "Google Cloud Staging Environment"
        if not raw_bullets: raw_bullets = ["Safe 1-Click Staging Environment", "Automated Daily Backups & Restore", "Zero Downtime WordPress Deployments"]
        if not cta_text: cta_text = "TEST STAGING FREE TODAY →"
    elif category == "green":
        if not badge_text: badge_text = "🌿 GOOGLE CLOUD GREEN POWER"
        if not headline_text: headline_text = "100% Green Energy Power"
        if not subtitle_text: subtitle_text = "Sustainable Google Cloud Infrastructure"
        if not raw_bullets: raw_bullets = ["100% Renewable Green Energy Servers", "Matches Brand Sustainability Goals", "Ultrafast NVMe Speed Engine"]
        if not cta_text: cta_text = "HOST GREEN TODAY →"
    elif category == "cdn":
        if not badge_text: badge_text = "⚡ BLAZING GLOBAL EDGE CDN"
        if not headline_text: headline_text = "Global Speed Acceleration"
        if not subtitle_text: subtitle_text = "Sub-Second Latency Across All Continents"
        if not raw_bullets: raw_bullets = ["Global Edge Network & Anycast DNS", "Sub-10ms Response Time Worldwide", "Automatic Dynamic Content Caching"]
        if not cta_text: cta_text = "ACCELERATE GLOBAL SPEED →"
    elif category == "discount":
        if not badge_text: badge_text = "⚡ LIMITED TIME 80% SAVINGS BLITZ"
        if not headline_text: headline_text = "Save 80% On Hosting"
        if not subtitle_text: subtitle_text = "Top-Rated Managed WordPress Hosting"
        if not raw_bullets: raw_bullets = ["80% Special Discount Promo Rate", "Free Site Migration & Daily Backups", "30-Day Money-Back Guarantee"]
        if not cta_text: cta_text = "CLAIM YOUR 80% DISCOUNT →"
    else:
        if not badge_text: badge_text = "⚡ 3X SUPERCACHER SPEED ENGINE"
        if not headline_text: headline_text = "3X Speed Acceleration"
        if not subtitle_text: subtitle_text = "NGINX Direct Delivery & Ultrafast PHP"
        if not raw_bullets: raw_bullets = ["500% Faster Page Loading Times", "Powered by Google Cloud Tech", "200% Higher Conversion Rates"]
        if not cta_text: cta_text = "BOOST YOUR SPEED NOW →"

    bullets = []
    for b in raw_bullets[:3]:
        cb = str(b).strip()
        if not cb.startswith("✔") and not cb.startswith("•"):
            cb = f"✔ {cb}"
        bullets.append(cb)

    # BASE CANVAS: DEEP OBSIDIAN NAVY
    if category == "clean_white" or explicit_white:
        base_bg = (250, 252, 255, 255)
        glow_primary = (150, 203, 76, 50)
        glow_secondary = (56, 189, 248, 40)
        card_acrylic = (255, 255, 255, 220)
        card_border = (150, 203, 76, 160)
        text_main = (15, 23, 42)
        text_sub = (71, 85, 105)
        accent_color = SG_LOGO_GREEN
    elif category == "staging" or explicit_blue:
        base_bg = (8, 16, 32, 255)
        glow_primary = (56, 189, 248, 100)
        glow_secondary = (30, 58, 138, 110)
        card_acrylic = (15, 28, 54, 180)
        card_border = (56, 189, 248, 120)
        text_main = (255, 255, 255)
        text_sub = (186, 230, 253)
        accent_color = (56, 189, 248)
    elif category == "cdn" or explicit_purple:
        base_bg = (14, 10, 28, 255)
        glow_primary = (168, 85, 247, 95)
        glow_secondary = (59, 130, 246, 90)
        card_acrylic = (26, 18, 50, 180)
        card_border = (168, 85, 247, 120)
        text_main = (255, 255, 255)
        text_sub = (233, 213, 255)
        accent_color = (168, 85, 247)
    else:
        # SiteGround Signature Obsidian & Emerald Glow
        base_bg = (8, 12, 22, 255)
        glow_primary = (150, 203, 76, 95)
        glow_secondary = (0, 168, 143, 90)
        card_acrylic = (15, 23, 42, 180)
        card_border = (150, 203, 76, 120)
        text_main = (255, 255, 255)
        text_sub = (203, 213, 225)
        accent_color = SG_LOGO_GREEN

    # 1. Base Layer + Ambient Mesh Lighting
    img = Image.new("RGBA", (w, h), base_bg)
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow_layer)

    # Volumetric Radial Gaussian Glows
    g_draw.ellipse([640, 60, 1180, 600], fill=glow_primary)
    g_draw.ellipse([460, 360, 1020, 920], fill=glow_secondary)
    g_draw.ellipse([100, 80, 520, 500], fill=(56, 189, 248, 40))

    glow_blurred = glow_layer.filter(ImageFilter.GaussianBlur(85))
    img = Image.alpha_composite(img, glow_blurred)

    draw = ImageDraw.Draw(img)

    # Subtle ambient background grid lines
    grid_opacity = 14 if not (category == "clean_white" or explicit_white) else 6
    for gx in range(0, w, 60):
        draw.line([(gx, 0), (gx, h)], fill=(255, 255, 255, grid_opacity))
    for gy in range(0, h, 60):
        draw.line([(0, gy), (w, gy)], fill=(255, 255, 255, grid_opacity))

    # 2. BRANDING LOGO & GOOGLE CLOUD PARTNER SEAL (TOP BAR)
    is_white_canvas = (category == "clean_white" or explicit_white)
    logo_style = "black" if is_white_canvas else "white"
    overlay_official_logo(img, x=60, y=42, logo_type=logo_style)
    
    # Top Partner Pill
    draw.rounded_rectangle([w - 360, 40, w - 60, 84], radius=22, fill=(15, 23, 42, 190) if not is_white_canvas else (240, 244, 248, 220), outline=accent_color, width=1)
    draw.text((w - 340, 52), "☁️ GOOGLE CLOUD PARTNER", font=get_safe_font(15), fill=accent_color)

    # 3. HERO CENTERPIECE: 3D HOLOGRAPHIC GLASS SPEED ORB & TELEMETRY WIDGETS (RIGHT HALF)
    orb_cx, orb_cy = 870, 340
    orb_r = 145

    # Glowing outer glass ring
    draw.ellipse([orb_cx - orb_r - 20, orb_cy - orb_r - 20, orb_cx + orb_r + 20, orb_cy + orb_r + 20], outline=accent_color, width=2)
    draw.ellipse([orb_cx - orb_r, orb_cy - orb_r, orb_cx + orb_r, orb_cy + orb_r], fill=card_acrylic, outline=card_border, width=2)

    # Arc telemetry ticks
    for angle in range(0, 300, 30):
        rad = math.radians(angle - 150)
        x1 = orb_cx + (orb_r - 18) * math.cos(rad)
        y1 = orb_cy + (orb_r - 18) * math.sin(rad)
        x2 = orb_cx + (orb_r - 6) * math.cos(rad)
        y2 = orb_cy + (orb_r - 6) * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=accent_color, width=2)

    # Big Holographic Metric Display
    metric_num = "0.4s" if "speed" in category or "speed" in prompt_lower else ("80%" if "discount" in category else "100%")
    metric_sub = "ULTRAFAST TTFB" if "speed" in category or "speed" in prompt_lower else ("SPECIAL PROMO" if "discount" in category else "PAGESPEED SCORE")
    
    f_num = get_safe_font(60)
    bbox_num = f_num.getbbox(metric_num)
    nw = bbox_num[2] - bbox_num[0]
    draw.text((orb_cx - (nw // 2), orb_cy - 45), metric_num, font=f_num, fill=(255, 255, 255))
    
    f_submetric = get_safe_font(14)
    bbox_sub = f_submetric.getbbox(metric_sub)
    sw = bbox_sub[2] - bbox_sub[0]
    draw.text((orb_cx - (sw // 2), orb_cy + 25), metric_sub, font=f_submetric, fill=accent_color)

    # Surrounding Floating Glass Chips
    chip_w, chip_h = 240, 48
    # Chip 1: Top Left of Orb
    draw.rounded_rectangle([630, 160, 630 + chip_w, 160 + chip_h], radius=12, fill=card_acrylic, outline=card_border, width=1)
    draw.text((645, 174), "🛡️ 99.99% Cloud Uptime", font=get_safe_font(14), fill=text_main)

    # Chip 2: Bottom Left of Orb
    draw.rounded_rectangle([630, 480, 630 + chip_w, 480 + chip_h], radius=12, fill=card_acrylic, outline=card_border, width=1)
    draw.text((645, 494), "⚡ NGINX Direct Delivery", font=get_safe_font(14), fill=accent_color)

    # Chip 3: Bottom Right of Orb
    draw.rounded_rectangle([890, 520, 890 + chip_w, 520 + chip_h], radius=12, fill=card_acrylic, outline=card_border, width=1)
    draw.text((905, 534), "★ ★ ★ ★ ★ 4.9 Trustpilot", font=get_safe_font(14), fill=SG_GOLD_STARS)

    # Chip 4: Top Right of Orb
    draw.rounded_rectangle([920, 140, 920 + chip_w, 140 + chip_h], radius=12, fill=card_acrylic, outline=card_border, width=1)
    draw.text((935, 154), "🌱 100% Renewable Match", font=get_safe_font(14), fill=SG_LOGO_GREEN)

    # 4. EDITORIAL CONVERSION FUNNEL (LEFT HALF - NO HEAVY BOXES)
    # Floating Category Badge Pill
    draw.rounded_rectangle([60, 125, 440, 162], radius=18, fill=(15, 23, 42, 190) if not is_white_canvas else (240, 244, 248, 220), outline=accent_color, width=1)
    draw.text((78, 136), f"✨ {badge_text or 'OFFICIAL MANAGED HOSTING'}", font=get_safe_font(13), fill=accent_color)

    # Massive Bold Punchy Headline
    f_head = get_safe_font(38)
    head_y = draw_wrapped_text(draw, headline_text or "Accelerate Your Site To 0.4s", font=f_head, x=60, y=180, max_width=520, fill=text_main, max_lines=2, line_spacing=6)

    # Subtitle
    f_subhead = get_safe_font(18)
    sub_y = draw_wrapped_text(draw, subtitle_text or "Experience 3X faster load speeds on Google Cloud infrastructure.", font=f_subhead, x=60, y=head_y + 8, max_width=520, fill=text_sub, max_lines=2)

    # Floating Benefit Checklist
    chk_y = sub_y + 18
    for bullet in bullets[:3]:
        clean_bullet = bullet.replace("✔", "").strip()
        draw.ellipse([62, chk_y + 4, 78, chk_y + 20], fill=accent_color)
        draw.text((66, chk_y + 4), "✓", font=get_safe_font(12), fill=(10, 20, 30))
        draw.text((90, chk_y + 2), clean_bullet, font=get_safe_font(16), fill=text_main)
        chk_y += 32

    # Promo Rate Pill
    draw.text((60, 480), "SPECIAL PROMO RATE:", font=get_safe_font(13), fill=text_sub)
    draw.text((60, 502), "$2.99/mo", font=get_safe_font(42), fill=accent_color)
    draw.rounded_rectangle([270, 508, 380, 542], radius=10, fill=(255, 96, 0))
    draw.text((285, 518), "SAVE 83%", font=get_safe_font(14), fill=(255, 255, 255))

    # Floating High-Contrast CTA Pill Button
    draw.rounded_rectangle([60, 565, 480, 625], radius=30, fill=accent_color, outline=(255, 255, 255, 200), width=2)
    cta_display = (cta_text or "BOOST YOUR SPEED NOW →").upper()
    f_cta = get_safe_font(18)
    draw_wrapped_text(draw, cta_display, font=f_cta, x=95, y=583, max_width=370, fill=(10, 20, 30) if not is_white_canvas else (255, 255, 255), max_lines=1)

    # 5. FOOTER SUBTLE FROSTED PROMPT METADATA BAR
    if prompt_clean:
        draw.rounded_rectangle([60, 680, 1140, 750], radius=14, fill=(15, 23, 42, 180) if not is_white_canvas else (240, 244, 248, 220), outline=card_border, width=1)
        draw.text((80, 692), "🤖 GEMINI OMNI HIGH-ABCD CREATIVE ENGINE:", font=get_safe_font(12), fill=accent_color)
        draw_wrapped_text(draw, f"\"{prompt_clean}\"", font=get_safe_font(15), x=80, y=714, max_width=1000, fill=text_main, max_lines=1)

    # Save to disk
    target_path = os.path.join(PROJECT_DIR, filename)
    img.save(target_path)

    media_dir = os.path.join(PROJECT_DIR, "media")
    os.makedirs(media_dir, exist_ok=True)
    media_target = os.path.join(media_dir, filename)
    img.save(media_target)

    slide_path = os.path.join(PROJECT_DIR, "slide.png")
    img.save(slide_path)

    return filename


def inpaint_campaign_asset(base_image_name: str, mask_bbox: list, inpaint_prompt: str) -> str:
    """Applies localized pixel inpainting/edit to an image asset within a bounding box."""
    import hashlib, time, shutil
    
    clean_name = os.path.basename(base_image_name.split("?")[0])
    src_path = os.path.join(PROJECT_DIR, "media", clean_name)
    if not os.path.exists(src_path):
        src_path = os.path.join(PROJECT_DIR, clean_name)
    if not os.path.exists(src_path):
        src_path = os.path.join(PROJECT_DIR, "media", "asset_supercacher_speed.png")

    try:
        base_img = Image.open(src_path).convert("RGBA")
    except Exception:
        base_img = Image.new("RGBA", (1200, 750), (15, 23, 42))

    w, h = base_img.size
    draw = ImageDraw.Draw(base_img)

    # Resolve bounding box [x0, y0, x1, y1] with sensible defaults
    if mask_bbox and len(mask_bbox) == 4:
        x0, y0, x1, y1 = mask_bbox
    else:
        # Default top-right badge area
        x0, y0, x1, y1 = int(w * 0.55), int(h * 0.18), int(w * 0.95), int(h * 0.78)

    # Inpainting style selection based on inpaint_prompt keywords
    prompt_lower = inpaint_prompt.lower()
    if "blue" in prompt_lower:
        box_bg = (30, 58, 138, 245)
        accent_col = (59, 130, 246)
    elif "gold" in prompt_lower or "yellow" in prompt_lower:
        box_bg = (202, 138, 4, 245)
        accent_col = (255, 215, 0)
    elif "orange" in prompt_lower or "discount" in prompt_lower:
        box_bg = (234, 88, 12, 245)
        accent_col = (255, 94, 19)
    else:
        box_bg = (16, 185, 129, 245)
        accent_col = SG_LOGO_GREEN

    # Draw refined inpainting patch
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=box_bg, outline=accent_col, width=3)
    
    f_title = get_safe_font(28)
    f_sub = get_safe_font(20)
    f_badge = get_safe_font(15)

    draw.text((x0 + 20, y0 + 20), "✨ INPAINTED REGION", font=f_badge, fill=accent_col)
    draw_wrapped_text(draw, inpaint_prompt.upper(), font=f_title, x=x0 + 20, y=y0 + 55, max_width=(x1 - x0 - 40), fill=(255, 255, 255), max_lines=2)
    draw_wrapped_text(draw, "SiteGround Verified Brand Asset", font=f_sub, x=x0 + 20, y=y1 - 45, max_width=(x1 - x0 - 40), fill=accent_col, max_lines=1)

    # Save versioned inpaint result
    out_hash = hashlib.md5((inpaint_prompt + str(time.time())).encode()).hexdigest()[:8]
    out_filename = f"asset_inpaint_{out_hash}.png"
    
    target_path = os.path.join(PROJECT_DIR, out_filename)
    base_img.save(target_path)

    media_dir = os.path.join(PROJECT_DIR, "media")
    os.makedirs(media_dir, exist_ok=True)
    media_target = os.path.join(media_dir, out_filename)
    base_img.save(media_target)

    return out_filename


def generate_multi_format_batch(asset_type: str, prompt_text: str) -> dict:
    """Synthesizes an asset and exports it formatted across all 5 standard marketing ratios."""
    base_filename = generate_campaign_asset(asset_type, prompt_text)
    src_path = os.path.join(PROJECT_DIR, "media", base_filename)
    if not os.path.exists(src_path):
        src_path = os.path.join(PROJECT_DIR, base_filename)

    base_img = Image.open(src_path).convert("RGBA")
    media_dir = os.path.join(PROJECT_DIR, "media")
    os.makedirs(media_dir, exist_ok=True)

    formats = {
        "blog_hero": {"size": (1920, 1080), "label": "Blog Hero (16:9)", "ratio": "16:9"},
        "og_meta": {"size": (1200, 628), "label": "OG Meta / Social Feed (1.91:1)", "ratio": "1.91:1"},
        "instagram_square": {"size": (1080, 1080), "label": "Instagram / LinkedIn Post (1:1)", "ratio": "1:1"},
        "linkedin_banner": {"size": (1584, 396), "label": "LinkedIn Profile Banner (4:1)", "ratio": "4:1"},
        "story_vertical": {"size": (1080, 1920), "label": "Story / Shorts / TikTok (9:16)", "ratio": "9:16"}
    }

    results = {}
    base_stem = os.path.splitext(base_filename)[0]

    for fmt_key, fmt_info in formats.items():
        tw, th = fmt_info["size"]
        # High quality fit and crop
        fitted = Image.new("RGBA", (tw, th), (8, 12, 22))
        
        # Scale preserving aspect ratio with crop
        scale = max(tw / base_img.width, th / base_img.height)
        new_w = int(base_img.width * scale)
        new_h = int(base_img.height * scale)
        resized_base = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        offset_x = (tw - new_w) // 2
        offset_y = (th - new_h) // 2
        fitted.paste(resized_base, (offset_x, offset_y), resized_base)

        fmt_filename = f"{base_stem}_{fmt_key}.png"
        fmt_target = os.path.join(media_dir, fmt_filename)
        fitted.save(fmt_target)

        results[fmt_key] = {
            "format": fmt_key,
            "label": fmt_info["label"],
            "ratio": fmt_info["ratio"],
            "dimensions": f"{tw}x{th}",
            "filename": fmt_filename,
            "url": f"/media/{fmt_filename}"
        }

    return {
        "status": "success",
        "base_filename": base_filename,
        "base_url": f"/media/{base_filename}",
        "prompt": prompt_text,
        "formats": results
    }


def upscale_campaign_asset(image_name: str, scale_factor: int = 2) -> dict:
    """Upscales an image asset by 2X or 4X with high-fidelity detail sharpening."""
    import hashlib, time
    from PIL import ImageEnhance, ImageFilter

    clean_name = os.path.basename(image_name.split("?")[0])
    src_path = os.path.join(PROJECT_DIR, "media", clean_name)
    if not os.path.exists(src_path):
        src_path = os.path.join(PROJECT_DIR, clean_name)
    if not os.path.exists(src_path):
        src_path = os.path.join(PROJECT_DIR, "media", "asset_supercacher_speed.png")

    try:
        base_img = Image.open(src_path).convert("RGBA")
    except Exception:
        base_img = Image.new("RGBA", (1200, 750), (15, 23, 42))

    orig_w, orig_h = base_img.size
    new_w = orig_w * scale_factor
    new_h = orig_h * scale_factor

    # High-quality Lanczos upscale + clarity/sharpness enhancement
    upscaled = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Sharpness(upscaled)
    upscaled = enhancer.enhance(1.35)
    
    contrast_enhancer = ImageEnhance.Contrast(upscaled)
    upscaled = contrast_enhancer.enhance(1.08)

    draw = ImageDraw.Draw(upscaled)
    f_badge = get_safe_font(int(18 * (new_w / 1200.0)))
    badge_txt = f"🔍 4K ULTRA-HD ({scale_factor}X UPSCALE)"
    draw.rounded_rectangle([new_w - 380, 25, new_w - 40, 75], radius=10, fill=(3, 7, 18, 220), outline=SG_LOGO_GREEN, width=2)
    draw.text((new_w - 360, 38), badge_txt, font=f_badge, fill=SG_LOGO_GREEN)

    out_hash = hashlib.md5((clean_name + str(time.time())).encode()).hexdigest()[:8]
    out_filename = f"asset_upscaled_{scale_factor}x_{out_hash}.png"

    media_dir = os.path.join(PROJECT_DIR, "media")
    os.makedirs(media_dir, exist_ok=True)
    media_target = os.path.join(media_dir, out_filename)
    upscaled.save(media_target)

    return {
        "status": "success",
        "scale_factor": f"{scale_factor}X",
        "resolution": f"{new_w}x{new_h}",
        "filename": out_filename,
        "image_url": f"/media/{out_filename}"
    }


def generate_image_variations(image_name: str, prompt_text: str = "") -> dict:
    """Generates 4 distinct thematic and stylistic variations of a campaign asset."""
    palettes = [
        {"name": "Signature Brand Green", "prompt": f"{prompt_text}. SiteGround brand signature emerald green with gold stars"},
        {"name": "Deep Cobalt Navy", "prompt": f"{prompt_text}. Deep cobalt navy blue background with cyan speed streaks"},
        {"name": "Emerald Speed Glow", "prompt": f"{prompt_text}. High tech neon green speed benchmark with glowing particles"},
        {"name": "Clean Editorial White", "prompt": f"{prompt_text}. Clean crisp white background with bold black typography"}
    ]

    import concurrent.futures

    def _generate_single_variation(item):
        idx, p = item
        v_filename = generate_campaign_asset("speed", p["prompt"])
        return {
            "variant_id": f"var_{idx+1}",
            "palette": p["name"],
            "prompt": p["prompt"],
            "filename": v_filename,
            "image_url": f"/media/{v_filename}"
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        variations = list(executor.map(_generate_single_variation, enumerate(palettes)))

    return {
        "status": "success",
        "count": len(variations),
        "variations": variations
    }


