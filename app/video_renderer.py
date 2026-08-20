import math
import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_fonts(w, h):
    scale = w / 1080.0
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    font_file = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_file = fp
            break

    if font_file:
        try:
            return {
                "title": ImageFont.truetype(font_file, int(46 * scale)),
                "header": ImageFont.truetype(font_file, int(36 * scale)),
                "sub": ImageFont.truetype(font_file, int(26 * scale)),
                "badge": ImageFont.truetype(font_file, int(22 * scale)),
                "large": ImageFont.truetype(font_file, int(52 * scale)),
                "huge": ImageFont.truetype(font_file, int(64 * scale)),
            }
        except Exception as e:
            print(f"Error loading truetype font {font_file}: {e}")

    def_font = ImageFont.load_default()
    return {
        "title": def_font, "header": def_font, "sub": def_font,
        "badge": def_font, "large": def_font, "huge": def_font,
    }


def draw_siteground_header(draw, w, h, fonts, tag_text="MANAGED CLOUD"):
    scale = w / 1080.0
    pad_x = int(50 * scale)
    pad_y = int(50 * scale)

    # Official SiteGround Brand Colors: #96CB4C Green, #333230 Black
    SG_GREEN = (150, 203, 76)
    SG_BLACK = (51, 50, 48)

    # Left Logo Box
    box1_w = int(320 * scale)
    box1_h = int(70 * scale)
    draw.rounded_rectangle(
        [pad_x, pad_y, pad_x + box1_w, pad_y + box1_h],
        radius=int(16 * scale),
        fill=SG_GREEN,
        outline=(180, 230, 110),
        width=int(2 * scale),
    )
    draw.text(
        (pad_x + int(20 * scale), pad_y + int(12 * scale)),
        "SiteGround",
        font=fonts["title"],
        fill=SG_BLACK,
    )

    # Right Tag Box
    box2_w = int(260 * scale)
    box2_h = int(70 * scale)
    right_x = w - pad_x - box2_w
    draw.rounded_rectangle(
        [right_x, pad_y, right_x + box2_w, pad_y + box2_h],
        radius=int(16 * scale),
        fill=(255, 96, 0),
        outline=(255, 140, 50),
        width=int(2 * scale),
    )
    draw.text(
        (right_x + int(18 * scale), pad_y + int(18 * scale)),
        tag_text,
        font=fonts["badge"],
        fill=(255, 255, 255),
    )


