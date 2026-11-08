from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control'

def noise(n,seed,sy,sx=None):
 sx=sy if sx is None else sx
 r=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sy*sy*fy*fy+sx*sx*fx*fx))
 a=np.fft.irfft2(np.fft.rfft2(r)*filt,s=(n,n)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-6)

def seam(a):
 n=a.shape[0];b=max(10,int(n*.032));a=a.astype('float32').copy()
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,n-1-j].copy())/2
  a[:,j]=a[:,j]*(1-t)+m*t;a[:,n-1-j]=a[:,n-1-j]*(1-t)+m*t
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[n-1-j].copy())/2
  a[j]=a[j]*(1-t)+m*t;a[n-1-j]=a[n-1-j]*(1-t)+m*t
 return np.uint8(np.clip(np.rint(a),0,255))

def scaffold(v):
 i='abc'.index(v);n=512;seed=19100+i*24
 src=np.asarray(Image.open(ROOT/f'comunes/madera/tablas_puertas_{v}.png'),dtype='float32')
 pale=np.array([(187,163,131),(175,152,123),(157,142,119)][i])
 a=src*.3+pale[None,None,:]*.7
 lime=np.maximum(noise(n,seed,32)-1.2,0)
 a+=lime[:,:,None]*np.array([20,20,18]);a-=np.maximum(noise(n,seed+2,28)-1.8,0)[:,:,None]*11
 return seam(a)

def rawstone(v):
 i='abc'.index(v);n=512;seed=19200+i*22
 src=np.asarray(Image.open(ROOT/f'comunes/muros/mamposteria_zocalo_{v}.png'),dtype='float32')
 target=np.array([(132,126,115),(122,119,109),(110,108,103)][i])
 a=src*.55+target[None,None,:]*.45+noise(n,seed,5)[:,:,None]*4
 # exposed chipped raw stones remain modeled geometry, this is albedo only
 return seam(a)

def mortar(v):
 i='abc'.index(v);n=512;seed=19300+i*20
 soil=np.asarray(Image.open(ROOT/f'comunes/suelos/tierra_apisonada_{v}.png'),dtype='float32')
 ash=np.maximum(0,noise(n,seed,24)-.4)
 a=soil*.8+np.array([151,139,119])[None,None,:]*.2+ash[:,:,None]*np.array([33,33,33])
 fragments=np.maximum(0,noise(n,seed+2,3)-2)
 a+=fragments[:,:,None]*np.array([30,11,5])
 return seam(a)

def castle(v):
 i='abc'.index(v);n=512;seed=19400+i*26
 # 60-100cm stones in 4m square tile; approx 5 blocks across × 6 courses.
 yy,xx=np.mgrid[:n,:n]
 bw=n/5;rh=n/6;row=np.floor(yy/rh).astype(int)
 off=(row%2)*bw/2
 u=np.mod(xx+off,bw);w=np.mod(yy,rh)
 block=np.floor((xx+off)/bw).astype(int)%5
 rng=np.random.default_rng(5025);shades=rng.normal(size=(6,5))[row,block]
 base=np.array([(127,116,98),(115,107,94),(105,100,91)][i])
 rock=noise(n,seed,3)*8+noise(n,seed+1,19)*7
 a=base[None,None,:]+rock[:,:,None]+shades[:,:,None]*4
 gap=np.minimum.reduce([u,bw-u,w,rh-w]);joint=np.clip((4+noise(n,seed+3,2)*.7-gap)/3,0,1)
 a=a*(1-joint[:,:,None])+(base-17)[None,None,:]*joint[:,:,None]
 lichens=noise(n,seed+5,20)>2.2
 a+=lichens[:,:,None]*np.array([-10,4,-5])
 return seam(a)

def brickcastle(v):
 i='abc'.index(v);n=512;seed=19500+i*16
 bricks=np.asarray(Image.open(ROOT/f'comunes/muros/ladrillo_lombardo_{v}.png'),dtype='float32')
 stone=np.asarray(Image.open(ROOT/f'comunes/piedra_noble/piedra_serena_sillares_{v}.png'),dtype='float32')
 yy=np.arange(n)[:,None]
 # stone courses every ~1m over a 4m high tile.
 st=np.mod(yy,128)<21
 a=np.where(st[:,:,None],stone*.8+np.array([128,121,109])[None,None,:]*.2,bricks)
 a-=np.maximum(noise(n,seed,29)-1.6,0)[:,:,None]*4
 return seam(a)

