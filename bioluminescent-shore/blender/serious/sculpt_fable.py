# A hand-shaped (not simulated) bioluminescent wave that rises, curls into a hollow,
# crashes, and washes up the beach. The wave's cross-section is drawn from a few
# key shapes and blended over time; the break "peels" along the beach.
#
# Run:  Blender --background --factory-startup --python sculpt_fable.py -- still <t> [<t> ...] [samples] [width]
#         t is the moment in the wave's life, 0 = gentle swell, 0.55 = hollow curl, 1 = washed up.
#       Blender --background --factory-startup --python sculpt_fable.py -- anim <frames> [samples] [width]
#         writes frames_fable/f_0001.png ...
import bpy, bmesh, sys, os, math, random

args = sys.argv[sys.argv.index('--') + 1:]
# Optional test switches, e.g.  cam=-7.5,-11,2.4,-1.5,8,0.3,32  tag=a  (camera x,y,z, target x,y,z, lens)
OPT = dict(a.split('=', 1) for a in args if '=' in a)
args = [a for a in args if '=' not in a]
MODE = args[0]
HERE = os.path.dirname(os.path.abspath(__file__))

if MODE == 'still':
    nums = args[1:]
    TS = [float(a) for a in nums if '.' in a]
    rest = [int(a) for a in nums if '.' not in a]
else:
    FRAMES = int(args[1]); rest = [int(a) for a in args[2:]]
SAMPLES = rest[0] if len(rest) > 0 else 32
WIDTH = rest[1] if len(rest) > 1 else 960

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ------------------------------------------------------------------ helpers
def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links

def mnode(N, L, op, a, b=None, c=None):
    n = N.new('ShaderNodeMath'); n.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: L.new(v, n.inputs[i])
    return n.outputs[0]

def mrange(N, L, v, a, b, c, d):
    n = N.new('ShaderNodeMapRange'); n.clamp = True
    L.new(v, n.inputs[0])
    for i, x in zip((1, 2, 3, 4), (a, b, c, d)): n.inputs[i].default_value = x
    return n.outputs[0]

def attr(N, name, vector=False):
    a = N.new('ShaderNodeAttribute'); a.attribute_name = name
    return a.outputs['Vector' if vector else 'Fac']

def emission(N, L, color, strength):
    e = N.new('ShaderNodeEmission')
    if isinstance(color, tuple): e.inputs['Color'].default_value = color
    else: L.new(color, e.inputs['Color'])
    L.new(strength, e.inputs['Strength']) if not isinstance(strength, (int, float)) else None
    if isinstance(strength, (int, float)): e.inputs['Strength'].default_value = strength
    return e.outputs[0]

def add(N, L, a, b):
    s = N.new('ShaderNodeAddShader'); L.new(a, s.inputs[0]); L.new(b, s.inputs[1]); return s.outputs[0]

def specks(N, L, vec, scale, size, density, stretch=None):
    """Tiny glowing points: returns brightness 0..~1 per speck."""
    if stretch:
        sc = N.new('ShaderNodeVectorMath'); sc.operation = 'MULTIPLY'
        L.new(vec, sc.inputs[0]); sc.inputs[1].default_value = stretch; vec = sc.outputs[0]
    v = N.new('ShaderNodeTexVoronoi'); v.voronoi_dimensions = '3D'
    v.inputs['Scale'].default_value = scale
    L.new(vec, v.inputs['Vector'])
    dot = mnode(N, L, 'POWER', mrange(N, L, v.outputs['Distance'], 0.0, size, 1.0, 0.0), 2.0)
    sep = N.new('ShaderNodeSeparateColor'); L.new(v.outputs['Color'], sep.inputs[0])
    keep = mrange(N, L, sep.outputs[1], 1.0 - density - 0.01, 1.0 - density, 0.0, 1.0)
    bright = mrange(N, L, sep.outputs[0], 0.0, 1.0, 0.25, 1.0)
    return mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', dot, keep), bright)

