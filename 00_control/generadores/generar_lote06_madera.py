from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control';N=512
Y,X=np.mgrid[:N,:N]

def pnoise(seed,sigmay,sigmax):
 raw=np.random.default_rng(seed).normal(size=(N,N)).astype('float32')
 fy=np.fft.fftfreq(N)[:,None];fx=np.fft.rfftfreq(N)[None,:]
 f=np.exp(-2*np.pi*np.pi*(sigmay**2*fy*fy+sigmax**2*fx*fx))
 a=np.fft.irfft2(np.fft.rfft2(raw)*f,s=(N,N)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-5)

def seam(a):
 a=a.astype('float32').copy();b=20
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,N-1-j].copy())/2
  a[:,j]=a[:,j]*(1-t)+m*t;a[:,N-1-j]=a[:,N-1-j]*(1-t)+m*t
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[N-1-j].copy())/2
  a[j]=a[j]*(1-t)+m*t;a[N-1-j]=a[N-1-j]*(1-t)+m*t
 return np.uint8(np.clip(np.rint(a),0,255))

def timber(kind,v):
 ix='abc'.index(v);seed=5400+ix*50+(700 if kind=='bark_olive' else 1400 if kind=='bark_cypress' else 300 if kind=='boards' else 0)
 fibers=pnoise(seed,145,2.7)*.75+pnoise(seed+1,69,7)*.5+pnoise(seed+2,19,1.1)*.20
 rough=pnoise(seed+3,7,7)*.7+pnoise(seed+4,2,2)*.7+pnoise(seed+5,47,38)*.38
 veins=pnoise(seed+6,145,1.4)
 if kind=='beam':
  base=np.array([(110,86,64),(99,76,58),(85,70,59)][ix])
  a=base[None,None,:]+fibers[:,:,None]*np.array([13,11,9])+rough[:,:,None]*np.array([4,4,4])
  crack=np.maximum(0,-veins-1.15)**1.5
  a-=crack[:,:,None]*np.array([12,12,11])
 elif kind=='boards':
  base=np.array([(132,98,68),(121,88,62),(102,81,62)][ix])
  width=N/7;u=np.mod(X,width)
  idx=np.floor(X/width).astype('int32')%7
  rng=np.random.default_rng(1975)
  col=rng.normal(0,1,size=7)[idx]
  a=base[None,None,:]+fibers[:,:,None]*np.array([13,11,9])+rough[:,:,None]*np.array([4,4,4])+col[:,:,None]*np.array([6,6,5])
  d=np.minimum(u,width-u)
  crack=np.clip((2.8+pnoise(seed+55,7,1.3)*.35-d)/2,0,1)
  a-=crack[:,:,None]*np.array([33,28,23])
 elif kind=='bark_olive':
  base=np.array([(117,111,101),(105,100,93),(90,87,82)][ix])
  bend=pnoise(seed+8,68,36)*19
  phase=(X+bend)/N*22*np.pi
  groves=np.abs(np.sin(phase))
  deep=np.maximum(0,.33-groves)/.33
  a=base[None,None,:]+fibers[:,:,None]*np.array([8,9,8])+rough[:,:,None]*np.array([10,10,9])
  a-=deep[:,:,None]*np.array([24,24,22]);a+=groves[:,:,None]*np.array([5,5,5])
 else:
  base=np.array([(120,79,60),(111,71,57),(97,66,56)][ix])
  bend=pnoise(seed+8,70,22)*8
  phase=(X+bend)/N*36*np.pi
  groves=np.abs(np.sin(phase))
  deep=np.maximum(0,.32-groves)/.32
  a=base[None,None,:]+fibers[:,:,None]*np.array([13,10,8])+rough[:,:,None]*np.array([7,6,6])
  a-=deep[:,:,None]*np.array([18,16,14])
 if ix:
  dirt=np.maximum(0,pnoise(seed+100,16,19))
  a-=dirt[:,:,None]*ix*4
 return seam(a)

items=[('vigas_viejas','comunes/madera','beam'),('tablas_puertas','comunes/madera','boards'),
       ('corteza_olivo_encina','comunes/arboles_y_troncos','bark_olive'),('corteza_cipres_pino','comunes/arboles_y_troncos','bark_cypress')]
