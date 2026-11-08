from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control';OUT=ROOT/'detalles/oficios_y_produccion';OUT.mkdir(parents=True,exist_ok=True)

def noise(n,seed,sy,sx=None):
 sx=sy if sx is None else sx
 r=np.random.default_rng(seed).normal(size=(n,n)).astype(np.float32)
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sy**2*fy**2+sx**2*fx**2))
 a=np.fft.irfft2(np.fft.rfft2(r)*filt,s=(n,n)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-5)

def seam(img,rep='ambos'):
 h,w=img.shape[:2];a=img.astype('float32').copy();b=max(10,round(min(h,w)*.032))
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,w-1-j].copy())/2
  a[:,j]=a[:,j]*(1-t)+m*t;a[:,w-1-j]=a[:,w-1-j]*(1-t)+m*t
 if rep=='ambos':
  for j in range(b):
   t=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[h-1-j].copy())/2
   a[j]=a[j]*(1-t)+m*t;a[h-1-j]=a[h-1-j]*(1-t)+m*t
 return np.uint8(np.clip(np.rint(a),0,255))

def base(n,color,seed,factor=6):
 fine=noise(n,seed,2)*factor+noise(n,seed+1,12)*factor*.55+noise(n,seed+2,37)*factor*.4
 return np.array(color)[None,None,:]+fine[:,:,None]

def sacks(v):
 i='abc'.index(v);n=256
 y,x=np.mgrid[:n,:n]
 threads=(np.sin(x*np.pi/2.4)+np.sin(y*np.pi/2.5))*.65
 a=base(n,[(167,145,112),(153,135,108),(140,124,102)][i],18000+i*12,5)+threads[:,:,None]*2
 a-=np.maximum(0,noise(n,18002+i,21))[:,:,None]*(2+i*3)
 return seam(a)

def woodpile(v):
 i='abc'.index(v);n=512;seed=18100+i*23;rng=np.random.default_rng(seed)
 a=base(n,[(71,61,51),(69,59,50),(65,55,49)][i],seed,7)
 im=Image.fromarray(np.uint8(np.clip(a,0,255)));d=ImageDraw.Draw(im)
 for row in range(-1,10):
  for col in range(-1,11):
   x=int(col*53+(row%2)*22+rng.integers(-9,9));y=int(row*54+rng.integers(-7,7));rad=int(rng.integers(21,30))
   c=[(168,133,91),(181,150,103),(148,120,88),(156,129,93)][int(rng.integers(0,4))]
   for ox in (-512,0,512):
    for oy in (-512,0,512):
     qx=x+ox;qy=y+oy
     d.ellipse((qx-rad-3,qy-rad-3,qx+rad+3,qy+rad+3),fill=(76,65,54))
     d.ellipse((qx-rad,qy-rad,qx+rad,qy+rad),fill=c)
     for k in (4,9,15):
      rr=rad-k
      if rr>1:d.ellipse((qx-rr,qy-rr,qx+rr,qy+rr),outline=(145,116,86),width=1)
 return seam(np.asarray(im,dtype='float32'))

def loose_hay(v):
 i='abc'.index(v);n=512;seed=18200+i*22;rng=np.random.default_rng(seed)
 a=base(n,[(156,137,91),(146,132,94),(131,121,98)][i],seed,13)
 im=Image.fromarray(np.uint8(np.clip(a,0,255)));d=ImageDraw.Draw(im)
 cols=[(188,170,112),(173,153,95),(123,119,85),(159,148,100),(184,159,113)]
 for k in range(6600):
  x=int(rng.integers(0,n));y=int(rng.integers(0,n));dx=int(rng.integers(-9,10));dy=int(rng.integers(-8,9))
  d.line((x,y,x+dx,y+dy),fill=cols[int(rng.integers(0,5))],width=1)
 return seam(np.asarray(im,dtype='float32'))

