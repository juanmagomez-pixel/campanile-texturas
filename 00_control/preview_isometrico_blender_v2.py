"""Escena de QA isométrica para Blender 4.x: tres tipologías y UV en metros.

Uso desde la raíz descomprimida:
    blender -b -P texturas_renacimiento_italiano/00_control/preview_isometrico_blender_v2.py

Salida en texturas_renacimiento_italiano/00_control/revision_v2/:
    blender_validacion_1600.png
    blender_validacion_800.png

IMPORTANTE: los modelos de aquí son geometrías de comprobación, no edificios
históricos finales. No garantiza fidelidad arqueológica del material. Este script
se ha comprobado sintácticamente, pero NO se ha ejecutado en este entorno porque
Blender no está instalado.
"""
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '00_control' / 'revision_v2'
OUT.mkdir(parents=True, exist_ok=True)


def material(nombre, ruta, roughness=0.88, alpha=False):
    f = ROOT / ruta
    if not f.exists():
        raise FileNotFoundError(f)
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = 0.0
    img = m.node_tree.nodes.new('ShaderNodeTexImage')
    img.image = bpy.data.images.load(str(f), check_existing=True)
    img.image.colorspace_settings.name = 'sRGB'
    img.extension = 'CLIP' if alpha else 'REPEAT'
    img.interpolation = 'Linear'
    uv = m.node_tree.nodes.new('ShaderNodeTexCoord')
    m.node_tree.links.new(uv.outputs['UV'], img.inputs['Vector'])
    m.node_tree.links.new(img.outputs['Color'], bsdf.inputs['Base Color'])
    if alpha:
        m.node_tree.links.new(img.outputs['Alpha'], bsdf.inputs['Alpha'])
        try:
            m.surface_render_method = 'DITHERED'
        except Exception:
            try: m.blend_method = 'HASHED'
            except Exception: pass
    return m


