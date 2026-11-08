from pathlib import Path
import csv,json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control';OUT=ROOT/'ciudad/milán';OUT.mkdir(parents=True,exist_ok=True)
N=512

def noise(seed,n,sy,sx=None):
 sx=sy if sx is None else sx
 r=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sy*sy*fy*fy+sx*sx*fx*fx))
 a=np.fft.irfft2(np.fft.rfft2(r)*filt,s=(n,n)).real.astype('float32')
 return (a-a.mean())/max(float(a.std()),1e-6)

def seam(ar):
 n=ar.shape[0];b=max(15,int(n*.035));a=ar.astype('float32').copy()
 for j in range(b):
  w=.5+.5*np.cos(np.pi*j/b);m=(a[:,j].copy()+a[:,n-1-j].copy())/2
  a[:,j]=a[:,j]*(1-w)+m*w;a[:,n-1-j]=a[:,n-1-j]*(1-w)+m*w
 for j in range(b):
  w=.5+.5*np.cos(np.pi*j/b);m=(a[j].copy()+a[n-1-j].copy())/2
  a[j]=a[j]*(1-w)+m*w;a[n-1-j]=a[n-1-j]*(1-w)+m*w
 return np.uint8(np.clip(np.rint(a),0,255))

def ceppo(v):
 i='abc'.index(v);n=512;seed=10190+i*21
 a=np.asarray(Image.open(ROOT/f'comunes/piedra_noble/piedra_serena_sillares_{v}.png'),dtype='float32')
 base=np.array([(133,134,127),(121,122,117),(110,111,108)][i],dtype='float32')
 a=.7*a+.3*base[None,None,:]
 # natural conglomerate pebbles 1-3 cm embedded in cut blocks, softly mottled.
 grain=noise(seed,n,1.4)*3.5+noise(seed+1,n,10)*4
 pebbles=np.maximum(0,noise(seed+3,n,1.1)-1.6)
 a+=grain[:,:,None]+pebbles[:,:,None]*np.array([8,7,7])
 return seam(a)

def plaster(v):
 i='abc'.index(v);seed=10230+i*17
 a=np.asarray(Image.open(ROOT/f'comunes/muros/enlucido_claro_{v}.png'),dtype='float32')
 target=np.array([(197,144,126),(186,131,118),(170,124,115)][i])
 a=a*.22+target[None,None,:]*.78+noise(seed,512,31)[:,:,None]*np.array([4,3,2])
 return seam(a)

def roof(v):
 i='abc'.index(v);paths=['a_hyper_realistic_high_detail_orthographic_close.png','a_detailed_close_up_texture_image_of_an_old_weath.png','a_crisp_ultra_detailed_orthographic_close_up_tex.png']
 a=np.asarray(Image.open(BASE/paths[i]).resize((1024,1024),Image.Resampling.LANCZOS),dtype='float32')
 target=np.array([(105,66,51),(92,57,46),(80,55,45)][i])
 a=a*.78+target[None,None,:]*.22
 return seam(a)

def cobbles(v):
 i='abc'.index(v);seed=10300+i*21;rng=np.random.default_rng(seed)
 n=512;a=np.asarray(Image.open(ROOT/f'comunes/suelos/grava_{v}.png'),dtype='float32')
 # 5–10cm stones across 2m => approximate 22-32 stones across.
 im=Image.fromarray(np.uint8(np.clip(a*.65+np.array([113,112,109])[None,None,:]*.35,0,255)))
 d=ImageDraw.Draw(im)
 stones=[(143,142,139),(171,168,160),(122,126,127),(190,184,174),(113,117,120),(152,154,154)]
 step=25
 for row in range(-1,23):
  for col in range(-1,23):
   x=col*step+(row%2)*12+int(rng.integers(-4,5));y=row*step+int(rng.integers(-4,5))
   rad=int(rng.integers(8,12));color=stones[int(rng.integers(0,len(stones)))]
   for ox in (-n,0,n):
    for oy in (-n,0,n):
     d.ellipse((x+ox-rad,y+oy-rad,x+ox+rad,y+oy+rad),fill=color)
 a=np.asarray(im,dtype='float32')
 # two broad wheel tracks in large flat stone slabs, subdued grout
 x=np.arange(n)
 wheel=((np.abs(x-n*.27)<10)|(np.abs(x-n*.73)<10)).astype('float32')
 wheel=np.tile(wheel,(n,1))
 track=np.array([(134,131,124),(124,121,115),(114,113,109)][i])
 a=a*(1-wheel[:,:,None]*.88)+track[None,None,:]*wheel[:,:,None]*.88
 return seam(a)
