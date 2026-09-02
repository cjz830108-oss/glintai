from PIL import Image
import os

# slug -> thumb filename (batch 4)
SLUGS = {
    "ai-tools-for-consultants-2026": "thumb-ai-tools-for-consultants-2026.png",
    "ai-tools-for-ecommerce-2026": "thumb-ai-tools-for-ecommerce-2026.png",
    "ai-tools-for-lawyers-2026": "thumb-ai-tools-for-lawyers-2026.png",
    "ai-tools-for-real-estate-2026": "thumb-ai-tools-for-real-estate-2026.png",
    "ai-tools-for-nonprofits-2026": "thumb-ai-tools-for-nonprofits-2026.png",
    "ai-tools-for-podcasters-2026": "thumb-ai-tools-for-podcasters-2026.png",
    "best-free-word-counter-tools-2026": "thumb-best-free-word-counter-tools-2026.png",
    "best-free-password-generator-tools-2026": "thumb-best-free-password-generator-tools-2026.png",
}
SRC = "blog/assets"
W, H = 480, 297
for slug, out in SLUGS.items():
    src = os.path.join(SRC, slug + ".png")
    dst = os.path.join(SRC, out)
    if os.path.exists(dst):
        print("SKIP", out); continue
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
