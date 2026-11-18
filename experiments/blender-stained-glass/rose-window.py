"""Create a Gothic rose window and keyframe its panes to a short rhythm study."""
from math import cos, sin, pi
from pathlib import Path
import os
import random

import bpy

OUTPUT = Path(os.environ.get("SOUNDCOLOR_OUTPUT", "/tmp/soundcolor-blender"))
FPS = 15
SECONDS = 6
CUES = [0.28, .49, .70, .94, 1.63, 1.84, 2.05, 2.30, 3.04, 3.47, 3.89, 4.34, 4.78, 5.22]
TAU = 2 * pi
random.seed(41)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = os.environ.get("SOUNDCOLOR_ENGINE", "CYCLES")
if scene.render.engine == "CYCLES":
    scene.cycles.samples = 3
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 3
scene.render.resolution_x = 768
scene.render.resolution_y = 432
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.frame_set(1)
scene.frame_end = FPS * SECONDS
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = str(OUTPUT / 'frame-')
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.world = bpy.data.worlds.new("Cathedral ambient")
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.063, .09, .16, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .25

def mineral(name, tones, scale, roughness, metallic=0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    surface = nodes.get('Principled BSDF')
    surface.inputs['Metallic'].default_value = metallic
    surface.inputs['Roughness'].default_value = roughness
    texture = nodes.new('ShaderNodeTexNoise')
    texture.inputs['Scale'].default_value = scale
    texture.inputs['Detail'].default_value = 4
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*tones[0], 1)
    ramp.color_ramp.elements[1].color = (*tones[1], 1)
    links.new(texture.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], surface.inputs['Base Color'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .28
    bump.inputs['Distance'].default_value = .065
    links.new(texture.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], surface.inputs['Normal'])
    return material

stone = mineral('Weathered sandstone', ((.032,.015,.011), (.27,.13,.058)), 32, .9)
trim = mineral('Warm carved stone', ((.063,.024,.01), (.36,.19,.08)), 25, .64)
lead = mineral('Dark bronze cames', ((.012,.007,.009), (.10,.039,.019)), 17, .36, .75)

def tube(name, points, width, material, closed=True):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 1
    curve.bevel_resolution = 3
    curve.bevel_depth = width
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, xyz in zip(spline.points, points):
        point.co = (*xyz, 1)
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material)

def polar(r, angle, z=0):
    return r * cos(angle), r * sin(angle), z

def ring(radius, z, width, mat):
    tube('Circular moulding', [polar(radius, i * TAU / 192, z) for i in range(192)], width, mat)

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, -.45))
wall = bpy.context.object
wall.name = "Cathedral wall"
wall.scale = (9, 6, .2)
wall.data.materials.append(stone)
for radius, z, width, mat in [(3.36,.03,.18,stone),(3.20,.11,.09,trim),(3.08,.16,.04,lead),(2.98,.06,.028,trim)]:
    ring(radius, z, width, mat)

