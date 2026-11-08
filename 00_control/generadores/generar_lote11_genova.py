from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates,gaussian_filter
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control';OUT=ROOT/'ciudad/génova';OUT.mkdir(parents=True,exist_ok=True)

def noise(seed,n,sy,sx=None):
 sx=sy if sx is None else sx
 r=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sy*sy*fy*fy+sx*sx*fx*fx))
 ar=np.fft.irfft2(np.fft.rfft2(r)*filt,s=(n,n)).real.astype('float32')
 return (ar-ar.mean())/max(float(ar.std()),1e-6)

def seam(img):
 n=img.shape[0];b=max(15,int(n*.034));a=img.astype('float32').copy()
 for j in range(b):
  w=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,n-1-j].copy())/2
  a[:,j]=a[:,j]*(1-w)+m*w;a[:,n-1-j]=a[:,n-1-j]*(1-w)+m*w
 for j in range(b):
  w=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[n-1-j].copy())/2
  a[j]=a[j]*(1-w)+m*w;a[n-1-j]=a[n-1-j]*(1-w)+m*w
 return np.uint8(np.clip(np.rint(a),0,255))

def facade(v,rose=False):
 i='abc'.index(v);n=1024;seed=12500+i*51+(500 if rose else 0)
 if rose:base=np.array([(204,147,135),(193,136,125),(177,129,121)][i])
 else:base=np.array([(207,184,140),(194,172,133),(182,162,131)][i])
 fine=noise(seed,n,2.4)*3.3+noise(seed+2,n,36)*5.1+noise(seed+3,n,113)*3
 bg=base[None,None,:]+fine[:,:,None]
 # Light and dark sgraffito strokes suggesting *painted* architectural window frames.
 # White false stones and central arches are not actual cavities.
 pattern=Image.new('L',(n,n),0);d=ImageDraw.Draw(pattern)
 for xx in (0,512):
  for yy in (0,512):
   x=xx+80;y=yy+60
   d.rectangle((x,y,x+344,y+390),outline=105,width=22)
   d.rectangle((x+25,y+27,x+320,y+364),outline=60,width=13)
   d.rectangle((x-12,y+389,x+357,y+421),fill=115)
   d.line((x+172,y+35,x+172,y+355),fill=70,width=12)
   d.arc((x+45,y+53,x+300,y+225),180,360,fill=78,width=11)
 mask=np.asarray(pattern,dtype='float32')/255
 mask*=np.clip((noise(seed+5,n,18)+2)/3,0,1)
 # The architecture is painted in gray-white mineral pigment weathered by salt air.
 fake=np.array([220,215,205],dtype='float32')[None,None,:]
 a=bg*(1-mask[:,:,None])+fake*mask[:,:,None]
 a-=np.maximum(noise(seed+11,n,64),0)[:,:,None]*(i*2.3)
 return seam(a)

def shutters(v):
 i='abc'.index(v);n=1024;seed=13100+i*33
 y,x=np.mgrid[:n,:n]
 slat=1024/20.0
 u=np.mod(y,slat)
 # dark slat gap and hand-painted green oak louvers
 crev=np.clip((7-u)/6,0,1)
 lift=np.clip((u-10)/20,0,1)
 fib=noise(seed,n,90,3)*5.0+noise(seed+2,n,7,2)*3
 base=np.array([(59,94,70),(52,83,62),(47,72,58)][i])
 a=base[None,None,:]+fib[:,:,None]+lift[:,:,None]*np.array([9,11,7])
 a-=crev[:,:,None]*np.array([17,18,17])
 # irregular weathered paint (underlying gray wood), low-frequency and tiny flakes
 worn=noise(seed+21,n,4)+.3*noise(seed+22,n,25)
 chips=worn>([2.8,2.5,2.2][i])
 a=np.where(chips[:,:,None],np.array([99,96,85])[None,None,:]+fib[:,:,None]*.4,a)
 return seam(a)

