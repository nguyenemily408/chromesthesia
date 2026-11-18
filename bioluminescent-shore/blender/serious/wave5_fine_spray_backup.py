# One big bioluminescent wave: dark choppy sea, a wave that steepens, curls,
# crashes into glowing foam and washes up the sand. Hand-built (not simulated)
# so every part can later be driven by music.
#
# Run:  Blender --background --factory-startup --python wave2.py -- still <samples> <width> <t> [<t> ...]
#           t = moment in the clip, 0 = start, 1 = end.  Writes w5_<t>.png
#       Blender --background --factory-startup --python wave2.py -- anim <samples> <width> <first> <last>
#           writes frames_w5/f_0001.png ...
import bpy, sys, os, math
import numpy as np

args = sys.argv[sys.argv.index('--') + 1:]
MODE, SAMPLES, WIDTH = args[0], int(args[1]), int(args[2])
HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES, FPS, DUR = 168, 24, 7.0
rng = np.random.default_rng(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

SLOPE = 0.07                     # sand rises 7 cm per metre up the beach
def sand_z(y): return -SLOPE * y

def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0); return t * t * (3 - 2 * t)

def lerp(a, b, t): return a + (b - a) * t

# ------------------------------------------------------------------ the wave
# x runs along the beach (camera looks toward -x), y runs out to sea, z is up.
NX = 440
ux = np.linspace(0, 1, NX)
X = 9.0 - 75.0 * ux ** 1.35                      # denser near the camera
NA, NB, ND, NE = 110, 90, 50, 150
NP = NA + NB + ND + NE
GA = np.concatenate([np.linspace(-8, -3.6, 12, endpoint=False), np.linspace(-3.6, 2.2, 70, endpoint=False),
                     np.linspace(2.2, 12, 28)])

def xnoise(x, seed, scale):
    r = np.random.default_rng(seed); out = np.zeros_like(x)
    for i in range(5):
        k = (0.6 + 1.7 * i) / scale
        out += np.sin(x * k + r.uniform(0, 6.28)) / (1 + 0.6 * i)
    return out / 2.0

N_W2, N_AMP2 = xnoise(X, 11, 6.0), xnoise(X, 12, 3.0)
N_A2B = xnoise(X, 13, 1.3)                     # shorter bumps along the second wave so its crest is uneven
N_LOBE = xnoise(X, 14, 0.9)                    # lobes along the broken wave's foam front
N_STAGE, N_AMP, N_PHI, N_PHI2 = xnoise(X, 1, 7.0), xnoise(X, 2, 5.0), xnoise(X, 3, 1.6), xnoise(X, 4, 0.5)

def stage_at(x, tn, ns):
    return 0.3 + 1.2 * tn - 0.0115 * np.abs(x - 3.0) + 0.07 * ns

def wave_params(S, namp, nphi):
    A = np.interp(S, [0, .25, .45, .62, .8, 1.0, 1.3], [.38, .8, 1.2, 1.15, .7, .3, .05]) * (1 + 0.28 * namp)
    a = A * np.interp(S, [0, .25, .45, .62], [3.2, 1.6, .64, .56])
    b = A / 2
    phim = np.interp(S, [0, .25, .4, .5, .58, .64], [-35, -5, 60, 130, 200, 262]) + 22 * nphi * smooth(.36, .5, S)
    yc = np.interp(S, [0, .5, .64, .85, 1.0, 1.4], [11.5, 3.0, 1.7, -0.3, -1.3, -1.6])
    return A, a, b, np.radians(phim), yc

# small wind chop: a sum of travelling ripples
CH = []
for i in range(30):
    lam = 0.35 * (18.0) ** rng.uniform(0, 1)
    k = 2 * math.pi / lam; ang = math.radians(rng.normal(-90, 42))
    CH.append((k * math.cos(ang), k * math.sin(ang), math.sqrt(9.8 * k), rng.uniform(0, 6.28), 0.007 * lam ** 0.9))
def throw(phi, A):
    # the lip is flung forward as it falls, so it lands on the sand in front of the wave, not back on its own face
    return 0.55 * A * smooth(math.radians(100), math.radians(250), phi)

def chop(x, y, t):
    z = np.zeros_like(y)
    for kx, ky, w, ph, amp in CH:
        z += amp * np.sin(kx * x + ky * y - w * t + ph)
    return z

def runup_line(x, S, t):
    R = np.interp(S, [0, .35, .6, .7, .8, 1.0, 1.15, 1.5], [0, -0.3, -0.9, -0.5, 0.6, 3.0, 2.8, 0.6])
    lobes = 0.32 * np.sin(x * 0.9 + 1.0) + 0.2 * np.sin(x * 2.3 + 0.4 * t) + 0.1 * np.sin(x * 5.1 - 0.7 * t) + 0.06 * np.sin(x * 11.0 + 1.3 * t) + 0.04 * np.sin(x * 23.0 - 2.0 * t)
    return lobes * (1 + 0.8 * smooth(.8, 1, S)) - R * (1 + 0.25 * np.sin(x * 0.6 + 2.0)) - 0.12 * np.sin(t * 0.9 + x * 0.3)

