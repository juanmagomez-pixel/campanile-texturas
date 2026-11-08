from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter
BASE=Path('/mnt/data');WORK=BASE/'texturas_renacimiento_italiano';CTL=WORK/'00_control';N=1024
Y,X=np.mgrid[:N,:N]

def noise(seed,sigma,n=N):
 raw=np.random.default_rng(seed).normal(size=(n,n)).astype(np.float32)
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*sigma*sigma*(fy*fy+fx*fx))
 z=np.fft.irfft2(np.fft.rfft2(raw)*filt,s=(n,n)).real.astype('float32')
 return (z-z.mean())/max(float(z.std()),1e-6)

def blend_seam(a,band=32):
 n=a.shape[0]; a=a.astype('float32').copy()
 for j in range(band):
  w=.5*(1+np.cos(np.pi*j/band));m=(a[:,j].copy()+a[:,n-1-j].copy())/2
  a[:,j]=a[:,j]*(1-w)+m*w;a[:,n-1-j]=a[:,n-1-j]*(1-w)+m*w
 for j in range(band):
  w=.5*(1+np.cos(np.pi*j/band));m=(a[j].copy()+a[n-1-j].copy())/2
  a[j]=a[j]*(1-w)+m*w;a[n-1-j]=a[n-1-j]*(1-w)+m*w
 return np.uint8(np.clip(np.rint(a),0,255))

def rulli(v):
 ix='abc'.index(v); seed=2100+ix*20
 cells=10;u=N/cells
 ox=np.mod(X,u)-u/2;oy=np.mod(Y,u)-u/2
 rad=np.sqrt(ox*ox+oy*oy); ring=np.abs(rad-u*.43)<3.8;glass=rad<u*.43
 cy=np.floor(Y/u).astype(int)%cells;cx=np.floor(X/u).astype(int)%cells
 rng=np.random.default_rng(3901)
 vari=rng.normal(size=(cells,cells)); vari=vari[cy,cx]
 cloud=noise(seed,20)*2.6+noise(seed+1,3)*2.2
 c=np.array([(143,160,155),(132,149,146),(122,142,138)][ix],dtype='float32')
 base=c[None,None,:]+cloud[:,:,None]+vari[:,:,None]*np.array([5,7,6])[None,None,:]
 # glass discs remain softly translucent; pale central bubble of rulli, no harsh glints
 pale=np.exp(-(rad/(u*.17))**2)
 base+=pale[:,:,None]*np.array([9,11,12])[None,None,:]
 lead=np.array((44,50,49),dtype='float32')+noise(seed+2,4)[:,:,None]*3
 a=np.where(glass[:,:,None],base,lead)
 a=np.where(ring[:,:,None],lead,a)
 pat=noise(seed+4,35)>1.0
 a-=pat[:,:,None]*ix*6
 return blend_seam(a)

