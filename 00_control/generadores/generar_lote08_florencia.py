from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/mnt/data');WORK=BASE/'texturas_renacimiento_italiano';CTL=WORK/'00_control';OUT=WORK/'ciudad'/'florencia';OUT.mkdir(parents=True,exist_ok=True)

def smooth_noise(n,seed,sigma_y,sigma_x=None):
 if sigma_x is None:sigma_x=sigma_y
 r=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sigma_y**2*fy**2+sigma_x**2*fx**2))
 a=np.fft.irfft2(np.fft.rfft2(r)*filt,s=(n,n)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-5)

def seam(ar):
 n=ar.shape[0];band=max(15,int(n*.035));a=ar.astype('float32').copy()
 for j in range(band):
  t=.5+.5*np.cos(np.pi*j/band);m=(a[:,j].copy()+a[:,n-1-j].copy())/2
  a[:,j]=a[:,j]*(1-t)+m*t;a[:,n-1-j]=a[:,n-1-j]*(1-t)+m*t
 for j in range(band):
  t=.5+.5*np.cos(np.pi*j/band);m=(a[j].copy()+a[n-1-j].copy())/2
  a[j]=a[j]*(1-t)+m*t;a[n-1-j]=a[n-1-j]*(1-t)+m*t
 return np.uint8(np.clip(np.rint(a),0,255))

def stone(v):
 n=512;i='abc'.index(v);seed=8410+i*33;y,x=np.mgrid[:n,:n]
 cols=4;rows=6;cw=n/cols;rh=n/rows
 row=(y//rh).astype('int32');off=(row%2)*cw/2
 xx=np.mod(x+off,cw);yy=np.mod(y,rh)
 cc=(np.floor((x+off)/cw).astype('int32'))%cols
 rng=np.random.default_rng(225)
 rv=rng.normal(size=(rows,cols))[row,cc]
 fine=smooth_noise(n,seed,2)*3.8+smooth_noise(n,seed+1,13)*6.5+smooth_noise(n,seed+2,38)*4
 color=np.array([(151,127,96),(139,114,89),(121,103,84)][i])
 a=color[None,None,:]+fine[:,:,None]+rv[:,:,None]*5.5
 veins=smooth_noise(n,seed+3,18,50)
 a+=veins[:,:,None]*np.array([3.3,2.5,1.6])
 mortar=np.clip((2.5+smooth_noise(n,seed+4,3)*.5 - np.minimum.reduce([xx,cw-xx,yy,rh-yy]))/2,0,1)
 a=a*(1-mortar[:,:,None])+(color-18)[None,None,:]*mortar[:,:,None]
 return seam(a)

def plaster(v):
 i='abc'.index(v);source=WORK/'comunes/muros'/f'enlucido_claro_{v}.png'
 a=np.asarray(Image.open(source).convert('RGB'),dtype='float32')
 # Keep physical plaster grain; use subtle mineral ochre limewash, not an opaque flat yellow paint.
 st=smooth_noise(512,9650+i,44)*5+smooth_noise(512,9700+i,90)*3
 target=np.array([(219,197,164),(207,184,149),(192,171,142)][i])
 result=a*.30+target[None,None,:]*.70+st[:,:,None]*np.array([1.0,.91,.8])
 return seam(result)

def roof(v):
 i='abc'.index(v)
 paths=['a_top_down_close_up_full_frame_seamless_texture_l.png',
        'a_close_up_top_down_orthographic_view_of_an_old_t.png',
        'a_photorealistic_top_down_perfectly_frontal_tig.png']
 source=BASE/paths[i];im=Image.open(source).convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS)
 a=np.asarray(im,dtype='float32')
 # Florentine warm orange coppi palette. Source visually captures barrel tiles,
 # but flat embrici/cup-shaped coppi mixture needs historical style review.
 a=a*np.array([1.035,1.04,.97])[None,None,:]
 return seam(a)

def lastrone(v):
 i='abc'.index(v);p=WORK/'comunes/suelos'/f'losas_piedra_{v}.png'
 a=np.asarray(Image.open(p).convert('RGB'),dtype='float32')
 # Grey-pardo Tuscan large lastrone, softened abrasion.
 a=a*.8+np.array([104,104,102])[None,None,:]*.2
 # Fine tooling near some surfaces; restrained so as not to create comic outlines.
 st=smooth_noise(512,9320+i,100,4)*2.4
 a+=st[:,:,None]
 return seam(a)