items=[('ceppo_lombardo',512,ceppo),('revoque_lombardo',512,plaster),('teja_lombarda_oscura',1024,roof),('rizada_cantos_rodados',512,cobbles)]
files=[]
for name,res,fn in items:
 for v in 'abc':
  p=OUT/f'{name}_milan_{v}.png';Image.fromarray(fn(v)).save(p,optimize=True);files.append(p)
# visual sheet
s=251;left=15;head=52;rh=281;gap=10
sheet=Image.new('RGB',(2*left+4*s+3*gap,head+3*rh+10),(239,236,231));d=ImageDraw.Draw(sheet)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
d.text((left,10),'L10 · Milán · ceppo, revoque, tejas y rizzada',font=f,fill=(40,39,38))
for c,(name,_,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_milan_{v}.png';im=Image.open(p).resize((s,s),Image.Resampling.LANCZOS)
  x=left+c*(s+gap);y=head+row*rh
  sheet.paste(im,(x,y));d.text((x,y+s+4),f'{name[:21]} · {v}',font=f,fill=(42,40,38))
sheet.save(CTL/'preview_L10_milan_12_texturas.jpg',quality=90)
for p in files:
 im=Image.open(p).resize((256,256));m=Image.new('RGB',(768,768))
 for y in range(3):
  for x in range(3):m.paste(im,(x*256,y*256))
 m.save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=87)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rdr=csv.DictReader(f);rows=list(rdr);fields=rdr.fieldnames
assert sum(r['lote']=='L10' for r in rows)==12
qa={'lote':'L10','archivos':[]}
for r in rows:
 if r['lote']!='L10':continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.size==tuple(map(int,r['resolucion'].split('x')))
 a=np.asarray(im,dtype=np.int16);mx=int(max(abs(a[:,0]-a[:,-1]).max(),abs(a[0]-a[-1]).max()));assert mx<=1
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha;r['notas']='Prototipo milanés, basado en material común adaptado; validación artística Blender pendiente.'
 qa['archivos'].append({'archivo':p.name,'resolucion':im.size,'sha256':sha,'max_diferencia_borde':mx})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if str(item.get('ciudad','')).lower() not in ('milán','milan'):continue
 if item['clave_id'] not in {x[0] for x in items}:continue
 for v in 'abc':
  p=next(x for x in files if x.name==f"{item['clave_id']}_milan_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Prototipo local; revisar contraste y realismo al tamaño de render.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote10.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';ls=plan.read_text('utf-8').splitlines()
for j,line in enumerate(ls):
 if line.startswith('**Progreso actual:**'):
  ls[j]=f'**Progreso actual:** {count}/294 PNG reales, L10 Milán completado como prototipo. L06 falta 12 PNG transparentes. Ninguno aprobado artísticamente en Blender.'
plan.write_text('\n'.join(ls)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text(f'''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado comprobado\n- Total de 98 materiales con 294 variantes. **{count}/294 PNG existentes**, quedan {294-count}.\n- L01-L05 y L07-L10 completos como prototipos; L06 parcial 12/24.\n- L10 Milán 12 PNG con ceppo, revoque, teja oscura y rizzada; todos en ZIP.\n- Todos los PNG producidos tienen checksum, resolución y bordes comprobados; falta prueba Blender y evaluación artística.\n\n## Continuar\n- Primero archivos pendientes L06 con alfa: ramillete_olivo, ramillete_encina, ramillete_cipres, corte_tronco (a/b/c). Si no es posible mantener realismo con transparencia, mantener pendientes.\n- L11 Génova (12 PNG), luego L12 Roma y L13 Palermo.\n- Usar primera fila `pendiente` en progreso_produccion.csv y actualizar al generar realmente cada archivo.\n\n## Recuperación\nAdjunta el ZIP `paquete_continuidad_L01_L10.zip` al nuevo chat y solicita reanudar desde este documento.\n''','utf-8')
lot=BASE/'lote_10_milan.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L10' in p.name or 'milan' in p.name):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L10.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('done',count,'/294 | lot',lot.stat().st_size,'| full',full.stat().st_size)