def ore(v):
 i='abc'.index(v);n=512;seed=18300+i*12;rng=np.random.default_rng(seed)
 a=base(n,[(104,69,56),(91,63,55),(83,59,54)][i],seed,11)
 im=Image.fromarray(np.uint8(np.clip(a,0,255)));d=ImageDraw.Draw(im)
 cols=[(129,69,51),(82,64,56),(113,74,56),(69,64,65),(137,82,60)]
 for row in range(-1,20):
  for col in range(-1,22):
   x=int(col*27+(row%2)*12+rng.integers(-6,6));y=int(row*27+rng.integers(-5,5))
   r=int(rng.integers(8,17));c=cols[int(rng.integers(0,5))]
   d.polygon([(x-r,y+r//2),(x-r//2,y-r),(x+r,y-r//2),(x+r//2,y+r)],fill=c)
 return seam(np.asarray(im,dtype='float32'))

def slag(v):
 i='abc'.index(v);n=512;seed=18400+i*17
 src=np.asarray(Image.open(ROOT/f'comunes/campos_jardines_e_industria/vertedero_{v}.png'),dtype='float32')
 dark=np.array([(42,42,40),(39,39,38),(35,35,35)][i])
 a=src*.30+dark[None,None,:]*.70+noise(n,seed,7)[:,:,None]*6
 ash=np.maximum(noise(n,seed+2,21)-1.4,0)
 a+=ash[:,:,None]*np.array([38,37,35])
 return seam(a)

def quarry(v):
 i='abc'.index(v);n=512;seed=18500+i*27
 src=np.asarray(Image.open(ROOT/f'comunes/marmoles/marmol_carrara_{v}.png'),dtype='float32')
 yy,xx=np.mgrid[:n,:n]
 tool=(np.mod(yy+xx*.11,19)<1.8)
 a=src*.9+np.array([229,226,212])[None,None,:]*.1
 a=np.where(tool[:,:,None],a-12,a)
 dust=np.maximum(noise(n,seed,34)-.5,0)
 a+=dust[:,:,None]*np.array([6,5,4])
 return seam(a)

def barrels(v):
 i='abc'.index(v);n=512
 wood=np.asarray(Image.open(ROOT/f'comunes/madera/tablas_puertas_{v}.png'),dtype='float32')
 a=wood*.76+np.array([(114,81,54),(105,73,52),(95,69,51)][i])[None,None,:]*.24
 im=Image.fromarray(np.uint8(np.clip(a,0,255)));d=ImageDraw.Draw(im)
 for y in (110,307,472):
  d.rectangle((0,y-13,511,y+13),fill=(43,44,42))
  d.line((0,y-9,511,y-9),fill=(94,93,87),width=3)
 return np.asarray(im)

def pottery(v):
 i='abc'.index(v);n=512
 src=np.asarray(Image.open(ROOT/f'comunes/tejados/teja_arabe_roja_{v}.png').convert('RGB'),dtype='float32')
 # Fired ceramic roof pieces packed in a craft yard; full geometry remains separate in Blender.
 tint=np.array([(176,110,72),(160,99,71),(149,91,69)][i])
 return np.uint8(np.clip(src*.76+tint[None,None,:]*.24,0,255))

def net(v):
 i='abc'.index(v);n=512;seed=18700+i*19
 im=Image.new('RGBA',(n,n),(0,0,0,0));d=ImageDraw.Draw(im)
 # Hemp diamond mesh ~5cm at 1m: 20 meshes across; natural rope opacity.
 step=25.6
 for j in range(-22,43):
  off=int(j*step)
  d.line((off-512,0,off+512,1024),fill=(124,102,73,230),width=3)
  d.line((off-512,1024,off+512,0),fill=(128,107,78,220),width=3)
 # avoid thick artificial black cords, add grayscale warm fibers
 arr=np.asarray(im,dtype='float32').copy();rough=noise(n,seed,1.2)
 arr[:,:,:3]+=rough[:,:,None]*4
 arr[:,:,3]=np.where(arr[:,:,3]>0,arr[:,:,3],0)
 return seam(arr)

def silk(v):
 i='abc'.index(v);n=512;seed=18800+i*24
 y,x=np.mgrid[:n,:n]
 band=(x//(n/3)).astype(int)%3
 pal=np.array([(142,44,62),(58,78,121),(160,126,59)],dtype='float32')
 a=pal[band]+noise(n,seed,32)[:,:,None]*np.array([9,8,7])
 folds=np.sin(y*.05+x*.011+noise(n,seed+1,40)*.3)
 a+=folds[:,:,None]*np.array([9,9,9])
 return a

def leather(v):
 i='abc'.index(v);n=256;seed=18900+i*23
 a=base(n,[(126,77,52),(112,70,51),(97,63,50)][i],seed,9)
 cracks=np.maximum(0,noise(n,seed+4,14)-1.6)
 a-=cracks[:,:,None]*np.array([14,13,13])
 return seam(a)
items=[('sacos_arpillera',256,'ambos',False,sacks),('lena_apilada',512,'ambos',False,woodpile),
       ('heno_paja',512,'ambos',False,loose_hay),('mineral_hierro',512,'ambos',False,ore),
       ('escoria_carbon',512,'ambos',False,slag),('cantera_marmol',512,'ambos',False,quarry),
       ('duelas_tonel',512,'no',False,barrels),('ceramica_apilada',512,'no',False,pottery),
       ('redes_pesca',512,'ambos',True,net),('telas_seda',512,'no',False,silk),('cuero_curtido',256,'ambos',False,leather)]
files=[]
for name,res,repeat,alpha,fn in items:
 for v in 'abc':
  p=OUT/f'{name}_{v}.png';Image.fromarray(np.uint8(np.clip(fn(v),0,255))).save(p,optimize=True);files.append(p)
# preview
thumb=109;left=8;head=48;gap=4;rh=142
sheet=Image.new('RGB',(2*left+11*thumb+10*gap,head+3*rh+15),(239,236,231));d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
d.text((left,10),'L15 · Oficios y producción · 33 PNG (a/b/c)',font=font,fill=(37,38,38))
for c,(name,_,_,_,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_{v}.png';im=Image.open(p)
  if im.mode=='RGBA':
   bg=Image.new('RGBA',im.size,(186,185,182,255));im=Image.alpha_composite(bg,im).convert('RGB')
  im=im.resize((thumb,thumb),Image.Resampling.LANCZOS)
  x=left+c*(thumb+gap);y=head+row*rh
  sheet.paste(im,(x,y));d.text((x,y+thumb+4),name[:13]+f' · {v}',font=font,fill=(42,43,40))
sheet.save(CTL/'preview_L15_33_texturas.jpg',quality=88)
for p in files:
 im=Image.open(p)
 if im.mode=='RGBA':
  bg=Image.new('RGBA',im.size,(187,187,184,255));im=Image.alpha_composite(bg,im).convert('RGB')
 else:im=im.convert('RGB')
 im=im.resize((256,256));proof=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):proof.paste(im,(x*256,y*256))
 proof.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=85)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.DictReader(f);rows=list(rd);fields=rd.fieldnames
assert sum(r['lote']=='L15' for r in rows)==33
qa={'lote':'L15','archivos':[]}
for r in rows:
 if r['lote']!='L15':continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==tuple(map(int,r['resolucion'].split('x')))
 a=np.asarray(im,dtype=np.int16)
 if r['repeticion']=='ambos':
  mx=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert mx<=1,(p,mx)
 else:mx=-1
 if r['alfa']=='True' and im.mode!='RGBA':raise ValueError(('No alpha',p))
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo procedural; objetos volumétricos necesitarán geometría Blender. Verificar material realista.'
 qa['archivos'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'mode':im.mode,'max_diff_borde':mx})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for it in cat['materiales']:
 if it['clave_id'] not in {z[0] for z in items}:continue
 for v in 'abc':
  p=next(x for x in files if x.name==f"{it['clave_id']}_{v}.png")
  it['variantes'][v]['estado']='generada';it['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  it['variantes'][v]['observaciones']='Prototipo de detalle, requiere revisión sobre objeto Blender.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote15.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';ls=plan.read_text('utf-8').splitlines()
for j,line in enumerate(ls):
 if line.startswith('**Progreso actual:**'):
  ls[j]=f'**Progreso actual:** {count}/294 PNG. L15 oficios creado como prototipo; L06 ramilletes transparentes pendientes. L16 obra/murallas siguiente.'
plan.write_text('\n'.join(ls)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md';resume.write_text(f'''# Reanudar aquí\n\nCorte: 2026-11-07.\n\n- 98 familias, 294 PNG previstos. **{count} generados**, {294-count} pendientes.\n- L01-L05, L07-L15 generados como prototipos. L06 parcial 12/24.\n- L15 33 PNG completos, incluyendo red pesca RGBA. Revisar la calidad fotográfica en juego y el volumen de objetos.\n- Cada PNG generado cuenta con SHA y pruebas de dimensiones/bordes cuando corresponden. No está aprobado en Blender.\n\n## Seguir\n- L16 obras y murallas 18 PNG.\n- L06: 12 PNG RGBA de follaje/corte tronco pendientes, sin repetición y con estética naturalista.\n- Adjuntar paquete de continuidad más reciente y consultar el CSV.\n''','utf-8')
lot=BASE/'lote_15_oficios_produccion.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L15' in p.name or any(it[0] in p.name for it in items)):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L15.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