PALETTE = [(1,.30,.009), (.032,.20,.95), (.87,.011,.022), (.023,.50,.23), (.24,.044,.80)]
palette_names = ['Amber','Cobalt','Ruby','Jade','Violet']
def glass(name, shade, cue):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    surface = nodes.get('Principled BSDF')
    surface.inputs['Roughness'].default_value = .27
    surface.inputs['Coat Weight'].default_value = .4
    texture = nodes.new('ShaderNodeTexNoise')
    texture.inputs['Scale'].default_value = 47
    texture.inputs['Detail'].default_value = 5
    texture.inputs['Roughness'].default_value = .7
    texcoord = nodes.new('ShaderNodeTexCoord')
    links.new(texcoord.outputs['Object'], texture.inputs['Vector'])
    fine = nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = 11
    fine.inputs['Detail'].default_value = 3
    links.new(texcoord.outputs['Object'], fine.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .22
    ramp.color_ramp.elements[0].color = (*(v * .12 for v in shade),1)
    ramp.color_ramp.elements[1].position = .78
    ramp.color_ramp.elements[1].color = (*(v * 1.13 + .04 for v in shade),1)
    links.new(fine.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], surface.inputs['Base Color'])
    links.new(ramp.outputs['Color'], surface.inputs['Emission Color'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .48
    bump.inputs['Distance'].default_value = .032
    links.new(texture.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], surface.inputs['Normal'])
    glow = surface.inputs['Emission Strength']
    start = max(2, round(cue * FPS))
    for frame, value in [(1,.025),(start-1,.025),(start+2,3.4),(start+8,1.65),(start+19,1.05)]:
        glow.default_value = value
        glow.keyframe_insert(data_path='default_value', frame=frame)
    return material

SECTORS = 12
def wedge(r1, r2, center, half, bend, inset=0):
    points = []
    for side in (-1,1):
        path = []
        for i in range(21):
            u = i / 20
            width = half * (.20 + .80 * sin(pi * u) ** .63)
            angle = center + bend * sin(pi * u) + side * (width - inset)
            path.append(polar(r1 + (r2-r1)*u, angle, .065))
        points.extend(path if side < 0 else reversed(path))
    return points

def add_pane(name, boundary, palette_index, cue, width):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(boundary, [], [tuple(range(len(boundary)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    shade = tuple(v * random.uniform(.84, 1.07) for v in PALETTE[palette_index])
    obj.data.materials.append(glass(name, shade, cue))
    tube(name + ' came', [(x,y,z+.035) for x,y,z in boundary], width, lead)

for row, (inner, outer, breadth) in enumerate([(.32,1.31,.24),(1.37,2.13,.158),(2.23,2.95,.158)]):
    for sector in range(SECTORS):
        angle = sector * TAU / SECTORS + (row % 2) * TAU / 24
        index = (sector * 2 + row) % len(PALETTE)
        cue = CUES[(sector * 5 + row * 4) % len(CUES)]
        bend = (.038 + .019 * row) * (-1 if sector % 2 else 1)
        add_pane(f'{palette_names[index]} petal {row+1}.{sector+1}',
                 wedge(inner,outer,angle,breadth,bend), index,cue,.029)
        if row > 0:
            add_pane(f'Filigree {row}.{sector+1}',
                     wedge(inner+.055,outer-.055,angle+TAU/24,.085,bend), (index+1)%5,
                     CUES[(sector * 3 + row * 6) % len(CUES)], .018)
for radius in [.30,1.32,2.18,2.97]:
    ring(radius,.11,.033,lead)
add_pane('Amber oculus', [polar(.295, i*TAU/48,.07) for i in range(48)], 0, .10, .033)

bpy.ops.object.camera_add(location=(0, 0, 14))
camera = bpy.context.object
camera.name = 'Front elevation'
camera.data.type = 'ORTHO'
camera.rotation_euler = (0,0,0)
camera.data.ortho_scale = 13.35
camera.keyframe_insert(data_path='location', frame=1)
camera.data.keyframe_insert(data_path='ortho_scale', frame=1)
camera.location.y = .13
camera.keyframe_insert(data_path='location', frame=scene.frame_end)
camera.data.ortho_scale = 12.65
camera.data.keyframe_insert(data_path='ortho_scale', frame=scene.frame_end)
scene.camera = camera

def light(name, location, rgb, power, size):
    bpy.ops.object.light_add(type='AREA', location=location)
    lamp = bpy.context.object
    lamp.name = name
    lamp.data.color = rgb
    lamp.data.energy = power
    lamp.data.shape = 'DISK'
    lamp.data.size = size
    from mathutils import Vector
    lamp.rotation_euler = (-Vector(location)).to_track_quat('-Z','Y').to_euler()

light('Amber rake', (-4, 3, 5), (1,.61,.31), 510, 4)
light('Cool fill', (4, -2, 5), (.40,.61,1), 225, 5)

scene.use_nodes = True
nodes, links = scene.node_tree.nodes, scene.node_tree.links
glare = nodes.new('CompositorNodeGlare')
glare.glare_type = 'FOG_GLOW'
glare.quality = 'HIGH'
links.new(nodes.get('Render Layers').outputs['Image'], glare.inputs['Image'])
links.new(glare.outputs['Image'], nodes.get('Composite').inputs['Image'])

scene.frame_set(1)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / 'stained-glass.blend'))
