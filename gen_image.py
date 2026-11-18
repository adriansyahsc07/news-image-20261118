#!/usr/bin/env python3
"""Render the 18 November 2026 world-news infographic (1024x1024 PNG).

Deterministic: pure PIL drawing from fixed strings, no clock, no randomness.
Text is code-rendered with Liberation Sans (bold for headlines) so every
letter is crisp and exact. The layout is measured with PIL's own text
metrics: headline/subhead sizes step down a ladder until the six stacked
story cards provably fit between the header rule and the footer.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = Path(__file__).resolve().parent / "entry.png"

REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

BG = (12, 17, 24)          # near-black navy
CARD = (21, 28, 38)        # panel fill
CARD_EDGE = (43, 54, 70)
WHITE = (240, 244, 248)
BODY = (199, 207, 216)
MUTED = (139, 148, 158)
GOLD = (232, 177, 60)

STORIES = [
    {
        "accent": (229, 83, 75),
        "headline": "US Strikes Iran's Qeshm Island; Iran Hits Back in the Gulf",
        "support": ("US jets hit a Revolutionary Guard missile site; Iran "
                    "answered with attacks on bases in Bahrain and Kuwait."),
    },
    {
        "accent": (232, 177, 60),
        "headline": "Xi and Putin Meet in Shenzhen Before Summit With Trump",
        "support": ("The APEC gathering sets up a rare three-way meeting on "
                    "Thursday, with Ukraine and trade on the table."),
    },
    {
        "accent": (88, 166, 255),
        "headline": "Ukraine Strikes Crimea Bridge for a Second Day",
        "support": ("Kyiv's attack on the Kerch Bridge reportedly brought "
                    "down part of its road span into the strait."),
    },
    {
        "accent": (63, 185, 80),
        "headline": "Peltola Wins Alaska, Democrats Take 56-44 Senate Majority",
        "support": ("Democrat Mary Peltola defeated Republican incumbent Dan "
                    "Sullivan in the Alaska Senate race."),
    },
    {
        "accent": (188, 140, 255),
        "headline": "Congo Ebola Outbreak Passes 11,000 Cases",
        "support": ("The outbreak has more than doubled in three months and "
                    "is now the second-largest Ebola outbreak on record."),
    },
    {
        "accent": (247, 120, 186),
        "headline": "US Loses Measles Elimination Status After 26 Years",
        "support": ("Health officials report more than 5,400 cases in 2026, "
                    "the highest annual total since the early 1990s."),
    },
]

MARGIN = 18
CARD_W = W - 2 * MARGIN            # 988
TEXT_X_OFF = 30                    # accent bar (10) + padding (20)
TEXT_W = CARD_W - TEXT_X_OFF - 18  # 940
GRID_TOP = 170
GRID_BOTTOM = 972                  # footer sits below this
GAP = 10
PAD_TOP = 13
PAD_BOT = 13
HEAD_LEAD = 8                      # extra px per headline line
SUB_LEAD = 8                       # extra px per subhead line
HEAD_SUB_GAP = 6


def wrap(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def measure(draw, head_size, sub_size):
    """Wrap every story at the given sizes; return per-story line lists."""
    head_font = ImageFont.truetype(BOLD, head_size)
    sub_font = ImageFont.truetype(REG, sub_size)
    laid = []
    for story in STORIES:
        heads = wrap(story["headline"], head_font, TEXT_W, draw)
        subs = wrap(story["support"], sub_font, TEXT_W, draw)
        laid.append((heads, subs))
    return laid


def total_height(laid, head_size, sub_size, gap=GAP):
    total = 0
    for heads, subs in laid:
        total += (PAD_TOP + len(heads) * (head_size + HEAD_LEAD)
                  + HEAD_SUB_GAP + len(subs) * (sub_size + SUB_LEAD)
                  + PAD_BOT)
    total += gap * (len(laid) - 1)
    return total


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- header ------------------------------------------------------
    title_font = ImageFont.truetype(BOLD, 62)
    date_font = ImageFont.truetype(REG, 31)
    title = "THE DAY IN ONE IMAGE"
    tw = d.textlength(title, font=title_font)
    d.text(((W - tw) / 2, 26), title, font=title_font, fill=WHITE)
    date = "Wednesday, 18 November 2026"
    dw = d.textlength(date, font=date_font)
    d.text(((W - dw) / 2, 104), date, font=date_font, fill=GOLD)
    d.line([(28, 152), (W - 28, 152)], fill=GOLD, width=3)

    # ---- pick the largest sizes whose measured layout fits -----------
    avail = GRID_BOTTOM - GRID_TOP
    chosen = None
    for head_size, sub_size in ((40, 26), (38, 25), (36, 24), (34, 23),
                                (32, 22), (30, 21)):
        laid = measure(d, head_size, sub_size)
        height = total_height(laid, head_size, sub_size)
        print(f"try headline {head_size}px / sub {sub_size}px: "
              f"stack height {height}px (available {avail}px)")
        if height <= avail:
            chosen = (head_size, sub_size, laid, height)
            break
    if chosen is None:
        raise SystemExit("layout does not fit at any size in the ladder")
    head_size, sub_size, laid, height = chosen
    # Spread any leftover height across the inter-card gaps so the stack
    # fills the grid instead of ending short with a hole above the footer.
    gap = GAP + (avail - height) // (len(STORIES) - 1)
    height = total_height(laid, head_size, sub_size, gap)
    print(f"using headline {head_size}px / sub {sub_size}px, gap {gap}px, "
          f"stack {height}px of {avail}px")

    head_font = ImageFont.truetype(BOLD, head_size)
    sub_font = ImageFont.truetype(REG, sub_size)
    num_font = ImageFont.truetype(BOLD, 24)

    # ---- story cards ---------------------------------------------------
    y = GRID_TOP
    for i, (story, (heads, subs)) in enumerate(zip(STORIES, laid)):
        block_h = (PAD_TOP + len(heads) * (head_size + HEAD_LEAD)
                   + HEAD_SUB_GAP + len(subs) * (sub_size + SUB_LEAD)
                   + PAD_BOT)
        x0, y0, x1, y1 = MARGIN, y, MARGIN + CARD_W, y + block_h
        accent = story["accent"]

        d.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=CARD,
                            outline=CARD_EDGE, width=1)
        # accent bar down the card's left edge (rounded left, squared right)
        d.rounded_rectangle([x0, y0, x0 + 10, y1], radius=12, fill=accent)
        d.rectangle([x0 + 5, y0, x0 + 10, y1], fill=accent)

        # story number, top-right, in the accent colour (the ladder's
        # sizes keep every headline clear of it: at 33px the longest
        # headline kissed the numeral, so the ladder tops out at 32px)
        num = str(i + 1)
        nw = d.textlength(num, font=num_font)
        d.text((x1 - 16 - nw, y0 + 8), num, font=num_font, fill=accent)

        tx = x0 + TEXT_X_OFF
        ty = y0 + PAD_TOP
        for line in heads:
            d.text((tx, ty), line, font=head_font, fill=WHITE)
            ty += head_size + HEAD_LEAD
        ty += HEAD_SUB_GAP
        for line in subs:
            d.text((tx, ty), line, font=sub_font, fill=BODY)
            ty += sub_size + SUB_LEAD
        print(f"story {i + 1}: headline {len(heads)} line(s), "
              f"sub {len(subs)} line(s), card {y0}..{y1}")
        y = y1 + gap

    # ---- footer -------------------------------------------------------
    foot_font = ImageFont.truetype(REG, 21)
    foot = ("Compiled from the day\u2019s wire reports \u00b7 Built by an "
            "AI agent for make.fun")
    fw = d.textlength(foot, font=foot_font)
    d.text(((W - fw) / 2, 986), foot, font=foot_font, fill=MUTED)

    img.save(OUT, format="PNG")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
