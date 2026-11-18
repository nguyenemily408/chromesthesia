# Step 2 of 2: light the simulated water as a bioluminescent night scene and render it.
# Run:  Blender --background <name>.blend --python render.py -- still <frame> [samples] [width]
#       Blender --background <name>.blend --python render.py -- anim <first> <last> [samples] [width]
import bpy, sys, os, math

args = sys.argv[sys.argv.index('--') + 1:]
mode = args[0]
HERE = os.path.dirname(os.path.abspath(__file__))
NAME = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
scene = bpy.context.scene
dom = bpy.data.objects['Domain']
beach = bpy.data.objects['Beach']
SEA = 1.0


def mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links


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


# ---------- Water: near-black and glossy, glowing where it moves fast ----------
wm, N, L = mat('Water')
b = N['Principled BSDF']
b.inputs['Base Color'].default_value = (0.0, 0.004, 0.012, 1)
b.inputs['Roughness'].default_value = 0.05
b.inputs['IOR'].default_value = 1.33
vel = N.new('ShaderNodeAttribute'); vel.attribute_name = 'velocity'
ln = N.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; L.new(vel.outputs['Vector'], ln.inputs[0])
speed = ln.outputs['Value']
geo = N.new('ShaderNodeNewGeometry')
sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
wgeo = N.new('ShaderNodeNewGeometry')
sepw = N.new('ShaderNodeSeparateXYZ'); L.new(wgeo.outputs['Position'], sepw.inputs[0])
agit = map_range(N, L, speed, 1.9, 6.0, 0.0, 1.0)                 # only fast, churned-up water
glow = math_node(N, L, 'POWER', agit, 1.4)
ramp = N.new('ShaderNodeValToRGB'); L.new(glow, ramp.inputs[0])
ramp.color_ramp.elements[0].color = (0.0, 0.03, 0.14, 1)
ramp.color_ramp.elements[1].color = (0.0, 0.85, 1.0, 1)
e = ramp.color_ramp.elements.new(0.4); e.color = (0.0, 0.3, 1.0, 1)
tc = N.new('ShaderNodeTexCoord')
noise = N.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 420
L.new(tc.outputs['Object'], noise.inputs['Vector'])
speck = map_range(N, L, noise.outputs[0], 0.64, 0.70, 0.0, 1.0)
strength = math_node(N, L, 'MULTIPLY', glow, math_node(N, L, 'MULTIPLY_ADD', speck, 14.0, 0.9))
sandz = math_node(N, L, 'MULTIPLY_ADD', sep.outputs[0] if False else sepw.outputs[0], -0.256, -0.2 + 0.256*1.5)
sandz = math_node(N, L, 'MAXIMUM', sandz, math_node(N, L, 'MULTIPLY_ADD', math_node(N, L, 'LESS_THAN', sepw.outputs[0], 2.9), 0.7, -0.2))
depth = math_node(N, L, 'SUBTRACT', sepw.outputs[2], sandz)
thin = map_range(N, L, depth, 0.03, 0.30, 1.0, 0.0)
moving = map_range(N, L, speed, 0.2, 1.0, 0.0, 1.0)
lnoise = N.new('ShaderNodeTexNoise'); lnoise.inputs['Scale'].default_value = 9; lnoise.inputs['Detail'].default_value = 6
L.new(tc.outputs['Object'], lnoise.inputs['Vector'])
lacepat = map_range(N, L, lnoise.outputs[0], 0.47, 0.53, 0.0, 1.0)
lace = math_node(N, L, 'MULTIPLY', math_node(N, L, 'MULTIPLY', thin, moving), math_node(N, L, 'MULTIPLY_ADD', lacepat, 0.8, 0.2))
mixc = N.new('ShaderNodeMix'); mixc.data_type = 'RGBA'
L.new(lace, mixc.inputs['Factor']); L.new(ramp.outputs[0], mixc.inputs['A'])
mixc.inputs['B'].default_value = (0.3, 0.75, 1.0, 1)
L.new(mixc.outputs['Result'], b.inputs['Emission Color'])
strength = math_node(N, L, 'ADD', strength, math_node(N, L, 'MULTIPLY', lace, math_node(N, L, 'MULTIPLY_ADD', speck, 8.0, 2.6)))
# Light glowing from inside the raised water, strongest where the wave is thick.
vol = N.new('ShaderNodeEmission')
vol.inputs['Color'].default_value = (0.0, 1.0, 0.72, 1)
vgeo = N.new('ShaderNodeNewGeometry')
vsep = N.new('ShaderNodeSeparateXYZ'); L.new(vgeo.outputs['Position'], vsep.inputs[0])
sandz_v = math_node(N, L, 'MULTIPLY_ADD', vsep.outputs[0], -0.256, -0.2 + 0.256*1.5)
rest_v = math_node(N, L, 'MAXIMUM', sandz_v, SEA)
lift_v = math_node(N, L, 'SUBTRACT', vsep.outputs[2], rest_v)
L.new(math_node(N, L, 'MULTIPLY', math_node(N, L, 'POWER', map_range(N, L, lift_v, 0.2, 1.0, 0.0, 1.0), 1.3), 10.0), vol.inputs['Strength'])
L.new(vol.outputs[0], next(n for n in N if n.type == 'OUTPUT_MATERIAL').inputs['Volume'])
b.inputs['Transmission Weight'].default_value = 0.6
L.new(strength, b.inputs['Emission Strength'])
dom.data.materials.clear(); dom.data.materials.append(wm)
for p in dom.data.polygons: p.use_smooth = True

