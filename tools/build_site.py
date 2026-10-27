"""Builds the plugin site from data/plugins.json.

usage: <python with Pillow> tools/build_site.py
  - images/<id>/cover.jpg and gallery-N.jpg from the image sources (optional crop)
  - downloads/<id>-<version>.zip: Fusion/... files, install_mac.command,
    install_windows.bat, README.txt and THIRD_PARTY_NOTICES.txt (when a credit
    carries a licence)
  - data/plugins.js: the JSON plus download file names and sizes, loaded by the
    pages with a <script> tag (works from file:// as well as from a server)

Adding a plugin = add an entry to data/plugins.json and run this script.
Paths in "src" are relative to the site folder.
"""
import json, os, shutil, zipfile
from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(SITE, "tools")
COVER = (1200, 675)


def src_path(p):
    return os.path.normpath(os.path.join(SITE, p))


def save_jpg(im, path, max_w=1600):
    im = im.convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, quality=86)


def cover_image(spec, path):
    im = Image.open(src_path(spec["src"])).convert("RGB")
    if spec.get("crop"):
        im = im.crop(tuple(spec["crop"]))
    if spec.get("fit"):
        # whole image on its own background colour (for wide images)
        bg = im.getpixel((2, im.height - 3))
        im.thumbnail((round(COVER[0] * 0.92), COVER[1]), Image.LANCZOS)
        canvas = Image.new("RGB", COVER, bg)
        canvas.paste(im, ((COVER[0] - im.width) // 2, (COVER[1] - im.height) // 2))
        save_jpg(canvas, path, COVER[0])
        return
    # fill 16:9: centre-crop to the cover aspect, then scale
    ar = COVER[0] / COVER[1]
    if im.width / im.height > ar:
        w = round(im.height * ar)
        im = im.crop(((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height))
    else:
        h = round(im.width / ar)
        im = im.crop((0, (im.height - h) // 2, im.width, (im.height - h) // 2 + h))
    save_jpg(im.resize(COVER, Image.LANCZOS), path, COVER[0])


def readme_text(site, p):
    inst = site["install"][p["install"]]
    lines = [p["name"] + " " + p["version"], "=" * 40, "", p["summary"], ""]
    lines += p["description"] + [""]
    lines += ["■ 使い方", ""] + ["  %d. %s" % (i + 1, s) for i, s in enumerate(p["usage"])] + [""]
    lines += ["■ インストール", "", "  Mac"] + ["    %d. %s" % (i + 1, s) for i, s in enumerate(inst["mac"])]
    lines += ["", "  Windows"] + ["    %d. %s" % (i + 1, s) for i, s in enumerate(inst["windows"])]
    lines += ["", "  " + inst["manual"], ""]
    lines += ["■ 動作環境", "", "  " + p["requirements"], ""]
    if p["credits"]:
        lines += ["■ クレジット", ""]
        for c in p["credits"]:
            lines.append("  " + c["text"] + (" (%s)" % c["license"] if c.get("license") else "") + (" " + c["url"] if c.get("url") else ""))
        if any(c.get("license") for c in p["credits"]):
            lines += ["", "  ライセンス表記は THIRD_PARTY_NOTICES.txt にあります。"]
        lines.append("")
    return "\n".join(lines)


def crlf(text):
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")


def build_zip(site, p, path):
    top = p["name"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        os.remove(path)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        def add_file(full, arc, mode=0o100644):
            info = zipfile.ZipInfo.from_file(full, arc)
            info.external_attr = mode << 16
            with open(full, "rb") as fh:
                z.writestr(info, fh.read(), zipfile.ZIP_DEFLATED)

        for f in p["files"]:
            s = src_path(f["src"])
            if os.path.isdir(s):
                for root, _, files in os.walk(s):
                    for fn in sorted(files):
                        if fn == ".DS_Store":
                            continue
                        full = os.path.join(root, fn)
                        add_file(full, top + "/" + f["dst"] + "/" + os.path.relpath(full, s).replace(os.sep, "/"))
            else:
                add_file(s, top + "/" + f["dst"])
        add_file(os.path.join(TOOLS, "install_mac.command"), top + "/install_mac.command", 0o100755)
        z.writestr(top + "/install_windows.bat", crlf(open(os.path.join(TOOLS, "install_windows.bat"), encoding="utf-8").read()))
        z.writestr(top + "/README.txt", crlf(readme_text(site, p)))
        if any(c.get("license") for c in p["credits"]):
            notices = ["Third-party notices", "===================", ""]
            for c in p["credits"]:
                notices.append(c["text"] + (" (%s)" % c["license"] if c.get("license") else ""))
            for c in p["credits"]:
                lic = c.get("license_file")
                if lic:
                    notices += ["", open(os.path.join(SITE, lic), encoding="utf-8").read().rstrip()]
            z.writestr(top + "/THIRD_PARTY_NOTICES.txt", crlf("\n".join(notices) + "\n"))


def main():
    data = json.load(open(os.path.join(SITE, "data", "plugins.json"), encoding="utf-8"))
    for p in data["plugins"]:
        pid = p["id"]
        img_dir = os.path.join(SITE, "images", pid)
        if os.path.exists(img_dir):
            shutil.rmtree(img_dir)
        cover_image(p["images"]["cover"], os.path.join(img_dir, "cover.jpg"))
        p["coverUrl"] = "images/%s/cover.jpg" % pid
        p["galleryUrls"] = []
        for n, g in enumerate(p["images"].get("gallery", []), 1):
            im = Image.open(src_path(g["src"]))
            if g.get("crop"):
                im = im.crop(tuple(g["crop"]))
            save_jpg(im, os.path.join(img_dir, "gallery-%d.jpg" % n))
            p["galleryUrls"].append({"url": "images/%s/gallery-%d.jpg" % (pid, n), "caption": g.get("caption", "")})
        zname = "%s-%s.zip" % (pid, p["version"])
        zpath = os.path.join(SITE, "downloads", zname)
        build_zip(data, p, zpath)
        p["download"] = {"url": "downloads/" + zname, "size": os.path.getsize(zpath)}
        # sources are build inputs only; the pages do not need them
        del p["files"], p["images"]
        print("%-16s %s  %6.1f KB" % (p["name"], zname, os.path.getsize(zpath) / 1024))
    # old zips of earlier versions are kept on purpose (links may point to them)
    with open(os.path.join(SITE, "data", "plugins.js"), "w", encoding="utf-8") as f:
        f.write("// generated by tools/build_site.py from data/plugins.json - do not edit\n")
        f.write("window.SITE_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    print("wrote data/plugins.js")


if __name__ == "__main__":
    main()
