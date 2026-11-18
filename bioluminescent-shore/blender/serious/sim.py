# Step 1 of 2: simulate real water breaking on a sloped beach.
# A tall block of water at the far end collapses, sends a wave across a shallow
# sea, and the wave breaks when it reaches the rising sand.
#
# Run:  Blender --background --python sim.py -- <detail> <last_frame> <name>
#       e.g.  ... -- 64 60 test      (quick test)
#             ... -- 200 144 final   (full detail)
import bpy, bmesh, sys, os, time

args = sys.argv[sys.argv.index('--') + 1:]
RES, END, NAME = int(args[0]), int(args[1]), args[2]
HERE = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(HERE, NAME + '.blend')
CACHE = os.path.join(HERE, 'cache_' + NAME)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, END

# Sizes in metres. X runs from the beach (-8) out to sea (+8).
DX, DY, DZ = 20.0, 12.0, 5.0
SEA = 1.0            # still water level
TOE = 1.5            # where the sand starts rising
TOP = 3.0            # sand height at the back of the beach


def box(name, x0, x1, y0, y1, z0, z1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    o = bpy.context.object; o.name = name
    o.scale = (x1-x0, y1-y0, z1-z0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return o


# The simulation box.
dom = box('Domain', -DX/2, DX/2, -DY/2, DY/2, 0, DZ)
dm = dom.modifiers.new('Fluid', 'FLUID'); dm.fluid_type = 'DOMAIN'
d = dm.domain_settings
d.domain_type = 'LIQUID'
d.resolution_max = RES
d.time_scale = 1.0
d.use_adaptive_timesteps = True
d.timesteps_max = 4; d.timesteps_min = 1
d.flip_ratio = 0.97
d.use_fractions = True
d.use_mesh = True
d.mesh_generator = 'IMPROVED'
d.mesh_scale = 2
d.mesh_particle_radius = 1.7
d.use_speed_vectors = True
d.use_spray_particles = True
d.use_foam_particles = True
d.use_bubble_particles = False
d.sndparticle_sampling_wavecrest = 45
d.sndparticle_sampling_trappedair = 16
d.sndparticle_life_min = 12
d.sndparticle_life_max = 22
d.sndparticle_boundary = 'DELETE'
d.cache_type = 'ALL'
d.cache_directory = CACHE
d.cache_frame_start = 1
d.cache_frame_end = END

# Shallow sea across the whole box, plus a tall block of water at the far end.
# The surge is split into uneven pieces so the wave breaks unevenly along the beach.
# Each piece has a slow bottom layer and a fast top layer: the top outruns the
# bottom, which is what makes a wave pitch over into a curl.
segs = [(-6.0, -3.0, 7.3, 2.2), (-3.0, 0.0, 6.9, 2.38), (0.0, 3.0, 7.2, 2.25), (3.0, 6.0, 7.6, 2.12)]
SPLIT = SEA + 0.5
blocks = [('Sea', (-DX/2+.05, DX/2-.05, -DY/2+.05, DY/2-.05, 0.02, SEA), None)]
for i, (y0, y1, x0, h) in enumerate(segs):
    yy = (max(y0, -DY/2+.05), min(y1, DY/2-.05))
    blocks.append(('SurgeLow%d' % i, (x0, DX/2-.05) + yy + (SEA, SPLIT), (-1.3, 0.0, 0.0)))
    blocks.append(('SurgeTop%d' % i, (x0 - 0.3, DX/2-.05) + yy + (SPLIT, h), (-3.4, 0.0, 0.0)))
# The beach: a solid wedge of sand rising toward -X, with a gently wavy edge.
# In front of it sits a shallow sandbar with a sloping seaward face: the bottom of
# the wave trips on the step while the top keeps going, so the wave plunges and curls.
def prism(name, profile_fn):
    """A solid strip of sand along Y whose cross-section (in X/Z) is given by profile_fn(y)."""
    me = bpy.data.meshes.new(name); ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    bm = bmesh.new(); rows = []
    for i in range(N+1):
        y = -DY/2 - 1 + (DY+2)*i/N
        rows.append([bm.verts.new((x, y, z)) for x, z in profile_fn(y)])
    for i in range(N):
        a, b = rows[i], rows[i+1]
        for k in range(len(a)):
            k2 = (k + 1) % len(a)
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    bm.faces.new(rows[0]); bm.faces.new(tuple(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    em = ob.modifiers.new('Fluid', 'FLUID'); em.fluid_type = 'EFFECTOR'
    em.effector_settings.effector_type = 'COLLISION'
    em.effector_settings.surface_distance = 0.0
    return ob

import math
N = 32
SLOPE = (TOP + 0.2) / (TOE + DX/2 + 1)     # same beach slope as before
BAR = 0.5                                  # height of the sandbar top (water there is 0.5 m deep)
toe_at = lambda y: TOE + 0.55*math.sin(y*0.9) + 0.3*math.sin(y*2.1+1.0)
# Each piece is a simple convex shape; one bent shape made the simulation blow up.
beach = prism('Beach', lambda y: [(toe_at(y), -0.2), (-DX/2-1, TOP), (-DX/2-1, -0.2)])
def bar_profile(y):
    toe = toe_at(y); meet = toe - (BAR + 0.2)/SLOPE - 0.6     # tucks into the beach
    return [(toe + 3.6, -0.2), (toe + 1.4, BAR), (meet, BAR), (meet, -0.2)]
bar = prism('Bar', bar_profile)

# Water: added after the sand so the starting sea can be cut around it.
for name, b, v in blocks:
    o = box(name, *b)
    if name == 'Sea':                     # don't start with water trapped inside the sand
        bo = o.modifiers.new('CutSand', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = beach; bo.solver = 'EXACT'
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=bo.name)
        bo = o.modifiers.new('CutBar', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = bar; bo.solver = 'EXACT'
        bpy.ops.object.modifier_apply(modifier=bo.name)
    fm = o.modifiers.new('Fluid', 'FLUID'); fm.fluid_type = 'FLOW'
    fm.flow_settings.flow_type = 'LIQUID'
    fm.flow_settings.flow_behavior = 'GEOMETRY'
    if v:
        fm.flow_settings.use_initial_velocity = True
        fm.flow_settings.velocity_coord = v
    o.hide_render = True


bpy.ops.wm.save_as_mainfile(filepath=BLEND)
t = time.time()
bpy.context.view_layer.objects.active = dom
with bpy.context.temp_override(object=dom, active_object=dom, selected_objects=[dom]):
    print('BAKE', bpy.ops.fluid.bake_all())
print('BAKE_SECONDS', round(time.time()-t))
bpy.ops.wm.save_mainfile()
print('SIM_DONE', d.has_cache_baked_data, d.has_cache_baked_mesh, d.has_cache_baked_particles)