def lace(N, L, vec, scale, width):
    """A broken web of thin, wobbly foam lines, like the lace foam leaves on the water."""
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale * 0.6
    nz.inputs['Detail'].default_value = 5
    L.new(vec, nz.inputs['Vector'])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'VECTOR'; mix.inputs['Factor'].default_value = 0.6
    L.new(vec, mix.inputs['A']); L.new(nz.outputs['Color'], mix.inputs['B'])
    v = N.new('ShaderNodeTexVoronoi'); v.feature = 'DISTANCE_TO_EDGE'; v.voronoi_dimensions = '3D'
    v.inputs['Scale'].default_value = scale
    L.new(mix.outputs['Result'], v.inputs['Vector'])
    br = N.new('ShaderNodeTexNoise'); br.inputs['Scale'].default_value = scale * 0.8
    L.new(vec, br.inputs['Vector'])
    w = mrange(N, L, br.outputs['Fac'], 0.35, 0.65, 0.0, width)          # line thickness varies, gaps appear
    line = mnode(N, L, 'LESS_THAN', v.outputs['Distance'], w)
    soft = mrange(N, L, mnode(N, L, 'DIVIDE', v.outputs['Distance'], mnode(N, L, 'MAXIMUM', w, 0.0001)), 0.0, 1.0, 1.0, 0.0)
    return mnode(N, L, 'MULTIPLY', line, soft)

SPECK_A = (0.0, 0.35, 1.0, 1)      # deep blue specks
SPECK_B = (0.0, 0.85, 1.0, 1)      # cyan specks
TURQ = (0.0, 1.0, 0.80, 1)         # light inside the curl
TURQ_DEEP = (0.0, 0.42, 1.0, 1)    # where the inside light thins out it turns electric blue
FOAM = (0.36, 0.72, 1.0, 1)        # white-blue foam lace

def speck_color(N, L, vec):
    n = N.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 3.0
    L.new(vec, n.inputs['Vector'])
    r = N.new('ShaderNodeValToRGB'); L.new(n.outputs['Fac'], r.inputs[0])
    r.color_ramp.elements[0].position = 0.35; r.color_ramp.elements[0].color = SPECK_A
    r.color_ramp.elements[1].position = 0.65; r.color_ramp.elements[1].color = SPECK_B
    return r.outputs[0]

def dark_water(N):
    b = N['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.0, 0.008, 0.025, 1)
    b.inputs['Roughness'].default_value = 0.07
    b.inputs['IOR'].default_value = 1.33
    return b

# ------------------------------------------------------------------ the wave shape
# Cross-sections in metres (x toward the sea, z up), ordered from the shoreward trough,
# up the face, under the lip, around the lip tip, over the crest and down the back.
STAGES = [
    # far out: a low, long swell rolling in
    (-0.50, [(-6, -.12), (-3, -.11), (-1.5, -.06), (-.7, .02), (-.35, .1), (-.15, .16), (0, .2), (.12, .22), (.3, .22), (1.2, .12), (3, -.02), (6, -.05)]),
    (0.00, [(-6, -.12), (-3, -.1), (-1.5, .0), (-.7, .25), (-.35, .45), (-.15, .62), (0, .72), (.12, .78), (.3, .78), (1.2, .5), (3, .1), (6, -.05)]),
    # face stands up, crest starts to feather
    (0.30, [(-6, -.12), (-3, -.12), (-1.4, -.02), (-.5, .35), (-.15, .85), (-.12, 1.25), (-.3, 1.46), (-.6, 1.4), (-.4, 1.56), (.2, 1.52), (1.6, .62), (6, -.05)]),
    # lip thrown out flat: the tube is wide open underneath
    (0.44, [(-6, -.12), (-3, -.13), (-1.7, -.05), (-.5, .28), (.02, .88), (-.02, 1.45), (-.6, 1.76), (-1.5, 1.5), (-1.2, 1.78), (-.3, 1.9), (1.2, 1.0), (6, -.05)]),
    # thin hollow tube: lip tip hangs well clear of the water so you can see in under it
    (0.58, [(-6, -.12), (-3, -.14), (-1.9, -.06), (-.5, .25), (.12, .9), (.02, 1.55), (-.8, 1.84), (-1.9, .95), (-1.62, 1.62), (-.45, 1.98), (1.0, 1.2), (6, -.05)]),
    # lip lands
    (0.76, [(-6, -.12), (-3, -.12), (-2.3, -.06), (-.7, .22), (-.15, .78), (-.3, 1.3), (-1.0, 1.38), (-2.2, .02), (-1.8, .72), (-.8, 1.46), (.6, .9), (6, -.05)]),
    # collapsed into a low bore of whitewater
    (1.00, [(-6, -.12), (-3.6, -.08), (-2.9, .12), (-2.5, .3), (-2.2, .4), (-2.0, .45), (-1.8, .46), (-1.6, .46), (-1.3, .44), (-.6, .3), (1.0, .1), (6, -.05)]),
    # spent: sinks back into the flat sea
    (1.40, [(-6, -.12), (-3.6, -.12), (-2.9, -.1), (-2.5, -.09), (-2.2, -.08), (-2.0, -.08), (-1.8, -.08), (-1.6, -.08), (-1.3, -.08), (-.6, -.08), (1.0, -.07), (6, -.05)]),
]
P_MIN, P_MAX = STAGES[0][0], STAGES[-1][0]
T_START, T_END = -0.35, 1.75       # the stretch of the wave's life an animation covers
# How strongly each key point glows when the wave is hollow: the face and the tube ceiling, not the outside.
GLOW_W = [0, 0, .12, .6, 1, 1, .9, .45, .03, 0, 0, 0]

def key_points(p):
    for (pa, a), (pb, b) in zip(STAGES, STAGES[1:]):
        if p <= pb:
            t = min(1.0, max(0.0, (p - pa) / (pb - pa)))
            return [(xa + (xb - xa) * t, za + (zb - za) * t) for (xa, za), (xb, zb) in zip(a, b)]
    return STAGES[-1][1]

def catmull(pts, per=10):
    out = []; P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)) + (i - 1 + t,))
    out.append(pts[-1] + (len(pts) - 1,))
    return out

