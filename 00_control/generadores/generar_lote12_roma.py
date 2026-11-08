from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control';OUT=ROOT/'ciudad/roma';OUT.mkdir(parents=True,exist_ok=True)

def noise(n,seed,sy,sx=None):
 if sx is None:sx=sy
 r=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sy**2*fy**2+sx**2*fx**2))
 a=np.fft.irfft2(np.fft.rfft2(r)*filt,s=(n,n)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-5)

def seam(a):
 n=a.shape[0];b=max(12,int(n*.034));a=a.astype('float32').copy()
 for j in range(b):
  w=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,n-1-j].copy())/2
  a[:,j]=a[:,j]*(1-w)+m*w;a[:,n-1-j]=a[:,n-1-j]*(1-w)+m*w
 for j in range(b):
  w=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[n-1-j].copy())/2
  a[j]=a[j]*(1-w)+m*w;a[n-1-j]=a[n-1-j]*(1-w)+m*w
 return np.uint8(np.clip(np.rint(a),0,255))

def brick(v):
 i='abc'.index(v);n=512;y,x=np.mgrid[:n,:n]
 cw=n/4;rh=n/36
 row=np.floor(y/rh).astype('int32');off=(row%2)*cw/2
 xx=np.mod(x+off,cw);yy=np.mod(y,rh)
 col=np.floor((x+off)/cw).astype('int32')%4
 rng=np.random.default_rng(12345);cc=rng.normal(size=(36,4))[row%36,col]
 base=np.array([(166,94,64),(150,82,59),(133,77,60)][i])
 st=noise(n,14000+i*40,2)*4.5+noise(n,14001+i*40,20)*4.3
 a=base[None,None,:]+st[:,:,None]+cc[:,:,None]*np.array([9,8,7])
 d=np.minimum.reduce([xx,cw-xx,yy,rh-yy]);grout=np.clip((2.7+noise(n,14012+i,2)*.2-d)/2,0,1)
 mortar=np.array([(193,177,150),(182,169,150),(165,155,138)][i])
 a=a*(1-grout[:,:,None])+mortar[None,None,:]*grout[:,:,None]
 return seam(a)

def peperino(v):
 i='abc'.index(v);n=512
 src=np.asarray(Image.open(ROOT/f'comunes/piedra_noble/piedra_serena_sillares_{v}.png'),dtype='float32')
 base=np.array([(112,115,114),(99,103,104),(87,93,95)][i])
 a=src*.25+base[None,None,:]*.75
 flecks=noise(n,14100+i,1.0)>2.0
 a-=flecks[:,:,None]*np.array([16,16,17])
 a+=noise(n,14105+i,8)[:,:,None]*5
 return seam(a)

def plaster(v):
 i='abc'.index(v);n=512
 src=np.asarray(Image.open(ROOT/f'comunes/muros/enlucido_claro_{v}.png'),dtype='float32')
 target=np.array([(220,182,112),(208,170,106),(191,157,106)][i])
 a=src*.24+target[None,None,:]*.76+noise(n,14200+i,47)[:,:,None]*5
 return seam(a)

def cobbles(v):
 i='abc'.index(v);n=512;y,x=np.mgrid[:n,:n]
 # fan-like small basalt paving stones (approx 12cm across, repeated over 2m)
 tw=n/16;rh=n/16
 shift=(np.sin(y/n*4*np.pi)+np.sin(y/n*2*np.pi))*7.2
 xx=np.mod(x+shift,tw);yy=np.mod(y+np.sin(x/n*2*np.pi)*3,rh)
 d=np.minimum.reduce([xx,tw-xx,yy,rh-yy])
 joint=np.clip((2.2+noise(n,14310+i,2)*.3-d)/1.8,0,1)
 stone=np.array([(78,81,80),(69,73,74),(62,66,69)][i])
 grain=noise(n,14300+i,2)*4+noise(n,14301+i,12)*3
 a=stone[None,None,:]+grain[:,:,None]
 a=a*(1-joint[:,:,None])+np.array([119,113,99])[None,None,:]*joint[:,:,None]
 return seam(a)

