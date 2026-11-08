from pathlib import Path
import hashlib,json,csv,zipfile
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image,ImageDraw,ImageFont

BASE=Path('/mnt/data');WORK=BASE/'texturas_renacimiento_italiano';CTL=WORK/'00_control';OUT=WORK/'comunes'/'piedra_noble'
OUT.mkdir(parents=True,exist_ok=True)

def arr_noise(n,seed,sigma=12):
 # FFT-based periodic Gaussian noise: O(N²logN) even for wide veins, avoids
 # giant spatial kernels (previous scipy Gaussian on 1024px could timeout).
 z=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None]
 fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*sigma*sigma*(fx*fx+fy*fy))
 a=np.fft.irfft2(np.fft.rfft2(z)*filt,s=(n,n)).real.astype('float32')
 std=max(float(a.std()),1e-6)
 return (a-a.mean())/std

def tone_texture(n,seed):
 return 1.8*arr_noise(n,seed,n/170)+.68*arr_noise(n,seed+101,n/41)+.38*arr_noise(n,seed+211,n/14)+.3*arr_noise(n,seed+311,n/4)

def seam(a,border=None):
 n=a.shape[0]; b=border or max(12,int(n*.033))
 a=a.astype('float32').copy()
 for i in range(b):
  w=.5+.5*np.cos(np.pi*i/b)
  m=(a[:,i,:]+a[:,n-1-i,:])/2
  a[:,i,:]=a[:,i,:]*(1-w)+m*w
  a[:,n-1-i,:]=a[:,n-1-i,:]*(1-w)+m*w
 for i in range(b):
  w=.5+.5*np.cos(np.pi*i/b)
  m=(a[i,:,:]+a[n-1-i,:,:])/2
  a[i,:,:]=a[i,:,:]*(1-w)+m*w
  a[n-1-i,:,:]=a[n-1-i,:,:]*(1-w)+m*w
 return np.uint8(np.clip(np.rint(a),0,255))

