from pathlib import Path
import io,json,hashlib,csv,zipfile,collections,math,random
import numpy as np, cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.ndimage import distance_transform_edt

OUT=Path('/mnt/data/revision_calidad_v2'); ROOT=OUT/'texturas_renacimiento_italiano';
ORIG=Path('/mnt/data/paquete_completo_texturas_renacimiento_italiano.zip')

# Alpha edge colors are cleaned but transparency silhouettes are not changed.
with open(OUT/'progreso_produccion.csv',newline='',encoding='utf-8-sig') as _f:
    _rep = {rr['ruta']:rr['repeticion'].strip().lower() for rr in csv.DictReader(_f)}
changed=[]
for p in ROOT.rglob('*.png'):
 im=Image.open(p)
 if im.mode!='RGBA':continue
 ar=np.array(im)
 rgb=ar[:,:,:3].astype(np.float32); a=ar[:,:,3]
 opaque=a>=max(145,round(float(a.max())*.62))
 if not opaque.any():continue
 near=np.array(distance_transform_edt(~opaque,return_distances=False,return_indices=True))
 ny,nx=near
 palette=rgb[ny,nx]
 mix=np.clip((175-a.astype(np.float32))/95,0,1)[...,None]
 # Restore source color from near solid leaf/metal areas wherever the edge is weak.
 out_rgb=np.rint(rgb*(1-mix)+palette*mix).clip(0,255).astype(np.uint8)
 arr=ar.copy();arr[:,:,:3]=out_rgb
 rep=_rep.get(p.relative_to(ROOT).as_posix(),'no')
 # Preserve exact toroidal RGB borders after dilation (including transparent texels).
 if rep in ('ambos','horizontal'):
  pair=np.rint((arr[:,0,:].astype(np.float32)+arr[:,-1,:].astype(np.float32))/2).clip(0,255).astype('uint8')
  arr[:,0,:]=pair;arr[:,-1,:]=pair
 if rep=='ambos':
  pair=np.rint((arr[0,:,:].astype(np.float32)+arr[-1,:,:].astype(np.float32))/2).clip(0,255).astype('uint8')
  arr[0,:,:]=pair;arr[-1,:,:]=pair
 if np.any(arr[:,:,:3]!=ar[:,:,:3]):
  Image.fromarray(arr,'RGBA').save(p,optimize=True)
  changed.append(p.relative_to(ROOT).as_posix())
print('Alpha defringe:',len(changed),changed[:6])

