from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control';OUT=ROOT/'ciudad/venecia';OUT.mkdir(parents=True,exist_ok=True)

def pnoise(n,seed,sy,sx=None):
 sx=sy if sx is None else sx
 raw=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sy*sy*fy*fy+sx*sx*fx*fx))
 a=np.fft.irfft2(np.fft.rfft2(raw)*filt,s=(n,n)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-6)

def seam(ar):
 n=ar.shape[0];b=max(14,int(n*.035));a=ar.astype('float32').copy()
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,n-1-j].copy())/2
  a[:,j]=a[:,j]*(1-t)+m*t;a[:,n-1-j]=a[:,n-1-j]*(1-t)+m*t
 for j in range(b):
  t=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[n-1-j].copy())/2
  a[j]=a[j]*(1-t)+m*t;a[n-1-j]=a[n-1-j]*(1-t)+m*t
 return np.uint8(np.clip(np.rint(a),0,255))

def plaster(v):
 n=512;i='abc'.index(v);im=np.asarray(Image.open(ROOT/f'comunes/muros/enlucido_desconchado_{v}.png'),dtype='float32')
 # Reference two-layer plaster; Venetian reddish marmorino and warm orange brick below.
 old_chip=(im[:,:,0]-im[:,:,1]>37).astype('float32')
 chip=old_chip[:,:,None]
 plaster_color=np.array([(159,95,78),(148,82,70),(128,76,67)][i],dtype='float32')
 underlying=np.array([(178,94,61),(167,83,55),(152,72,50)][i],dtype='float32')
 fine=pnoise(n,3900+i,2)*4+pnoise(n,3911+i,28)*5
 a=plaster_color[None,None,:]+fine[:,:,None]
 brick=underlying[None,None,:]+(im-np.array([169,96,76])[None,None,:])*.28
 a=a*(1-chip)+brick*chip
 a-=np.maximum(0,pnoise(n,3931+i,33))[:,:,None]*i*4
 return seam(a)

def roof(v):
 i='abc'.index(v);n=1024
 files=['a_top_down_close_up_full_frame_seamless_texture_l.png','a_close_up_top_down_orthographic_view_of_an_old_t.png','a_photorealistic_top_down_perfectly_frontal_tig.png']
 a=np.asarray(Image.open(BASE/files[i]).convert('RGB').resize((n,n),Image.Resampling.LANCZOS),dtype='float32')
 # More sun-washed, pale orange Venetian cotto, preserve natural tiles and pits.
 a=a*.72+np.array([(224,165,116),(205,149,113),(180,131,101)][i])[None,None,:]*.28
 return seam(a)

def masegni(v):
 i='abc'.index(v);n=512
 src=np.asarray(Image.open(ROOT/f'comunes/suelos/losas_piedra_{v}.png').convert('RGB'),dtype='float32')
 y,x=np.mgrid[:n,:n]
 theta=np.deg2rad(30)
 xsrc=np.mod((x-n/2)*np.cos(theta)+(y-n/2)*np.sin(theta)+n/2,n)
 ysrc=np.mod(-(x-n/2)*np.sin(theta)+(y-n/2)*np.cos(theta)+n/2,n)
 a=np.stack([map_coordinates(src[:,:,c],(ysrc,xsrc),order=1,mode='wrap') for c in range(3)],2)
 target=np.array([(88,91,93),(79,83,87),(72,76,81)][i],dtype='float32')
 a=a*.5+target[None,None,:]*.5
 return seam(a)

