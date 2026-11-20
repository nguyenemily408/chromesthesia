"""Package the existing app for Chrome without duplicating its source."""
from pathlib import Path
import json
import re
import shutil
import zipfile

SOURCE = Path(__file__).resolve().parent
PROJECT = SOURCE.parent
OUTPUT = SOURCE / "build" / "sound-of-color"
OUTPUT.mkdir(parents=True, exist_ok=True)

for name in ("manifest.json", "background.js", "popup.html", "popup.css", "popup.js"):
    shutil.copyfile(SOURCE / name, OUTPUT / name)

files = [
    "experiments/fable-ink/three-styles-full.html",
    "experiments/fable-ink/concept-styles.js",
    "living-watercolor/watercolor.html",
    "experiments/aurora-norway/aurora.html",
    "bioluminescent-shore/music-wave-preview.html",
    "bioluminescent-shore/blender/serious/wave5.mp4",
]
for folder in ("assets/home", "assets/watercolor", "experiments/aurora-norway/photos"):
    files.extend(str(p.relative_to(PROJECT)) for p in (PROJECT / folder).iterdir() if p.is_file())

def copy_page(source, target):
    # Chrome extension pages run only packaged scripts. Extract each inline script
    # beside its page, preserving the order of both inline and external scripts.
    count = 0
    def extract(match):
        nonlocal count
        attrs, code = match.groups()
        if re.search(r"\bsrc\s*=", attrs, re.I):
            return match.group(0)
        count += 1
        script = target.with_name(target.stem + f"-inline-{count}.js")
        script.write_text(code)
        return f'<script src="{script.name}"{attrs}></script>'
    page = re.sub(r"<script([^>]*)>([\s\S]*?)</script>", extract, source.read_text(), flags=re.I)
    target.write_text(page)

for name in files:
    source = PROJECT / name
    target = OUTPUT / "app" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix == ".html":
        copy_page(source, target)
    else:
        shutil.copyfile(source, target)

archive = OUTPUT.parent / "sound-of-color-extension.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    for item in sorted(OUTPUT.rglob("*")):
        if item.is_file():
            bundle.write(item, item.relative_to(OUTPUT))
print(json.dumps({"folder": str(OUTPUT), "zip": str(archive), "bytes": archive.stat().st_size}))