Y0, Y1, NY = -16.0, 34.0, 260
PEEL = [float(v) for v in OPT.get('peel', '0.24,-6,10,0.004').split(',')]
def phase_raw(T, y):
    # Low shore-break: the wave pitches over along most of its length almost at once.
    # Only the stretch nearest the camera lags behind, so the open end of the tube faces us.
    lag, ya, yb, drift = PEEL
    return T - lag * (1 - smooth(ya, yb, y)) + drift * (y - yb) + 0.02 * math.sin(0.35 * y + 1.3)
def phase_at(T, y):
    return min(P_MAX, max(P_MIN, phase_raw(T, y)))

WS = float(OPT.get('ws', 0.75))    # overall wave size (1.0 = about 2 m tall)
def wave_x(p, y):
    return 0.5 - 2.6 * min(p, 1.0) - 0.5 * smooth(1.0, P_MAX, p) + 0.35 * math.sin(0.21 * y) + 0.2 * math.sin(0.5 * y + 2.0)

def height_mul(y):
    return (1.0 + 0.14 * math.sin(0.27 * y + 0.4)) * smooth(Y0, Y0 + 3, y) * (1 - smooth(Y1 - 6, Y1, y))

def build_wave(T):
    me = bpy.data.meshes.new('Wave'); bm = bmesh.new()
    uv_l, glow_l, foam_l = [], [], []
    rows = []
    for j in range(NY + 1):
        y = Y0 + (Y1 - Y0) * j / NY
        p = phase_at(T, y); h = height_mul(y); x0 = wave_x(p, y)
        prof = catmull(key_points(p))
        row = []; s = 0.0; prev = None
        curl = smooth(0.3, 0.5, p) * (1 - smooth(0.7, 0.9, p))          # 1 while the wave is hollow
        steep = 0.10 * smooth(0.05, 0.3, p) * (1 - smooth(0.7, 0.9, p))  # faint teal on the standing face
        for (x, z, k) in prof:
            v = bm.verts.new((x0 + x * WS * (0.6 + 0.4 * h), y, z * WS * h))
            if prev: s += math.hypot(x - prev[0], z - prev[1])
            prev = (x, z)
            ki = min(int(k), len(GLOW_W) - 2); kf = k - ki
            gw = GLOW_W[ki] * (1 - kf) + GLOW_W[ki + 1] * kf
            glow_l.append(gw * (steep + curl) * min(1.0, h))
            lipness = math.exp(-((k - 7.15) / 0.5) ** 2) * smooth(0.33, 0.5, p)      # around the lip tip
            feather = 0.55 * math.exp(-((k - 8.6) / 0.7) ** 2) * smooth(0.15, 0.32, p) * (1 - smooth(0.7, 0.9, p))
            crash = smooth(0.7, 0.92, p) * math.exp(-((k - 6.3) / 2.4) ** 2) * (1 - 0.75 * smooth(1.05, 1.35, p))
            foam_l.append(min(1.0, lipness * (1 - smooth(0.9, 1.0, p)) + feather + crash) * min(1.0, h))
            uv_l.append((s, y))
            row.append(v)
        rows.append(row)
    for j in range(NY):
        a, b = rows[j], rows[j + 1]
        for i in range(len(a) - 1):
            bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
    bm.to_mesh(me); bm.free()
    for name, vals in (('glow', glow_l), ('foam', foam_l)):
        at = me.attributes.new(name, 'FLOAT', 'POINT'); at.data.foreach_set('value', vals)
    at = me.attributes.new('wuv', 'FLOAT_VECTOR', 'POINT')
    at.data.foreach_set('vector', [c for (u, v) in uv_l for c in (u, v, 0.0)])
    for f in me.polygons: f.use_smooth = True
    return me