def paviment(v):
 i='abc'.index(v);n=512
 brick=np.asarray(Image.open(ROOT/f'comunes/muros/ladrillo_toscano_{v}.png'),dtype='float32')
 pebble=np.asarray(Image.open(ROOT/f'comunes/suelos/grava_{v}.png'),dtype='float32')
 y,x=np.mgrid[:n,:n]
 theta=np.deg2rad(43)
 xx=np.mod((x-n/2)*np.cos(theta)+(y-n/2)*np.sin(theta)+n/2,n)
 yy=np.mod(-(x-n/2)*np.sin(theta)+(y-n/2)*np.cos(theta)+n/2,n)
 rot=np.stack([map_coordinates(brick[:,:,c],(yy,xx),mode='wrap',order=1) for c in range(3)],2)
 # Footpaths framed by bands of grey Ligurian river pebble stripes.
 band=((x%256)<35)|((x%256)>221)
 a=np.where(band[:,:,None],pebble*.8+np.array([116,116,111])[None,None,:]*.2,rot)
 return seam(a)
items=[('fachada_pintada',1024,lambda v:facade(v,False)),('fachada_rosa',1024,lambda v:facade(v,True)),
       ('persianas_verdes',1024,shutters),('pavimento_ladrillo_pizarra',512,paviment)]
files=[]
for name,res,fn in items:
 for v in 'abc':
  p=OUT/f'{name}_genova_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# preview
thumb=247;left=14;head=53;rh=280;gap=10
sheet=Image.new('RGB',(2*left+4*thumb+3*gap,head+3*rh+9),(241,238,232));d=ImageDraw.Draw(sheet)
fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
d.text((left,11),'L11 · Génova · fachadas, persianas y creuza',font=fnt,fill=(38,39,37))
for c,(name,_,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_genova_{v}.png';im=Image.open(p).resize((thumb,thumb),Image.Resampling.LANCZOS)
  x=left+c*(thumb+gap);y=head+row*rh
  sheet.paste(im,(x,y));d.text((x,y+thumb+5),f'{name[:21]} · {v}',font=fnt,fill=(44,42,39))
sheet.save(CTL/'preview_L11_genova_12_texturas.jpg',quality=90)
for p in files:
 im=Image.open(p).resize((256,256));m=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):m.paste(im,(x*256,y*256))
 m.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=86)
# metadata
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.DictReader(f);rows=list(rd);fields=rd.fieldnames
assert sum(r['lote']=='L11' for r in rows)==12
qa={'lote':'L11','archivos':[]}
for r in rows:
 if r['lote']!='L11':continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==tuple(map(int,r['resolucion'].split('x')))
 a=np.asarray(im,dtype=np.int16);mx=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert mx<=1
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha;r['notas']='Material genovés de base procedimental, revisar realismo y anacronismos en Blender.'
 qa['archivos'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'max_diferencia_borde':mx})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for it in cat['materiales']:
 if str(it.get('ciudad','')).lower() not in ('génova','genova'):continue
 if it['clave_id'] not in {q[0] for q in items}:continue
 for v in 'abc':
  p=next(p for p in files if p.name==f"{it['clave_id']}_genova_{v}.png")
  it['variantes'][v]['estado']='generada';it['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  it['variantes'][v]['observaciones']='Prototipo genovés, revisión visual en juego pendiente.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote11.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';lines=plan.read_text('utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[i]=f'**Progreso actual:** {count}/294 PNG reales. L11 Génova completado como prototipo. L06 12/24, alfa pendiente. Aún no validados en Blender.'
plan.write_text('\n'.join(lines)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí — control de producción\n\nFecha de corte: 2026-11-07.\n\n## Estado\n- 98 familias, 294 variantes, **{count} PNG reales generados**; faltan {294-count}.\n- L01-L05, L07-L11 completos como prototipos. L06 a la mitad: 12 PNG de madera/corteza; 12 PNG con alfa pendientes.\n- L11 Génova: 12 PNG, incluyendo fachadas pintadas y persianas verdes.\n- SHA-256, tamaño y bordes comprobados; pendiente Blender y aprobación artística/histórica.\n\n## Siguiente\nL06: 12 transparentes a crear fotorealistas sin repetición. L12 Roma: 15 PNG y L13 Palermo: 15 PNG. Continuar con el primer estado pendiente del manifiesto.\n\n## Continuación\nAdjuntar `paquete_continuidad_L01_L11.zip` y pedir continuar desde REANUDAR_AQUI.md y CSV.\n''','utf-8')
lot=BASE/'lote_11_genova.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L11' in p.name or 'genova' in p.name):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L11.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