def build(tn):
    t = tn * DUR
    S = stage_at(X, tn, N_STAGE)[:, None]
    A, a, b, phim, yc = wave_params(S, N_AMP[:, None], N_PHI[:, None] + 0.5 * N_PHI2[:, None])
    z0 = -0.05; zc = z0 + b
    c = smooth(.64, .72, S)                                   # 0 = curling wave, 1 = collapsed foam bore
    x2 = np.broadcast_to(X[:, None], (NX, NP)).copy()

    # --- curling shape
    fb = np.linspace(0, 1, NB)[None, :]
    phiB = lerp(-math.pi / 2, phim, fb)
    yB, zB = yc + a * np.cos(phiB) - throw(phiB, A), zc + b * np.sin(phiB)
    kd = np.linspace(0, 1, ND)[None, :]
    over = np.maximum(phim - math.radians(60), 0)
    phiD = phim - kd * over
    tau = (0.045 + (0.28 * A - 0.045) * kd ** 0.8) * smooth(math.radians(60), math.radians(95), phim)
    yD, zD = yc + (a + tau) * np.cos(phiD) - throw(phiD, A), zc + (b + tau) * np.sin(phiD)
    toe_c = yc + 0 * fb[:, :1]
    # --- foam bore shape
    af = (0.75 * A + 0.15) * (1 + 0.45 * N_LOBE[:, None] + 0.2 * xnoise(X * 2.3 + 1.5 * t, 15, 1.0)[:, None])
    hb = 1 + 0.35 * xnoise(X * 1.7 - 2.2 * t, 16, 1.0)[:, None]          # the tumbling roll is taller in some places
    th = fb * math.pi / 2
    yBb, zBb = yc - af * np.cos(th), z0 + (A + 0.05) * hb * np.sin(th) ** 0.8
    yDb, zDb = yc + 0.45 * A * kd, z0 + (A + 0.05) * hb * (1 - 0.12 * kd)
    toe_b = yc - af
    yB, zB = lerp(yB, yBb, c), lerp(zB, zBb, c)
    yD, zD = lerp(yD, yDb, c), lerp(zD, zDb, c)
    toe = lerp(toe_c, toe_b, c)
    # --- back of the wave, out to sea
    qe = np.linspace(0, 1, NE)[None, :]
    yb, zb = yD[:, -1:], zD[:, -1:]
    dE = 0.02 + (60.0 - yb) * qe ** 1.8
    Lb = 1.3 + 1.6 * A + 2.0 * c
    yE, zE = yb + dE, zb / (1 + (dE / Lb) ** 2) ** 1.2
    # --- a second wave following behind
    y2 = lerp(25.0, 8.5, tn) + 0.9 * N_W2[:, None]
    A2 = lerp(0.3, 0.85, smooth(0, 1, tn)) * np.clip(1 + 0.45 * N_AMP2[:, None] + 0.25 * N_A2B[:, None], 0.25, 2)
    d2 = yE - y2
    zE = zE + A2 * np.where(d2 < 0, np.exp(-(d2 / lerp(2.6, 1.6, tn)) ** 2), np.exp(-(d2 / 3.6) ** 2))
    # --- flat water and thin swash in front of the wave
    yA = np.minimum(GA[None, :], toe)
    dA = toe - yA
    yr = runup_line(X, S[:, 0], t)[:, None]
    sheet = 0.06 * np.clip((yA - yr) / 0.6, 0, 1)
    zA = np.where(yA > yr, np.maximum(z0 * np.exp(-dA / 0.8) * (1 - c), sand_z(yA) + sheet), sand_z(yA) - 0.04)

    Y = np.concatenate([yA, yB, yD, yE], 1); Z = np.concatenate([zA, zB, zD, zE], 1)
    for _ in range(3):                                         # round off any sharp corners
        Y[:, 1:-1] = 0.5 * Y[:, 1:-1] + 0.25 * (Y[:, :-2] + Y[:, 2:])
        Z[:, 1:-1] = 0.5 * Z[:, 1:-1] + 0.25 * (Z[:, :-2] + Z[:, 2:])
    yA2 = Y[:, :NA]; Z[:, :NA] = np.where(yA2 > yr, np.maximum(Z[:, :NA], sand_z(yA2) + 0.06 * np.clip((yA2 - yr) / 0.6, 0, 1)), sand_z(yA2) - 0.04)

    Z[:, NA:] = np.maximum(Z[:, NA:], sand_z(Y[:, NA:]) + 0.02)
    # chop everywhere except the glassy face of the curl
    cm = np.ones((NX, NP))
    cm[:, :NA] = smooth(0.2, 3.5, Y[:, :NA])
    cm[:, NA:NA + NB] = lerp(lerp(1.0, 0.12, smooth(0, 0.3, fb)), 1.3, c); cm[:, NA + NB:NA + NB + ND] = lerp(0.12, 1.3, c)
    cm[:, NA + NB + ND:] = lerp(lerp(0.12, 1.0, smooth(0, 1.2, dE)), 1.0, c)
    cz = chop(x2, Y, t)
    Z += cz * cm
    lump = xnoise(X * 3.1 + 2.0 * t, 9, 1.0)[:, None] * 0.14 * c * np.sin(np.linspace(0, math.pi, NP))[None, :]
    Z[:, NA:NA + NB + ND] += lump[:, NA:NA + NB + ND]

    # --- where it glows, where it foams
    glow = np.zeros((NX, NP)); foam = np.zeros((NX, NP))
    env = smooth(.05, .45, S) * (1 - smooth(.68, .84, S))
    fade = 1 - 0.75 * smooth(1.0, 1.45, S)
    lip = smooth(.4, .5, S)
    sB, sD = slice(NA, NA + NB), slice(NA + NB, NA + NB + ND)
    glow[:, sB] = env * (0.06 + 0.94 * np.exp(-((phiB - math.radians(5)) / math.radians(50)) ** 2))
    inside = smooth(.42, .55, S) * (1 - smooth(.7, .84, S)) * smooth(0.3, 0.75, fb)      # light the roof of the tube
    glow[:, sB] = np.maximum(glow[:, sB], 0.8 * inside)
    glow[:, sD] = env * 0.55 * (1 - 0.6 * kd)
    glow[:, NA + NB + ND:] = 0.3 * smooth(.05, .4, S) * np.exp(-dE / 0.9) * (1 - smooth(.9, 1.2, S))
    glow[:, :NA] = 0.25 * env * np.exp(-dA / 1.2) + 0.5 * c * fade * np.exp(-dA / 1.5)
    foam[:, sB] = np.maximum(np.maximum(lip * smooth(0.72, 1.0, fb) * (1 - c), c * fade), 0.85 * smooth(.52, .62, S) * (1 - smooth(.72, .84, S)) * smooth(0.3, 0.7, fb))
    foam[:, sD] = np.maximum(lip * (1 - 0.75 * kd) * (1 - c), c * fade)
    foam[:, NA + NB + ND:] = np.maximum(c * fade * 0.6 * np.exp(-dE / (0.5 + 1.6 * smooth(.62, 1, S))),
                                        0.7 * smooth(.3, .42, S) * (1 - c) * np.exp(-dE / 0.18))
    sE = slice(NA + NB + ND, NP)
    front2 = np.where(d2 < 0, np.exp(-(d2 / 1.5) ** 2), np.exp(-(d2 / 0.5) ** 2))
    front2 = front2 * (0.4 + 0.6 * smooth(-0.5, 0.6, N_A2B + 0.6 * N_AMP2)[:, None])
    glow[:, sE] = np.maximum(glow[:, sE], (0.14 + 0.5 * smooth(.3, 1, tn)) * front2)
    foam[:, sE] = np.maximum(foam[:, sE], 0.8 * smooth(.55, .95, tn) * np.exp(-(d2 / 0.22) ** 2))
    amb = 0.34 * smooth(4.5, 0.8, yA)
    foam[:, :NA] = np.maximum.reduce([c * fade * np.exp(-dA / 0.6), amb + 0 * dA,
                                      0.55 * smooth(.76, .9, S) * fade * smooth(3.2, 1.5, yA) + 0 * dA])
    flow = np.concatenate([yA, (phiB + 1.6) * a * 1.2 - 1.6 * t, (phiD + 1.6) * a * 1.2 - 1.6 * t, yE], 1)
    return x2, Y, Z, glow, foam, flow