# ---------- Glowing droplets for spray, foam and bubbles ----------
gm, N, L = mat('Droplet')
for n in list(N):
    if n.type != 'OUTPUT_MATERIAL': N.remove(n)
outn = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
info = N.new('ShaderNodeObjectInfo')
mask = map_range(N, L, info.outputs['Random'], 0.48, 0.52, 0.0, 1.0)
em = N.new('ShaderNodeEmission')
rr = N.new('ShaderNodeValToRGB'); L.new(info.outputs['Random'], rr.inputs[0])
rr.color_ramp.elements[0].color = (0.0, 0.35, 1.0, 1)
rr.color_ramp.elements[1].color = (0.0, 0.95, 1.0, 1)
L.new(rr.outputs[0], em.inputs['Color'])
L.new(math_node(N, L, 'MULTIPLY_ADD', info.outputs['Random'], 22.0, 5.0), em.inputs['Strength'])
tr = N.new('ShaderNodeBsdfTransparent')
mix = N.new('ShaderNodeMixShader')
L.new(mask, mix.inputs[0]); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
L.new(mix.outputs[0], outn.inputs['Surface'])
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(0, 0, -50))
drop = bpy.context.object; drop.name = 'Droplet'; drop.data.materials.append(gm)
fo, N2, L2 = mat('Foam')
for n in list(N2):
    if n.type != 'OUTPUT_MATERIAL': N2.remove(n)
fem = N2.new('ShaderNodeEmission')
fem.inputs['Color'].default_value = (0.08, 0.6, 1.0, 1)
fem.inputs['Strength'].default_value = 3.0
L2.new(fem.outputs[0], next(n for n in N2 if n.type == 'OUTPUT_MATERIAL').inputs['Surface'])
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(0, 0, -60))
foamdrop = bpy.context.object; foamdrop.name = 'FoamDrop'; foamdrop.data.materials.append(fo)
SIZES = {'spray': 0.0035, 'foam': 0.005}
for ps in dom.particle_systems:
    s = ps.settings
    key = next((k for k in SIZES if k in ps.name.lower()), None)
    if key is None:                      # the simulator's own internal particles
        s.render_type = 'NONE'; continue
    s.render_type = 'OBJECT'; s.instance_object = foamdrop if key == 'foam' else drop
    s.particle_size = SIZES[key]; s.size_random = 0.5
    print('PSYS', ps.name, s.type)

# ---------- Sand ----------
sm, N, L = mat('Sand')
sb = N['Principled BSDF']
sb.inputs['Base Color'].default_value = (0.010, 0.009, 0.008, 1)
geo = N.new('ShaderNodeNewGeometry')
sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
wet = map_range(N, L, sep.outputs[2], SEA + 0.75, SEA + 0.15, 0.0, 1.0)      # lower sand is wet
L.new(map_range(N, L, wet, 0, 1, 0.75, 0.12), sb.inputs['Roughness'])
tc = N.new('ShaderNodeTexCoord')
n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 90; L.new(tc.outputs['Object'], n1.inputs['Vector'])
bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.25
L.new(n1.outputs[0], bump.inputs['Height']); L.new(bump.outputs[0], sb.inputs['Normal'])
n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 140; L.new(tc.outputs['Object'], n2.inputs['Vector'])
sp = map_range(N, L, n2.outputs[0], 0.66, 0.72, 0.0, 1.0)
L.new(math_node(N, L, 'MULTIPLY', math_node(N, L, 'MULTIPLY', sp, wet), 0.5), sb.inputs['Emission Strength'])
sb.inputs['Emission Color'].default_value = (0.0, 0.55, 1.0, 1)
beach.data.materials.clear(); beach.data.materials.append(sm)
if 'Bar' in bpy.data.objects:
    bpy.data.objects['Bar'].data.materials.clear(); bpy.data.objects['Bar'].data.materials.append(sm)

