from pathlib import Path
import csv, json, hashlib, zipfile, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BASE=Path('/mnt/data')
WORK=BASE/'texturas_renacimiento_italiano'
CTL=WORK/'00_control'
OUT=WORK/'comunes'/'tejados'
OUT.mkdir(parents=True,exist_ok=True)
ATLAS=Image.open(BASE/'a_high_resolution_compilation_texture_atlas_image.png').convert('RGB')
# Exact 15 isolated image regions inside the source contact sheet; remove all text and gutter regions.
# Atlas square columns x rows, crop within actual 300x284 texture zones.
CROPS = {
    2:(625, 918),   # Slate
    3:(932, 1221),  # Thatch
    4:(1244, 1526), # Dome lead
}
ROWS={0:(7,287),1:(336,607),2:(663,922)}
# Each tile has tiny margins, then a centered square crop: no white borders/labels.
INDIVIDUAL={
 'a': BASE/'a_hyper_realistic_high_detail_orthographic_close.png',
 'b': BASE/'a_detailed_close_up_texture_image_of_an_old_weath.png',
 'c': BASE/'a_crisp_ultra_detailed_orthographic_close_up_tex.png'
}

def get_atlas_cell(col, row):
    x0,x1=CROPS[col]; y0,y1=ROWS[row]
    im=ATLAS.crop((x0,y0,x1,y1))
    w,h=im.size; z=min(w,h)
    return im.crop(((w-z)//2,(h-z)//2,(w+z)//2,(h+z)//2))

def seamless(im, size=512, border=28):
    # uniform effective resolution. Seam correction blends matched opposite edge pixels
    # without wholesale texture stylization or generating fake outlines.
    im=im.convert('RGB').resize((size,size), Image.Resampling.LANCZOS)
    ar=np.asarray(im,dtype=np.float32).copy()
    for j in range(border):
        weight=.5*(1+np.cos(np.pi*j/border))
        left=ar[:,j].copy();right=ar[:,size-1-j].copy()
        mean=.5*(left+right)
        ar[:,j]=left*(1-weight)+mean*weight
        ar[:,size-1-j]=right*(1-weight)+mean*weight
    for j in range(border):
        weight=.5*(1+np.cos(np.pi*j/border))
        top=ar[j].copy();bottom=ar[size-1-j].copy()
        mean=.5*(top+bottom)
        ar[j]=top*(1-weight)+mean*weight
        ar[size-1-j]=bottom*(1-weight)+mean*weight
    result=Image.fromarray(np.uint8(np.clip(np.rint(ar),0,255)),'RGB')
    r=np.asarray(result,dtype=np.int16)
    return result, {
        'borde_izq_der_max':int(np.abs(r[:,0]-r[:,-1]).max()),
        'borde_sup_inf_max':int(np.abs(r[0]-r[-1]).max()),
        'resolucion':[size,size]
    }

new={}
for v,p in INDIVIDUAL.items():
    image=Image.open(p)
    tile, metrics=seamless(image)
    fn=f'teja_oscura_vieja_{v}.png'
    tile.save(OUT/fn,optimize=True)
    new[fn]={**metrics,'fuente':p.name,'fuente_tipo':'individual','revisado_mosaico':False}

for col,kind in ((2,'pizarra_liguria'), (3,'paja_techumbre'), (4,'plomo_cupula')):
    for row,v in enumerate('abc'):
        tile, metrics=seamless(get_atlas_cell(col,row))
        fn=f'{kind}_{v}.png'
        tile.save(OUT/fn,optimize=True)
        new[fn]={**metrics,'fuente':'a_high_resolution_compilation_texture_atlas_image.png','fuente_tipo':'recorte_atlas_upsample','revisado_mosaico':False}

# All 15 generated files now exist, prior three retained intact.
# Build visual contact and 3x3 tile preview for all variants.
FAMILIES=['teja_arabe_roja','teja_oscura_vieja','pizarra_liguria','paja_techumbre','plomo_cupula']
LABELS={'teja_arabe_roja':'Teja roja','teja_oscura_vieja':'Teja oscura','pizarra_liguria':'Pizarra','paja_techumbre':'Paja','plomo_cupula':'Plomo'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
ft=ImageFont.truetype(FONT,18)
cap=ImageFont.truetype(FONT,14)
thumb=236; gap=9; top=54; left=16; rh=thumb+32; w=left*2+5*thumb+4*gap; h=top+3*rh+25
contact=Image.new('RGB',(w,h),(238,236,229));d=ImageDraw.Draw(contact)
d.text((left,12),'L01 · Cubiertas del Renacimiento italiano · variantes a/b/c',font=ft,fill=(40,39,37))
for col,mat in enumerate(FAMILIES):
 for row,v in enumerate('abc'):
    f=OUT/f'{mat}_{v}.png'
    assert f.exists(), f
    t=Image.open(f).convert('RGB').resize((thumb,thumb),Image.Resampling.LANCZOS)
    x=left+col*(thumb+gap);y=top+row*rh
    contact.paste(t,(x,y));d.text((x+3,y+thumb+5),f'{LABELS[mat]} · {v}',font=cap,fill=(45,44,42))
contact.save(CTL/'preview_L01_15_texturas.jpg',quality=92)
for mat in FAMILIES:
 for v in 'abc':
    f=OUT/f'{mat}_{v}.png'
    src=Image.open(f).convert('RGB')
    grid=Image.new('RGB',(src.width*3,src.height*3))
    for x in range(3):
     for y in range(3): grid.paste(src,(x*src.width,y*src.height))
    grid.resize((768,768),Image.Resampling.LANCZOS).save(CTL/f'preview_{mat}_{v}_mosaico3x3.jpg',quality=87)
    if f.name in new:new[f.name]['revisado_mosaico']=True

# Amend catalog and manifest only after PNG files created and checked.
cat_path=CTL/'catalogo_texturas_v2.json'
cat=json.loads(cat_path.read_text(encoding='utf-8'))
for item in cat['materiales']:
    if item['clave_id'] not in FAMILIES:continue
    for v in 'abc':
        p=OUT/f"{item['clave_id']}_{v}.png"
        assert p.exists()
        variation=item['variantes'][v]
        variation['estado']='generada' # Not final approved without Blender render
        variation['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        variation['observaciones']='PNG 512×512, bordes idénticos; mosaico 3x3 exportado. Pendiente revisión de escala/patrón en Blender.'
        if p.name in new and new[p.name]['fuente_tipo']=='recorte_atlas_upsample':
            variation['observaciones']+=' Fuente original recortada de atlas ~270px; candidato a regenerar de forma individual para mayor fidelidad.'
cat_path.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
progress=CTL/'progreso_produccion.csv'
with progress.open(encoding='utf-8-sig',newline='') as f:
    rr=csv.DictReader(f); rows=list(rr); cols=rr.fieldnames
for r in rows:
 if r['id_material'] in FAMILIES:
    p=OUT/r['archivo']
    assert p.exists(),p
    r['estado']='generada'
    r['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    r['notas']='PNG 512px y mosaico 3×3; pendiente validación de escala y prueba Blender.'
    if p.name in new and new[p.name]['fuente_tipo']=='recorte_atlas_upsample':r['notas']+=' Fuente del atlas a resolución menor (prototipo).'
with progress.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader();writer.writerows(rows)
num=sum(r['estado']=='generada' for r in rows)
assert num==15,(num,len(rows))
plan=CTL/'plan_produccion_v2.md'
old=plan.read_text('utf-8')
lines=old.splitlines()
for i,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[i]='**Progreso actual:** L01: 15/15 PNG generados (prototipos), 15 pruebas de mosaico 3×3. Total: 15/294 variantes producidas. Pendiente validación en Blender, precisión de escala física y regenerar los tres materiales extraídos del atlas si su detalle no es suficiente.'
  break
plan.write_text('\n'.join(lines)+'\n',encoding='utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text('''# Reanudar aquí — control de producción\n\nCorte de producción: 2026-11-07, lote L01 generado.\n\n## Estado verificado\n- 98 familias de materiales; 294 variantes a/b/c.\n- **15 PNG reales** generados para **L01 – comunes/tejados**. Verificados con checksum SHA-256 y resolución 512×512.\n- Cada PNG dispone de prueba visual de mosaico 3×3; bordes izquierdo/derecho y superior/inferior iguales.\n- **No aprobados definitivamente**: validar en Blender densidad de piezas y proyección isométrica.\n- Teja árabe roja (3 PNG, lote anterior) y teja oscura vieja (3 PNG, imágenes individuales) son fuentes más detalladas.\n- Pizarra Liguria, paja y plomo (9 PNG) son recortes ~270px de un atlas fotorealista, reescalados a 512: considerarlos provisionales para revisar nitidez.\n- Todos los 279 PNG restantes están pendientes.\n\n## Próxima tarea concreta\n1. Probar L01 sobre planos de Blender y render isométrico, verificar densidad y ausencia de patrones repetitivos indeseados.\n2. Si la nitidez resulta insuficiente, sustituir los nueve PNG de pizarra, paja y plomo por imágenes originales individuales.\n3. Iniciar **L02 – comunes/muros** (18 PNG): enlucido claro, enlucido desconchado, adobe, ladrillo toscano, ladrillo lombardo y mampostería de zócalo.\n4. Tras cada lote actualizar `progreso_produccion.csv`, `catalogo_texturas_v2.json` y el ZIP. No dar ningún archivo por producido si no figura en el ZIP.\n\n## Continuación en nuevo chat\nAdjunta el ZIP más reciente y pide: «Continúa desde REANUDAR_AQUI.md; estilo fotográfico realista, nada de ilustración/cartoon, archivos 512px seamless y ZIP por lote».\n''',encoding='utf-8')
# QA checks
qa={'resolucion':'512x512','lote':'L01','imagenes':[]}
for mat in FAMILIES:
 for v in 'abc':
    p=OUT/f'{mat}_{v}.png'; im=Image.open(p); a=np.asarray(im,dtype=np.int16)
    maxlr=int(np.abs(a[:,0]-a[:,-1]).max()); maxtb=int(np.abs(a[0]-a[-1]).max())
    assert im.size==(512,512) and maxlr<=1 and maxtb<=1,(p,maxlr,maxtb)
    qa['imagenes'].append({'archivo':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'max_diff_bordes':max(maxlr,maxtb),'fuente':new.get(p.name,{}).get('fuente_tipo','individual')})
(CTL/'verificacion_lote01.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
zipname=BASE/'lote_01_comunes_tejados.zip'
with zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(CTL.iterdir()): z.write(f,Path('texturas_renacimiento_italiano')/f.relative_to(WORK))
 for f in sorted(OUT.iterdir()): z.write(f,Path('texturas_renacimiento_italiano')/f.relative_to(WORK))
print('Created',zipname,'bytes',zipname.stat().st_size,'PNG',num,'/',len(rows))
print('All seams <=1LSB. Contact:',CTL/'preview_L01_15_texturas.jpg')