# ------------------------------------------------------------------ spray
ND_ = 150000
dx = 9.0 - 60.0 * rng.uniform(0, 1, ND_) ** 1.3
# 0 = thrown off the lip, 1 = impact splash, 2 = tumbling foam front, 3 = spit blown out of the closing tube, 4 = hanging mist
dkind = rng.choice(5, ND_, p=[0.11, 0.42, 0.13, 0.10, 0.24])
u_ = rng.uniform(0, 1, ND_)
dsb = np.select([dkind == 0, dkind == 1, dkind == 2, dkind == 3], [lerp(.44, .62, u_), lerp(.635, .70, u_), lerp(.7, .95, u_), lerp(.60, .69, u_)], lerp(.64, .78, u_))
dns, dna, dnp = xnoise(dx, 1, 7.0), xnoise(dx, 2, 5.0), xnoise(dx, 3, 1.6) + 0.5 * xnoise(dx, 4, 0.5)
dtb = (dsb - 0.3 + 0.0115 * np.abs(dx - 3.0) - 0.07 * dns) / 1.2 * DUR      # birth time in seconds
dA_, da_, db_, dph_, dyc_ = wave_params(dsb, dna, dnp)
tipy, tipz = dyc_ + da_ * np.cos(dph_) - throw(dph_, dA_), -0.05 + db_ + db_ * np.sin(dph_)
r1, r2, r3, r4 = (rng.uniform(0, 1, ND_) for _ in range(4))
# the splash goes up in uneven bursts along the beach: tall plumes in some places, barely anything in others
burst = 0.3 + 1.0 * smooth(-0.15, 0.8, xnoise(dx, 21, 1.1) + 0.5 * xnoise(dx, 22, 0.35)) ** 1.5
p0 = np.zeros((ND_, 3)); v0 = np.zeros((ND_, 3)); life = np.zeros(ND_); grav = np.ones(ND_)
k0, k1, k2, k3, k4 = (dkind == i for i in range(5))
nrm = lambda sd, k: rng.normal(0, sd, k.sum())
p0[:, 0] = dx
p0[k0, 1], p0[k0, 2] = tipy[k0], tipz[k0]                              # thrown off the curling lip
v0[k0] = np.stack([nrm(.5, k0), -2.6 - 1.6 * r1[k0], 0.2 + 2.0 * r2[k0] ** 2], 1); life[k0] = 0.35 + 0.4 * r3[k0]
landy = dyc_ - 0.55 * dA_
p0[k1, 1], p0[k1, 2] = landy[k1] - 0.5 * da_[k1] * (r1[k1] - 0.3), 0.02 + 0.15 * r4[k1]   # where the lip lands
v0[k1] = np.stack([nrm(.8, k1), -0.3 - 3.2 * r2[k1], (1.6 + 4.0 * r3[k1] ** 1.3) * burst[k1]], 1); life[k1] = (0.45 + 0.6 * r4[k1]) * (0.6 + 0.5 * burst[k1])
p0[k2, 1], p0[k2, 2] = dyc_[k2] - (0.75 * dA_[k2] + 0.15) * r1[k2], 0.1 + dA_[k2] * r4[k2]  # tumbling foam front
v0[k2] = np.stack([nrm(.5, k2), -1.5 - 1.5 * r2[k2], 0.5 + 1.6 * r3[k2] ** 2], 1); life[k2] = 0.3 + 0.4 * r4[k2]
side = np.sign(3.0 - dx)                                               # the open end of the tube faces the part that has already broken
p0[k3, 1], p0[k3, 2] = dyc_[k3] - 0.3 * dA_[k3] + 0.4 * da_[k3] * (r1[k3] - 0.5), 0.05 + 1.5 * db_[k3] * r4[k3]
v0[k3] = np.stack([side[k3] * (1.5 + 4.0 * r2[k3]) + nrm(.6, k3), -0.8 - 1.8 * r1[k3], 0.3 + 2.2 * r3[k3] ** 1.5], 1); life[k3] = 0.35 + 0.5 * r4[k3]
p0[k4, 1], p0[k4, 2] = landy[k4] - 0.8 * (r1[k4] - 0.2), 0.15 + 1.5 * dA_[k4] * burst[k4] * r4[k4] ** 1.3   # fine mist left hanging over the impact
v0[k4] = np.stack([nrm(.35, k4), -0.5 - 0.9 * r2[k4], 0.3 + 1.2 * r3[k4]], 1); life[k4] = 1.0 + 0.9 * r4[k4]; grav[k4] = 0.1
dsize = 0.003 + 0.007 * rng.uniform(0, 1, ND_) ** 3
dbright = rng.uniform(0, 1, ND_)
dsize[k1] = 0.0025 + 0.0045 * r1[k1] ** 2
dsize[k4] = 0.0022 + 0.002 * r3[k4]; dbright[k4] = 0.25 + 0.3 * r2[k4]
OCT = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
OCTF = np.array([[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4], [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]])