def cuarterones(v):
 ix='abc'.index(v);seed=2200+ix*25
 cols=6;rows=5;cw=N/cols;rh=N/rows
 jx=np.mod(X,cw);jy=np.mod(Y,rh)
 rough=noise(seed,6)
 lead=(jx<(5+rough)) | (jx>cw-(5+rough)) | (jy<(5+rough)) | (jy>rh-(5+rough))
 cx=(X//cw).astype(int)%cols;cy=(Y//rh).astype(int)%rows
 rng=np.random.default_rng(3612)
 vars=rng.normal(size=(rows,cols));variation=vars[cy,cx]
 cloud=noise(seed+4,27)*3.7+noise(seed+5,5)*2.1
 base=np.array([(142,157,151),(133,151,147),(121,139,138)][ix],dtype='float32')
 a=base[None,None,:]+cloud[:,:,None]+variation[:,:,None]*np.array([4.8,6.0,5.7])[None,None,:]
 a=np.where(lead[:,:,None],np.array([44,49,48])[None,None,:]+cloud[:,:,None]*.2,a)
 a-=np.maximum(noise(seed+22,21),0)[:,:,None]*ix*4
 return blend_seam(a)

def churchglass(v):
 ix='abc'.index(v);seed=2400+ix*22
 rows=8;cols=8;cw=N/cols;ch=N/rows
 u=np.mod(X,cw)/cw;w=np.mod(Y,ch)/ch
 cell_x=(X//cw).astype('int32');cell_y=(Y//ch).astype('int32')
 # Mixed diamond lead geometries with deep historical glass colors, not figurative panels.
 palette=np.array([(48,76,103),(115,57,61),(128,105,63),(53,95,80)],dtype='float32')
 choice=((cell_x+2*cell_y)%4).astype('int32')
 # interlocking diagonal rhombi within lead cells
 tri=np.where(u>w,1,0)
 choice=(choice+tri)%4
 glass=palette[choice]
 joint=(u<.037)|(w<.037)|(abs(u-w)<.031)|(u>.971)|(w>.971)
 cloud=noise(seed,9)*5+noise(seed+1,30)*3
 out=glass+cloud[:,:,None]
 out=np.where(joint[:,:,None],np.array([30,32,34])[None,None,:]+cloud[:,:,None]*.2,out)
 # exterior view: deliberately subdued, opaque stained glass
 out=np.clip(out*(1.0-ix*.07),0,255)
 return blend_seam(out)

def sgraffito(v):
 ix='abc'.index(v);seed=2500+ix*24
 micro=noise(seed,3)*3.2+noise(seed+1,28)*4
 base=np.array([(208,196,173),(196,185,164),(182,172,153)][ix],dtype='float32')
 a=base[None,None,:]+micro[:,:,None]
 # physically scratched repeated Renaissance geometric rombi and plant scrollwork
 # Draw dark layer as very delicate sgraffito, then erode by surface noise.
 mask=Image.new('L',(N,N),0);d=ImageDraw.Draw(mask)
 c=256
 for row in range(4):
  for col in range(4):
   x=col*c;y=row*c
   d.line([(x+128,y+18),(x+238,y+128),(x+128,y+238),(x+18,y+128),(x+128,y+18)],fill=80,width=5)
   d.ellipse((x+102,y+102,x+154,y+154),outline=70,width=4)
   # simplified vegetal arabesques with moderately imperfect curves
   for shift in (-1,1):
    d.arc((x+73+shift*18,y+75,x+178+shift*18,y+174), 30 if shift==1 else 160,270 if shift==1 else 350,fill=74,width=5)
   for dx,dy in ((0,-72),(72,0),(0,72),(-72,0)):
    d.ellipse((x+124+dx-9,y+124+dy-6,x+124+dx+9,y+124+dy+6),outline=64,width=3)
 opacity=np.asarray(mask,dtype='float32')/255
 opacity*=np.clip((noise(seed+5,5)+2.0)/3.0,0,1)
 below=np.array([88,89,85],dtype='float32')
 a=a*(1-opacity[:,:,None])+below[None,None,:]*opacity[:,:,None]
 a-=np.maximum(noise(seed+17,38),0)[:,:,None]*ix*3
 return blend_seam(a)

def terracotta(v):
 ix='abc'.index(v);seed=2600+ix*29
 # Four handmade relief rosettes horizontally and vertically across 1 × 1 m.
 tile=256
 height=Image.new('F',(N,N),0.15);d=ImageDraw.Draw(height)
 # height in emboss rather than crisp ink strokes
 for i in range(4):
  for j in range(4):
   cx=j*tile+tile//2;cy=i*tile+tile//2
   d.ellipse((cx-104,cy-104,cx+104,cy+104),fill=.52)
   d.ellipse((cx-88,cy-88,cx+88,cy+88),fill=.38)
   for petal in range(8):
    a=2*np.pi*petal/8;px=cx+52*np.cos(a);py=cy+52*np.sin(a)
    d.ellipse((int(px)-27,int(py)-27,int(px)+27,int(py)+27),fill=.78)
   d.ellipse((cx-25,cy-25,cx+25,cy+25),fill=.85)
 bump=gaussian_filter(np.asarray(height,dtype='float32'),sigma=3.0,mode='wrap')
 gy,gx=np.gradient(bump)
 grain=noise(seed,2.0)*4.6+noise(seed+1,12)*4.9+noise(seed+2,38)*2.0
 colors=np.array([(173,93,66),(159,82,57),(144,74,55)][ix],dtype='float32')
 a=colors[None,None,:]+grain[:,:,None]-bump[:,:,None]*np.array([10,9,8])[None,None,:]
 a+=(gx-gy)[:,:,None]*np.array([900,820,720])[None,None,:]
 a+=(bump-.43)[:,:,None]*np.array([37,34,31])[None,None,:]
 a-=np.maximum(noise(seed+3,40),0)[:,:,None]*ix*4
 return blend_seam(a)

items=[('vidrio_rulli','comunes/vidrio',rulli),('vidrio_cuarterones','comunes/vidrio',cuarterones),
       ('vidriera_iglesia','comunes/vidrio',churchglass),('esgrafiado_florentino','comunes/fachadas_decoradas',sgraffito),
       ('terracota_decorativa','comunes/fachadas_decoradas',terracotta)]
files=[]
for name,dir_,fn in items:
 out=WORK/dir_;out.mkdir(parents=True,exist_ok=True)
 for v in 'abc':
  p=out/f'{name}_{v}.png'
  if not p.exists(): Image.fromarray(fn(v)).save(p,optimize=True)
  files.append(p)
# Preview and mosaic
thumb=223;gap=8;head=48;rh=255;left=14
sheet=Image.new('RGB',(left*2+5*thumb+4*gap,head+rh*3+20),(239,237,231))
d=ImageDraw.Draw(sheet);ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
d.text((left,10),'L05 · Vidrio y fachadas decorativas · prototipos',font=ft,fill=(36,37,38))
for c,(name,dir_,_) in enumerate(items):
 for r,v in enumerate('abc'):
  p=WORK/dir_/f'{name}_{v}.png'
  im=Image.open(p).resize((thumb,thumb),Image.Resampling.LANCZOS)
  x=left+c*(thumb+gap);y=head+r*rh
  sheet.paste(im,(x,y));d.text((x,y+thumb+4),name[:18]+f' · {v}',font=ft,fill=(45,44,43))
sheet.save(CTL/'preview_L05_15_texturas.jpg',quality=90)
for p in files:
 im=Image.open(p).resize((384,384),Image.Resampling.LANCZOS)
 m=Image.new('RGB',(1152,1152))
 for y in range(3):
  for x in range(3):m.paste(im,(x*384,y*384))
 m.resize((768,768),Image.Resampling.LANCZOS).save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=85)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);cols=rdr.fieldnames
