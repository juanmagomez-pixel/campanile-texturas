from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/mnt/data');WORK=BASE/'texturas_renacimiento_italiano';CTL=WORK/'00_control';N=512
Y,X=np.mgrid[:N,:N]

def noise(seed,sy,sx=None):
 sx=sy if sx is None else sx
 z=np.random.default_rng(seed).normal(size=(N,N)).astype('float32')
 fy=np.fft.fftfreq(N)[:,None];fx=np.fft.rfftfreq(N)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sy*sy*fy*fy+sx*sx*fx*fx))
 a=np.fft.irfft2(np.fft.rfft2(z)*filt,s=(N,N)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-6)

def grain(seed):
 return 0.9*noise(seed,1.4)+.59*noise(seed+10,6)+.45*noise(seed+20,25)+.24*noise(seed+30,74)

def seamless(ar,b=18):
 a=ar.astype('float32').copy()
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,N-1-j].copy())/2
  a[:,j]=a[:,j]*(1-t)+m*t;a[:,N-1-j]=a[:,N-1-j]*(1-t)+m*t
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[N-1-j].copy())/2
  a[j]=a[j]*(1-t)+m*t;a[N-1-j]=a[N-1-j]*(1-t)+m*t
 return np.uint8(np.clip(np.rint(a),0,255))

def slabs(v):
 i='abc'.index(v); seed=10120+i*40
 # 3 rows ×4 columns for 2m of paved stone, staggered joints.
 cw=N/4;ch=N/4
 row=(Y//ch).astype(int);shift=(row%2)*(cw/2)
 x=np.mod(X+shift,cw);y=np.mod(Y,ch)
 col=np.floor((X+shift)/cw).astype(int)%4
 rng=np.random.default_rng(201)
 lum=rng.normal(size=(4,4))[row%4,col]*6
 mortar=np.clip((3.8+noise(seed+99,5)*.5-np.minimum.reduce((x,cw-x,y,ch-y)))/2,0,1)
 base=np.array([(137,130,119),(128,123,112),(117,112,104)][i])
 val=grain(seed)*5+lum
 stone=base[None,None,:]+val[:,:,None]
 grout=base[None,None,:]-np.array([14,14,12])[None,None,:]+grain(seed+30)[:,:,None]*2
 a=stone*(1-mortar[:,:,None])+grout*mortar[:,:,None]
 return seamless(a)

def earth(v):
 i='abc'.index(v);seed=10200+i*20
 a=np.array([(142,117,88),(133,109,83),(119,99,78)][i])[None,None,:]+grain(seed)[:,:,None]*np.array([8,7,6])[None,None,:]
 st=noise(seed+12,1.0)>2.4
 a=np.where(st[:,:,None],a+np.array([16,13,10])[None,None,:],a)
 return seamless(a)

def gravel(v):
 i='abc'.index(v);seed=10300+i*20;rng=np.random.default_rng(seed)
 a=np.array([(158,148,128),(148,139,123),(138,130,115)][i])[None,None,:]+grain(seed)[:,:,None]*np.array([10,9,8])[None,None,:]
 im=Image.fromarray(np.uint8(np.clip(a,0,255)))
 d=ImageDraw.Draw(im)
 # 1–4 cm stones across 2m = 2.5–10px; naturally colored granules.
 for j in range(8000):
  x=int(rng.integers(0,N));y=int(rng.integers(0,N));rad=int(rng.choice([1,2,3,4,5],p=[.3,.33,.22,.12,.03]))
  colors=[(171,162,145),(132,127,118),(192,178,151),(119,117,109),(157,148,130)]
  c=colors[int(rng.integers(0,len(colors)))]
  d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=c)
 return seamless(np.asarray(im,dtype='float32')*.8+a*.2)