def spray(tn):
    t = tn * DUR; age = t - dtb
    m = (age > 0) & (age < life)
    ag = age[m][:, None]; g = np.array([0, 0, -9.8]) * grav[m][:, None]
    pos = p0[m] + v0[m] * ag * (1 - 0.25 * ag) + 0.5 * g * ag ** 2
    vel = v0[m] + g * ag
    sp = np.linalg.norm(vel, axis=1, keepdims=True) + 1e-6
    d = vel / sp
    off = OCT[None] * dsize[m][:, None, None]
    stretch = (off @ d[:, :, None]) * d[:, None, :] * (sp[:, None, :] * 0.0045 / dsize[m][:, None, None])
    verts = pos[:, None, :] + off + stretch
    br = dbright[m] * (1 - age[m] / life[m]) ** 0.6
    return verts.reshape(-1, 3), np.repeat(br, 6)

if MODE == 'dump':
    for a_ in args[3:]:
        r = build(float(a_)); np.save(os.path.join(HERE, 'dump_%s.npy' % a_), np.stack(r))
    sys.exit(0)
# ------------------------------------------------------------------ materials
def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links

def M(N, L, op, a, b=None, c=None):
    n = N.new('ShaderNodeMath'); n.operation = op; n.use_clamp = False
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: L.new(v, n.inputs[i])
    return n.outputs[0]