def lip_spray(T, rng):
    """Points for glowing droplets thrown off the lip and the crashing water."""
    pts = []
    for j in range(0, NY + 1, 1):
        y = Y0 + (Y1 - Y0) * j / NY
        p = phase_at(T, y); h = height_mul(y)
        if h < 0.2: continue
        x0 = wave_x(p, y); kp = key_points(p)
        lx, lz = kp[7]; cx, cz = kp[9]
        # Glow stays on the water: only a thin sprinkle right at the lip tip and where it lands.
        throw = smooth(0.45, 0.6, p) * (1 - smooth(0.8, 0.9, p))
        for _ in range(int(5 * throw * h)):
            pts.append((x0 + (lx + rng.gauss(0, .04)) * WS * (0.6 + 0.4 * h), y + rng.uniform(-.1, .1),
                        (lz * h - abs(rng.gauss(0, .05))) * WS))
        splash = smooth(0.7, 0.8, p) * (1 - smooth(0.88, 0.96, p))
        for _ in range(int(10 * splash * h)):
            pts.append((x0 + (lx + rng.gauss(0, .2)) * WS * (0.6 + 0.4 * h), y + rng.uniform(-.1, .1), abs(rng.gauss(0, .05)) * h * WS))
    return pts

# ------------------------------------------------------------------ materials
GLOW_STR = float(OPT.get('glow', 3.0)); FOAM_STR = float(OPT.get('foam', 3.2))
# Wave water
wm, N, L = mat('WaveWater')
b = dark_water(N)
uvw = attr(N, 'wuv', True); gl = attr(N, 'glow'); fo = attr(N, 'foam')
tc = N.new('ShaderNodeTexCoord')
pat = N.new('ShaderNodeTexNoise'); pat.inputs['Scale'].default_value = 1.2; pat.inputs['Detail'].default_value = 4
L.new(uvw, pat.inputs['Vector'])
patchy = mrange(N, L, pat.outputs['Fac'], 0.35, 0.7, 0.35, 1.0)
# light inside the hollow: streaked down the face, turquoise at its core and electric blue where it thins
stv = N.new('ShaderNodeVectorMath'); stv.operation = 'MULTIPLY'; stv.inputs[1].default_value = (0.5, 7.0, 1.0)
L.new(uvw, stv.inputs[0])
stn = N.new('ShaderNodeTexNoise'); stn.inputs['Scale'].default_value = 1.0; stn.inputs['Detail'].default_value = 3
L.new(stv.outputs[0], stn.inputs['Vector'])
streak = mrange(N, L, stn.outputs['Fac'], 0.3, 0.72, 0.3, 1.0)
gv = mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', gl, patchy), streak)
gramp = N.new('ShaderNodeValToRGB'); L.new(gv, gramp.inputs[0])
gramp.color_ramp.elements[0].position = 0.05; gramp.color_ramp.elements[0].color = TURQ_DEEP
gramp.color_ramp.elements[1].position = 0.5; gramp.color_ramp.elements[1].color = TURQ
glow = emission(N, L, gramp.outputs[0], mnode(N, L, 'MULTIPLY', mnode(N, L, 'POWER', gv, 1.5), GLOW_STR))
wpos = tc.outputs['Object']
fine = mnode(N, L, 'ADD', specks(N, L, wpos, 24, 0.17, 0.85), specks(N, L, wpos, 52, 0.2, 0.75))
sp = mnode(N, L, 'ADD', mnode(N, L, 'ADD', specks(N, L, wpos, 13, 0.14, 0.7), specks(N, L, wpos, 10, 0.12, 0.7, stretch=(1.0, 1.0, 0.3))), fine)
# streaky specks running down the face inside the hollow
sp = mnode(N, L, 'ADD', sp, mnode(N, L, 'MULTIPLY', specks(N, L, uvw, 16, 0.2, 0.8, stretch=(0.22, 1.0, 1.0)), mnode(N, L, 'MULTIPLY', gl, 2.0)))
# sparkle is densest where the water is churned: the lip and the crashing front
sp = mnode(N, L, 'MULTIPLY', sp, mnode(N, L, 'MULTIPLY_ADD', mnode(N, L, 'MAXIMUM', fo, gl), 1.3, 0.6))
sp_e = emission(N, L, speck_color(N, L, uvw), mnode(N, L, 'MULTIPLY', sp, 26.0))
# foam: clumps of solid froth plus a web of lace
lc = mnode(N, L, 'MAXIMUM', lace(N, L, uvw, 12.0, 0.05), mnode(N, L, 'MULTIPLY', lace(N, L, uvw, 30.0, 0.06), 0.7))
fz = N.new('ShaderNodeTexNoise'); fz.inputs['Scale'].default_value = 5.0; fz.inputs['Detail'].default_value = 6
L.new(uvw, fz.inputs['Vector'])
froth = mnode(N, L, 'MULTIPLY', mrange(N, L, fz.outputs['Fac'], 0.42, 0.6, 0.0, 1.0), mnode(N, L, 'POWER', fo, 2.0))
foamv = mnode(N, L, 'MULTIPLY', fo, mnode(N, L, 'MAXIMUM', lc, mnode(N, L, 'MULTIPLY', froth, 0.8)))
fm_e = emission(N, L, FOAM, mnode(N, L, 'MULTIPLY', foamv, FOAM_STR))
out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
L.new(add(N, L, add(N, L, add(N, L, b.outputs[0], glow), sp_e), fm_e), out.inputs['Surface'])

