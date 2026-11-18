# Stitches short pieces of each attempt into one video with "Version N" labels.
# Run:  Blender --background --python montage.py
import bpy, os
here = os.path.dirname(os.path.abspath(__file__))
SEG = 36   # frames per version (1.5 s at 24 fps)
# (file, fraction of the clip where the excerpt starts)
clips = [('../glowing_waves.mp4', 0.3), ('breaking_wave.mp4', 0.35), ('sculpt_wave.mp4', 0.3),
         ('wave2.mp4', 0.25), ('wave3.mp4', None)]   # None = play the whole clip
notes = ['Flat water with glowing ribbons', 'Physics simulation of splashing water',
         'Wave sculpted as a solid shape', 'Hand-built wave that glows only where it breaks',
         'Second wave added, patchier foam on the sand']
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
se = scene.sequence_editor_create()
strips = se.strips if hasattr(se, 'strips') else se.sequences
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
pos = 1
mids = []
for i, (f, frac) in enumerate(clips):
    start = pos
    m = strips.new_movie('v%d' % (i + 1), os.path.join(here, f), 1, start, fit_method='ORIGINAL')
    total = m.frame_duration
    n = total if frac is None else SEG
    off = 0 if frac is None else min(int(total * frac), max(0, total - SEG))
    pos += n
    mids.append(start + (n * 3) // 4)
    m.frame_start = start - off
    m.frame_offset_start = off
    m.frame_final_duration = n
    sc = 1280 / m.elements[0].orig_width
    if 'sculpt' in f: sc = 4 / 3   # this clip has black borders baked in
    m.transform.scale_x = m.transform.scale_y = sc
    print('CH', m.channel, 'scale', sc)
    print('CLIP', f, total, 'frames, offset', off, m.elements[0].orig_width, m.elements[0].orig_height)
    try: t = strips.new_effect('t%d' % (i + 1), 'TEXT', 12, start, length=n)
    except TypeError: t = strips.new_effect('t%d' % (i + 1), 'TEXT', 12, start, frame_end=start + n)
    t.text = 'Version %d' % (i + 1)
    t.font_size = 64
    t.location = (0.05, 0.15)
    for a, v in (('anchor_x', 'LEFT'), ('align_x', 'LEFT'), ('anchor_y', 'BOTTOM')):
        try: setattr(t, a, v)
        except Exception as e: print(a, e)
    t.use_shadow = True
    t.color = (1, 1, 1, 1)
    try: d = strips.new_effect('d%d' % (i + 1), 'TEXT', 13, start, length=n)
    except TypeError: d = strips.new_effect('d%d' % (i + 1), 'TEXT', 13, start, frame_end=start + n)
    d.text = notes[i]
    d.font_size = 30
    d.location = (0.05, 0.08)
    for a, v in (('anchor_x', 'LEFT'), ('anchor_y', 'BOTTOM')):
        try: setattr(d, a, v)
        except Exception as e: print(a, e)
    d.use_shadow = True
    d.color = (0.8, 0.9, 1, 1)
scene.frame_start, scene.frame_end = 1, pos - 1
print('TOTAL', pos - 1)
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
for i in range(len(clips)):
    scene.frame_set(mids[i])
    scene.render.filepath = os.path.join(here, 'montage_check_%d.png' % (i + 1))
    bpy.ops.render.render(write_still=True)
try: scene.render.image_settings.media_type = 'VIDEO'
except Exception as e: print('media_type', e)
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.filepath = os.path.join(here, 'attempts_montage.mp4')
bpy.ops.render.render(animation=True)
print('DONE')