def MR(N, L, v, a, b, c=0.0, d=1.0, smoothstep=False):
    n = N.new('ShaderNodeMapRange'); n.clamp = True
    if smoothstep: n.interpolation_type = 'SMOOTHSTEP'
    L.new(v, n.inputs[0])
    for i, x in zip((1, 2, 3, 4), (a, b, c, d)): n.inputs[i].default_value = x
    return n.outputs[0]

def attr(N, name):
    n = N.new('ShaderNodeAttribute'); n.attribute_name = name; return n

TIME = [0.0]
def time_value(N):
    n = N.new('ShaderNodeValue'); n.name = 'TIME'; return n.outputs[0]

wm, N, L = mat('Water')
bs = N['Principled BSDF']
bs.inputs['Base Color'].default_value = (0.0, 0.006, 0.014, 1)
bs.inputs['Roughness'].default_value = 0.035
bs.inputs['IOR'].default_value = 1.33
geo = N.new('ShaderNodeNewGeometry')
sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
tv = time_value(N)
glow = attr(N, 'glow').outputs['Fac']; foamA = attr(N, 'foam').outputs['Fac']; flow = attr(N, 'flow').outputs['Fac']
# glowing rim wherever the water is thin over the sand
depth = M(N, L, 'ADD', sep.outputs[2], M(N, L, 'MULTIPLY', sep.outputs[1], SLOPE))
en = N.new('ShaderNodeTexNoise'); en.inputs['Scale'].default_value = 5.0; en.inputs['Detail'].default_value = 4.0; L.new(geo.outputs['Position'], en.inputs['Vector'])
edge = MR(N, L, M(N, L, 'ADD', depth, M(N, L, 'MULTIPLY_ADD', en.outputs['Fac'], 0.036, -0.018)), 0.004, 0.022, 1.0, 0.0)
# lacy foam: cell edges, drifting slowly
drift = N.new('ShaderNodeCombineXYZ'); L.new(M(N, L, 'MULTIPLY', tv, 0.05), drift.inputs[1]); L.new(M(N, L, 'MULTIPLY', tv, 0.11), drift.inputs[2])
pos2 = N.new('ShaderNodeVectorMath'); pos2.operation = 'ADD'
L.new(geo.outputs['Position'], pos2.inputs[0]); L.new(drift.outputs[0], pos2.inputs[1])
warp = N.new('ShaderNodeTexNoise'); warp.inputs['Scale'].default_value = 1.1; warp.inputs['Detail'].default_value = 4.0; L.new(pos2.outputs[0], warp.inputs['Vector'])
wv = N.new('ShaderNodeVectorMath'); wv.operation = 'MULTIPLY_ADD'
L.new(warp.outputs['Color'], wv.inputs[0]); wv.inputs[1].default_value = (1.7, 1.7, 1.7); L.new(pos2.outputs[0], wv.inputs[2])
def lace(scale, width):
    v = N.new('ShaderNodeTexVoronoi'); v.feature = 'DISTANCE_TO_EDGE'; v.inputs['Scale'].default_value = scale
    st = N.new('ShaderNodeVectorMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = (1.0, 0.55, 1.0)
    L.new(wv.outputs[0], st.inputs[0]); L.new(st.outputs[0], v.inputs['Vector'])
    return MR(N, L, v.outputs['Distance'], 0.0, width, 1.0, 0.0)
lace_all = M(N, L, 'MAXIMUM', lace(3.0, 0.15), M(N, L, 'MULTIPLY', lace(8.0, 0.15), 0.6))
pn = N.new('ShaderNodeTexNoise'); pn.inputs['Scale'].default_value = 1.3; pn.inputs['Detail'].default_value = 3.0; L.new(pos2.outputs[0], pn.inputs['Vector'])
foamv = M(N, L, 'MAXIMUM', M(N, L, 'MULTIPLY', foamA, M(N, L, 'MAXIMUM', MR(N, L, pn.outputs['Fac'], 0.36, 0.66, 0.0, 1.35), MR(N, L, foamA, 0.6, 0.9, 0.0, 1.25))), edge)
fmask = MR(N, L, M(N, L, 'ADD', M(N, L, 'MULTIPLY', foamv, 0.85), M(N, L, 'MULTIPLY', lace_all, 0.42)), 0.5, 0.64, 0.0, 1.0, True)
fmask = M(N, L, 'MULTIPLY', fmask, MR(N, L, foamv, 0.02, 0.1))
# streaks running up the face of the wave
sc = N.new('ShaderNodeCombineXYZ'); L.new(M(N, L, 'MULTIPLY', sep.outputs[0], 3.2), sc.inputs[0]); L.new(M(N, L, 'MULTIPLY', flow, 0.55), sc.inputs[1])
sn = N.new('ShaderNodeTexNoise'); sn.inputs['Scale'].default_value = 1.0; sn.inputs['Detail'].default_value = 5.0
L.new(sc.outputs[0], sn.inputs['Vector']); sn.inputs['Distortion'].default_value = 1.6; sn.inputs['Roughness'].default_value = 0.65
streak = MR(N, L, sn.outputs['Fac'], 0.32, 0.72, 0.12, 1.0)
gl = M(N, L, 'MULTIPLY', M(N, L, 'POWER', glow, 1.4), streak)
ramp = N.new('ShaderNodeValToRGB'); L.new(gl, ramp.inputs[0])
ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.0, 0.05, 0.6, 1)
ramp.color_ramp.elements[1].position = 1.0; ramp.color_ramp.elements[1].color = (0.25, 1.0, 0.9, 1)
e = ramp.color_ramp.elements.new(0.35); e.color = (0.0, 0.3, 1.0, 1)
e = ramp.color_ramp.elements.new(0.7); e.color = (0.02, 0.85, 0.95, 1)
# tiny bright specks, only where the water is disturbed
def specks(scale, cut):
    v = N.new('ShaderNodeTexVoronoi'); v.inputs['Scale'].default_value = scale; L.new(geo.outputs['Position'], v.inputs['Vector'])
    s2 = N.new('ShaderNodeSeparateColor'); L.new(v.outputs['Color'], s2.inputs[0])
    return M(N, L, 'MULTIPLY', MR(N, L, v.outputs['Distance'], 0.06, 0.2, 1.0, 0.0), MR(N, L, s2.outputs[0], cut, cut + 0.05))
