from PIL import Image
import os

# slug (hero png) -> thumb filename, for the 5 new 2026-09-08 posts
SLUGS = {
    "ai-tools-for-cold-email-2026": "thumb-ai-tools-for-cold-email-2026.png",
    "ai-tools-for-photographers-2026": "thumb-ai-tools-for-photographers-2026.png",
    "ai-tools-for-therapists-2026": "thumb-ai-tools-for-therapists-2026.png",
    "ai-tools-for-accountants-2026": "thumb-ai-tools-for-accountants-2026.png",
    "ai-tools-for-remote-teams-2026": "thumb-ai-tools-for-remote-teams-2026.png",
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