def marble(v):
 i='abc'.index(v);n=1024
 red=np.asarray(Image.open(ROOT/f'comunes/marmoles/marmol_rojo_verona_{v}.png').resize((n,n),Image.Resampling.LANCZOS),dtype='float32')
 pale=np.asarray(Image.open(ROOT/f'comunes/piedra_noble/piedra_istria_{v}.png').resize((n,n),Image.Resampling.LANCZOS),dtype='float32')
 y,x=np.mgrid[:n,:n]
 # Geometric marble inlay bands: limestone ivory with red squares and small green inserts.
 bx=np.mod(x,n/4);by=np.mod(y,n/4)
 border=(bx<n*.05)|(by<n*.05)|(bx>n*.20)|(by>n*.20)
 rectred=((x//(n/4)+y//(n/4))%2)==0
 use_red=rectred & (~border)
 a=np.where(use_red[:,:,None],red,pale)
 ins=((np.abs(bx-n*.125)+np.abs(by-n*.125))<n*.038) & (~border)
 green=np.array([63,76,65],dtype='float32')
 a=np.where(ins[:,:,None],green[None,None,:]+pnoise(n,4500+i,15)[:,:,None]*6,a)
 return seam(a)

def wood(v):
 i='abc'.index(v);n=512
 src=np.asarray(Image.open(ROOT/f'comunes/madera/vigas_viejas_{v}.png').convert('RGB'),dtype='float32')
 dark=np.array([(73,64,59),(64,59,55),(55,52,50)][i])
 a=src*.48+dark[None,None,:]*.52
 # dispersed salt bloom and wet algae staining; localized waterline belongs in Blender height mask
 lime=np.maximum(pnoise(n,4600+i,20)-1.2,0)
 algae=np.maximum(pnoise(n,4620+i,36)-1.0,0)
 a+=lime[:,:,None]*np.array([12,13,13])
 a+=algae[:,:,None]*np.array([-9,5,-4])
 return seam(a)

items=[('ladrillo_revoque_rojo',512,plaster),('teja_clara',1024,roof),('masegni_traquita',512,masegni),
       ('marmol_rojo_istria',1024,marble),('madera_pilotes',512,wood)]
files=[]
for name,res,fn in items:
 for v in 'abc':
  p=OUT/f'{name}_venecia_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# Preview
sz=210;left=15;head=50;rh=245;gap=9
sheet=Image.new('RGB',(2*left+5*sz+4*gap,head+rh*3+10),(240,238,234));d=ImageDraw.Draw(sheet)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
d.text((left,10),'L09 · Venecia · materiales en tres estados',font=f,fill=(37,38,38))
for col,(name,_,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_venecia_{v}.png';im=Image.open(p).resize((sz,sz),Image.Resampling.LANCZOS)
  x=left+col*(sz+gap);y=head+row*rh
  sheet.paste(im,(x,y));d.text((x,y+sz+4),f'{name[:21]} · {v}',font=f,fill=(43,42,41))
sheet.save(CTL/'preview_L09_venecia_15_texturas.jpg',quality=91)
for p in files:
 im=Image.open(p).resize((256,256),Image.Resampling.LANCZOS)
 proof=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):proof.paste(im,(x*256,y*256))
 proof.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=87)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);fields=rdr.fieldnames
assert sum(r['lote']=='L09' for r in rows)==15
qa={'lote':'L09','archivos':[]}
for r in rows:
 if r['lote']!='L09':continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);res=tuple(int(x) for x in r['resolucion'].split('x'));assert im.size==res
 a=np.asarray(im,dtype=np.int16);mx=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert mx<=1
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo local adaptado con base común, escala/bordes verificados; pendiente revisión histórica Blender.'
 qa['archivos'].append({'archivo':p.name,'resolucion':im.size,'sha256':sha,'max_diferencia_borde':mx})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for i in cat['materiales']:
 if i['clave_id'] not in {z[0] for z in items}:continue
 if str(i.get('ciudad','')).lower()!='venecia':continue
 for v in 'abc':
  p=next(p for p in files if p.name==f"{i['clave_id']}_venecia_{v}.png")
  i['variantes'][v]['estado']='generada';i['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  i['variantes'][v]['observaciones']='Prototipo adaptado local; revisar detalle y render Blender.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote09.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';lines=plan.read_text('utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[i]=f'**Progreso actual:** {count}/294 PNG reales; L09 Venecia completo como prototipo. L06 12/24 pendiente de transparencias. Sin validación final Blender.'
plan.write_text('\n'.join(lines)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado\n- 98 familias / 294 variantes. {count} PNG existentes; quedan {294-count}.\n- L01-L05, L07-L09 completados como prototipos. L06 parcial 12/24 (4 materiales transparentes pendientes).\n- L09: Venecia 15/15 PNG. Las maderas de pilotes incorporan manchas dispersas; una línea de agua localizada debe implementarse con máscara en Blender, no como textura repetible.\n- Todos los PNG generados tienen pruebas 3×3, tamaños y SHA-256. La aprobación visual de los materiales sigue pendiente.\n\n## Siguiente paso\nCompletar transparentes L06 (ramilletes y corte de tronco, PNG alfa 512 no repetibles) cuando puedan producirse de forma fotorealista. Después L10 Milán (12 PNG), primera fila `pendiente` en el CSV.\n\n## Continuación\nAdjunta `paquete_continuidad_L01_L09.zip` y solicita continuar desde REANUDAR_AQUI.md y progreso_produccion.csv.\n''','utf-8')
lot=BASE/'lote_09_venecia.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L09' in p.name or 'venecia' in p.name):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L09.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