def simple_material(name, rgba, roughness=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = rgba
    p.inputs['Roughness'].default_value = roughness
    return m


def face(nombre, coords, mat, uv_size, m_coverage=(2.0, 2.0)):
    """Quad plano con UV propias en unidades de metros, sin depender del cubo estándar."""
    mesh = bpy.data.meshes.new(nombre + '_mesh')
    mesh.from_pydata(coords, [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new(nombre, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    uv = mesh.uv_layers.new(name='UVMap')
    su = max(0.0001, uv_size[0] / m_coverage[0])
    sv = max(0.0001, uv_size[1] / m_coverage[1])
    lut = [(0, 0), (su, 0), (su, sv), (0, sv)]
    for poly in mesh.polygons:
        for l in poly.loop_indices:
            uv.data[l].uv = lut[mesh.loops[l].vertex_index]
    return obj


def block(nombre, location, dimensions, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    ob = bpy.context.object
    ob.name = nombre
    ob.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Bordes tallados', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        if hasattr(mod, 'affect'): mod.affect = 'EDGES'
        ob.modifiers.new('Normales', 'WEIGHTED_NORMAL')
    return ob


bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
try:
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    try: bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    except Exception: bpy.context.scene.render.engine = 'CYCLES'

m_ground = material('Lastrone florentino', 'ciudad/florencia/empedrado_lastrone_florencia_b.png')
m_humble = material('Enlucido humilde', 'comunes/muros/enlucido_desconchado_c.png')
m_merchant = material('Revoque ocre', 'ciudad/florencia/revoque_ocre_crema_florencia_b.png')
m_palazzo = material('Pietraforte', 'ciudad/florencia/pietraforte_florencia_b.png')
m_brick = material('Ladrillo toscano', 'comunes/muros/ladrillo_toscano_b.png')
m_roof_a = material('Teja roja cuidada', 'comunes/tejados/teja_arabe_roja_a.png')
m_roof_b = material('Teja Florencia usada', 'ciudad/florencia/teja_caballete_florencia_b.png')
m_roof_c = material('Teja oscura vieja', 'comunes/tejados/teja_oscura_vieja_c.png')
m_door = material('Puerta de madera', 'detalles/puertas_ventanas_y_herrajes/puerta_humilde_b.png')
m_gate = material('Portón de palacio', 'detalles/puertas_ventanas_y_herrajes/porton_claveteado_a.png')
m_glass = material('Vidrio emplomado', 'comunes/vidrio/vidrio_cuarterones_b.png')
m_dark = simple_material('Oscuridad de huecos', (0.09,0.095,0.09,1))
m_stone_trim = simple_material('Piedra de marcos', (0.49,0.46,0.39,1))
m_lintel = simple_material('Cornisas', (0.39,0.37,0.32,1))

# Pavimento de 15x8 m; cada copia representa los 3x3 m del catálogo.
face('Plaza de validación',
     [(-7.5,-4,0),(7.5,-4,0),(7.5,4,0),(-7.5,4,0)],
     m_ground, (15,8), (3,3))


def house(name, cx, width, depth, walls, roof, base=None, height=2.4, rise=.78, fancy=False):
    d = depth / 2
    w = width / 2
    y0 = -d
    x0 = cx
    # Three visible wall planes, no generic UV scaling on a cube.
    face(name + ' fachada',[(cx-w,y0,0),(cx+w,y0,0),(cx+w,y0,height),(cx-w,y0,height)],
         walls,(width,height),(2,2) if walls in [m_humble,m_merchant] else (3,3))
    face(name + ' lateral',[(cx+w,y0,0),(cx+w,d,0),(cx+w,d,height),(cx+w,y0,height)],
         walls,(depth,height),(2,2) if walls in [m_humble,m_merchant] else (3,3))
    # A thin foot of exposed stone, if relevant.
    if base is not None:
        face(name+' zócalo',[(cx-w,y0-.015,0),(cx+w,y0-.015,0),(cx+w,y0-.015,.34),(cx-w,y0-.015,.34)],
             base,(width,.34),(3,3))
    # Front gable triangle as custom mesh with UV coordinates consistent with wall scale.
    me=bpy.data.meshes.new(name+'_fronton')
    me.from_pydata([(cx-w,y0,height),(cx+w,y0,height),(cx,y0,height+rise)],[],[(0,1,2)])
    me.update(); ob=bpy.data.objects.new(name+' frontón',me)
    bpy.context.collection.objects.link(ob);ob.data.materials.append(walls)
    uv=me.uv_layers.new()
    for poly in me.polygons:
        for l in poly.loop_indices:
            idx=me.loops[l].vertex_index
            coords=[(0,0),(width/2,0),(width/4,rise/2)][idx]
            uv.data[l].uv=coords
    over=.18; eave_w=w+over; roof_depth=d+over
    slen=math.sqrt(eave_w**2+rise**2)
    # Each panel is flat; normals and tiles are determined by roof geometry.
    face(name+' faldón izq',
         [(cx-eave_w,-roof_depth,height+.04),(cx,-roof_depth,height+rise+.04),
          (cx,roof_depth,height+rise+.04),(cx-eave_w,roof_depth,height+.04)],
         roof,(slen,2*roof_depth),(2,2))
    face(name+' faldón dcho',
         [(cx,-roof_depth,height+rise+.04),(cx+eave_w,-roof_depth,height+.04),
          (cx+eave_w,roof_depth,height+.04),(cx,roof_depth,height+rise+.04)],
         roof,(slen,2*roof_depth),(2,2))
    # Trim and openings. Doors are one image per portal: UV from 0 to 1.
    def portal(x, pw, ph, mat):
        face(name+' puerta',[(x-pw/2,y0-.035,.015),(x+pw/2,y0-.035,.015),
                            (x+pw/2,y0-.035,ph),(x-pw/2,y0-.035,ph)],mat,(1,1),(1,1))
        block(name+' dintel',(x,y0-.06,ph+.055), (pw+.14,.11,.12),m_stone_trim)
    portal(cx,.72 if not fancy else 1.04,1.46 if not fancy else 1.82,
           m_door if not fancy else m_gate)
    for xx in (cx-.69,cx+.69):
        if abs(xx-cx)>w-.27:continue
        a=.45 if not fancy else .54; zh=height-.50
        face(name+' ventana',[(xx-a/2,y0-.05,zh-.48),(xx+a/2,y0-.05,zh-.48),
                              (xx+a/2,y0-.05,zh),(xx-a/2,y0-.05,zh)],
             m_glass,(1,1),(1,1))
        for offset in [-a/2-.045,a/2+.045]:
            block(name+' jamba',(xx+offset,y0-.075,zh-.22),(.08,.09,.64),m_stone_trim)
        block(name+' alféizar',(xx,y0-.08,zh-.52),(a+.18,.13,.10),m_stone_trim)
        block(name+' piedra dintel',(xx,y0-.08,zh+.045),(a+.16,.13,.095),m_stone_trim)
    if fancy:
        block(name+' cornisa',(cx,0,height-.03),(width+.18,depth+.18,.18),m_lintel,.02)

house('Casa humilde',-3.5,2.55,2.25,m_humble,m_roof_c,m_palazzo,2.05,.74)
house('Casa mercantil',0,2.65,2.55,m_merchant,m_roof_b,m_brick,2.52,.73)
house('Casa rica',3.55,2.75,2.65,m_palazzo,m_roof_a,m_palazzo,2.83,.68,True)

# Lighting, shadowing and camera are shared across all specimens.
world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new('Ambiente');bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.7,0.76,0.83,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
bpy.ops.object.light_add(type='AREA',location=(-5,-7,11))
sun=bpy.context.object;sun.name='Cielo difuso';sun.data.energy=1050;sun.data.shape='DISK';sun.data.size=6
bpy.ops.object.camera_add(location=(12,-17,15))
cam=bpy.context.object;cam.name='Isométrica 3/4';
cam.rotation_euler=(Vector((0,0,1.6))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=13.8
bpy.context.scene.camera=cam
scene=bpy.context.scene
scene.render.image_settings.file_format='PNG'
scene.render.resolution_percentage=100
scene.render.film_transparent=False
try:
    scene.view_settings.view_transform='AgX'
except Exception:pass
for siz,name in [(1600,'blender_validacion_1600.png'),(800,'blender_validacion_800.png')]:
    scene.render.resolution_x=siz
    scene.render.resolution_y=int(round(siz*9/16))
    scene.render.filepath=str(OUT/name)
    bpy.ops.render.render(write_still=True)
    print('Generado',scene.render.filepath)
