#!/usr/bin/env python3
"""
generate_assets.py
Generates AppIcon.png (1024×1024) and ui_preview.png for PDF Text Extractor.
Run:  python3 generate_assets.py
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import os, sys

OUT   = os.path.dirname(os.path.abspath(__file__))
FBOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FREG  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def rr(draw, box, radius, *, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                            outline=outline, width=width)

def centered_text(draw, cx, cy, text, font, fill):
    """Draw text centred on (cx, cy)."""
    bb = draw.textbbox((0, 0), text, font=font)
    x = cx - (bb[2] - bb[0]) // 2 - bb[0]
    y = cy - (bb[3] - bb[1]) // 2 - bb[1]
    draw.text((x, y), text, font=font, fill=fill)


# ══════════════════════════════════════════════════════════════════
#  APP ICON  (1024 × 1024 RGBA)
# ══════════════════════════════════════════════════════════════════

def _gradient_bg(size):
    """Diagonal blue → indigo gradient."""
    c1 = np.array([  0, 122, 255], dtype=float)   # macOS Blue
    c2 = np.array([ 88,  86, 214], dtype=float)   # macOS Indigo
    y, x = np.indices((size, size))
    t = ((x + y) / (2.0 * (size - 1)))[..., np.newaxis]
    arr = (c1 * (1 - t) + c2 * t).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _squircle_mask(size, n=5.0):
    """Super-ellipse alpha mask with soft anti-aliased edge."""
    c, r = size / 2.0, size / 2.0 * 0.96
    y, x = np.ogrid[:size, :size]
    nx = np.abs((x - c + 0.5) / r)
    ny = np.abs((y - c + 0.5) / r)
    val   = nx**n + ny**n
    alpha = np.clip((1.06 - val) / 0.06, 0.0, 1.0)
    return (alpha * 255).astype(np.uint8)


def _doc_poly(x, y, w, h, fold):
    return [(x, y), (x+w-fold, y), (x+w, y+fold), (x+w, y+h), (x, y+h)]


def make_icon() -> Image.Image:
    S = 1024

    # ── background ──────────────────────────────────────────────
    base = _gradient_bg(S).convert("RGBA")

    # Subtle top-edge specular highlight
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hld = ImageDraw.Draw(hl)
    hld.ellipse([-S//2, -S//2, S + S//2, S//3], fill=(255, 255, 255, 28))
    base = Image.alpha_composite(base, hl)

    # ── document geometry ────────────────────────────────────────
    DX, DY = 210, 148
    DW, DH, DF = 604, 740, 96

    # Drop shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shd = ImageDraw.Draw(sh)
    shd.polygon(_doc_poly(DX+12, DY+22, DW, DH, DF), fill=(0, 30, 100, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, sh)

    # Document body
    doc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dd  = ImageDraw.Draw(doc)
    dd.polygon(_doc_poly(DX, DY, DW, DH, DF), fill=(244, 248, 255))
    # Fold triangle
    dd.polygon([(DX+DW-DF, DY), (DX+DW, DY+DF), (DX+DW-DF, DY+DF)],
               fill=(196, 212, 232))
    # Crease lines
    dd.line([(DX+DW-DF, DY),     (DX+DW-DF, DY+DF)], fill=(170, 190, 218), width=3)
    dd.line([(DX+DW-DF, DY+DF),  (DX+DW,    DY+DF)], fill=(170, 190, 218), width=3)
    base = Image.alpha_composite(base, doc)

    # ── text lines ───────────────────────────────────────────────
    fd  = ImageDraw.Draw(base)
    LX  = DX + 70
    LY  = DY + 128
    LH  = 15            # line height
    GAP = 54            # gap between lines
    LC  = (165, 182, 210)
    pcts = [0.87, 0.68, 0.94, 0.58, 0.80, 0.71, 0.91, 0.53, 0.77, 0.44]
    MAX_LINE = DW - 138

    for i, pct in enumerate(pcts):
        ly  = LY + i * GAP
        lx2 = LX + int(MAX_LINE * pct)
        fd.rounded_rectangle([LX, ly, lx2, ly+LH], radius=LH//2, fill=LC)

    # ── "PDF" red badge ──────────────────────────────────────────
    BW, BH = 200, 66
    BX = DX + DW//2 - BW//2
    BY = DY + DH - 116
    fd.rounded_rectangle([BX, BY, BX+BW, BY+BH], radius=BH//2,
                         fill=(255, 59, 48))
    fnt_badge = load_font(FBOLD, 54)
    centered_text(fd, BX + BW//2, BY + BH//2, "PDF", fnt_badge, (255, 255, 255))

    # ── squircle clip ────────────────────────────────────────────
    mask_arr = _squircle_mask(S)
    r, g, b, a = base.split()
    new_a = np.minimum(np.array(a), mask_arr).astype(np.uint8)
    base = Image.merge("RGBA", (r, g, b, Image.fromarray(new_a, "L")))
    return base


# ══════════════════════════════════════════════════════════════════
#  UI PREVIEW  (1440 × 900 RGB)  — dark-mode macOS mockup
# ══════════════════════════════════════════════════════════════════

# ── palette ──
P = dict(
    win         = ( 28,  28,  30),
    toolbar     = ( 40,  40,  42),
    sidebar     = ( 34,  34,  36),
    border      = ( 58,  58,  62),
    text        = (255, 255, 255),
    text2       = (152, 152, 158),
    accent      = ( 10, 132, 255),
    sel         = ( 58,  58,  62),
    status_bg   = ( 22,  22,  24),
    red_btn     = (255,  95,  86),
    yel_btn     = (255, 189,  46),
    grn_btn     = ( 39, 201,  63),
    page_hdr    = ( 90, 110, 155),
    line1       = (200, 210, 230),
    line2       = (155, 168, 192),
    search_bg   = ( 46,  46,  50),
    highlight   = (255, 214,  10),
    hi_text     = ( 28,  28,  30),
    dot_accent  = ( 10, 132, 255),
    dot_purple  = (191,  90, 242),
    dot_teal    = ( 48, 209, 170),
)

def make_ui_preview() -> Image.Image:
    W, H       = 1440, 900
    SIDEBAR_W  = 228
    TITLE_H    = 40
    TOOLBAR_H  = 44
    STATUS_H   = 28
    CONTENT_Y  = TITLE_H + TOOLBAR_H
    CONTENT_H  = H - CONTENT_Y - STATUS_H

    img = Image.new("RGB", (W, H), P["win"])
    d   = ImageDraw.Draw(img)

    # ── Fonts ────────────────────────────────────────────────────
    F = dict(
        sm    = load_font(FREG,  11),
        reg   = load_font(FREG,  13),
        reg14 = load_font(FREG,  14),
        bold  = load_font(FBOLD, 13),
        bold14= load_font(FBOLD, 14),
        title = load_font(FBOLD, 14),
        hdr   = load_font(FBOLD, 11),
        page  = load_font(FBOLD, 12),
        mono  = load_font(FREG,  13),
    )

    def t(x, y, text, font="reg", color="text"):
        d.text((x, y), text, font=F[font], fill=P[color])

    def t_bb(text, fk):
        bb = d.textbbox((0,0), text, font=F[fk])
        return bb[2]-bb[0], bb[3]-bb[1], bb

    # ══════════════════════════════════════════════════════════════
    #  TITLE BAR
    # ══════════════════════════════════════════════════════════════
    d.rectangle([0, 0, W, TITLE_H], fill=P["toolbar"])
    d.line([0, TITLE_H-1, W, TITLE_H-1], fill=P["border"], width=1)

    # Traffic lights
    for i, (fill, out) in enumerate([
        (P["red_btn"], (220, 70, 60)),
        (P["yel_btn"], (220, 160, 36)),
        (P["grn_btn"], ( 28, 170, 44)),
    ]):
        cx = 16 + i * 22
        cy = TITLE_H // 2
        d.ellipse([cx-7, cy-7, cx+7, cy+7], fill=fill, outline=out, width=1)

    # Title
    tw, th, tbb = t_bb("PDF Text Extractor", "title")
    d.text(((W-tw)//2 - tbb[0], (TITLE_H-th)//2 - tbb[1]),
           "PDF Text Extractor", font=F["title"], fill=P["text"])

    # ══════════════════════════════════════════════════════════════
    #  TOOLBAR
    # ══════════════════════════════════════════════════════════════
    TY = TITLE_H
    d.rectangle([0, TY, W, TY+TOOLBAR_H], fill=P["toolbar"])
    d.line([0, TY+TOOLBAR_H-1, W, TY+TOOLBAR_H-1], fill=P["border"], width=1)

    ITEMS = [
        ("Open PDF…",    "accent",  True),
        (None,           None,      False),
        ("Copy Text",    "text2",   False),
        ("Save as .txt…","text2",   False),
        (None,           None,      False),
        ("Search…",      "accent",  True),
        (None,           None,      False),
        ("Remove File",  "text2",   False),
    ]
    ix = 16
    for label, col, active in ITEMS:
        if label is None:
            d.line([ix+4, TY+10, ix+4, TY+TOOLBAR_H-10], fill=P["border"], width=1)
            ix += 18; continue
        tw, th, bb = t_bb(label, "reg")
        ty = TY + (TOOLBAR_H - th) // 2 - bb[1]
        if active:
            rr(d, [ix-10, TY+7, ix+tw+10, TY+TOOLBAR_H-7], radius=6, fill=P["sel"])
        d.text((ix, ty), label, font=F["reg"],
               fill=P[col] if col in P else P["text"])
        ix += tw + 28

    # ══════════════════════════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════════════════════════
    CY = CONTENT_Y
    d.rectangle([0, CY, SIDEBAR_W, H-STATUS_H], fill=P["sidebar"])
    d.line([SIDEBAR_W-1, CY, SIDEBAR_W-1, H-STATUS_H], fill=P["border"], width=1)

    # Sidebar label
    d.text((16, CY+12), "PDFs", font=F["hdr"], fill=P["text2"])

    FILES = [
        ("annual_report_2024.pdf",  "12 pages · 8,431 chars",   True,  P["dot_accent"]),
        ("invoice_march.pdf",       "2 pages · 1,204 chars",    False, P["dot_purple"]),
        ("research_paper.pdf",      "28 pages · 42,810 chars",  False, P["dot_teal"]),
    ]
    for i, (name, meta, sel, dot) in enumerate(FILES):
        fy = CY + 42 + i * 62
        if sel:
            rr(d, [5, fy-4, SIDEBAR_W-5, fy+52], radius=9, fill=P["sel"])
        # Icon dot
        d.ellipse([15, fy+9, 26, fy+20], fill=dot)
        display = (name[:23]+"…") if len(name)>26 else name
        d.text((35, fy+5),  display, font=F["bold"], fill=P["text"])
        d.text((35, fy+25), meta,    font=F["sm"],   fill=P["text2"])

    # ══════════════════════════════════════════════════════════════
    #  SEARCH BAR  (visible, showing active search)
    # ══════════════════════════════════════════════════════════════
    SEARCH_H = 38
    SBY = CY
    d.rectangle([SIDEBAR_W, SBY, W, SBY+SEARCH_H], fill=P["search_bg"])
    d.line([SIDEBAR_W, SBY+SEARCH_H-1, W, SBY+SEARCH_H-1],
           fill=P["border"], width=1)

    # Search icon + input box
    rr(d, [SIDEBAR_W+12, SBY+6, SIDEBAR_W+12+340, SBY+SEARCH_H-6],
       radius=6, fill=P["win"])
    d.text((SIDEBAR_W+22, SBY+10), "🔍  shareholders",
           font=F["reg"], fill=P["text"])
    # match count
    d.text((SIDEBAR_W+370, SBY+11), "3 matches", font=F["sm"], fill=P["text2"])
    # close button
    rr(d, [W-44, SBY+8, W-20, SBY+SEARCH_H-8], radius=5, fill=P["sel"])
    centered_text(d, W-32, SBY+SEARCH_H//2, "✕", F["sm"], P["text2"])

    # ══════════════════════════════════════════════════════════════
    #  MAIN TEXT CONTENT
    # ══════════════════════════════════════════════════════════════
    TX  = SIDEBAR_W + 36
    TY2 = CY + SEARCH_H + 20
    LH  = 24

    PAGES = [
        ("── Page 1 of 12 ──", [
            ("ACME Corporation  —  Annual Report 2024",          "bold14", "text"),
            ("",                                                  "reg14",  "text"),
            ("Dear Shareholders,",                                "reg14",  "text"),
            ("",                                                  "reg14",  "text"),
            ("It is with great pleasure that we present the Annual Report for 2024,", "reg14", "text"),
            ("reflecting a year of remarkable growth, resilience, and transformation", "reg14", "text"),
            ("across all segments of our business.",                                   "reg14", "text"),
            ("",                                                  "reg14",  "text"),
            # "shareholders" gets highlighted below — special markup
            ("Revenue for the fiscal year reached $4.2 billion. Our shareholders",    "reg14", "text"),
            ("have benefited from disciplined capital allocation and record EPS.",     "reg14", "text"),
        ]),
        ("── Page 2 of 12 ──", [
            ("Financial Highlights",                              "bold14", "text"),
            ("",                                                  "reg14",  "text"),
            ("  Total Revenue:      $4.2B   (+17% YoY)",         "mono",   "text"),
            ("  Operating Income:   $892M   (+24% YoY)",         "mono",   "text"),
            ("  Net Income:         $641M   (+19% YoY)",         "mono",   "text"),
            ("  Earnings per Share: $3.84   (+22% YoY)",         "mono",   "text"),
            ("",                                                  "mono",   "text"),
            ("These results underscore our commitment to all shareholders and",       "reg14", "text"),
            ("long-term value creation across all business units worldwide.",         "reg14", "text"),
        ]),
    ]

    SEARCH_WORD = "shareholders"

    for page_title, lines in PAGES:
        # Page header row
        pw, ph, pbb = t_bb(page_title, "page")
        d.line([TX, TY2+ph//2, TX+14, TY2+ph//2], fill=P["page_hdr"], width=2)
        d.text((TX+22, TY2 - pbb[1]), page_title, font=F["page"], fill=P["page_hdr"])
        d.line([TX+22+pw+14, TY2+ph//2, W-36, TY2+ph//2],
               fill=P["page_hdr"], width=1)
        TY2 += LH + 8

        for text, fk, col in lines:
            if TY2 > H - STATUS_H - 20:
                break
            if text == "":
                TY2 += LH // 2; continue

            # Check if line contains search term and highlight it
            lw = text.lower()
            if SEARCH_WORD in lw:
                # Draw with highlight for the matching word
                before_idx = lw.index(SEARCH_WORD)
                before = text[:before_idx]
                match  = text[before_idx:before_idx+len(SEARCH_WORD)]
                after  = text[before_idx+len(SEARCH_WORD):]

                bw = d.textlength(before, font=F[fk]) if before else 0
                mw = d.textlength(match,  font=F[fk])

                bby = TY2
                # Highlight rectangle
                rr(d, [int(TX+bw)-2, bby-2, int(TX+bw+mw)+2, bby+LH-2],
                   radius=3, fill=P["highlight"])

                # Draw text segments
                cx = TX
                if before:
                    d.text((cx, bby), before, font=F[fk], fill=P[col])
                    cx += int(bw)
                d.text((cx, bby), match, font=F[fk], fill=P["hi_text"])
                cx += int(mw)
                if after:
                    d.text((cx, bby), after, font=F[fk], fill=P[col])
            else:
                d.text((TX, TY2), text, font=F[fk], fill=P[col])

            TY2 += LH

        TY2 += LH * 2  # inter-page gap

    # ══════════════════════════════════════════════════════════════
    #  STATUS BAR
    # ══════════════════════════════════════════════════════════════
    SY = H - STATUS_H
    d.rectangle([0, SY, W, H], fill=P["status_bg"])
    d.line([0, SY, W, SY], fill=P["border"], width=1)
    status = "annual_report_2024.pdf  ·  12 pages  ·  8,431 characters"
    d.text((SIDEBAR_W+16, SY + (STATUS_H - 11)//2), status,
           font=F["sm"], fill=P["text2"])

    # ── Outer window border ──────────────────────────────────────
    d.rectangle([0, 0, W-1, H-1], outline=P["border"], width=1)

    return img


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating AppIcon.png …", end=" ", flush=True)
    icon = make_icon()
    icon.save(os.path.join(OUT, "AppIcon.png"), "PNG", optimize=True)
    print(f"saved ({icon.size[0]}×{icon.size[1]})")

    print("Generating ui_preview.png …", end=" ", flush=True)
    ui = make_ui_preview()
    ui.save(os.path.join(OUT, "ui_preview.png"), "PNG", optimize=True)
    print(f"saved ({ui.size[0]}×{ui.size[1]})")

    print("Done ✅")
