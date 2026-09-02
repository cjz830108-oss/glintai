from PIL import Image
import os

# slug -> thumb filename (batch 2)
SLUGS = {
    "ai-tools-for-fiction-writers-2026": "thumb-fiction.png",
    "ai-tools-for-freelancers-2026": "thumb-freelance.png",
    "ai-tools-for-job-seekers-2026": "thumb-jobseek.png",
    "ai-tools-for-researchers-2026": "thumb-research.png",
    "ai-tools-for-small-business-2026": "thumb-smb.png",
    "ai-tools-for-social-media-managers-2026": "thumb-social.png",
    "ai-writing-tools-non-native-english": "thumb-esl.png",
    "free-ai-content-detector-no-upload": "thumb-noupload.png",
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