def make_stones(name,v,size):
 idx='abc'.index(v)
 n=size
 y,x=np.mgrid[0:n,0:n]
 seed=820+idx*73+sum(map(ord,name))
 st=tone_texture(n,seed)
 # Hand cut courses; physically related approximate block counts for 3m x 3m textures.
 config={
 'piedra_serena_sillares':(5,8,(125,136,140),(115,125,130),(107,116,122),2.0),
 'almohadillado_rustico':(3,6,(139,130,117),(130,122,109),(117,109,100),7.5),
 'travertino':(4,6,(196,177,147),(185,167,140),(169,152,128),3.0),
 'toba_dorada':(5,8,(178,145,91),(168,130,82),(147,117,77),3.3),
 'piedra_istria':(5,8,(214,210,194),(205,199,184),(191,187,176),2.3)
 }
 cc,rr,ca,cb,ccol,gap=config[name]
 base=np.array([ca,cb,ccol][idx],dtype='float32')
 tw=n/cc;th=n/rr
 row=(y//th).astype('int32')
 xoff=(row%2)*(tw/2)
 xx=np.mod(x+xoff,tw)
 yy=np.mod(y,th)
 col=(np.floor((x+xoff)/tw).astype('int32'))%cc
 rng=np.random.default_rng(343+sum(map(ord,name)))
 material_var=rng.normal(size=(rr,cc)).astype('float32')
 bv=material_var[row%rr,col]
 d=np.minimum(np.minimum(xx,tw-xx),np.minimum(yy,th-yy))
 # IRREGULAR HAND TOOLING: faint edges, no perfect vector outlines
 rough=arr_noise(n,seed+500,n/180)*.38+arr_noise(n,seed+510,n/65)*.38
 mortar=np.clip((gap+rough-d)*.75,0,1)
 colors=base[None,None,:]+bv[:,:,None]*np.array([6,5.8,5.6])[None,None,:]+st[:,:,None]*np.array([4.3,4.2,4.1])[None,None,:]
 if name=='travertino':
  # Local horizontal vein/pore pattern characteristic of real porous limestone.
  pores=arr_noise(n,seed+77,n/440)>2.0
  pn=gaussian_filter(pores.astype('float32'),sigma=(.38,1.1),mode='wrap')
  colors-=pn[:,:,None]*np.array([18,16,12])[None,None,:]
  colors+=arr_noise(n,seed+87,n/11)[:,:,None]*np.array([1.8,1.6,1.2])
 if name=='toba_dorada':
  pores=arr_noise(n,seed+77,n/310)>1.45
  colors-=pores[:,:,None]*np.array([6,7,6])[None,None,:]
 if name=='piedra_istria':
  # very slight mineral deposits, not artificial shading of whole wall
  colors+=arr_noise(n,seed+37,n/15)[:,:,None]*np.array([2,2,2])
 if name=='almohadillado_rustico':
  # Discrete raised rustic center and hand-chiseled rough face; physical joints
  bump=np.clip(d/(min(tw,th)*.25),0,1)
  colors+=(bump-0.4)[:,:,None]*np.array([9,8,7])[None,None,:]
  colors+=st[:,:,None]*np.array([2.8,2.7,2.6])
 mortarcolor=base-np.array([13,13,13])+arr_noise(n,seed+22,n/160)[:,:,None]*3
 colors=colors*(1-mortar[:,:,None])+mortarcolor*mortar[:,:,None]
 if idx:
  dirt=np.maximum(0,arr_noise(n,seed+98,n/36))
  colors-=dirt[:,:,None]*(idx*3.0)
 return seam(colors)

def marble_frames(v,n):
 idx='abc'.index(v)
 y,x=np.mgrid[0:n,0:n]
 seed=7120+idx*17
 # Italian polychrome Florentine geometric panels: white Carrara, deep green Prato.
 panel_x=(x%(n/4))/(n/4);panel_y=(y%(n/2))/(n/2)
 green=(panel_x<.11)|(panel_x>.89)|(panel_y<.055)|(panel_y>.945)
 st=tone_texture(n,seed)
 white=np.stack([218+st*2,215+st*2,203+st*2],2)
 dark=np.stack([52+st*2.6,69+st*2.9,60+st*2.4],2)
 # Periodic organic mineral veining, non-graphic and low contrast
 diag=arr_noise(n,seed+59,n/65)+.33*arr_noise(n,seed+70,n/24)
 veins=(np.abs(diag)<.09).astype('float32')
 veins=gaussian_filter(veins,1.3,mode='wrap')
 white-=veins[:,:,None]*np.array([6,7,7])
 dark+=veins[:,:,None]*np.array([8,11,7])
 a=np.where(green[:,:,None],dark,white)
 if idx:
  a-=np.maximum(0,arr_noise(n,seed+81,n/40))[:,:,None]*idx*2.8
 return seam(a)

def genoa_stripes(v,n):
 idx='abc'.index(v)
 y,x=np.mgrid[0:n,0:n]
 rr=8
 row=(y//(n/rr)).astype('int32')
 black=(row%2==1)
 st=tone_texture(n,8122+idx*25)
 white=np.stack([218+st*3.2,214+st*3.2,201+st*3.0],2)
 dark=np.stack([61+st*3.5,65+st*3.5,68+st*3.6],2)
 a=np.where(black[:,:,None],dark,white)
 boundary=(y%(n/rr))<1.3
 a[boundary]-=6
 if idx:
  a-=np.maximum(0,arr_noise(n,9000+idx,n/40))[:,:,None]*idx*5
 return seam(a)

specs=[
 ('piedra_serena_sillares',512),
 ('almohadillado_rustico',1024),
 ('travertino',512),
 ('marmol_blanco_verde',1024),
 ('piedra_franjas',512),
 ('toba_dorada',512),
 ('piedra_istria',512)
]
images=[]
for name,sz in specs:
 for v in 'abc':
  if name=='marmol_blanco_verde':a=marble_frames(v,sz)
  elif name=='piedra_franjas':a=genoa_stripes(v,sz)
  else:a=make_stones(name,v,sz)
  p=OUT/f'{name}_{v}.png';Image.fromarray(a).save(p,optimize=True)
  images.append(p)
# Catalog / output preview
csize=180;pad=10;head=45;rowheight=215
contact=Image.new('RGB',(pad*2+7*csize+6*8,head+3*rowheight+10),(240,238,233))
d=ImageDraw.Draw(contact)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
d.text((pad,7),'L03 · Piedra noble · prototipos con patrón físico y variaciones de conservación',font=f,fill=(40,39,38))
for col,(name,sz) in enumerate(specs):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_{v}.png';im=Image.open(p).resize((csize,csize),Image.Resampling.LANCZOS)
  xx=pad+col*(csize+8);yy=head+row*rowheight
  contact.paste(im,(xx,yy))
  d.text((xx,yy+csize+3),f'{name[:17]} {v}',font=f,fill=(45,43,41))
contact.save(CTL/'preview_L03_21_texturas.jpg',quality=90)
for p in images:
 im=Image.open(p).convert('RGB').resize((384,384),Image.Resampling.LANCZOS)
 m=Image.new('RGB',(1152,1152))
 for y in range(3):
  for x in range(3): m.paste(im,(x*384,y*384))
 m.resize((768,768),Image.Resampling.LANCZOS).save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=86)

# Integrity and manifest update.
progress=CTL/'progreso_produccion.csv'
with progress.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);fields=rdr.fieldnames
assert sum(r['lote']=='L03' for r in rows)==21
for r in rows:
 if r['lote']!='L03':continue
 p=WORK/r['ruta'];assert p.exists(),p
 im=Image.open(p)
 expect=int(r['resolucion'].split('x')[0]);assert im.size==(expect,expect),(p,im.size)
 arr=np.asarray(im,dtype='int16');mx=max(abs(arr[:,0]-arr[:,-1]).max(),abs(arr[0]-arr[-1]).max());assert mx<=1,(p,mx)
 r['estado']='generada';r['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();r['notas']='Prototipo procedural; bordes verificados; revisión Blender y realismo pendiente.'
with progress.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';catalog=json.loads(catp.read_text('utf-8'))
for item in catalog['materiales']:
 if item['clave_id'] not in {x[0] for x in specs}:continue
 for v in 'abc':
  p=OUT/f"{item['clave_id']}_{v}.png";assert p.exists()
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Textura procedimental provisional (no fotografía). Pendiente prueba en edificio y revisión histórica.'
catp.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n','utf-8')
qa={'lote':'L03','archivos':[]}
for p in images:
 im=Image.open(p);a=np.asarray(im,dtype='int16');mx=max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max())
 qa['archivos'].append({'archivo':p.name,'resolucion':im.size,'diferencia_borde_max':int(mx),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(CTL/'verificacion_lote03.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
plan=CTL/'plan_produccion_v2.md';ls=plan.read_text('utf-8').splitlines()
for i,line in enumerate(ls):
 if line.startswith('**Progreso actual:**'):
  ls[i]='**Progreso actual:** L01 15, L02 18, L03 21 texturas generadas como prototipos; total 54/294. Todas con pruebas de mosaico y bordes, ninguna validada de forma final en Blender. L02 y L03 son procedimentales, revisar realismo con referencias fotográficas.'
plan.write_text('\n'.join(ls)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text('''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado verificado\n- Catálogo: 98 materiales, 294 PNG previstas en tres variantes a/b/c.\n- **L01** tejados comunes: 15 PNG (fuentes generadas y recortadas de atlas); provisional.\n- **L02** muros comunes: 18 PNG (procedimentales); provisional.\n- **L03** piedra noble: 21 PNG (procedimentales; 512 y 1024 px); provisional.\n- **54/294 PNG creados y checksums SHA-256 en manifiesto; 240 PNG pendientes.**\n- QA técnico: bordes opuestos igualados y mosaicos 3×3, resoluciones correctas. No se ha hecho validación en Blender ni aprobación artística/histórica.\n- Riesgo de calidad: las fuentes L02 y L03 son procedimentales y pueden parecer demasiado sintéticas. Priorizar verificación en render de juego y reemplazo por materiales fotográficos cuando se necesite.\n\n## Continuar en L04\nL04: mármoles lisos, piedra serena lisa y piedra clara labrada (6 familias, 18 PNG). Primer pendiente: `marmol_carrara_a.png` (ver manifiesto).\n\n## En otra conversación\nAdjuntar `paquete_continuidad_L01_L03.zip`; pedir «continúa desde 00_control/REANUDAR_AQUI.md, usando el manifiesto de progreso, sin rehacer lo producido salvo mejoras de calidad».\n''','utf-8')
lot=BASE/'lote_03_comunes_piedra_noble.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.iterdir()):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L03' in p.name or 'piedra' in p.name or 'travertino' in p.name or 'marmol' in p.name or 'toba' in p.name or 'almohadillado' in p.name):
   z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
full=BASE/'paquete_continuidad_L01_L03.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(WORK.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
print('L03',lot.stat().st_size,'full',full.stat().st_size,'generated',sum(r['estado']=='generada' for r in rows))
