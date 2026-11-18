# Joins the rendered pictures into one video file.
# Run:  Blender --background --python encode.py -- <frames_folder> <output.mp4>
import bpy, sys, os

args = sys.argv[sys.argv.index('--') + 1:]
folder, out = os.path.abspath(args[0]), os.path.abspath(args[1])
files = sorted(f for f in os.listdir(folder) if f.endswith('.png'))
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
se = scene.sequence_editor_create()
strips = se.strips if hasattr(se, 'strips') else se.sequences
strip = strips.new_image('frames', os.path.join(folder, files[0]), 1, 1)
for f in files[1:]:
    strip.elements.append(f)
scene.frame_start, scene.frame_end = 1, len(files)
scene.render.fps = 24
# Optional: <width> <height> after the output name (default 1280 x 720).
scene.render.resolution_x = int(args[2]) if len(args) > 2 else 1280
scene.render.resolution_y = int(args[3]) if len(args) > 3 else 720
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
try: scene.render.image_settings.media_type = 'VIDEO'
except Exception as e: print('media_type', e)
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.filepath = out
bpy.ops.render.render(animation=True)
print('ENCODED', len(files), out)