assert sum(r['lote']=='L05' for r in rows)==15
qa={'lote':'L05','imagenes':[]}
for r in rows:
 if r['lote']!='L05':continue
 p=WORK/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==(1024,1024)
 ar=np.asarray(im,dtype=np.int16)
 maxedge=int(max(abs(ar[:,0]-ar[:,-1]).max(),abs(ar[0]-ar[-1]).max()))
 assert maxedge<=1,(p,maxedge)
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo geométrico/procedural, bordes verificados. Pendiente validar realismo en Blender y exactitud histórica.'
 qa['imagenes'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'max_diferencia_borde':maxedge})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if item['clave_id'] not in {z[0] for z in items}:continue
 for v in 'abc':
  p=next(p for p in files if p.name==f"{item['clave_id']}_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Prototipo procedimental de patrón geométrico, requerirá validación artística y Blender.'
catp.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n','utf-8')
(CTL/'verificacion_lote05.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';lines=plan.read_text('utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[i]=f'**Progreso actual:** L01-L05 generados como prototipos, {count}/294 PNG físicos. Bordes y mosaicos verificados; falta validación en Blender y revisión de realismo, principalmente L02-L05.'
plan.write_text('\n'.join(lines)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado comprobado\n- Catálogo de 98 materiales y 294 variantes PNG.\n- L01 tejados: 15; L02 muros: 18; L03 piedra noble: 21; L04 mármoles lisos y columnas: 18; L05 vidrio y decoración: 15.\n- **{count}/294 PNG reales, 207 pendientes.**\n- Tests: resolución correcta, coincidencia de bordes y mosaicos 3×3.\n- Ningún lote está aprobado artísticamente aún; L02-L05 están hechos por procedimiento y podrían requerir fotografías/escaneos o una revisión adicional.\n- L01 contiene algunos recortes de atlas de menor calidad efectiva; revisar en render del juego.\n\n## Siguiente lote\nL06 — madera y árboles (8 materiales x 3 = 24 PNG). Iniciar por `vigas_viejas_a.png` del manifiesto. En hojas/cortes de tronco, utilizar PNG alfa no repetible.\n\n## Cómo continuar\nAdjunta `paquete_continuidad_L01_L05.zip` al abrir otro chat y pide seguir desde REANUDAR_AQUI.md, sin rehacer archivos existentes.\n''','utf-8')
lot=BASE/'lote_05_comunes_vidrio_decoracion.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L05' in p.name or any(it[0] in p.name for it in items)):
   z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
full=BASE/'paquete_continuidad_L01_L05.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(WORK.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
print('Done',count,'/294 | lot',lot.stat().st_size,'| continuity',full.stat().st_size)