sp = M(N, L, 'ADD', specks(24.0, 0.55), specks(55.0, 0.7))
disturbed = MR(N, L, M(N, L, 'ADD', M(N, L, 'ADD', M(N, L, 'MULTIPLY', glow, 0.45), M(N, L, 'MULTIPLY', foamv, 0.9)), 0.0), 0.05, 0.6)
spk = M(N, L, 'MULTIPLY', sp, disturbed)
# combine: dark water + face glow, foam on top, specks over all
water_em = N.new('ShaderNodeEmission'); L.new(ramp.outputs[0], water_em.inputs[0]); L.new(M(N, L, 'MULTIPLY', gl, 1.3), water_em.inputs[1])
add1 = N.new('ShaderNodeAddShader'); L.new(bs.outputs[0], add1.inputs[0]); L.new(water_em.outputs[0], add1.inputs[1])
fb_ = N.new('ShaderNodeBsdfPrincipled')
fb_.inputs['Base Color'].default_value = (0.5, 0.72, 0.9, 1); fb_.inputs['Roughness'].default_value = 0.6
fb_.inputs['Emission Color'].default_value = (0.1, 0.5, 1.0, 1)
cl = N.new('ShaderNodeTexNoise'); cl.inputs['Scale'].default_value = 11.0; cl.inputs['Detail'].default_value = 8.0; cl.inputs['Roughness'].default_value = 0.7; L.new(pos2.outputs[0], cl.inputs['Vector'])
clump = MR(N, L, cl.outputs['Fac'], 0.3, 0.72, 0.12, 1.0)
L.new(M(N, L, 'MULTIPLY', M(N, L, 'MULTIPLY_ADD', glow, 0.5, 0.42), clump), fb_.inputs['Emission Strength'])
fbump = N.new('ShaderNodeBump'); fbump.inputs['Strength'].default_value = 0.9; fbump.inputs['Distance'].default_value = 0.08; L.new(cl.outputs['Fac'], fbump.inputs['Height']); L.new(fbump.outputs[0], fb_.inputs['Normal'])
mix = N.new('ShaderNodeMixShader'); L.new(fmask, mix.inputs[0]); L.new(add1.outputs[0], mix.inputs[1]); L.new(fb_.outputs[0], mix.inputs[2])
sp_em = N.new('ShaderNodeEmission'); sp_em.inputs[0].default_value = (0.25, 0.9, 1.0, 1); L.new(M(N, L, 'MULTIPLY', spk, 9.0), sp_em.inputs[1])
add2 = N.new('ShaderNodeAddShader'); L.new(mix.outputs[0], add2.inputs[0]); L.new(sp_em.outputs[0], add2.inputs[1])
L.new(add2.outputs[0], N['Material Output'].inputs['Surface'])
# fine ripples
rip = N.new('ShaderNodeTexNoise'); rip.noise_dimensions = '4D'; rip.inputs['Scale'].default_value = 5.0; rip.inputs['Detail'].default_value = 6.0
L.new(geo.outputs['Position'], rip.inputs['Vector']); L.new(M(N, L, 'MULTIPLY', tv, 0.6), rip.inputs['W'])
bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35; bump.inputs['Distance'].default_value = 0.06
L.new(rip.outputs['Fac'], bump.inputs['Height']); L.new(bump.outputs[0], bs.inputs['Normal'])

