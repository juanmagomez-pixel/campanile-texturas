from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control';OUT=ROOT/'ciudad/palermo';OUT.mkdir(parents=True,exist_ok=True)

def noise(n,seed,sigma):
 r=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*sigma*sigma*(fy**2+fx**2))
 a=np.fft.irfft2(np.fft.rfft2(r)*filt,s=(n,n)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-6)

def seam(a):
 n=a.shape[0];b=max(14,int(n*.035));a=a.astype('float32').copy()
 for j in range(b):
  w=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,n-1-j].copy())/2
  a[:,j]=a[:,j]*(1-w)+m*w;a[:,n-1-j]=a[:,n-1-j]*(1-w)+m*w
 for j in range(b):
  w=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[n-1-j].copy())/2
  a[j]=a[j]*(1-w)+m*w;a[n-1-j]=a[n-1-j]*(1-w)+m*w
 return np.uint8(np.clip(np.rint(a),0,255))

def plaster(v):
 i='abc'.index(v);n=512
 im=np.asarray(Image.open(ROOT/f'comunes/muros/enlucido_desconchado_{v}.png'),dtype='float32')
 chips=(im[:,:,0]-im[:,:,1])>38
 plaster_color=np.array([(231,218,187),(220,207,178),(206,190,165)][i])
 toba=np.array([(188,150,96),(178,137,89),(157,121,83)][i])
 st=noise(n,15500+i,3)*3+noise(n,15501+i,27)*4
 a=plaster_color[None,None,:]+st[:,:,None]
 a=np.where(chips[:,:,None],toba[None,None,:]+st[:,:,None],a)
 a-=np.maximum(noise(n,15502+i,53),0)[:,:,None]*i*3
 return seam(a)

def cupola(v):
 i='abc'.index(v);n=512
 src=np.asarray(Image.open(ROOT/f'comunes/muros/enlucido_claro_{v}.png'),dtype='float32')
 red=np.array([(171,66,54),(157,62,54),(142,59,53)][i])
 a=red[None,None,:]+(src-src.mean(axis=(0,1),keepdims=True))*.68
 a+=noise(n,15550+i,21)[:,:,None]*np.array([5,3,3])
 return seam(a)

def arches(v):
 i='abc'.index(v);n=1024;seed=15600+i
 st=noise(n,seed,3)*4+noise(n,seed+1,36)*5
 golden=np.array([(183,147,98),(170,134,92),(156,122,87)][i])
 base=golden[None,None,:]+st[:,:,None]
 # Arabic-Norman blind pointed arcades, intersecting relief, repeating geometry.
 height=Image.new('F',(n,n),.15);d=ImageDraw.Draw(height)
 width=n/4
 for row in range(2):
  for col in range(4):
   cx=int((col+.5)*width);y0=int(row*n/2)
   # pointed arc composed of two rounded curves meeting at apex
   d.line([(cx-105,y0+380),(cx-105,y0+205),(cx,y0+60),(cx+105,y0+205),(cx+105,y0+380)],fill=.8,width=22)
   d.line([(cx-120,y0+380),(cx-120,y0+195),(cx,y0+39),(cx+120,y0+195),(cx+120,y0+380)],fill=.55,width=8)
   # intertwine adjacent arc outlines without human figures
   d.arc((cx-170,y0+126,cx+170,y0+403),210,330,fill=.6,width=12)
 bump=gaussian_filter(np.asarray(height,dtype='float32'),2,mode='wrap')
 dy,dx=np.gradient(bump)
 a=base+(bump-.25)[:,:,None]*np.array([16,14,10])+(dx-dy)[:,:,None]*np.array([230,205,175])
 # occasional dark lava inserts, small and not a full graphic outline
 lava=noise(n,seed+30,12)>2.4
 a-=lava[:,:,None]*np.array([36,33,28])
 return seam(a)

def majolica(v):
 i='abc'.index(v);n=1024;seed=15700+i;unit=n/5
 y,x=np.mgrid[:n,:n]
 cx=np.mod(x,unit)-unit/2;cy=np.mod(y,unit)-unit/2
 edge=(np.abs(cx)>unit*.455)|(np.abs(cy)>unit*.455)
 rr=np.sqrt(cx**2+cy**2)
 floral=(np.abs(cx)+np.abs(cy)<unit*.24)
 ring=np.abs(rr-unit*.32)<unit*.037
 base=np.array([(216,209,187),(205,197,178),(189,186,173)][i])
 a=base[None,None,:]+(noise(n,seed,3)*3+noise(n,seed+1,30)*3)[:,:,None]
 blue=np.array([(65,96,134),(60,87,126),(59,79,115)][i])
 yellow=np.array([(177,142,69),(160,133,73),(150,123,70)][i])
 green=np.array([(81,111,84),(75,105,79),(68,94,75)][i])
 a=np.where(ring[:,:,None],blue[None,None,:]+noise(n,seed+2,4)[:,:,None]*3,a)
 a=np.where(floral[:,:,None],yellow[None,None,:]+noise(n,seed+3,4)[:,:,None]*2,a)
 diamond=np.abs(cx)<unit*.05
 diamond=diamond & (np.abs(cy)<unit*.26)
 a=np.where(diamond[:,:,None],green[None,None,:],a)
 a=np.where(edge[:,:,None],np.array([148,141,129])[None,None,:],a)
 return seam(a)