def render_marketing_video(
    variant_id: str,
    aspect_ratio: str,
    target_path: str,
    edit_prompt: str = "",
    audio_path: str = None,
    duration_sec: int = 15,
):
    """Renders pixel-perfect, highly compelling SiteGround branded marketing video frames and encodes to H.264 MP4."""
    dimensions = {
        "16:9": (1920, 1080),
        "9:16": (1080, 1920),
        "1:1": (1080, 1080),
        "4:5": (1080, 1350),
    }
    W, H = dimensions.get(aspect_ratio, (1080, 1920))
    fps = 4
    total_frames = int(fps * duration_sec)

    import hashlib, re, time
    prompt_tag = hashlib.md5(edit_prompt.encode()).hexdigest()[:6] if edit_prompt else "def"
    temp_dir = os.path.join(PROJECT_DIR, f"temp_frames_{variant_id}_{aspect_ratio.replace(':', '_')}_{prompt_tag}")
    os.makedirs(temp_dir, exist_ok=True)

    fonts = get_fonts(W, H)
    scale = W / 1080.0

    # Parse attached image asset from edit_prompt
    attached_img = None
    attached_filename = None
    asset_match = re.search(r'(asset_[a-zA-Z0-9_]+\.png)', edit_prompt)
    if not asset_match:
        asset_match = re.search(r'([a-zA-Z0-9_]+\.png)', edit_prompt)

    if asset_match:
        fname = asset_match.group(1)
        fpath = os.path.join(PROJECT_DIR, fname)
        if os.path.exists(fpath):
            try:
                raw_img = Image.open(fpath).convert("RGBA")
                attached_filename = fname
                # Scale attached image
                max_w = int((W - 2 * int(60 * scale)) * 0.75)
                max_h = int((H * 0.72) * 0.35)
                raw_img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                attached_img = raw_img
            except Exception as e:
                print(f"Failed loading attached asset {fpath}: {e}")

    # Dynamic styling from edit_prompt
    prompt_lower = edit_prompt.lower()
    minimal_mode = "minimal" in prompt_lower or "no boxes" in prompt_lower
    
    # Base Colors
    BG_DARK = (11, 15, 25)
    SG_TEAL = (0, 168, 143)
    SG_ORANGE = (255, 96, 0)
    SG_GREEN = (150, 203, 76)
    CARD_BG = (18, 26, 42)
    CARD_BORDER = (45, 60, 85)
    TEXT_WHITE = (255, 255, 255)
    TEXT_MUTED = (160, 174, 192)
    GREEN_ACCENT = (16, 185, 129)
    RED_ACCENT = (239, 68, 68)
    YELLOW_ACCENT = (255, 215, 0)
    PURPLE_ACCENT = (168, 85, 247)
    BLUE_ACCENT = (59, 130, 246)

    if "red" in prompt_lower or "warning" in prompt_lower or "error" in prompt_lower:
        MAIN_ACCENT = RED_ACCENT
    elif "yellow" in prompt_lower or "gold" in prompt_lower or "promo" in prompt_lower:
        MAIN_ACCENT = YELLOW_ACCENT
    elif "teal" in prompt_lower or "cyan" in prompt_lower or "neon" in prompt_lower:
        MAIN_ACCENT = SG_TEAL
    elif "green" in prompt_lower or "speed" in prompt_lower:
        MAIN_ACCENT = SG_GREEN
    elif "purple" in prompt_lower or "violet" in prompt_lower:
        MAIN_ACCENT = PURPLE_ACCENT
    elif "blue" in prompt_lower:
        MAIN_ACCENT = BLUE_ACCENT
    else:
        MAIN_ACCENT = SG_ORANGE

    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)
        img = Image.new("RGB", (W, H), BG_DARK)
        draw = ImageDraw.Draw(img)

        # Ambient background glow circles with dynamic colors
        glow_x = int(W * 0.5 + math.sin(t * 1.5) * 100 * scale)
        glow_y = int(H * 0.4 + math.cos(t * 1.5) * 80 * scale)
        glow_fill = (MAIN_ACCENT[0] // 4, MAIN_ACCENT[1] // 4, MAIN_ACCENT[2] // 4)
        draw.ellipse(
            [glow_x - int(250 * scale), glow_y - int(250 * scale), glow_x + int(250 * scale), glow_y + int(250 * scale)],
            fill=glow_fill,
        )

        draw_siteground_header(draw, W, H, fonts, tag_text="MANAGED CLOUD")

        # Main Glassmorphism Card
        card_margin_x = int(60 * scale)
        card_w = W - 2 * card_margin_x
        card_y = int(H * 0.16)
        card_h = int(H * 0.72)

        if not minimal_mode:
            draw.rounded_rectangle(
                [card_margin_x, card_y, card_margin_x + card_w, card_y + card_h],
                radius=int(28 * scale),
                fill=CARD_BG,
                outline=MAIN_ACCENT if edit_prompt else CARD_BORDER,
                width=int(3 * scale),
            )

        # Prompt Edit Active Pill
        if edit_prompt:
            pill_text = f"✨ PROMPT EDIT: {edit_prompt[:42]}..." if len(edit_prompt) > 42 else f"✨ PROMPT EDIT: {edit_prompt}"
            draw.rounded_rectangle(
                [card_margin_x + int(20 * scale), card_y + int(12 * scale), card_margin_x + card_w - int(20 * scale), card_y + int(42 * scale)],
                radius=int(10 * scale),
                fill=MAIN_ACCENT,
            )
            draw.text((card_margin_x + int(35 * scale), card_y + int(16 * scale)), pill_text, font=fonts["badge"], fill=TEXT_WHITE)

        content_offset_y = int(45 * scale) if edit_prompt else 0

        # DYNAMIC SCENE & PROMPT CARD RENDERER
        # Handles any specific scene box (scene_1, scene_2, scene_3, etc.) or custom prompt
        if edit_prompt or attached_img or variant_id.startswith("scene_"):
            clean_prompt = re.sub(r'Overlay\s+asset_[a-zA-Z0-9_]+\.png', '', edit_prompt).strip()
            if not clean_prompt:
                clean_prompt = f"SiteGround Scene: {variant_id.replace('_', ' ').title()}"

            # Classify prompt theme & dynamic copy
            prompt_l = clean_prompt.lower()
            if "500" in prompt_l or "error" in prompt_l or "frustrated" in prompt_l or "crash" in prompt_l:
                scene_badge = "🚨 HOOK: SITE CRASH ALERT"
                headline_text = "500 SERVER ERROR!"
                cta_text = "FIX SITE DOWN IN 10 SECONDS"
                theme_accent = RED_ACCENT
            elif "google" in prompt_l or "cloud" in prompt_l or "server" in prompt_l or "rack" in prompt_l or "infrastructure" in prompt_l:
                scene_badge = "☁️ GOOGLE CLOUD INFRASTRUCTURE"
                headline_text = "ULTRA-FAST NVME SERVERS"
                cta_text = "POWERED BY GOOGLE CLOUD"
                theme_accent = BLUE_ACCENT
            elif "end-card" in prompt_l or "discount" in prompt_l or "promo" in prompt_l or "green" in prompt_l or "offer" in prompt_l or "80%" in prompt_l:
                scene_badge = "🎁 SPECIAL LIMITED OFFER"
                headline_text = "GET 80% OFF TODAY"
                cta_text = "CLAIM SITEGROUND DISCOUNT"
                theme_accent = SG_GREEN
            elif "speed" in prompt_l or "supercacher" in prompt_l or "fast" in prompt_l or "booster" in prompt_l:
                scene_badge = "⚡ 3X SUPERCACHER BOOST"
                headline_text = "100/100 PAGESPEED SCORE"
                cta_text = "BOOST YOUR SITE SPEED"
                theme_accent = SG_TEAL
            elif "support" in prompt_l or "chat" in prompt_l or "24/7" in prompt_l or "trustpilot" in prompt_l:
                scene_badge = "💬 24/7 EXPERT SUPPORT"
                headline_text = "CONNECTED IN 7 SECONDS"
                cta_text = "TALK TO EXPERT SUPPORT"
                theme_accent = SG_ORANGE
            else:
                scene_badge = f"🎬 SCENE: {variant_id.upper()}"
                headline_text = "SITEGROUND MANAGED HOSTING"
                cta_text = "EXPLORE SITEGROUND HOSTING"
                theme_accent = SG_ORANGE

            # Top Badge Pill
            draw.rounded_rectangle(
                [card_margin_x + int(30 * scale), card_y + int(20 * scale), card_margin_x + card_w - int(30 * scale), card_y + int(65 * scale)],
                radius=int(14 * scale),
                fill=theme_accent,
            )
            draw.text((card_margin_x + int(45 * scale), card_y + int(28 * scale)), scene_badge, font=fonts["header"], fill=TEXT_WHITE)

            current_y = card_y + int(85 * scale)

            # Attached Image Asset Section
            if attached_img:
                img_w, img_h = attached_img.size
                img_x = card_margin_x + int((card_w - img_w) / 2)
                img_y = current_y + int(10 * scale)

                # Framing container
                draw.rounded_rectangle(
                    [img_x - int(8 * scale), img_y - int(8 * scale), img_x + img_w + int(8 * scale), img_y + img_h + int(8 * scale)],
                    radius=int(14 * scale),
                    fill=(15, 23, 38),
                    outline=theme_accent,
                    width=int(2 * scale),
                )
                img.paste(attached_img, (img_x, img_y), attached_img)

                current_y = img_y + img_h + int(20 * scale)

            # Headline Title
            draw.text((card_margin_x + int(30 * scale), current_y), headline_text, font=fonts["large"], fill=TEXT_WHITE)
            current_y += int(60 * scale)

            # Scene Prompt Description Box (Multi-line text box)
            desc_box_h = int(180 * scale)
            draw.rounded_rectangle(
                [card_margin_x + int(25 * scale), current_y, card_margin_x + card_w - int(25 * scale), current_y + desc_box_h],
                radius=int(16 * scale),
                fill=(24, 34, 52),
                outline=(50, 70, 95),
                width=int(2 * scale),
            )

            # Wrap text helper
            words = clean_prompt.split()
            lines = []
            curr_line = ""
            for w in words:
                test_line = f"{curr_line} {w}".strip()
                if len(test_line) > 34:
                    lines.append(curr_line)
                    curr_line = w
                else:
                    curr_line = test_line
            if curr_line:
                lines.append(curr_line)

            line_y = current_y + int(20 * scale)
            for line in lines[:4]:
                draw.text((card_margin_x + int(45 * scale), line_y), line, font=fonts["sub"], fill=(220, 230, 245))
                line_y += int(35 * scale)

            # Bottom CTA Button
            cta_y = card_y + card_h - int(110 * scale)
            draw.rounded_rectangle(
                [card_margin_x + int(30 * scale), cta_y, card_margin_x + card_w - int(30 * scale), cta_y + int(80 * scale)],
                radius=int(20 * scale),
                fill=theme_accent,
            )
            draw.text((card_margin_x + int(50 * scale), cta_y + int(20 * scale)), cta_text, font=fonts["title"], fill=TEXT_WHITE)

        elif "variant_2" in variant_id:
            # VARIANT 2: PRODUCT FEATURE & SITE TOOLS FOCUS
            if t < 5.0:
                # Scene 1: Site Tools Dashboard UI
                draw.text((card_margin_x + int(40 * scale), card_y + int(50 * scale) + content_offset_y), "SITEGROUND SITE TOOLS", font=fonts["sub"], fill=SG_TEAL)
                draw.text((card_margin_x + int(40 * scale), card_y + int(100 * scale) + content_offset_y), "1-Click Speed & Security", font=fonts["large"], fill=TEXT_WHITE)

                # Feature items box
                item_y = card_y + int(210 * scale) + content_offset_y
                features = [
                    ("✔ SuperCacher 3X Booster", "ENABLED", SG_TEAL),
                    ("✔ Free SSL Certificate", "INSTALLED", GREEN_ACCENT),
                    ("✔ Daily Automatic Backups", "PROTECTED", GREEN_ACCENT),
                    ("✔ 1-Click Staging Tool", "READY", SG_ORANGE),
                ]
                for idx, (title, status, col) in enumerate(features):
                    box_y = item_y + idx * int(75 * scale)
                    draw.rounded_rectangle(
                        [card_margin_x + int(40 * scale), box_y, card_margin_x + card_w - int(40 * scale), box_y + int(60 * scale)],
                        radius=int(14 * scale),
                        fill=(26, 36, 56),
                        outline=(50, 68, 95),
                        width=int(2 * scale),
                    )
                    draw.text((card_margin_x + int(60 * scale), box_y + int(14 * scale)), title, font=fonts["header"], fill=TEXT_WHITE)
                    draw.text((card_margin_x + card_w - int(200 * scale), box_y + int(16 * scale)), status, font=fonts["badge"], fill=col)

                # Kinetic Overlay Badge
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + card_h - int(130 * scale), card_margin_x + card_w - int(40 * scale), card_y + card_h - int(40 * scale)],
                    radius=int(20 * scale),
                    fill=MAIN_ACCENT,
                )
                draw.text((card_margin_x + int(80 * scale), card_y + card_h - int(105 * scale)), "1-CLICK SITE MANAGEMENT", font=fonts["title"], fill=TEXT_WHITE)

            else:
                # Scene 2: 24/7 Support & 5-Star Rating
                draw.text((card_margin_x + int(40 * scale), card_y + int(50 * scale) + content_offset_y), "24/7 EXPERT SUPPORT", font=fonts["sub"], fill=SG_ORANGE)
                draw.text((card_margin_x + int(40 * scale), card_y + int(100 * scale) + content_offset_y), "Connected in 7 Seconds!", font=fonts["large"], fill=TEXT_WHITE)

                # Chat Bubble Mockup
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + int(200 * scale) + content_offset_y, card_margin_x + card_w - int(40 * scale), card_y + int(360 * scale) + content_offset_y],
                    radius=int(20 * scale),
                    fill=(26, 42, 62),
                    outline=SG_TEAL,
                    width=int(2 * scale),
                )
                draw.text((card_margin_x + int(70 * scale), card_y + int(230 * scale) + content_offset_y), "💬 Senior WordPress Engineer:", font=fonts["badge"], fill=SG_TEAL)
                draw.text((card_margin_x + int(70 * scale), card_y + int(270 * scale) + content_offset_y), "\"Hello! Your speed optimization is live.", font=fonts["header"], fill=TEXT_WHITE)
                draw.text((card_margin_x + int(70 * scale), card_y + int(310 * scale) + content_offset_y), " PageSpeed score is now 100/100!\"", font=fonts["header"], fill=GREEN_ACCENT)

                # Star Rating Badge
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + int(400 * scale) + content_offset_y, card_margin_x + card_w - int(40 * scale), card_y + int(500 * scale) + content_offset_y],
                    radius=int(18 * scale),
                    fill=(40, 30, 20),
                    outline=SG_ORANGE,
                    width=int(2 * scale),
                )
                draw.text((card_margin_x + int(70 * scale), card_y + int(425 * scale) + content_offset_y), "★★★★★ 4.9/5 Trustpilot (3,000,000+ Sites)", font=fonts["header"], fill=(255, 215, 0))

                # CTA Button
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + card_h - int(130 * scale), card_margin_x + card_w - int(40 * scale), card_y + card_h - int(40 * scale)],
                    radius=int(20 * scale),
                    fill=MAIN_ACCENT,
                )
                draw.text((card_margin_x + int(80 * scale), card_y + card_h - int(105 * scale)), "TRY SITEGROUND RISK-FREE", font=fonts["title"], fill=TEXT_WHITE)

        elif "variant_3" in variant_id:
            # VARIANT 3: DEVELOPER FRICTION & UPTIME PROOF
            if t < 6.0:
                # Scene 1: 100/100 PageSpeed Gauge
                draw.text((card_margin_x + int(40 * scale), card_y + int(50 * scale) + content_offset_y), "GOOGLE CLOUD INFRASTRUCTURE", font=fonts["sub"], fill=GREEN_ACCENT)
                draw.text((card_margin_x + int(40 * scale), card_y + int(100 * scale) + content_offset_y), "100/100 PageSpeed Score", font=fonts["large"], fill=TEXT_WHITE)

                # Animated Progress Bar
                progress_pct = min(1.0, t / 4.0)
                gauge_w = int((card_w - int(80 * scale)) * progress_pct)
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + int(240 * scale) + content_offset_y, card_margin_x + card_w - int(40 * scale), card_y + int(320 * scale) + content_offset_y],
                    radius=int(20 * scale),
                    fill=(20, 35, 30),
                )
                if gauge_w > 20:
                    draw.rounded_rectangle(
                        [card_margin_x + int(40 * scale), card_y + int(240 * scale) + content_offset_y, card_margin_x + int(40 * scale) + gauge_w, card_y + int(320 * scale) + content_offset_y],
                        radius=int(20 * scale),
                        fill=GREEN_ACCENT,
                    )
                score_val = int(progress_pct * 100)
                draw.text((card_margin_x + int(70 * scale), card_y + int(260 * scale) + content_offset_y), f"Google PageSpeed Score: {score_val} / 100", font=fonts["header"], fill=TEXT_WHITE)

                # Uptime badge
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + int(380 * scale) + content_offset_y, card_margin_x + card_w - int(40 * scale), card_y + int(480 * scale) + content_offset_y],
                    radius=int(18 * scale),
                    fill=(20, 30, 50),
                    outline=SG_TEAL,
                    width=int(2 * scale),
                )
                draw.text((card_margin_x + int(70 * scale), card_y + int(415 * scale) + content_offset_y), "⚡ 99.99% Guaranteed Network Uptime", font=fonts["header"], fill=SG_TEAL)

                # Kinetic Overlay Badge
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + card_h - int(130 * scale), card_margin_x + card_w - int(40 * scale), card_y + card_h - int(40 * scale)],
                    radius=int(20 * scale),
                    fill=MAIN_ACCENT,
                )
                draw.text((card_margin_x + int(80 * scale), card_y + card_h - int(105 * scale)), "MAXIMUM SPEED & RELIABILITY", font=fonts["title"], fill=TEXT_WHITE)

            else:
                # Scene 2: Staging to Production & CTA
                draw.text((card_margin_x + int(40 * scale), card_y + int(50 * scale) + content_offset_y), "DEVELOPER WORKFLOW", font=fonts["sub"], fill=SG_TEAL)
                draw.text((card_margin_x + int(40 * scale), card_y + int(100 * scale) + content_offset_y), "1-Click Staging to Prod", font=fonts["large"], fill=TEXT_WHITE)

                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + int(220 * scale) + content_offset_y, card_margin_x + card_w - int(40 * scale), card_y + int(440 * scale) + content_offset_y],
                    radius=int(20 * scale),
                    fill=(20, 30, 45),
                    outline=SG_ORANGE,
                    width=int(2 * scale),
                )
                draw.text((card_margin_x + int(70 * scale), card_y + int(260 * scale) + content_offset_y), "🚀 Instant Staging Environment", font=fonts["header"], fill=TEXT_WHITE)
                draw.text((card_margin_x + int(70 * scale), card_y + int(310 * scale) + content_offset_y), "✔ Push updates safely without downtime", font=fonts["sub"], fill=GREEN_ACCENT)
                draw.text((card_margin_x + int(70 * scale), card_y + int(360 * scale) + content_offset_y), "✔ Git Integration & SSH Access", font=fonts["sub"], fill=SG_TEAL)

                # CTA Button
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + card_h - int(130 * scale), card_margin_x + card_w - int(40 * scale), card_y + card_h - int(40 * scale)],
                    radius=int(20 * scale),
                    fill=MAIN_ACCENT,
                )
                draw.text((card_margin_x + int(80 * scale), card_y + card_h - int(105 * scale)), "BUILD FASTER WITH SITEGROUND", font=fonts["title"], fill=TEXT_WHITE)

        else:
            # DEFAULT & SPEED PERFORMANCE PROMO (SiteGround 3X Speed Benchmark & Google Cloud)
            if t < 5.0:
                # Scene 1: 3X SuperCacher Speed Acceleration
                draw.text((card_margin_x + int(40 * scale), card_y + int(50 * scale) + content_offset_y), "SITEGROUND SUPERCACHER", font=fonts["sub"], fill=SG_TEAL)
                draw.text((card_margin_x + int(40 * scale), card_y + int(100 * scale) + content_offset_y), "3X Speed Boost Activated!", font=fonts["large"], fill=TEXT_WHITE)

                pulse = int(25 + 15 * math.sin(t * 6))
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + int(220 * scale) + content_offset_y, card_margin_x + card_w - int(40 * scale), card_y + int(420 * scale) + content_offset_y],
                    radius=int(20 * scale),
                    fill=(15, pulse, 35),
                    outline=SG_GREEN,
                    width=int(3 * scale),
                )
                draw.text((card_margin_x + int(70 * scale), card_y + int(260 * scale) + content_offset_y), "⚡ 0.4s Page Load Time", font=fonts["title"], fill=SG_GREEN)
                draw.text((card_margin_x + int(70 * scale), card_y + int(320 * scale) + content_offset_y), "100/100 Google PageSpeed Score", font=fonts["header"], fill=TEXT_WHITE)

                # Kinetic Subtitle
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + card_h - int(130 * scale), card_margin_x + card_w - int(40 * scale), card_y + card_h - int(40 * scale)],
                    radius=int(20 * scale),
                    fill=SG_GREEN,
                )
                draw.text((card_margin_x + int(80 * scale), card_y + card_h - int(105 * scale)), "BOOST SITE SPEED 3X", font=fonts["title"], fill=(15, 23, 42))

            elif t < 10.0:
                # Scene 2: Google Cloud Infrastructure Proof
                draw.text((card_margin_x + int(40 * scale), card_y + int(50 * scale) + content_offset_y), "GOOGLE CLOUD INFRASTRUCTURE", font=fonts["sub"], fill=SG_TEAL)
                draw.text((card_margin_x + int(40 * scale), card_y + int(100 * scale) + content_offset_y), "Ultra-Fast Premium Hosting", font=fonts["large"], fill=TEXT_WHITE)

                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + int(220 * scale) + content_offset_y, card_margin_x + card_w - int(40 * scale), card_y + int(420 * scale) + content_offset_y],
                    radius=int(20 * scale),
                    fill=(15, 30, 48),
                    outline=SG_TEAL,
                    width=int(3 * scale),
                )
                draw.text((card_margin_x + int(70 * scale), card_y + int(260 * scale) + content_offset_y), "☁️ 100% Renewable NVMe Cloud", font=fonts["header"], fill=TEXT_WHITE)
                draw.text((card_margin_x + int(70 * scale), card_y + int(320 * scale) + content_offset_y), "✔ Free CDN + Daily Backups + SSL", font=fonts["sub"], fill=GREEN_ACCENT)

                # Kinetic Subtitle
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + card_h - int(130 * scale), card_margin_x + card_w - int(40 * scale), card_y + card_h - int(40 * scale)],
                    radius=int(20 * scale),
                    fill=SG_TEAL,
                )
                draw.text((card_margin_x + int(80 * scale), card_y + card_h - int(105 * scale)), "TRY SITEGROUND TODAY", font=fonts["title"], fill=TEXT_WHITE)

            else:
                # Scene 3: High Converting 80% Offer CTA
                draw.text((card_margin_x + int(40 * scale), card_y + int(50 * scale) + content_offset_y), "SPECIAL PROMO RATE", font=fonts["sub"], fill=SG_ORANGE)
                draw.text((card_margin_x + int(40 * scale), card_y + int(100 * scale) + content_offset_y), "Save 80% on WordPress Hosting", font=fonts["large"], fill=TEXT_WHITE)

                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + int(220 * scale) + content_offset_y, card_margin_x + card_w - int(40 * scale), card_y + int(420 * scale) + content_offset_y],
                    radius=int(20 * scale),
                    fill=(45, 25, 10),
                    outline=SG_ORANGE,
                    width=int(3 * scale),
                )
                draw.text((card_margin_x + int(70 * scale), card_y + int(260 * scale) + content_offset_y), "🔥 UP TO 80% OFF TODAY", font=fonts["huge"], fill=(255, 215, 0))
                draw.text((card_margin_x + int(70 * scale), card_y + int(340 * scale) + content_offset_y), "Free SSL • Daily Backups • 24/7 Chat", font=fonts["header"], fill=TEXT_WHITE)

                # CTA Button
                draw.rounded_rectangle(
                    [card_margin_x + int(40 * scale), card_y + card_h - int(130 * scale), card_margin_x + card_w - int(40 * scale), card_y + card_h - int(40 * scale)],
                    radius=int(20 * scale),
                    fill=MAIN_ACCENT,
                )
                draw.text((card_margin_x + int(80 * scale), card_y + card_h - int(105 * scale)), "CLAIM 80% DISCOUNT NOW", font=fonts["title"], fill=TEXT_WHITE)

        frame_path = os.path.join(temp_dir, f"frame_{frame_idx:04d}.png")
        img.save(frame_path)

    # Resolve ffmpeg binary
    ffmpeg_bin = shutil.which("ffmpeg") or "/tmp/ffmpeg" or "ffmpeg"

    # Encode to MP4 using FFmpeg
    cmd = [
        ffmpeg_bin,
        "-y",
        "-framerate", str(fps),
        "-i", os.path.join(temp_dir, "frame_%04d.png"),
    ]

    fallback_audio = os.path.join(PROJECT_DIR, "fallback_voiceover.mp3")
    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-i", audio_path])
    elif os.path.exists(fallback_audio):
        cmd.extend(["-i", fallback_audio])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
    ])

    if (audio_path and os.path.exists(audio_path)) or os.path.exists(fallback_audio):
        cmd.extend(["-c:a", "aac", "-shortest"])

    cmd.append(target_path)

    try:
        subprocess.run(cmd, capture_output=True, check=True)
    finally:
        # Clean up temporary frames
        shutil.rmtree(temp_dir, ignore_errors=True)