def linen(v):
 i='abc'.index(v);seed=10400+i*20
 u=(np.sin(X*2*np.pi/4.3)+np.sin(Y*2*np.pi/4.3))*.6
 weather=noise(seed,28)*2.2+noise(seed+10,100,40)*3.8
 a=np.array([(206,197,172),(195,185,165),(182,172,154)][i])[None,None,:]+(u+grain(seed)*1.5+weather)[:,:,None]*np.array([2.5,2.6,2.4])
 return seamless(a)

def furrows(v):
 i='abc'.index(v);seed=10500+i*50
 bend=noise(seed,45,75)*4
 # about 7 longitudinal furrows spaced 30cm across 2m.
 phase=np.mod((X+bend)/N*7,1)
 trough=np.exp(-((phase-.2)/.16)**2)
 ridge=np.exp(-((phase-.7)/.25)**2)
 texture=grain(seed)*7
 base=np.array([(123,96,68),(113,89,65),(104,82,62)][i],dtype='float32')
 a=base[None,None,:]+texture[:,:,None]+ridge[:,:,None]*np.array([9,8,6])-trough[:,:,None]*np.array([20,16,12])
 return seamless(a)

def grass(v):
 i='abc'.index(v);seed=10600+i*21
 grassnoise=grain(seed)*7+noise(seed+14,13)*9
 base=np.array([(102,120,65),(109,115,67),(107,103,65)][i])
 a=base[None,None,:]+grassnoise[:,:,None]*np.array([.8,1.1,.4])
 holes=noise(seed+60,15)>([1.9,1.65,1.37][i])
 soil=np.array([139,118,80],dtype='float32')[None,None,:]+grain(seed+31)[:,:,None]*4
 a=np.where(holes[:,:,None],soil,a)
 straw=(noise(seed+2,1.2)>2.3)&(~holes)
 a[straw]+=[11,9,-2]
 return seamless(a)

def clay(v):
 i='abc'.index(v);seed=10700+i*20
 base=np.array([(158,102,72),(145,90,66),(130,82,65)][i])
 a=base[None,None,:]+grain(seed)[:,:,None]*np.array([7,6,5])
 damp=np.clip(noise(seed+18,21),0,2)/2
 a-=damp[:,:,None]*np.array([12+2*i,10+2*i,10+2*i])
 pools=np.clip(noise(seed+31,65)-1.2,0,1)
 a-=pools[:,:,None]*np.array([10,11,8])
 return seamless(a)

def landfill(v):
 i='abc'.index(v);seed=10800+i*40;rng=np.random.default_rng(seed)
 base=np.array([(85,77,64),(76,70,61),(68,63,57)][i])
 a=base[None,None,:]+grain(seed)[:,:,None]*np.array([12,11,10])
 # Ash patches in soil; small remnants of organic matter only.
 ash=np.maximum(noise(seed+10,22)-1.25,0)/2
 a+=ash[:,:,None]*np.array([38,36,33])
 im=Image.fromarray(np.uint8(np.clip(a,0,255)))
 d=ImageDraw.Draw(im)
 colors=[(157,140,98),(112,101,75),(90,85,76),(139,127,108),(167,150,123)]
 for k in range(850):
  x=int(rng.integers(0,N));y=int(rng.integers(0,N))
  length=int(rng.integers(2,14));dx=int(rng.integers(-3,4));dy=length
  d.line((x,y,x+dx,y+dy),fill=colors[int(rng.integers(0,len(colors)))],width=int(rng.integers(1,3)))
 return seamless(np.asarray(im,dtype='float32'))

items=[('losas_piedra','comunes/suelos',slabs),('tierra_apisonada','comunes/suelos',earth),('grava','comunes/suelos',gravel),
       ('toldo_lino','comunes/telas',linen),('tierra_arada','comunes/campos_jardines_e_industria',furrows),
       ('hierba_corta','comunes/campos_jardines_e_industria',grass),('arcilla_humeda','comunes/campos_jardines_e_industria',clay),
       ('vertedero','comunes/campos_jardines_e_industria',landfill)]