def basalt(v):
 i='abc'.index(v);n=512
 src=np.asarray(Image.open(ROOT/f'comunes/suelos/losas_piedra_{v}.png'),dtype='float32')
 target=np.array([(83,85,85),(74,77,78),(68,72,74)][i])
 a=src*.46+target[None,None,:]*.54+noise(n,15800+i,15)[:,:,None]*3
 return seam(a)

items=[('revoque_claro',512,plaster),('cupula_roja',512,cupola),('arcos_entrelazados',1024,arches),('mayolica_siciliana',1024,majolica),('basalto_etna',512,basalt)]
files=[]
for name,res,fn in items:
 for v in 'abc':
  p=OUT/f'{name}_palermo_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# previews
size=216;left=13;head=48;rh=245;gap=8
sheet=Image.new('RGB',(2*left+5*size+4*gap,head+3*rh+9),(239,235,230));d=ImageDraw.Draw(sheet)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
d.text((left,11),'L13 · Palermo · materiales árabe-normandos y sicilianos',font=f,fill=(38,39,39))
for c,(name,_,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_palermo_{v}.png';im=Image.open(p).resize((size,size),Image.Resampling.LANCZOS)
  xx=left+c*(size+gap);yy=head+row*rh
  sheet.paste(im,(xx,yy));d.text((xx,yy+size+3),f'{name[:20]} · {v}',font=f,fill=(44,42,40))
sheet.save(CTL/'preview_L13_palermo_15_texturas.jpg',quality=90)
for p in files:
 im=Image.open(p).resize((256,256),Image.Resampling.LANCZOS);proof=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):proof.paste(im,(x*256,y*256))
 proof.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=86)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);fields=rdr.fieldnames
assert sum(r['lote']=='L13' for r in rows)==15
qa={'lote':'L13','archivos':[]}
for r in rows:
 if r['lote']!='L13':continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==tuple(map(int,r['resolucion'].split('x')))
 a=np.asarray(im,dtype=np.int16);mx=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert mx<=1
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo Palermo con motivos procedimentales, revisar precisión histórica y realismo Blender.'
 qa['archivos'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'max_diferencia_borde':mx})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if str(item.get('ciudad','')).lower()!='palermo':continue
 if item['clave_id'] not in {z[0] for z in items}:continue
 for v in 'abc':
  p=next(x for x in files if x.name==f"{item['clave_id']}_palermo_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Prototipo histórico a validar visualmente.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote13.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';ls=plan.read_text('utf-8').splitlines()
for j,line in enumerate(ls):
 if line.startswith('**Progreso actual:**'):
  ls[j]=f'**Progreso actual:** {count}/294 PNG reales. L13 Palermo completado como prototipo. L06 12/24, RGBA pendientes. Ninguna revisión Blender definitiva.'
plan.write_text('\n'.join(ls)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí — texturas del Renacimiento\n\nCorte: 2026-11-07.\n\n## Estado comprobado\n- 98 familias, 294 variantes. **{count} PNG reales**, {294-count} pendientes.\n- L01-L05 y L07-L13 generados como prototipos. L06 12/24, con alfa pendiente.\n- Los PNG generados tienen hash, dimensiones y coincidencia de bordes comprobados. Pendiente comprobar realismo, escala y contexto histórico con render Blender.\n\n## Continuación\n- L06: producir ramillete_olivo, ramillete_encina, ramillete_cipres y corte_tronco (a/b/c), 512px, PNG alfa NO repetibles; solo imágenes naturalistas, evitar cartoon.\n- L14, L15 y L16 son los últimos lotes de detalles. Revisar primero el manifiesto y documentar variantes.\n- Adjuntar `paquete_continuidad_L01_L13.zip` si se cambia de conversación.\n''','utf-8')
lot=BASE/'lote_13_palermo.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L13' in p.name or '_palermo_' in p.name):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L13.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