def cosmatesco(v):
 i='abc'.index(v);n=1024;y,x=np.mgrid[:n,:n]
 # Cosm a tesque intarsia: interlocking stone circles and squares without saints/figures.
 unit=n/4;u=np.mod(x,unit)-unit/2;w=np.mod(y,unit)-unit/2
 rad=np.sqrt(u*u+w*w)
 diamond=(np.abs(u)+np.abs(w)<unit*.38)
 center=(rad<unit*.26)
 roundrim=(np.abs(rad-unit*.38)<unit*.035)
 tileborder=(np.abs(u)>unit*.465)|(np.abs(w)>unit*.465)
 white=np.array([(198,190,174),(186,180,165),(170,166,154)][i],dtype='float32')
 red=np.array([(120,58,56),(112,53,53),(101,52,50)][i],dtype='float32')
 green=np.array([(58,73,61),(52,67,57),(47,61,55)][i],dtype='float32')
 st=noise(n,14400+i,3)*3+noise(n,14402+i,35)*4
 a=white[None,None,:]+st[:,:,None]
 a=np.where(diamond[:,:,None],green[None,None,:]+st[:,:,None],a)
 a=np.where(center[:,:,None],red[None,None,:]+st[:,:,None],a)
 a=np.where(roundrim[:,:,None],white[None,None,:]-st[:,:,None],a)
 a=np.where(tileborder[:,:,None],np.array([97,94,88])[None,None,:]+st[:,:,None]*.5,a)
 return seam(a)
items=[('ladrillo_antiguo',512,brick),('peperino_gris',512,peperino),('revoque_amarillo',512,plaster),
       ('sampietrini',512,cobbles),('mosaico_cosmatesco',1024,cosmatesco)]
files=[]
for name,res,fn in items:
 for v in 'abc':
  p=OUT/f'{name}_roma_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# preview
size=215;left=14;head=49;rh=244;gap=8
sheet=Image.new('RGB',(2*left+5*size+4*gap,head+3*rh+8),(240,237,230));d=ImageDraw.Draw(sheet)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
d.text((left,10),'L12 · Roma · ladrillo, peperino, revoque y pavimentos',font=f,fill=(38,40,39))
for col,(name,_,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_roma_{v}.png';im=Image.open(p).resize((size,size),Image.Resampling.LANCZOS)
  xx=left+col*(size+gap);yy=head+row*rh
  sheet.paste(im,(xx,yy));d.text((xx,yy+size+3),f'{name[:19]} · {v}',font=f,fill=(43,42,40))
sheet.save(CTL/'preview_L12_roma_15_texturas.jpg',quality=90)
for p in files:
 im=Image.open(p).resize((256,256));proof=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):proof.paste(im,(x*256,y*256))
 proof.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=87)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);fields=rdr.fieldnames
assert sum(r['lote']=='L12' for r in rows)==15
qa={'lote':'L12','archivos':[]}
for r in rows:
 if r['lote']!='L12':continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==tuple(map(int,r['resolucion'].split('x')))
 a=np.asarray(im,dtype=np.int16);mx=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert mx<=1
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo romano; bordes/mosaicos probados. Revisar cronología del pavimento y render de juego.'
 qa['archivos'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'max_diferencia_borde':mx})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if str(item.get('ciudad','')).lower()!='roma':continue
 if item['clave_id'] not in {z[0] for z in items}:continue
 for v in 'abc':
  p=next(x for x in files if x.name==f"{item['clave_id']}_roma_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Prototipo romano, pendiente contraste histórico y Blender.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote12.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';lines=plan.read_text('utf-8').splitlines()
for idx,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[idx]=f'**Progreso actual:** {count}/294 PNG reales; L12 Roma terminado como prototipo. L06 aún 12/24, faltan recursos RGBA. No hay revisión Blender final.'
plan.write_text('\n'.join(lines)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí\n\nCorte: 2026-11-07.\n\n## Estado comprobado\n- 98 familias ×3 variantes, 294 PNG. **{count} generadas; {294-count} pendientes.**\n- L01-L05 y L07-L12 están creados como prototipos. L06 parcial: 12/24 (follajes y corte de tronco transparentes pendientes).\n- L12 Roma 15/15 variantes existentes. SHA-256, resolución y bordes comprobados; sin prueba Blender ni aprobación histórica final.\n\n## Continuación\n- Pendientes L06 transparentes: ramillete_olivo, ramillete_encina, ramillete_cipres y corte_tronco (a/b/c).\n- Seguir L13 Palermo (15 PNG), después L14-L16 detalles.\n- Adjuntar `paquete_continuidad_L01_L12.zip` en nuevo chat, leer este archivo y la primera fila pendiente del CSV.\n''','utf-8')
lot=BASE/'lote_12_roma.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L12' in p.name or '_roma_' in p.name):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L12.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
