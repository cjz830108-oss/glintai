from PIL import Image
import os

# slug (hero png) -> thumb filename, for the 5 new 2026-10-04 posts
SLUGS = {
    "how-to-outline-a-novel-with-ai": "thumb-how-to-outline-a-novel-with-ai.png",
    "how-to-fix-plot-holes-ai": "thumb-how-to-fix-plot-holes-ai.png",
    "how-to-write-a-romance-novel-with-ai": "thumb-how-to-write-a-romance-novel-with-ai.png",
    "ai-tools-for-screenwriters-2026": "thumb-ai-tools-for-screenwriters-2026.png",
    "ai-tools-for-journalists-2026": "thumb-ai-tools-for-journalists-2026.png",
}
SRC = "blog/assets"
W, H = 480, 297
for slug, out in SLUGS.items():
    src = os.path.join(SRC, slug + ".png")
    dst = os.path.join(SRC, out)
    if os.path.exists(dst):
        print("SKIP", out)
        continue
    im = Image.open(src).convert("RGB")
    target = W / H
    cur = im.width / im.height
    if cur > target:
        nw = int(im.height * target)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width / target)
        im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
    im = im.resize((W, H), Image.LANCZOS)
    im.save(dst, "PNG", optimize=True)
    print("OK", out, os.path.getsize(dst))
