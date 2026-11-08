"""Escena de comprobación visual de prototipos; ejecutar con Blender instalado.

Ejemplo: blender -b -P 00_control/preview_isometrico_blender.py
Crea tres bloques de edificio y una calle de prueba con cubiertas, zócalos y muros.
Este script NO fue ejecutado en el entorno de generación, porque Blender no estaba disponible.
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '00_control' / 'preview_isometrica_blender.png'

def material(nombre, ruta, metros=2):
    path = ROOT / ruta
    if not path.exists():
        raise FileNotFoundError(path)
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    im = nodes.new('ShaderNodeTexImage')
    im.image = bpy.data.images.load(str(path), check_existing=True)
    im.extension = 'REPEAT'
    im.interpolation = 'Linear'
    uv = nodes.new('ShaderNodeTexCoord')
    vec = nodes.new('ShaderNodeVectorMath')
    vec.operation = 'SCALE'
    vec.inputs[3].default_value = 1.0 / float(metros)
    links.new(uv.outputs['Object'], vec.inputs[0])
    links.new(vec.outputs[0], im.inputs['Vector'])
    links.new(im.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.85
    return m

def cube(nombre, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = nombre
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Aristas discretas', 'BEVEL')
    bevel.width = 0.02
    bevel.segments = 1
    return o

def gable_roof(x, wallmat, roofmat, z=2.1):
    # Dos faldones simplificados; geométricamente no es un edificio final.
    for side in (-1, 1):
        o = cube('Faldón', (x + side*0.58, 0, z+0.26), (1.45,2.7,.08), roofmat)
        o.rotation_euler[1] = -side*math.radians(27)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
try:
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    bpy.context.scene.render.engine = 'CYCLES'

paved = material('Lastrone', 'ciudad/florencia/empedrado_lastrone_florencia_b.png',3)
roof = material('Tejas toscanas', 'ciudad/florencia/teja_caballete_florencia_b.png',2)
plaster = material('Revoque Florencia', 'ciudad/florencia/revoque_ocre_crema_florencia_b.png',2)
stone = material('Pietraforte', 'ciudad/florencia/pietraforte_florencia_b.png',3)
brick = material('Ladrillo', 'comunes/muros/ladrillo_toscano_b.png',1.5)

cube('Calle', (0,0,-.18), (12,7,.3), paved)
for x, name, walls in ((-3.2,'Casa humilde',plaster),(0,'Casa mercantil',brick),(3.2,'Casa rica',stone)):
    cube(name, (x,0,1), (2.35,2.3,2), walls)
    cube(name+' zócalo', (x,0,.12), (2.48,2.39,.35), stone)
    gable_roof(x,walls,roof,z=2.08)

bpy.ops.object.light_add(type='AREA', location=(-4,-6,11))
light=bpy.context.object
light.data.energy=950
light.data.shape='DISK'
light.data.size=8
bpy.ops.object.camera_add(location=(11,-14,12))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=13
bpy.context.scene.camera=cam
world=bpy.context.scene.world
world.color=(0.72,0.72,0.72)
scene=bpy.context.scene
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(OUT)
bpy.ops.render.render(write_still=True)
print('Render generado en:',OUT)