# Sea (around and beyond the wave) with lace foam near the shore
sm_, N, L = mat('Sea')
b = dark_water(N)
tc = N.new('ShaderNodeTexCoord'); pos = tc.outputs['Object']
near = attr(N, 'near'); lacew = attr(N, 'lace')
dn = N.new('ShaderNodeTexNoise'); dn.inputs['Scale'].default_value = 0.35; dn.inputs['Detail'].default_value = 3
L.new(pos, dn.inputs['Vector'])
drift = mrange(N, L, dn.outputs['Fac'], 0.3, 0.7, 0.25, 1.0)          # sparkle gathers in loose drifts
sp = mnode(N, L, 'ADD', mnode(N, L, 'ADD', specks(N, L, pos, 9, 0.13, 0.55), specks(N, L, pos, 21, 0.17, 0.7)), specks(N, L, pos, 46, 0.2, 0.6))
sp = mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', sp, near), drift)
sp_e = emission(N, L, speck_color(N, L, pos), mnode(N, L, 'MULTIPLY', sp, 28.0))
lc = lace(N, L, pos, 7.0, 0.035)
lnz = N.new('ShaderNodeTexNoise'); lnz.inputs['Scale'].default_value = 0.6; L.new(pos, lnz.inputs['Vector'])
lmask = mnode(N, L, 'MULTIPLY', lacew, mrange(N, L, lnz.outputs['Fac'], 0.45, 0.62, 0.0, 1.0))
lc_e = emission(N, L, FOAM, mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', lc, lmask), 1.4))
rip = N.new('ShaderNodeTexNoise'); rip.inputs['Scale'].default_value = 6; rip.inputs['Detail'].default_value = 6
L.new(pos, rip.inputs['Vector'])
bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.15
L.new(rip.outputs['Fac'], bump.inputs['Height']); L.new(bump.outputs[0], b.inputs['Normal'])
out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
L.new(add(N, L, add(N, L, b.outputs[0], sp_e), lc_e), out.inputs['Surface'])

# Thin water washing up the sand: a foam sheet with a thick, lumpy, bright lace edge
swm, N, L = mat('Swash')
b = dark_water(N); b.inputs['Roughness'].default_value = 0.04
tc = N.new('ShaderNodeTexCoord'); pos = tc.outputs['Object']
dist = attr(N, 'dist'); power = attr(N, 'power'); depth = attr(N, 'edge')
wn = N.new('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value = 2.2; wn.inputs['Detail'].default_value = 4
L.new(pos, wn.inputs['Vector'])
rimw = mrange(N, L, wn.outputs['Fac'], 0.3, 0.7, 0.07, 0.30)                    # the foam rim is 7 to 30 cm wide
rim = mrange(N, L, mnode(N, L, 'DIVIDE', dist, rimw), 0.25, 1.0, 1.0, 0.0)
band = mrange(N, L, dist, 0.1, 2.6, 1.0, 0.0)                                   # lace is thickest just behind the rim
lc = mnode(N, L, 'MAXIMUM', lace(N, L, pos, 6.0, 0.05), mnode(N, L, 'MULTIPLY', lace(N, L, pos, 15.0, 0.06), 0.8))
lnz = N.new('ShaderNodeTexNoise'); lnz.inputs['Scale'].default_value = 0.8; L.new(pos, lnz.inputs['Vector'])
holes = mrange(N, L, lnz.outputs['Fac'], 0.38, 0.6, 0.15, 1.0)
sheet = mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', lc, holes), mnode(N, L, 'MULTIPLY_ADD', band, 0.8, 0.2))
foamy = mnode(N, L, 'MAXIMUM', mnode(N, L, 'MULTIPLY', rim, mnode(N, L, 'MULTIPLY_ADD', lc, 0.4, 0.75)), mnode(N, L, 'MULTIPLY', sheet, 0.8))
lc_e = emission(N, L, FOAM, mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', foamy, power), FOAM_STR))
sp = mnode(N, L, 'ADD', mnode(N, L, 'ADD', specks(N, L, pos, 7, 0.13, 0.5), specks(N, L, pos, 19, 0.17, 0.75)), specks(N, L, pos, 44, 0.2, 0.65))
sp = mnode(N, L, 'MULTIPLY', sp, mnode(N, L, 'MULTIPLY_ADD', mnode(N, L, 'MAXIMUM', band, rim), 0.9, 0.35))
sp_e = emission(N, L, speck_color(N, L, pos), mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', sp, power), 30.0))
# a little of the turquoise light carried up the sand in the rushing water
tq_e = emission(N, L, TURQ_DEEP, mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', band, attr(N, 'rush')), 0.10))
out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
L.new(add(N, L, add(N, L, add(N, L, b.outputs[0], lc_e), sp_e), tq_e), out.inputs['Surface'])

# Wet sand, a few glowing grains
sandm, N, L = mat('Sand')
b = N['Principled BSDF']
b.inputs['Base Color'].default_value = (0.012, 0.011, 0.010, 1)
tc = N.new('ShaderNodeTexCoord'); pos = tc.outputs['Object']
wet = attr(N, 'wet')
L.new(mrange(N, L, wet, 0, 1, 0.7, 0.12), b.inputs['Roughness'])
n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 40; L.new(pos, n1.inputs['Vector'])
bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.3
L.new(n1.outputs['Fac'], bump.inputs['Height']); L.new(bump.outputs[0], b.inputs['Normal'])
sp = mnode(N, L, 'MULTIPLY', specks(N, L, pos, 6, 0.1, 0.2), wet)
sp_e = emission(N, L, SPECK_A, mnode(N, L, 'MULTIPLY', sp, 10.0))
out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
L.new(add(N, L, b.outputs[0], sp_e), out.inputs['Surface'])

# Glowing droplets
dm, N, L = mat('Droplet')
for n in list(N):
    if n.type != 'OUTPUT_MATERIAL': N.remove(n)
info = N.new('ShaderNodeObjectInfo')
rr = N.new('ShaderNodeValToRGB'); L.new(info.outputs['Random'], rr.inputs[0])
rr.color_ramp.elements[0].color = SPECK_A; rr.color_ramp.elements[1].color = SPECK_B
e = emission(N, L, rr.outputs[0], mnode(N, L, 'MULTIPLY_ADD', info.outputs['Random'], 30.0, 10.0))
L.new(e, next(n for n in N if n.type == 'OUTPUT_MATERIAL').inputs['Surface'])

rockm, N, L = mat('Rock')
b = N['Principled BSDF']; b.inputs['Base Color'].default_value = (0.006, 0.006, 0.007, 1); b.inputs['Roughness'].default_value = 0.18

# ------------------------------------------------------------------ fixed scenery
SHORE = -4.2                       # where still water meets the sand
SLOPE = 0.075
def sand_z(x, y):
    return SLOPE * (SHORE - x) + 0.05 * math.sin(0.7 * y + 0.3 * x) + 0.03 * math.sin(1.9 * y + 1.0)

def grid(name, x0, x1, y0, y1, nx, ny, zf, attrs):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); vals = {k: [] for k in attrs}
    vs = []
    for j in range(ny + 1):
        y = y0 + (y1 - y0) * j / ny; row = []
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * (i / nx) ** 1.0
            row.append(bm.verts.new((x, y, zf(x, y))))
            for k, f in attrs.items(): vals[k].append(f(x, y))
        vs.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    bm.to_mesh(me); bm.free()
    for k, v in vals.items():
        a = me.attributes.new(k, 'FLOAT', 'POINT'); a.data.foreach_set('value', v)
    for f in me.polygons: f.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob

sand = grid('Sand', -40, 4, -30, 50, 220, 300, sand_z,
            {'wet': lambda x, y: 1 - smooth(SHORE - 6, SHORE - 2.5, x)})
sand.data.materials.append(sandm)

def sea_z(x, y):
    far = smooth(6, 30, x)
    return 0.12 * far * (math.sin(0.55 * x + 0.13 * y) + 0.6 * math.sin(0.9 * x - 0.31 * y + 1.0) + 0.4 * math.sin(1.7 * x + 0.5 * y))
sea = grid('Sea', SHORE - 0.5, 90, -40, 70, 360, 300, sea_z,
           {'near': lambda x, y: 1 - smooth(10, 40, x),
            'lace': lambda x, y: smooth(SHORE - 0.3, SHORE + 0.4, x) * (1 - smooth(SHORE + 1.2, SHORE + 3.0, x))})
sea.data.materials.append(sm_)

NOW = [0.0]
RUN_MAX = float(OPT.get('run', 3.6))
def swash_state(y):
    """How far the sheet has run up the sand (0..1) and how lively its foam is, for this stretch of beach."""
    p = phase_raw(NOW[0], y)
    up = smooth(0.84, 1.14, p); back = smooth(1.16, 1.6, p)
    return up * (1 - 0.8 * back), 0.45 + 0.55 * up * (1 - 0.75 * back), up * (1 - back)
def swash_edge(y):     # how far up the sand the thin water reaches
    run, _, _ = swash_state(y)
    lobes = 0.7 * math.sin(0.33 * y + 0.5) + 0.35 * math.sin(0.9 * y) + 0.16 * math.sin(2.3 * y + 1.0) + 0.08 * math.sin(5.1 * y)
    return SHORE - 1.2 - RUN_MAX * run + lobes * (0.7 + 0.6 * run)
def swash_build():
    me = bpy.data.meshes.new('Swash'); bm = bmesh.new(); ed = []; di = []; pw = []; ru = []; rows = []
    NX = 60
    for j in range(401):
        y = -30 + 80 * j / 400; xe = swash_edge(y); row = []
        _, power, rush = swash_state(y)
        for i in range(NX + 1):
            t = (i / NX) ** 1.6; x = xe + (SHORE + 0.3 - xe) * t          # finer near the leading edge
            row.append(bm.verts.new((x, y, max(sand_z(x, y) + 0.012, 0.0))))
            ed.append(1 - t); di.append(x - xe); pw.append(power); ru.append(rush)
        rows.append(row)
    for j in range(400):
        for i in range(NX):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    bm.to_mesh(me); bm.free()
    for name, vals in (('edge', ed), ('dist', di), ('power', pw), ('rush', ru)):
        a = me.attributes.new(name, 'FLOAT', 'POINT'); a.data.foreach_set('value', vals)
    for f in me.polygons: f.use_smooth = True
    me.materials.append(swm)
    return me
swash_ob = bpy.data.objects.new('Swash', swash_build()); scene.collection.objects.link(swash_ob)

rng0 = random.Random(7)
for (x, y, r) in [(-8.2, -9.6, 0.35), (-7.0, -7.4, 0.22), (-9.5, -6.0, 0.28), (-6.6, -10.3, 0.18), (-8.8, -3.5, 0.2)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, sand_z(x, y) - r * 0.35), segments=24, ring_count=12)
    ob = bpy.context.object; ob.scale = (1.2 + rng0.random() * .4, 1.0, 0.55); ob.data.materials.append(rockm)
    for f in ob.data.polygons: f.use_smooth = True

drops = []
for k, r in enumerate((0.0035, 0.005, 0.0075)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=(0, 0, -50))
    d = bpy.context.object; d.name = 'Drop%d' % k; d.data.materials.append(dm); drops.append(d)

# ------------------------------------------------------------------ sky, moon, camera, renderer
world = bpy.data.worlds.new('Night'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.0010, 0.0022, 0.0065, 1)
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(70), 0, math.radians(-60)))
moon = bpy.context.object; moon.data.energy = 0.15; moon.data.color = (0.55, 0.72, 1.0); moon.data.angle = math.radians(3)

CAM = [float(v) for v in OPT.get('cam', '-7.5,-12,2.3,-2.2,6,0.35,32').split(',')]
bpy.ops.object.empty_add(location=CAM[3:6]); target = bpy.context.object
bpy.ops.object.camera_add(location=CAM[0:3]); cam = bpy.context.object
cam.data.lens = CAM[6]
cam.data.dof.use_dof = True; cam.data.dof.focus_object = target; cam.data.dof.aperture_fstop = 4.0
con = cam.constraints.new('TRACK_TO'); con.target = target; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
scene.camera = cam

scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'; prefs.get_devices()
for dv in prefs.devices: dv.use = True
scene.cycles.device = 'GPU'
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.sample_clamp_indirect = 4.0
scene.cycles.max_bounces = 6
scene.render.resolution_x, scene.render.resolution_y = WIDTH, round(WIDTH * 9 / 16)
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
try:
    tree = bpy.data.node_groups.new('Glow', 'CompositorNodeTree')
    scene.compositing_node_group = tree
    rl = tree.nodes.new('CompositorNodeRLayers'); g = tree.nodes.new('CompositorNodeGlare'); o = tree.nodes.new('NodeGroupOutput')
    tree.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    tree.links.new(rl.outputs['Image'], g.inputs['Image']); tree.links.new(g.outputs['Image'], o.inputs[0])
    for k, v in (('Type', 'Bloom'), ('Threshold', 0.35), ('Strength', 0.6), ('Size', 0.45), ('Saturation', 1.0)):
        try: g.inputs[k].default_value = v
        except Exception as ex: print('GLARE_SET', k, ex)
except Exception as ex:
    print('COMP_FAIL', ex)

# ------------------------------------------------------------------ per-moment objects
wave_ob = bpy.data.objects.new('Wave', bpy.data.meshes.new('tmp')); scene.collection.objects.link(wave_ob)
spray_obs = []
for k, d in enumerate(drops):
    ob = bpy.data.objects.new('Spray%d' % k, bpy.data.meshes.new('tmp')); scene.collection.objects.link(ob)
    ob.instance_type = 'VERTS'; d.parent = ob; d.location = (0, 0, 0); spray_obs.append(ob)

def set_moment(T, seed):
    NOW[0] = T
    old = swash_ob.data; swash_ob.data = swash_build(); bpy.data.meshes.remove(old)
    old = wave_ob.data; wave_ob.data = build_wave(T); wave_ob.data.materials.append(wm); bpy.data.meshes.remove(old)
    rng = random.Random(seed)
    pts = lip_spray(T, rng); groups = [[], [], []]
    for pnt in pts: groups[min(2, int(rng.random() ** 2.2 * 3))].append(pnt)
    for ob, g in zip(spray_obs, groups):
        old = ob.data; me = bpy.data.meshes.new('pts'); me.from_pydata(g, [], []); ob.data = me; bpy.data.meshes.remove(old)

if MODE == 'still':
    for T in TS:
        set_moment(T, int(T * 1000))
        scene.render.filepath = os.path.join(HERE, 'fable_%s%03d.png' % (OPT.get('tag', ''), round(T * 100)))
        if 'dry' not in OPT: bpy.ops.render.render(write_still=True)   # dry=1 builds the scene without rendering
        print('STILL_DONE', T)
else:
    outdir = os.path.join(HERE, 'frames_fable'); os.makedirs(outdir, exist_ok=True)
    for f in range(1, FRAMES + 1):
        path = os.path.join(outdir, 'f_%04d.png' % f)
        if os.path.exists(path): continue
        set_moment(T_START + (T_END - T_START) * (f - 1) / (FRAMES - 1), f)
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print('FRAME_DONE', f)
print('RENDER_DONE')