files=[]
for name,folder,fn in items:
 dest=WORK/folder;dest.mkdir(parents=True,exist_ok=True)
 for v in 'abc':
  p=dest/f'{name}_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# Preview
size=157;gap=5;head=48;rh=183;left=9
sheet=Image.new('RGB',(2*left+8*size+7*gap,head+3*rh+12),(239,236,230));d=ImageDraw.Draw(sheet)
ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
d.text((left,11),'L07 · Suelos, campo, lino e industria (24 variantes)',font=ft,fill=(40,39,38))
for col,(name,folder,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=WORK/folder/f'{name}_{v}.png';im=Image.open(p).resize((size,size),Image.Resampling.LANCZOS)
  x=left+col*(size+gap);y=head+row*rh
  sheet.paste(im,(x,y));d.text((x,y+size+3),name[:17]+f' · {v}',font=ft,fill=(46,45,44))
sheet.save(CTL/'preview_L07_24_texturas.jpg',quality=90)
for p in files:
 im=Image.open(p).resize((256,256));m=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):m.paste(im,(x*256,y*256))
 m.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=87)
# QA and states
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);cols=rdr.fieldnames
assert sum(row['lote']=='L07' for row in rows)==24
qa={'lote':'L07','archivos':[]}
for row in rows:
 if row['lote']!='L07':continue
 p=WORK/row['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==(512,512)
 ar=np.asarray(im,dtype=np.int16)
 mx=int(max(abs(ar[:,0]-ar[:,-1]).max(),abs(ar[0]-ar[-1]).max()))
 assert mx<=1,(p,mx)
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 row['estado']='generada';row['sha256']=sha;row['notas']='Prototipo procedimental; textura y mosaico 3×3; pendiente Blender y comparación con foto.'
 qa['archivos'].append({'archivo':p.name,'resolucion':im.size,'max_diferencia_borde':mx,'sha256':sha})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if item['clave_id'] not in {i[0] for i in items}:continue
 for v in 'abc':
  p=next(p for p in files if p.name==f"{item['clave_id']}_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Procedimental de base, no foto: revisar textura histórica en Blender.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote07.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(row['estado']=='generada' for row in rows)
plan=CTL/'plan_produccion_v2.md';lines=plan.read_text('utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[i]=f'**Progreso actual:** {count}/294 PNG generados como prototipos. L01-L05 + L07 completos; L06 12/24 (transparencias pendientes). Nada validado definitivamente en Blender.'
plan.write_text('\n'.join(lines)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado comprobado\n- Catálogo 98 materiales y 294 PNG (tres variantes a/b/c).\n- L01: 15; L02: 18; L03: 21; L04: 18; L05: 15; L06 parcial: 12/24; L07: 24.\n- **{count}/294 PNG generados**, faltan {294-count}.\n- Se han verificado tamaños y coincidencia de bordes en todas las variantes marcadas «generada»; los mosaicos 3×3 están en 00_control.\n- Aún no hay revisión final en Blender; L02-L07 son materiales procedimentales y podrían requerir sustitución por fuentes fotográficas para cumplir el objetivo realista.\n\n## Continuación exacta\n1. L06: completar 12 PNG alfa, empezando por `ramillete_olivo_a.png`; ramillete encina, ciprés y corte de tronco. Estos NO son repetibles; deben ser fotorrealistas sobre transparencia real.\n2. L08: comenzar Florencia (12 PNG) según manifiesto.\n3. Continuar L09 Venecia ... L16 detalles.\n\n## Recuperación\nAdjuntar `paquete_continuidad_L01_L07.zip` y pedir continuar desde este archivo y la primera fila pendiente en progreso_produccion.csv.\n''','utf-8')
lot=BASE/'lote_07_comunes_suelos_campos.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L07' in p.name or any(it[0] in p.name for it in items)):
   z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
full=BASE/'paquete_continuidad_L01_L07.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(WORK.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
