from PIL import Image
import os

# slug -> thumb filename (batch 5)
SLUGS = {
    "how-to-convert-csv-to-json": "thumb-how-to-convert-csv-to-json.png",
    "how-to-check-password-strength": "thumb-how-to-check-password-strength.png",
    "how-to-count-words-in-a-pdf": "thumb-how-to-count-words-in-a-pdf.png",
    "how-to-write-youtube-tags": "thumb-how-to-write-youtube-tags.png",
    "how-to-create-alt-text-for-images": "thumb-how-to-create-alt-text-for-images.png",
    "how-to-summarize-a-research-paper": "thumb-how-to-summarize-a-research-paper.png",
    "how-to-write-product-descriptions-with-ai": "thumb-how-to-write-product-descriptions-with-ai.png",
    "how-to-make-a-twitter-bio": "thumb-how-to-make-a-twitter-bio.png",
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
