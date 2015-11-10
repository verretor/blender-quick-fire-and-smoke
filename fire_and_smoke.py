import bpy

origin_obj = bpy.context.object.name

bpy.ops.object.shade_smooth()
bpy.ops.object.modifier_add(type='SMOKE')
bpy.ops.object.material_slot_add()
bpy.ops.object.quick_smoke()

bpy.context.object.modifiers["Smoke"].domain_settings.use_adaptive_domain = True
bpy.context.object.scale[0] = 3
bpy.context.object.scale[1] = 3
bpy.context.object.scale[2] = 6

bpy.data.objects[origin_obj].modifiers["Smoke"].flow_settings.smoke_flow_type = 'BOTH'
bpy.context.scene.render.engine = "CYCLES"

# Save time with variable names.
mat = bpy.context.object.active_material
mat.use_nodes = True
material_output = mat.node_tree.nodes['Material Output']

# Delete every node but 'Material Output'
for k in mat.node_tree.nodes.keys():
    if k != 'Material Output':
        mat.node_tree.nodes.remove(mat.node_tree.nodes[k])

# Always use material_output as reference.
x,y = material_output.location

# Add all nodes
volume_scatter = mat.node_tree.nodes.new('ShaderNodeVolumeScatter')
volume_scatter.location = (x - 450, y)

volume_abs = mat.node_tree.nodes.new('ShaderNodeVolumeAbsorption')
volume_abs.location = (x - 450, y - 150)

add_shader1 = mat.node_tree.nodes.new('ShaderNodeAddShader')
add_shader1.location = (x - 300, y)

add_shader2 = mat.node_tree.nodes.new('ShaderNodeAddShader')
add_shader2.location = (x - 150, y)

emission = mat.node_tree.nodes.new('ShaderNodeEmission')
emission.location = (x - 300, y - 200)

color_ramp = mat.node_tree.nodes.new('ShaderNodeValToRGB')
color_ramp.location = (x - 550, y - 300)

attr_flame = mat.node_tree.nodes.new('ShaderNodeAttribute')
attr_flame.location = (x - 700, y - 400)

attr_density = mat.node_tree.nodes.new('ShaderNodeAttribute')
attr_density.location = (x - 800, y)

bright_contr = mat.node_tree.nodes.new('ShaderNodeBrightContrast')
bright_contr.location = (x - 600, y)

# Link nodes together.
mat.node_tree.links.new(add_shader2.outputs['Shader'], material_output.inputs['Volume'])
mat.node_tree.links.new(add_shader1.outputs['Shader'], add_shader2.inputs['Shader'])
mat.node_tree.links.new(emission.outputs['Emission'], add_shader2.inputs[1])
mat.node_tree.links.new(color_ramp.outputs[0], emission.inputs[0])
mat.node_tree.links.new(attr_flame.outputs[2], color_ramp.inputs[0])
mat.node_tree.links.new(volume_scatter.outputs[0], add_shader1.inputs[0])
mat.node_tree.links.new(volume_abs.outputs[0], add_shader1.inputs[1])
mat.node_tree.links.new(bright_contr.outputs[0], volume_scatter.inputs[1])
mat.node_tree.links.new(bright_contr.outputs[0], volume_abs.inputs[1])
mat.node_tree.links.new(attr_density.outputs[2], bright_contr.inputs[0])

# Change attribute names for density and flame.
attr_density.attribute_name = 'density'
attr_flame.attribute_name = 'flame'

# Change colors in color ramp.
color_ramp.color_ramp.elements[1].color = (1, 1, 1, 0.75)
color_ramp.color_ramp.elements.new(0.75)
color_ramp.color_ramp.elements[1].color = (0.509, 0.437, 0.057, 1)
color_ramp.color_ramp.elements.new(0.5)
color_ramp.color_ramp.elements[1].color = (0.541, 0.165, 0, 1)
color_ramp.color_ramp.elements.new(0.25)
color_ramp.color_ramp.elements[1].color = (0.189, 0.022, 0, 1)

# Increase smoke density using contrast.
bright_contr.inputs[2].default_value = 5