items=[('pietraforte',512,stone),('revoque_ocre_crema',512,plaster),('teja_caballete',1024,roof),('empedrado_lastrone',512,lastrone)]
files=[]
for name,res,fn in items:
 for v in 'abc':
  p=OUT/f'{name}_florencia_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# preview
sz=263;left=16;head=53;row_h=289;gap=10
sheet=Image.new('RGB',(2*left+4*sz+3*gap,head+row_h*3+13),(239,236,231));d=ImageDraw.Draw(sheet)
ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
d.text((left,10),'L08 · Florencia · piedra, revoque, cubierta y lastrone',font=ft,fill=(37,38,38))
for col,(name,_,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_florencia_{v}.png';im=Image.open(p).resize((sz,sz),Image.Resampling.LANCZOS)
  x=left+col*(sz+gap);y=head+row*row_h
  sheet.paste(im,(x,y));d.text((x,y+sz+4),f'{name} · {v}',font=ft,fill=(45,44,43))
sheet.save(CTL/'preview_L08_florencia_12_texturas.jpg',quality=90)
for p in files:
 im=Image.open(p).resize((256,256),Image.Resampling.LANCZOS);m=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):m.paste(im,(x*256,y*256))
 m.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=86)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);cols=rdr.fieldnames
assert sum(r['lote']=='L08' for r in rows)==12
qa={'lote':'L08','archivos':[]}
for r in rows:
 if r['lote']!='L08':continue
 p=WORK/r['ruta'];assert p.exists(),p
 im=Image.open(p);res=tuple(int(x) for x in r['resolucion'].split('x'));assert im.size==res
 a=np.asarray(im,dtype=np.int16);edge=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert edge<=1,(p,edge)
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 r['estado']='generada';r['sha256']=sha
 r['notas']='Material florentino provisional, borde y mosaico verificados. Teja: fuente coppi; revisar embrici/coppie en Blender.' if r['id_material']=='teja_caballete' else 'Prototipo florentino: adaptación de material base, revisar escala, color y contexto histórico.'
 qa['archivos'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'max_diferencia_borde':edge})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if item['clave_id'] not in {i[0] for i in items}:continue
 if item.get('ciudad','') not in ('Florencia','florencia'):continue
 for v in 'abc':
  p=next(x for x in files if x.name==f"{item['clave_id']}_florencia_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Prototipo local, pendiente revisión estilo y render Blender.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote08.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';ls=plan.read_text('utf-8').splitlines()
for i,line in enumerate(ls):
 if line.startswith('**Progreso actual:**'):
  ls[i]=f'**Progreso actual:** {count}/294 PNG reales; L08 Florencia 12/12 provisional; L06 sigue 12/24 pendiente de transparentes. Aún sin validación final Blender.'
plan.write_text('\n'.join(ls)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado comprobado\n- 98 familias y 294 variantes. **{count}/294 PNG reales**, faltan {294-count}.\n- L01-L05 y L07-L08 terminados en fase de prototipos; L06 12/24 (follaje alfa pendiente).\n- L08 Florencia son 12 PNG: pietraforte, revoque ocre, teja y lastrone.\n- Los PNG tienen checksums y pruebas 3×3; sin aprobación artística en Blender. La teja florentina utiliza una fuente de coppi y está pendiente de comprobar la alternancia con embrici.\n\n## Continuación exacta\n1. L06 pendientes: ramillete_olivo, ramillete_encina, ramillete_cipres, corte_tronco (a,b,c; 512px RGBA).\n2. Continuar L09 Venecia (15 PNG), empezando por el primer `estado=pendiente` con `lote=L09` en el CSV.\n3. Mantener referencias históricas, resolución y estilo realista.\n\n## Recuperación\nAdjunta `paquete_continuidad_L01_L08.zip` en otro chat, abre `00_control/REANUDAR_AQUI.md` y usa el CSV para retomar.\n''','utf-8')
lot=BASE/'lote_08_florencia.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L08' in p.name or 'florencia' in p.name):
   z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
full=BASE/'paquete_continuidad_L01_L08.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(WORK.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
print('Created',lot,lot.stat().st_size,full,full.stat().st_size,'count',count)