# A dark sea beyond the simulated area so the water reaches the horizon.
bpy.ops.mesh.primitive_plane_add(size=900, location=(0, 0, SEA - 0.04))
far = bpy.context.object
fm, N, L = mat('FarSea')
fb = N['Principled BSDF']
fb.inputs['Base Color'].default_value = (0.0, 0.004, 0.012, 1); fb.inputs['Roughness'].default_value = 0.12
far.data.materials.append(fm)

# Sand continuing beyond the simulated area, on the same slope as the beach.
bpy.ops.mesh.primitive_plane_add(size=900, location=(1.5, 0, -0.23), rotation=(0, math.atan(3.2/12.5), 0))
bpy.context.object.data.materials.append(sm)

# ---------- Night sky, moonlight, camera ----------
world = bpy.data.worlds.new('Night'); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.0012, 0.0025, 0.007, 1); bg.inputs[1].default_value = 1.0
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(74), 0, math.radians(-70)))
moon = bpy.context.object; moon.data.energy = 0.12; moon.data.color = (0.55, 0.72, 1.0); moon.data.angle = math.radians(4)

bpy.ops.object.empty_add(location=(0.8, 1.2, 1.0)); target = bpy.context.object
bpy.ops.object.camera_add(location=(-6.2, -5.6, 2.9)); cam = bpy.context.object
cam.data.lens = 28
cam.data.dof.use_dof = True; cam.data.dof.focus_object = target; cam.data.dof.aperture_fstop = 5.6
con = cam.constraints.new('TRACK_TO'); con.target = target
con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
scene.camera = cam
if os.environ.get('SIDECAM'):                 # side-on view, to check the wave's curl
    cam.constraints.remove(con)
    cam.location = (2.4, -13.5, 1.5); cam.rotation_euler = (math.radians(90), 0, 0)
    cam.data.lens = 35; cam.data.dof.use_dof = False
    NAME = NAME + '_side'

# ---------- Renderer ----------
samples = int(args[3 if mode == 'anim' else 2]) if len(args) > (3 if mode == 'anim' else 2) else 48
width = int(args[4 if mode == 'anim' else 3]) if len(args) > (4 if mode == 'anim' else 3) else 1280
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'; prefs.get_devices()
for dv in prefs.devices: dv.use = True
scene.cycles.device = 'GPU'
scene.cycles.samples = samples
scene.cycles.use_denoising = True
scene.cycles.sample_clamp_indirect = 4.0
scene.cycles.max_bounces = 6
scene.render.resolution_x, scene.render.resolution_y = width, round(width*9/16)
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
scene.render.use_motion_blur = False

# Soft halo around the bright parts.
try:
    tree = bpy.data.node_groups.new('Glow', 'CompositorNodeTree')
    scene.compositing_node_group = tree
    rl = tree.nodes.new('CompositorNodeRLayers')
    gl = tree.nodes.new('CompositorNodeGlare')
    out = tree.nodes.new('NodeGroupOutput')
    tree.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    tree.links.new(rl.outputs['Image'], gl.inputs['Image'])
    tree.links.new(gl.outputs['Image'], out.inputs[0])
    print('GLARE_INPUTS', [(i.name, i.type) for i in gl.inputs])
    for k, v in (('Type', 'Bloom'), ('Threshold', 0.35), ('Strength', 0.6), ('Size', 0.45), ('Saturation', 1.0)):
        try: gl.inputs[k].default_value = v
        except Exception as ex: print('GLARE_SET', k, ex)
except Exception as ex:
    print('COMP_FAIL', ex)

if mode == 'still':
    f = int(args[1]); scene.frame_set(f)
    ev = dom.evaluated_get(bpy.context.evaluated_depsgraph_get())
    print('ATTRS', [a.name for a in ev.data.attributes], 'VERTS', len(ev.data.vertices))
    print('PCOUNTS', [(ps.name, len(ps.particles)) for ps in ev.particle_systems])
    scene.render.filepath = os.path.join(HERE, f'{NAME}_{f:03d}.png')
    bpy.ops.render.render(write_still=True)
else:
    out = os.path.join(HERE, 'frames_' + NAME); os.makedirs(out, exist_ok=True)
    scene.frame_start, scene.frame_end = int(args[1]), int(args[2])
    scene.render.use_overwrite = False
    scene.render.filepath = os.path.join(out, 'f_')
    bpy.ops.render.render(animation=True)
print('RENDER_DONE')