sm, N, L = mat('Sand')
sb = N['Principled BSDF']; sb.inputs['Base Color'].default_value = (0.018, 0.015, 0.013, 1)
geo = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
wn = N.new('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value = 0.8; L.new(geo.outputs['Position'], wn.inputs['Vector'])
wet = MR(N, L, M(N, L, 'ADD', sep.outputs[1], M(N, L, 'MULTIPLY', wn.outputs['Fac'], 1.6)), -3.6, -2.2, 0.0, 1.0)
L.new(MR(N, L, wet, 0, 1, 0.75, 0.16), sb.inputs['Roughness'])
gr = N.new('ShaderNodeTexNoise'); gr.inputs['Scale'].default_value = 90; L.new(geo.outputs['Position'], gr.inputs['Vector'])
gr2 = N.new('ShaderNodeTexNoise'); gr2.inputs['Scale'].default_value = 2.5; L.new(geo.outputs['Position'], gr2.inputs['Vector'])
sbump = N.new('ShaderNodeBump'); sbump.inputs['Strength'].default_value = 0.5; sbump.inputs['Distance'].default_value = 0.02
L.new(M(N, L, 'ADD', M(N, L, 'MULTIPLY', gr.outputs['Fac'], 0.25), gr2.outputs['Fac']), sbump.inputs['Height']); L.new(sbump.outputs[0], sb.inputs['Normal'])
sv = N.new('ShaderNodeTexVoronoi'); sv.inputs['Scale'].default_value = 26; L.new(geo.outputs['Position'], sv.inputs['Vector'])
sc2 = N.new('ShaderNodeSeparateColor'); L.new(sv.outputs['Color'], sc2.inputs[0])
dots = M(N, L, 'MULTIPLY', MR(N, L, sv.outputs['Distance'], 0.05, 0.16, 1.0, 0.0), MR(N, L, sc2.outputs[0], 0.72, 0.76))
zone = M(N, L, 'MULTIPLY', MR(N, L, sep.outputs[1], -2.9, -1.2), MR(N, L, sep.outputs[1], 1.5, 0.3))
sb.inputs['Emission Color'].default_value = (0.05, 0.45, 1.0, 1)
L.new(M(N, L, 'MULTIPLY', M(N, L, 'MULTIPLY', dots, zone), 5.0), sb.inputs['Emission Strength'])

dm, N, L = mat('Spray')
N.remove(N['Principled BSDF'])
em = N.new('ShaderNodeEmission'); em.inputs[0].default_value = (0.35, 0.85, 1.0, 1)
L.new(M(N, L, 'MULTIPLY_ADD', M(N, L, 'POWER', attr(N, 'bright').outputs['Fac'], 2.0), 6.0, 0.4), em.inputs[1])
L.new(em.outputs[0], N['Material Output'].inputs['Surface'])

rm, N, L = mat('Rock')
N['Principled BSDF'].inputs['Base Color'].default_value = (0.012, 0.012, 0.014, 1); N['Principled BSDF'].inputs['Roughness'].default_value = 0.22

# ------------------------------------------------------------------ objects
me = bpy.data.meshes.new('Wave')
ii, jj = np.meshgrid(np.arange(NX - 1), np.arange(NP - 1), indexing='ij')
v00 = (ii * NP + jj).ravel()
faces = np.stack([v00, v00 + NP, v00 + NP + 1, v00 + 1], 1)
me.from_pydata(np.zeros((NX * NP, 3)).tolist(), [], faces.tolist())
for p in me.polygons: p.use_smooth = True
for nm in ('glow', 'foam', 'flow'): me.attributes.new(nm, 'FLOAT', 'POINT')
wave = bpy.data.objects.new('Wave', me); scene.collection.objects.link(wave); me.materials.append(wm)

sme = bpy.data.meshes.new('SprayMesh'); sobj = bpy.data.objects.new('Spray', sme); scene.collection.objects.link(sobj)

bpy.ops.mesh.primitive_plane_add(size=1); sand = bpy.context.object
sand.scale = (240, 60, 1); sand.location = (-40, -6, 0); sand.rotation_euler = (-math.atan(SLOPE), 0, 0)
sand.location.z = sand_z(-6); sand.data.materials.append(sm)
bpy.ops.mesh.primitive_plane_add(size=1); far = bpy.context.object
far.scale = (900, 600, 1); far.location = (-200, 330, -0.02); far.data.materials.append(wm)
for nm in ('glow', 'foam', 'flow'): far.data.attributes.new(nm, 'FLOAT', 'POINT')

for (rx, ry, rs) in [(-1.6, -3.7, .34), (-2.6, -3.0, .16), (-3.3, -3.5, .2), (-4.6, -2.9, .13), (-5.6, -3.4, .24), (-7.5, -3.1, .15), (-2.0, -2.6, .1), (-9.5, -3.6, .2)]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=rs, location=(rx, ry, sand_z(ry) + rs * 0.12))
    o = bpy.context.object; o.scale = (1.25, 1.0, 0.5); bpy.ops.object.shade_smooth(); o.data.materials.append(rm)

