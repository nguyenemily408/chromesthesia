# Builds a night beach with glowing waves in Blender and renders it.
# Run:  Blender --background --python make_waves.py -- still 60
#       Blender --background --python make_waves.py -- anim 1 120
import bpy, math, sys, os

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['still', '60']
mode = args[0]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'frames')
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
SLOPE, SHORE_X = 0.10, -4.0          # the beach rises toward -X, waterline near x = -4


def math_node(N, L, op, a, b=None, c=None):
    n = N.new('ShaderNodeMath'); n.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: L.new(v, n.inputs[i])
    return n.outputs[0]


def map_range(N, L, v, a, b, c, d):
    n = N.new('ShaderNodeMapRange'); n.clamp = True
    L.new(v, n.inputs[0])
    for i, x in zip((1, 2, 3, 4), (a, b, c, d)): n.inputs[i].default_value = x
    return n.outputs[0]


# ---------------- Ocean ----------------
bpy.ops.mesh.primitive_plane_add(size=2)
ocean = bpy.context.object
mod = ocean.modifiers.new('Ocean', 'OCEAN')
mod.geometry_mode = 'GENERATE'
mod.repeat_x = 4; mod.repeat_y = 4
mod.spatial_size = 45
mod.resolution = 16
mod.viewport_resolution = 16
mod.wave_scale = 1.0
mod.choppiness = 1.7
mod.wind_velocity = 13
mod.wave_scale_min = 0.5
mod.wave_alignment = 4.0
mod.wave_direction = math.radians(180)
mod.damping = 0.8
mod.use_foam = True
mod.foam_layer_name = 'foam'
mod.foam_coverage = 0.35
mod.time = 0.0; mod.keyframe_insert('time', frame=1)
mod.time = 10.0; mod.keyframe_insert('time', frame=241)
for fc in ocean.animation_data.action.fcurves if hasattr(ocean.animation_data.action, 'fcurves') else []:
    for k in fc.keyframe_points: k.interpolation = 'LINEAR'
bpy.ops.object.shade_smooth()

wm = bpy.data.materials.new('Water'); wm.use_nodes = True
N, L = wm.node_tree.nodes, wm.node_tree.links
bsdf = N['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.002, 0.008, 0.022, 1)
bsdf.inputs['Roughness'].default_value = 0.14
attr = N.new('ShaderNodeAttribute'); attr.attribute_name = 'foam'
geo = N.new('ShaderNodeNewGeometry')
sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
sand_z = math_node(N, L, 'MULTIPLY_ADD', sep.outputs[0], -SLOPE, SLOPE * SHORE_X)
thick = math_node(N, L, 'SUBTRACT', sep.outputs[2], sand_z)
shore = map_range(N, L, thick, 0.0, 0.22, 1.0, 0.0)            # glow where water is thin over sand
crest = map_range(N, L, sep.outputs[2], 0.15, 0.9, 0.0, 1.0)  # faint glow inside tall waves
foam = math_node(N, L, 'POWER', attr.outputs[0], 2.0)
total = math_node(N, L, 'ADD', foam, math_node(N, L, 'MULTIPLY', shore, 0.9))
total = math_node(N, L, 'ADD', total, math_node(N, L, 'MULTIPLY', crest, 0.55))
total = map_range(N, L, total, 0.0, 1.0, 0.0, 1.0)
ramp = N.new('ShaderNodeValToRGB'); L.new(total, ramp.inputs[0])
ramp.color_ramp.elements[0].color = (0.0, 0.02, 0.25, 1)
ramp.color_ramp.elements[1].color = (0.25, 0.95, 1.0, 1)
mid = ramp.color_ramp.elements.new(0.5); mid.color = (0.0, 0.25, 1.0, 1)
tc = N.new('ShaderNodeTexCoord')
noise = N.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 55
L.new(tc.outputs['Object'], noise.inputs['Vector'])
speck = map_range(N, L, noise.outputs[0], 0.60, 0.70, 0.0, 1.0)
strength = math_node(N, L, 'MULTIPLY', math_node(N, L, 'POWER', total, 1.6), math_node(N, L, 'MULTIPLY_ADD', speck, 9.0, 0.9))
L.new(ramp.outputs[0], bsdf.inputs['Emission Color'])
L.new(strength, bsdf.inputs['Emission Strength'])
ocean.data.materials.append(wm)

# ---------------- Sand ----------------
bpy.ops.mesh.primitive_plane_add(size=400, location=(SHORE_X, 0, 0), rotation=(0, math.atan(SLOPE), 0))
sand = bpy.context.object
sm = bpy.data.materials.new('Sand'); sm.use_nodes = True
N, L = sm.node_tree.nodes, sm.node_tree.links
sb = N['Principled BSDF']
sb.inputs['Base Color'].default_value = (0.012, 0.011, 0.010, 1)
sb.inputs['Roughness'].default_value = 0.35
geo = N.new('ShaderNodeNewGeometry')
sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
wet = map_range(N, L, sep.outputs[0], SHORE_X - 9.0, SHORE_X - 1.0, 0.0, 1.0)   # wet strip near the water
tc = N.new('ShaderNodeTexCoord')
noise = N.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 60
L.new(tc.outputs['Object'], noise.inputs['Vector'])
speck = map_range(N, L, noise.outputs[0], 0.68, 0.73, 0.0, 1.0)
L.new(math_node(N, L, 'MULTIPLY', math_node(N, L, 'MULTIPLY', wet, speck), 5.0), sb.inputs['Emission Strength'])
sb.inputs['Emission Color'].default_value = (0.02, 0.35, 1.0, 1)
sand.data.materials.append(sm)

# ---------------- World, light, camera ----------------
world = bpy.data.worlds.new('Night'); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.0015, 0.003, 0.009, 1); bg.inputs[1].default_value = 1.0

bpy.ops.object.light_add(type='SUN', rotation=(math.radians(62), 0, math.radians(120)))
moon = bpy.context.object; moon.data.energy = 0.03; moon.data.color = (0.5, 0.7, 1.0)

bpy.ops.object.empty_add(location=(8, 10, 0.2)); target = bpy.context.object
bpy.ops.object.camera_add(location=(-14, -18, 4.6)); cam = bpy.context.object
cam.data.lens = 30
con = cam.constraints.new('TRACK_TO'); con.target = target
con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
scene.camera = cam

# ---------------- Render ----------------
for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
    try: scene.render.engine = eng; break
    except TypeError: pass
scene.render.resolution_x, scene.render.resolution_y = 960, 540
scene.render.fps = 24
try: scene.view_settings.view_transform = 'Standard'
except TypeError: pass
try: scene.eevee.taa_render_samples = 16
except AttributeError: pass
scene.render.image_settings.file_format = 'PNG'

if mode == 'still':
    scene.frame_set(int(args[1]))
    scene.render.filepath = os.path.join(HERE, 'test.png')
    bpy.ops.render.render(write_still=True)
else:
    scene.frame_start, scene.frame_end = int(args[1]), int(args[2])
    try: scene.render.image_settings.media_type = 'VIDEO'
    except Exception as e: print('media_type', e)
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.filepath = os.path.join(HERE, 'glowing_waves.mp4')
    bpy.ops.render.render(animation=True)
print('DONE', scene.render.engine)