def yard(v):
 i='abc'.index(v);n=512;seed=19600+i*20;rng=np.random.default_rng(seed)
 a=np.asarray(Image.open(ROOT/f'comunes/suelos/tierra_apisonada_{v}.png'),dtype='float32')
 target=np.array([(139,112,82),(128,105,82),(115,97,78)][i])
 a=a*.7+target[None,None,:]*.3
 # moderately used horse-and-cart yard: a few tracks and straw flecks, no giant icon-like hoofprints
 y,x=np.mgrid[:n,:n]
 tracks=(np.abs(x-(n*.28+noise(n,seed,61)*3))<3)|(np.abs(x-(n*.74+noise(n,seed+1,59)*3))<3)
 a-=tracks[:,:,None]*np.array([13,11,9])
 im=Image.fromarray(np.uint8(np.clip(a,0,255)));d=ImageDraw.Draw(im)
 for k in range(320):
  xx=int(rng.integers(0,n));yy=int(rng.integers(0,n))
  d.line((xx,yy,xx+int(rng.integers(-4,4)),yy+int(rng.integers(-3,8))),fill=(174,148,93),width=1)
 return seam(np.asarray(im,dtype='float32'))
items=[('madera_andamio','detalles/obras',scaffold),('piedra_bruto','detalles/obras',rawstone),('cal_mortero','detalles/obras',mortar),
       ('sillares_muralla','detalles/murallas_y_militar',castle),('muralla_ladrillo_piedra','detalles/murallas_y_militar',brickcastle),('tierra_cuartel','detalles/murallas_y_militar',yard)]
files=[]
for name,folder,fn in items:
 dest=ROOT/folder;dest.mkdir(parents=True,exist_ok=True)
 for v in 'abc':
  p=dest/f'{name}_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# preview
size=196;left=12;head=48;rh=227;gap=7
sheet=Image.new('RGB',(left*2+6*size+5*gap,head+3*rh+10),(241,238,232));d=ImageDraw.Draw(sheet)
fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
d.text((left,10),'L16 · Obras, murallas y terreno militar (18 variantes)',font=fnt,fill=(40,39,38))
for col,(name,folder,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=ROOT/folder/f'{name}_{v}.png';im=Image.open(p).resize((size,size),Image.Resampling.LANCZOS)
  x=left+col*(size+gap);y=head+row*rh
  sheet.paste(im,(x,y));d.text((x,y+size+4),f'{name[:19]} · {v}',font=fnt,fill=(44,43,42))
sheet.save(CTL/'preview_L16_18_texturas.jpg',quality=88)
for p in files:
 im=Image.open(p).resize((256,256));m=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):m.paste(im,(x*256,y*256))
 m.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=85)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);fields=rdr.fieldnames
assert sum(r['lote']=='L16' for r in rows)==18
qa={'lote':'L16','archivos':[]}
for r in rows:
 if r['lote']!='L16':continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==tuple(map(int,r['resolucion'].split('x')))
 a=np.asarray(im,dtype=np.int16);mx=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert mx<=1
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo físico de obra o muralla, pendiente vista Blender y detalle arquitectónico.'
 qa['archivos'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'max_diferencia_borde':mx})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if item['clave_id'] not in {z[0] for z in items}:continue
 for v in 'abc':
  p=next(p for p in files if p.name==f"{item['clave_id']}_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Prototipo, pendiente revisión de escena y realismo.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote16.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';lines=plan.read_text('utf-8').splitlines()
for j,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[j]=f'**Progreso actual:** {count}/294 PNG. Todos los lotes L01-L16 prototipados salvo 12 imágenes RGBA de follajes/tronco en L06. Nada validado definitivamente en Blender.'
plan.write_text('\n'.join(lines)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md';resume.write_text(f'''# Reanudar aquí — Texturas Renacimiento italiano\n\nCorte: 2026-11-07.\n\n## Estado verificado\n- 98 familias, 294 PNG (tres variantes a/b/c).\n- **{count}/294 PNG reales existentes**, **12 pendientes**.\n- Todos los lotes han generado sus PNG de superficie, salvo los cuatro tipos de imágenes transparentes de L06.\n- Pendientes precisos:\n  - `ramillete_olivo_a/b/c.png`\n  - `ramillete_encina_a/b/c.png`\n  - `ramillete_cipres_a/b/c.png`\n  - `corte_tronco_a/b/c.png`\n  - Deben ser 512×512 RGBA, con fondo realmente transparente, no repetibles, silueta natural y realismo fotográfico.\n- Los demás tienen SHA-256, tamaño comprobado, continuidad de bordes donde aplica y mosaicos 3x3.\n- Ninguna textura ha recibido aprobación artística final: las capas L02-L16 son mayoritariamente procedimentales y necesitan comparación con fotos y render Blender al tamaño real.\n\n## Reanudar\nAdjuntar `paquete_continuidad_L01_L16_parcial.zip`; continuar los 12 recursos RGBA que faltan y después revisar calidad/escala para decidir sustituciones.\n''','utf-8')
lot=BASE/'lote_16_obras_murallas.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L16' in p.name or any(it[0] in p.name for it in items)):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L16_parcial.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