world = bpy.data.worlds.new('Night'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.010, 0.022, 0.06, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.3
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(74), 0, math.radians(-118)))
moon = bpy.context.object; moon.data.energy = 0.0; moon.hide_render = True; moon.data.color = (0.55, 0.7, 1.0); moon.data.angle = math.radians(6)

bpy.ops.object.empty_add(location=(-9.0, 4.0, -1.3)); target = bpy.context.object
bpy.ops.object.camera_add(location=(3.4, -3.4, 2.0)); cam = bpy.context.object
cam.data.lens = 30; cam.data.clip_end = 2000
con = cam.constraints.new('TRACK_TO'); con.target = target; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
scene.camera = cam

# ------------------------------------------------------------------ render setup
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'; prefs.get_devices()
for dv in prefs.devices: dv.use = True
scene.cycles.device = 'GPU'
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.sample_clamp_indirect = 4.0
scene.cycles.max_bounces = 5
scene.render.resolution_x, scene.render.resolution_y = WIDTH, int(WIDTH * 9 / 16)
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
try:
    tree = bpy.data.node_groups.new('Glow', 'CompositorNodeTree')
    scene.compositing_node_group = tree
    rl = tree.nodes.new('CompositorNodeRLayers'); glr = tree.nodes.new('CompositorNodeGlare'); out = tree.nodes.new('NodeGroupOutput')
    tree.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    tree.links.new(rl.outputs['Image'], glr.inputs['Image']); tree.links.new(glr.outputs['Image'], out.inputs[0])
    for k, v in (('Type', 'Bloom'), ('Threshold', 0.6), ('Strength', 0.3), ('Size', 0.4), ('Saturation', 1.0)):
        try: glr.inputs[k].default_value = v
        except Exception as ex: print('GLARE_SET', k, ex)
except Exception as ex:
    print('COMP_FAIL', ex)

def update(tn):
    x, y, z, g, f, fl = build(tn)
    co = np.stack([x, y, z], 2).reshape(-1)
    me.vertices.foreach_set('co', co)
    me.attributes['glow'].data.foreach_set('value', g.ravel())
    me.attributes['foam'].data.foreach_set('value', f.ravel())
    me.attributes['flow'].data.foreach_set('value', fl.ravel())
    me.update()
    v, br = spray(tn)
    sme.clear_geometry()
    n = len(v) // 6
    if n:
        fc = (OCTF[None] + (np.arange(n) * 6)[:, None, None]).reshape(-1, 3)
        sme.from_pydata(v.tolist(), [], fc.tolist())
        a = sme.attributes.new('bright', 'FLOAT', 'POINT'); a.data.foreach_set('value', br)
        if not sme.materials: sme.materials.append(dm)
    sme.update()
    for m in (wm,):
        m.node_tree.nodes['TIME'].outputs[0].default_value = tn * DUR
    print('UPDATED', round(tn, 3), 'droplets', n, flush=True)

if MODE == 'still':
    for a in args[3:]:
        tn = float(a); update(tn)
        scene.render.filepath = os.path.join(HERE, 'w5_%03d.png' % round(tn * 100))
        bpy.ops.render.render(write_still=True)
else:
    first, last = int(args[3]), int(args[4])
    out = os.path.join(HERE, 'frames_w5'); os.makedirs(out, exist_ok=True)
    for f in range(first, last + 1):
        update((f - 1) / (FRAMES - 1))
        scene.render.filepath = os.path.join(out, 'f_%04d.png' % f)
        bpy.ops.render.render(write_still=True)
print('RENDER_DONE')
