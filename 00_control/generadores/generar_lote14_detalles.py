from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control'

def noise(n,seed,sy,sx=None):
 sx=sy if sx is None else sx
 r=np.random.default_rng(seed).normal(size=(n,n)).astype(np.float32)
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sy**2*fy**2+sx**2*fx**2))
 a=np.fft.irfft2(np.fft.rfft2(r)*filt,s=(n,n)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-5)

def equal_edges(a,kind='ambos',band=12):
 h,w=a.shape[:2];a=a.astype(np.float32).copy()
 for j in range(min(band,w//3)):
  b=.5+.5*np.cos(np.pi*j/band);m=(a[:,j].copy()+a[:,w-1-j].copy())/2
  a[:,j]=a[:,j]*(1-b)+m*b;a[:,w-1-j]=a[:,w-1-j]*(1-b)+m*b
 if kind=='ambos':
  for j in range(min(band,h//3)):
   b=.5+.5*np.cos(np.pi*j/band);m=(a[j].copy()+a[h-1-j].copy())/2
   a[j]=a[j]*(1-b)+m*b;a[h-1-j]=a[h-1-j]*(1-b)+m*b
 return np.uint8(np.clip(np.rint(a),0,255))

def plank_background(v,green=False,humble=False):
 n=512;i='abc'.index(v)
 src=np.asarray(Image.open(ROOT/f'comunes/madera/tablas_puertas_{v}.png').convert('RGB'),dtype=np.float32)
 if green:
  src=src*.27+np.array([(49,86,64),(44,77,58),(43,68,54)][i])[None,None,:]*.73
 elif humble:
  src=src*.37+np.array([(155,149,131),(142,138,124),(126,125,113)][i])[None,None,:]*.63
 else:src=src*.62+np.array([(76,59,46),(69,54,45),(60,51,45)][i])[None,None,:]*.38
 return Image.fromarray(np.uint8(np.clip(src,0,255)))

def door(v,kind):
 i='abc'.index(v);n=512
 if kind=='porton':im=plank_background(v)
 elif kind=='humble':im=plank_background(v,humble=True)
 elif kind=='shutter_green':im=plank_background(v,green=True)
 else:im=plank_background(v)
 d=ImageDraw.Draw(im,'RGBA')
 if kind=='porton':
  # Historical hand-forged round nail heads at regular board intersections, oxide patina.
  for x in range(23,n,70):
   for y in range(25,n,66):
    r=5
    d.ellipse((x-r-1,y-r-1,x+r+1,y+r+1),fill=(26,27,27,230))
    d.ellipse((x-r+1,y-r+1,x+r-2,y+r-2),fill=(66,58,52,210))
  d.line((n//2,0,n//2,n),fill=(31,28,28,135),width=8)
 else:
  # Two hardwood battens and wrought-iron hinge straps, with Z brace on shutters.
  if kind in ('shutter_green','shutter_brown'):
   c=(33,61,46,170) if kind=='shutter_green' else (59,45,38,155)
   d.line((38,75,474,75),fill=c,width=26)
   d.line((38,432,474,432),fill=c,width=26)
   d.line((90,407,420,109),fill=c,width=20)
  else:
   d.line((30,113,482,113),fill=(91,82,70,170),width=20)
   d.line((30,391,482,391),fill=(90,80,69,170),width=20)
  for y in (114,394):
   d.rounded_rectangle((0,y-10,96,y+10),radius=4,fill=(33,34,31,215))
   d.ellipse((78,y-4,87,y+5),fill=(90,87,78,200))
 if kind in ('porton','humble'):
  d.ellipse((425,250,457,282),outline=(25,27,24,230),width=7)
 return np.asarray(im)

def grille(v):
 i='abc'.index(v);n=512;seed=17000+i*23
 a=np.zeros((n,n,4),dtype=np.float32)
 rough=noise(n,seed,3);warm=noise(n,seed+2,20)
 # Bars are RGBA; transparent space must remain genuinely alpha=0.
 y,x=np.mgrid[:n,:n]
 bx=(np.mod(x+32,64)<10);by=(np.mod(y+32,64)<10)
 mask=bx|by
 rust=np.maximum(0,rough-1.5)
 a[:,:,0]=35+rough*4+rust*(10+i*8)
 a[:,:,1]=38+rough*4+rust*(3+i*3)
 a[:,:,2]=37+rough*3
 a[:,:,3]=np.where(mask,255,0)
 # Metallic surfaces dark gray, not a black silhouette painted on a solid square.
 a[~mask,:3]=0
 return np.uint8(np.clip(a,0,255))

def iron(v):
 i='abc'.index(v);n=256;seed=17100+i*32
 fine=noise(n,seed,2)*8+noise(n,seed+1,18)*7
 a=np.array([(54,56,52),(50,48,45),(44,42,40)][i])[None,None,:]+fine[:,:,None]
 rust=np.maximum(0,noise(n,seed+5,8)+noise(n,seed+6,21)*.4-1.0)
 a+=rust[:,:,None]*np.array([31+i*9,14+i*4,3])
 return equal_edges(a,'ambos',12)

def moss(v):
 i='abc'.index(v);n=256;seed=17200+i*22
 patch=noise(n,seed,7)*.85+noise(n,seed+1,19)*.34+noise(n,seed+2,2)*.17
 cov=[1.6,1.28,.92][i]
 a=np.zeros((n,n,4),dtype=np.float32)
 a[:,:,3]=np.clip((patch-cov)*110,0,255)
 n2=noise(n,seed+4,3)
 a[:,:,0]=95+n2*18;a[:,:,1]=115+n2*13;a[:,:,2]=76+n2*14
 pale=noise(n,seed+10,14)>1.0
 a[pale,0]+=28;a[pale,1]+=25;a[pale,2]+=19
 return equal_edges(a,'ambos',14)

def rain(v):
 i='abc'.index(v);n=256;seed=17300+i*33
 y,x=np.mgrid[:n,:n]
 streak=noise(n,seed,50,2)
 amplitude=np.clip(streak,0,2)
 fade=np.clip(1-y/n,0,1)**1.3
 gray=255-amplitude*(20+i*13)*fade
 a=np.repeat(gray[:,:,None],3,axis=2)
 return equal_edges(a,'horizontal',12)

def humidity(v):
 i='abc'.index(v);h=256;w=512;seed=17400+i*23
 # 60cm rise into 1m of wall: dark bottom increasing upward irregularly.
 yy,xx=np.mgrid[:h,:w]
 r=noise(w,seed,30)[0,:]
 elevation=(.57+.055*r)*h
 d=np.clip((yy-(h-elevation))/(elevation+.0001),0,1)
 base=(254-(24+i*19)*(d**1.5)).astype(np.float32)
 a=np.repeat(base[:,:,None],3,axis=2)
 return equal_edges(a,'horizontal',16)
items=[
 ('porton_claveteado','detalles/puertas_ventanas_y_herrajes','no',False,lambda v:door(v,'porton')),
 ('puerta_humilde','detalles/puertas_ventanas_y_herrajes','no',False,lambda v:door(v,'humble')),
 ('contraventanas_tablas','detalles/puertas_ventanas_y_herrajes','no',False,lambda v:door(v,'shutter_brown')),
 ('contraventanas_verdes','detalles/puertas_ventanas_y_herrajes','no',False,lambda v:door(v,'shutter_green')),
 ('reja_hierro','detalles/puertas_ventanas_y_herrajes','no',True,grille),
 ('hierro_oxidado','detalles/puertas_ventanas_y_herrajes','ambos',False,iron),
 ('musgo_liquen_teja','detalles/envejecimiento_(capas_para_mezclar)','ambos',True,moss),
 ('suciedad_lluvia','detalles/envejecimiento_(capas_para_mezclar)','horizontal',False,rain),
 ('humedad_base','detalles/envejecimiento_(capas_para_mezclar)','horizontal',False,humidity)
]
files=[]
for name,folder,repeat,alpha,fn in items:
 dest=ROOT/folder;dest.mkdir(parents=True,exist_ok=True)
 for v in 'abc':
  p=dest/f'{name}_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# Preview with checkerboard under transparency.
size=136;head=48;rh=168;gap=5;left=8
sheet=Image.new('RGB',(2*left+9*size+8*gap,head+3*rh+12),(240,237,233));d=ImageDraw.Draw(sheet)
fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
d.text((left,10),'L14 · Puertas, herrajes y envejecimiento (27 variantes)',font=fnt,fill=(40,38,37))
for c,(name,folder,_,alpha,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=ROOT/folder/f'{name}_{v}.png';im=Image.open(p)
  if im.mode=='RGBA':
   bg=Image.new('RGBA',im.size,(203,203,203,255))
   im=Image.alpha_composite(bg,im).convert('RGB')
  im=im.resize((size,size),Image.Resampling.LANCZOS)
  x=left+c*(size+gap);y=head+row*rh
  sheet.paste(im,(x,y));d.text((x,y+size+3),f'{name[:15]} · {v}',font=fnt,fill=(45,44,43))
sheet.save(CTL/'preview_L14_27_texturas.jpg',quality=89)
for p in files:
 im=Image.open(p)
 if im.mode=='RGBA':
  bg=Image.new('RGBA',im.size,(188,187,184,255));im=Image.alpha_composite(bg,im).convert('RGB')
 else:im=im.convert('RGB')
 im=im.resize((256,256),Image.Resampling.LANCZOS);proof=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):proof.paste(im,(x*256,y*256))
 proof.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=84)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);fields=rdr.fieldnames
assert sum(r['lote']=='L14' for r in rows)==27
qa={'lote':'L14','archivos':[]}
for r in rows:
 if r['lote']!='L14':continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);res=tuple(int(x) for x in r['resolucion'].split('x'));assert im.size==res,(p,im.size,res)
 a=np.asarray(im,dtype=np.int16)
 if r['repeticion']=='ambos':
  mx=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert mx<=1,(p,mx)
 elif r['repeticion']=='horizontal':
  mx=int(abs(a[:,0]-a[:,-1]).max());assert mx<=1,(p,mx)
 else:mx=-1
 if r['alfa']=='True' and im.mode!='RGBA':raise ValueError(('Need RGBA',p))
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo detalle, con canal alfa donde procede. Verificar presencia de objetos y calidad en Blender.'
 qa['archivos'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'mode':im.mode,'diferencia_borde':mx})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if item['clave_id'] not in {z[0] for z in items}:continue
 for v in 'abc':
  p=next(p for p in files if p.name==f"{item['clave_id']}_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Prototipo detalle; revisar desgaste y legibilidad en render pequeño.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote14.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';ls=plan.read_text('utf-8').splitlines()
for j,line in enumerate(ls):
 if line.startswith('**Progreso actual:**'):
  ls[j]=f'**Progreso actual:** {count}/294 PNG generados como prototipos. L14 completo, L06 12/24 (follaje alfa pendiente). Faltan L15-L16.'
plan.write_text('\n'.join(ls)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md';resume.write_text(f'''# Reanudar aquí — texturas del Renacimiento italiano\n\nCorte: 2026-11-07.\n\n## Estado comprobado\n- 98 materiales, 294 variantes; **{count}/294 PNG producidos**, faltan {294-count}.\n- L01-L05, L07-L14 completos como prototipos; L06 parcial 12/24.\n- L14 puertas, hierro y envejecimiento: 27 PNG, con alfa en reja y musgo, y repetición solo horizontal en lluvia y humedad.\n- Los PNG generados tienen checksum, dimensiones y bordes comprobados. Falta validación de realismo y Blender.\n\n## Continuación\n- L06 ramilletes y corte de tronco: 12 PNG RGBA naturalistas pendientes.\n- L15 oficios (33 PNG), L16 obras/murallas (18 PNG).\n- En chat nuevo adjuntar `paquete_continuidad_L01_L14.zip` y leer este documento y CSV.\n''',encoding='utf-8')
lot=BASE/'lote_14_detalles_puertas_envejecimiento.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L14' in p.name or any(it[0] in p.name for it in items)):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L14.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