# Collage of nine representative tiles for QA: 3x3 tessellation, a true 1x1 at 128 px,
# and no false suggestion of a Blender render.
materials=[
 ('Teja común', 'comunes/tejados/teja_arabe_roja_b.png'),
 ('Ladrillo toscano','comunes/muros/ladrillo_toscano_b.png'),
 ('Pietraforte, Florencia','ciudad/florencia/pietraforte_florencia_b.png'),
 ('Enlucido florentino','ciudad/florencia/revoque_ocre_crema_florencia_b.png'),
 ('Teja de Florencia','ciudad/florencia/teja_caballete_florencia_b.png'),
 ('Lastrone','ciudad/florencia/empedrado_lastrone_florencia_b.png'),
 ('Mármol verde','comunes/marmoles/marmol_verde_prato_b.png'),
 ('Pizarra, Liguria','comunes/tejados/pizarra_liguria_b.png'),
 ('Ladrillo lombardo','comunes/muros/ladrillo_lombardo_b.png'),
]
font_paths=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
fp=next(x for x in font_paths if Path(x).exists())
fnt=ImageFont.truetype(fp,21);small=ImageFont.truetype(fp,14)
W=1540;cell_w=500;cell_h=380
sheet=Image.new('RGB',(W,1300),(233,232,227));dr=ImageDraw.Draw(sheet)
dr.text((34,20),'Control visual · repetición y escala de texturas',font=ImageFont.truetype(fp,31),fill=(40,43,46))
dr.text((36,69),'Vista diagnóstica: mosaico 3×3 y muestra de 128 px. NO es un render de Blender.',font=small,fill=(79,82,85))
for i,(label,path) in enumerate(materials):
 img=Image.open(ROOT/path).convert('RGB'); x=20+(i%3)*cell_w; y=106+(i//3)*cell_h
 dr.text((x+7,y),label,font=fnt,fill=(34,34,34))
 tsmall=img.resize((108,108),Image.Resampling.LANCZOS)
 m=Image.new('RGB',(324,324))
 for yy in range(3):
  for xx in range(3):m.paste(tsmall,(xx*108,yy*108))
 sheet.paste(m,(x,y+35))
 tile=img.resize((128,128),Image.Resampling.LANCZOS)
 sheet.paste(tile,(x+336,y+35))
 dr.text((x+336,y+174),'128 px',font=small,fill=(40,44,48))
 dr.text((x+7,y+360),path,font=ImageFont.truetype(fp,12),fill=(78,81,85))
sheet.save(OUT/'diagnostico_repeticion_9_materiales.jpg',quality=89,subsampling=0)

# Diagnostic source-size thumbnail for three foliage variants, before the conversion.
fg_names=['ramillete_olivo_b.png','ramillete_encina_b.png','ramillete_cipres_b.png','corte_tronco_b.png']
bgcols=[(233,230,222),(42,47,51)]
audit=Image.new('RGB',(1250,748),(244,243,240)); d=ImageDraw.Draw(audit)
d.text((24,19),'Recursos transparentes · verificación de recorte y halo',font=ImageFont.truetype(fp,28),fill=(24,30,36))
d.text((26,59),'Cada recorte se muestra sobre fondo claro y oscuro. Pendiente evaluación botánica en Blender.',font=small,fill=(70,74,80))
for i,fn in enumerate(fg_names):
 p=next(ROOT.rglob(fn)); im=Image.open(p).convert('RGBA')
 for j,bg in enumerate(bgcols):
  bgim=Image.new('RGBA',(256,256),(*bg,255))
  bgim.alpha_composite(im.resize((256,256),Image.Resampling.LANCZOS))
  x=22+i*306; y=100+j*306
  audit.paste(bgim.convert('RGB'),(x,y))
 d.text((22+i*306,670),fn,font=small,fill=(42,46,49))
audit.save(OUT/'diagnostico_alfa_botanica.jpg',quality=92)

# Validate physical pixel properties and update CSV hashes without claiming artistic approval.
entries=[]; hashdict={}; dimdict=collections.Counter(); opaque_cnt=0; edge_results=[]
orig_csv=OUT/'progreso_produccion.csv'
with open(orig_csv,newline='',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
for r in rows:
 p=ROOT/r['ruta']; im=Image.open(p); ar=np.asarray(im)
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['sha256']=sha;r['estado']='generada';r['fecha_entrega']=''
 r['estado_qa']='pendiente_blender'
 if 'ramillete_encina' in r['archivo'] or 'ramillete_cipres' in r['archivo']:r['prioridad_qa']='critica'
 elif any(t in r['archivo'] for t in ['corte_tronco','ramillete_olivo','paja_techumbre','plomo_cupula','pizarra_liguria']):r['prioridad_qa']='alta'
 elif any(t in r['archivo'] for t in ['ladrillo_','mamposteria','esgrafiado','terracota_decorativa','mosaico_cosmatesco','mayolica']):r['prioridad_qa']='alta'
 else:r['prioridad_qa']='media'
 r['alfa_defringe_v2']='sí' if r['ruta'] in changed else 'no'
 dims=im.size; dimdict[dims]+=1
 mode=im.mode
 rep=r['repeticion'].lower().strip()
 a=np.asarray(im).astype('int16')
 lr=(abs(a[0,:,:]-a[-1,:,:]).max() if a.ndim==3 else abs(a[0,:]-a[-1,:]).max())
 tb=(abs(a[:,0,:]-a[:,-1,:]).max() if a.ndim==3 else abs(a[:,0]-a[:,-1]).max())
 # LR vs TB: top-to-bottom and left-to-right separately.
 max_tb=int(lr); max_lr=int(tb)
 edge_results.append((r['archivo'],rep,max_lr,max_tb))
 entries.append(dict(archivo=r['archivo'],ruta=r['ruta'],resolution=list(dims),mode=mode,sha256=sha,repeticion=rep,lr_error=max_lr,tb_error=max_tb,estado='generada',estado_qa='pendiente_blender',prioridad=r['prioridad_qa']))
fields=list(rows[0]);
with open(OUT/'progreso_produccion_v2.csv','w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
assert len(entries)==294
bad_edge=[]
for fn,rep,lr,tb in edge_results:
 if rep=='ambos' and (lr>0 or tb>0):bad_edge.append((fn,rep,lr,tb))
 if rep=='horizontal' and lr>0:bad_edge.append((fn,rep,lr,tb))
print('Edge failures:',len(bad_edge),bad_edge[:12])

verified=dict(fecha='2026-11-07',total=294,generados=294,revisados_blender=0,estado_qa='pendiente',dimensiones={f'{k[0]}x{k[1]}':v for k,v in dimdict.items()},alfa_corregido=len(changed),incidencias_bordes=bad_edge,archivos=entries)
(OUT/'ESTADO_VERIFICADO_v2.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2),encoding='utf-8')

# A versioned, reportable QA note.
crit=sum(r['prioridad_qa']=='critica' for r in rows)
high=sum(r['prioridad_qa']=='alta' for r in rows)
report=f'''# Auditoría visual y técnica — versión 2

Fecha: 7 de noviembre de 2026.

## Estado contrastado

- **294 archivos PNG válidos** (98 familias × 3 estados), sin duplicados exactos.
- Resoluciones: **512×512: {dimdict[(512,512)]}**; **1024×1024: {dimdict[(1024,1024)]}**; **256×256: {dimdict[(256,256)]}**; **512×256: {dimdict[(512,256)]}**.
- Archivos RGBA: **{len(changed)}** corregidos con dilatación del color RGB hacia los bordes transparentes para evitar halos del filtrado.
- Verificación de continuidad exigida por la ficha: **{len(bad_edge)} errores** de bordes exactos (cero no garantiza repetición visual natural).
- **294 generados, 0 revisados en Blender, 0 aprobados artísticamente**. No equiparar generación con calidad final.
- Archivo `ESTADO_VERIFICADO.json` del ZIP antiguo desfasado (123 de 294). Corregido en `ESTADO_VERIFICADO_v2.json`.

## Prioridades

- **Crítica ({crit} PNG):** ramilletes de encina y ciprés. Morfología ilustrada, poco fotográfica. Rehacer con recortes fotográficos/licencia compatible y alfa limpio.
- **Alta ({high} PNG):** olivo (bordes), corte de tronco (anillos esquemáticos), pizarra, paja y plomo (detalle limitado de fuente atlas), algunas fábricas de ladrillo y decoraciones de aspecto demasiado geométrico.
- **Media:** restantes. Deben pasar comprobación a escala de sprite y en edificios reales.

## Archivos de inspección

- `diagnostico_repeticion_9_materiales.jpg`: mosaicos de 3 × 2 y miniaturas de 128 px.
- `diagnostico_alfa_botanica.jpg`: recortes transparentes sobre fondos claro y oscuro.
- `preview_isometrico_blender_v2.py`: escena de evaluación ejecutable localmente. **No se ha ejecutado aquí (Blender no instalado)**.
- `progreso_produccion_v2.csv`: hashes actualizados, estados QA y prioridades por PNG.

## Condición para cerrar un material

1. Escala física y lenguaje de material consistentes.
2. Losas, sillares y tejas sin artefactos evidentes tras mosaico 3 × 3.
3. Recorte correcto sin halos, si procede.
4. Aspecto convincente en Blender a la resolución final del sprite y en la misma iluminación para las tres variantes.
5. Solo después cambiar `estado_qa=pendiente_blender` por `aprobada` y conservar captura de la prueba.

## Licencias

Los PNG de esta entrega fueron generados para el proyecto; no se ha incorporado ninguna fotografía descargada de terceros en esta revisión. Si se sustituyen recursos por fotos externos, utilizar preferiblemente CC0 y documentar fuente y licencia por fichero.
'''
(OUT/'AUDITORIA_CALIDAD_V2.md').write_text(report,encoding='utf-8')
print('READY',len(entries),'critical',crit,'high',high)