files=[]
for mat,folder,kind in items:
 dest=ROOT/folder;dest.mkdir(parents=True,exist_ok=True)
 for v in 'abc':
  p=dest/f'{mat}_{v}.png';Image.fromarray(timber(kind,v)).save(p,optimize=True);files.append(p)
# Preview
size=251;left=15;top=51;rh=282;gap=10
sheet=Image.new('RGB',(2*left+4*size+3*gap,top+3*rh+12),(241,238,234));d=ImageDraw.Draw(sheet)
ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
d.text((left,10),'L06 · Maderas y cortezas · 12 PNG (follaje pendiente)',font=ft,fill=(38,38,38))
for j,(name,folder,_) in enumerate(items):
 for k,v in enumerate('abc'):
  p=ROOT/folder/f'{name}_{v}.png';im=Image.open(p).resize((size,size),Image.Resampling.LANCZOS)
  x=left+j*(size+gap);y=top+k*rh
  sheet.paste(im,(x,y));d.text((x,y+size+4),f'{name[:20]} · {v}',font=ft,fill=(41,39,40))
sheet.save(CTL/'preview_L06_maderas_12_texturas.jpg',quality=90)
for p in files:
 im=Image.open(p);im=im.resize((256,256))
 m=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):m.paste(im,(x*256,y*256))
 m.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=86)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);cols=rdr.fieldnames
families={i[0] for i in items}
assert sum(r['id_material'] in families for r in rows)==12
qa={'lote':'L06','estado':'parcial 12/24','imagenes':[]}
for r in rows:
 if r['id_material'] not in families:continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==(512,512)
 ar=np.asarray(im,dtype='int16');d=int(max(abs(ar[:,0]-ar[:,-1]).max(),abs(ar[0]-ar[-1]).max()))
 assert d<=1,(p,d)
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo procedural sin foto, borde validado. Pendiente prueba en Blender.'
 qa['imagenes'].append({'archivo':p.name,'resolucion':im.size,'sha256':sha,'borde_max':d})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for i in cat['materiales']:
 if i['clave_id'] not in families:continue
 for v in 'abc':
  p=next(p for p in files if p.name==f"{i['clave_id']}_{v}.png")
  i['variantes'][v]['estado']='generada';i['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  i['variantes'][v]['observaciones']='Procedimental provisional, no procedente de fotografía; revisar aspecto del material real.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote06_parcial.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';ls=plan.read_text('utf-8').splitlines()
for i,line in enumerate(ls):
 if line.startswith('**Progreso actual:**'):
  ls[i]=f'**Progreso actual:** {count}/294 PNG reales generados como prototipos. L01-L05 completos y L06 parcialmente 12/24 (maderas y cortezas). Pendiente validación artística y Blender.'
plan.write_text('\n'.join(ls)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado comprobado\n- Catálogo 98 materiales × 3 variantes = 294 PNG previstos.\n- L01: 15; L02: 18; L03: 21; L04: 18; L05: 15 completos como prototipos.\n- **L06 parcial:** 12/24 (vigas, tablas, corteza olivo/encina y corteza ciprés/pino).\n- **Total {count}/294 PNG existentes; quedan 195.**\n- Cada PNG tiene checksum y pruebas de bordes. No se ha verificado en Blender.\n- L02-L06 incluyen materiales procedimentales que deben revisarse estéticamente contra fotografías reales.\n\n## Continuación exacta\nL06: iniciar `ramillete_olivo_a.png`, luego ramillete encina, ciprés y corte de tronco. Son elementos de **512×512 RGBA con fondo transparente y NO repetibles**. Deben tener aspecto fotorealista natural. No producirlos como dibujo vectorial simplificado. Luego continuar L07 según manifiesto.\n\n## Recuperación\nAdjunta `paquete_continuidad_L01_L06_parcial.zip` al nuevo chat y pide seguir desde el primer estado pendiente (CSV y REANUDAR_AQUI.md).\n''','utf-8')
lot=BASE/'lote_06_parcial_madera_cortezas.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L06' in p.name or any(it[0] in p.name for it in items)):
   z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L06_parcial.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('Done',count,'/294 | lot',lot.stat().st_size,'| continuity',full.stat().st_size)
