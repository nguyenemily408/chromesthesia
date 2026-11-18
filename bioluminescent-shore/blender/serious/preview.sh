#!/bin/zsh
# Render preview stills (960px, 32 samples) and a contact sheet.
# Usage: ./preview.sh <name> <sheet.jpg> <frame> <frame> ...
cd "${0:A:h}"
NAME=$1; SHEET=$2; shift 2
for f in "$@"; do
  /Applications/Blender.app/Contents/MacOS/Blender --background $NAME.blend --python render.py -- still $f 32 960 2>&1 | grep -E "RENDER_DONE|Error|Traceback"
done
python3 - "$NAME" "$SHEET" "$@" <<'PY'
import sys
from PIL import Image, ImageDraw
name, out, fs = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3:]]
w, h = 640, 360; rows = (len(fs)+1)//2
sheet = Image.new('RGB', (w*2, h*rows))
for i, f in enumerate(fs):
    im = Image.open(f'{name}_{f:03d}.png').convert('RGB').resize((w, h))
    ImageDraw.Draw(im).text((10, 8), f'{i+1}  (frame {f})', fill=(255, 255, 255))
    sheet.paste(im, ((i % 2)*w, (i//2)*h))
sheet.save(out, quality=90)
PY
echo ALL_DONE