def render_image_to_video_segment(
    image_path: str,
    target_path: str,
    duration_sec: int = 8,
    prompt_text: str = "",
    fps: int = 24
):
    """Renders a cinematic 8-second motion video segment from an input image asset with Ken Burns pan/zoom and SiteGround header overlay."""
    if not os.path.exists(image_path):
        image_path = os.path.join(PROJECT_DIR, "media", "asset_supercacher_speed.png")
        if not os.path.exists(image_path):
            image_path = os.path.join(PROJECT_DIR, "slide.png")

    try:
        source_img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening image for video segment: {e}")
        source_img = Image.new("RGBA", (1200, 800), (12, 38, 28, 255))

    w, h = 1280, 720
    total_frames = duration_sec * fps
    temp_dir = os.path.join(PROJECT_DIR, f"temp_frames_{os.path.basename(target_path)}")
    os.makedirs(temp_dir, exist_ok=True)

    fonts = get_fonts(w, h)
    
    # Pre-scale source image to fit canvas base
    sw, sh = source_img.size
    scale_fit = max(w / sw, h / sh)
    base_resized = source_img.resize((int(sw * scale_fit), int(sh * scale_fit)), Image.Resampling.LANCZOS)

    for frame_idx in range(total_frames):
        t = frame_idx / float(total_frames - 1) if total_frames > 1 else 0.0
        
        # Ken Burns Smooth Pan & Zoom effect (1.00x -> 1.15x zoom with gentle pan)
        zoom = 1.00 + 0.15 * (0.5 - 0.5 * math.cos(math.pi * t))
        
        frame_base = base_resized.resize((int(base_resized.width * zoom), int(base_resized.height * zoom)), Image.Resampling.BILINEAR)
        
        # Pan coordinates offset
        crop_x = int((frame_base.width - w) * (0.5 + 0.2 * math.sin(math.pi * t)))
        crop_y = int((frame_base.height - h) * 0.5)
        crop_x = max(0, min(crop_x, max(0, frame_base.width - w)))
        crop_y = max(0, min(crop_y, max(0, frame_base.height - h)))

        frame = frame_base.crop((crop_x, crop_y, crop_x + w, crop_y + h)).convert("RGB")
        draw = ImageDraw.Draw(frame)

        # Header overlay
        draw_siteground_header(draw, w, h, fonts, tag_text="8S MOTION SEGMENT")

        # Bottom Subtitle / Prompt Overlay Banner
        banner_h = 70
        banner_y = h - banner_h - 30
        draw.rounded_rectangle([40, banner_y, w - 40, banner_y + banner_h], radius=16, fill=(11, 18, 32, 220), outline=(150, 203, 76), width=2)
        
        display_txt = prompt_text[:85] + ("..." if len(prompt_text) > 85 else "")
        draw.text((60, banner_y + 18), f"🎬 {display_txt or 'SiteGround AI Marketing Campaign Segment'}", font=fonts["sub"], fill=(255, 255, 255))

        frame_path = os.path.join(temp_dir, f"frame_{frame_idx:04d}.png")
        frame.save(frame_path)

    # Encode with FFmpeg
    ffmpeg_bin = shutil.which("ffmpeg") or "/tmp/ffmpeg" or "ffmpeg"
    cmd = [
        ffmpeg_bin, "-y",
        "-framerate", str(fps),
        "-i", os.path.join(temp_dir, "frame_%04d.png")
    ]

    fallback_audio = os.path.join(PROJECT_DIR, "fallback_voiceover.mp3")
    if os.path.exists(fallback_audio):
        cmd.extend(["-i", fallback_audio])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p"
    ])

    if os.path.exists(fallback_audio):
        cmd.extend(["-c:a", "aac", "-shortest"])

    cmd.append(target_path)

    try:
        subprocess.run(cmd, capture_output=True, check=True)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


