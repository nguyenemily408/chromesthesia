import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
m=o.modifiers.new('F','FLUID'); m.fluid_type='DOMAIN'
d=m.domain_settings
print('DOMAIN', sorted(p.identifier for p in d.bl_rna.properties))
m.fluid_type='FLOW'
print('FLOW', sorted(p.identifier for p in m.flow_settings.bl_rna.properties))
m.fluid_type='EFFECTOR'
print('EFF', sorted(p.identifier for p in m.effector_settings.bl_rna.properties))
print('FLUIDOPS', [x for x in dir(bpy.ops.fluid)])
s=bpy.context.scene
print('COMP', [a for a in dir(s) if 'comp' in a.lower() or 'node' in a.lower()])
print('GLARE', sorted(p.identifier for p in bpy.types.CompositorNodeGlare.bl_rna.properties)[:60])
s.render.engine='CYCLES'
prefs=bpy.context.preferences.addons['cycles'].preferences
print('DEVTYPES', [d[0] for d in prefs.get_device_types(bpy.context)])
import sys; print(sys.version)
try:
    import numpy; print('numpy', numpy.__version__)
except Exception as e: print(e)
