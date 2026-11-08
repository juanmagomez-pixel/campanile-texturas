from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,csv,json,hashlib,zipfile
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control'

def pnoise(n,seed,sigma):
 z=np.random.default_rng(seed).normal(size=(n,n)).astype('float32')
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 filt=np.exp(-2*np.pi*np.pi*(sigma*sigma)*(fy*fy+fx*fx))
 ar=np.fft.irfft2(np.fft.rfft2(z)*filt,s=(n,n)).real.astype('float32')
 return (ar-ar.mean())/max(float(ar.std()),.00001)

def seam(a):
 n=a.shape[0];b=max(9,round(n*.042));a=a.astype('float32').copy()
 for i in range(b):
  w=.5+.5*np.cos(np.pi*i/b)
  m=(a[:,i].copy()+a[:,n-1-i].copy())*.5
  a[:,i]=a[:,i]*(1-w)+m*w;a[:,n-1-i]=a[:,n-1-i]*(1-w)+m*w
 for i in range(b):
  w=.5+.5*np.cos(np.pi*i/b)
  m=(a[i].copy()+a[n-1-i].copy())*.5
  a[i]=a[i]*(1-w)+m*w;a[n-1-i]=a[n-1-i]*(1-w)+m*w
 return np.uint8(np.clip(np.rint(a),0,255))

def make(name,v,n):
 idx='abc'.index(v); seed=1750+idx*71+sum(map(ord,name))
 y,x=np.mgrid[0:n,0:n]
 micro=pnoise(n,seed,max(1,n/190))*.9+pnoise(n,seed+90,max(1,n/45))*.65+pnoise(n,seed+115,max(1,n/12))*.26
 large=pnoise(n,seed+40,max(1,n/18))
 if name=='marmol_carrara':
  base=np.array([(222,220,213),(218,216,208),(209,206,199)][idx])
  # white marble: delicate branching, semi-diagonal gray veins.
  warp=pnoise(n,seed+208,n/29)*n*.014
  phase=(x*.43+y*.68)/n*7*np.pi +pnoise(n,seed+205,n/35)*.65
  veins_raw=np.exp(-np.abs(np.sin(phase))*28)
  vein=veins_raw*np.clip((pnoise(n,seed+244,n/28)+1.0)*.5,0,1)
  a=base[None,None,:]+micro[:,:,None]*np.array([3,3,3])[None,None,:]
  a-=vein[:,:,None]*np.array([32,33,35])[None,None,:]
  a-=np.clip(large,0,2)[:,:,None]*3
 elif name=='marmol_verde_prato':
  base=np.array([(40,59,49),(35,52,43),(32,46,39)][idx])
  warp=pnoise(n,seed+208,n/30)*n*.02
  phase=(x*.77+y*.25)/n*9*np.pi +pnoise(n,seed+207,n/38)*.68
  vein=np.exp(-np.abs(np.sin(phase))*29)*np.clip((pnoise(n,seed+245,n/37)+1.0)*.6,0,1)
  a=base[None,None,:]+micro[:,:,None]*np.array([4.5,5,4.4])[None,None,:]
  a+=vein[:,:,None]*np.array([34,43,33])[None,None,:]
  a+=np.clip(large,0,2)[:,:,None]*np.array([3,4,2])[None,None,:]
 elif name=='marmol_rosa_maremma':
  base=np.array([(215,160,146),(207,151,139),(196,145,136)][idx])
  warp=pnoise(n,seed+208,n/25)*n*.02
  phase=(x*.31+y*.72)/n*7*np.pi+pnoise(n,seed+209,n/34)*.7
  vein=np.exp(-np.abs(np.sin(phase))*28)*np.clip((pnoise(n,seed+248,n/28)+1.0)*.5,0,1)
  a=base[None,None,:]+micro[:,:,None]*np.array([4,4,4])[None,None,:]
  a+=vein[:,:,None]*np.array([32,38,40])[None,None,:]
  a-=np.clip(large,0,2)[:,:,None]*np.array([5,4,5])[None,None,:]
 elif name=='marmol_rojo_verona':
  base=np.array([(165,86,64),(153,78,58),(143,72,53)][idx])
  a=base[None,None,:]+micro[:,:,None]*np.array([5,4,3.5])[None,None,:]
  fossils=pnoise(n,seed+550,n/24)+.35*pnoise(n,seed+551,n/7)
  shape=np.clip((fossils-.65)/1.7,0,1)
  a+=shape[:,:,None]*np.array([19,15,12])[None,None,:]
  a-=np.clip(large,0,2)[:,:,None]*np.array([7,6,4])[None,None,:]
 elif name=='piedra_serena_lisa':
  base=np.array([(130,140,142),(121,130,132),(111,122,125)][idx]);
  a=base[None,None,:]+micro[:,:,None]*np.array([4.0,4.0,4.0])[None,None,:]
  a+=large[:,:,None]*np.array([2.2,2.2,2.3])[None,None,:]
 else:
  base=np.array([(200,192,175),(187,180,164),(177,169,156)][idx]);
  a=base[None,None,:]+micro[:,:,None]*np.array([4,4,3.6])[None,None,:]
  pores=pnoise(n,seed+550,max(1,n/260))>2.0
  a-=pores[:,:,None]*np.array([7,7,6])[None,None,:]
 return seam(a)

items=[('marmol_carrara',512,'comunes/marmoles'),('marmol_verde_prato',512,'comunes/marmoles'),
       ('marmol_rosa_maremma',512,'comunes/marmoles'),('marmol_rojo_verona',512,'comunes/marmoles'),
       ('piedra_serena_lisa',256,'comunes/columnas_y_piedra_lisa'),('piedra_clara_labrada',256,'comunes/columnas_y_piedra_lisa')]
files=[]
for name,size,directory in items:
 target=ROOT/directory;target.mkdir(parents=True,exist_ok=True)
 for v in 'abc':
  p=target/f'{name}_{v}.png';Image.fromarray(make(name,v,size)).save(p,optimize=True)
  files.append(p)
# preview
sz=214;pad=12;head=51;rh=249
sheet=Image.new('RGB',(6*sz+5*7+2*pad,3*rh+head+13),(238,235,230))
d=ImageDraw.Draw(sheet)
fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
d.text((pad,10),'L04 · Mármoles y piedras labradas · variaciones a, b, c',font=fnt,fill=(37,38,38))
for j,(name,size,directory) in enumerate(items):
 for k,v in enumerate('abc'):
  p=ROOT/directory/f'{name}_{v}.png';im=Image.open(p).resize((sz,sz),Image.Resampling.LANCZOS)
  x=pad+j*(sz+7);y=head+k*rh
  sheet.paste(im,(x,y));d.text((x,y+sz+3),f'{name[:21]} · {v}',font=fnt,fill=(45,44,43))
sheet.save(CTL/'preview_L04_18_texturas.jpg',quality=91)
for p in files:
 im=Image.open(p).convert('RGB').resize((384,384),Image.Resampling.LANCZOS);proof=Image.new('RGB',(1152,1152))
 for y in range(3):
  for x in range(3):proof.paste(im,(x*384,y*384))
 proof.resize((768,768),Image.Resampling.LANCZOS).save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=86)
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 r=csv.DictReader(f);rows=list(r);cols=r.fieldnames
assert sum(row['lote']=='L04' for row in rows)==18
qa={'lote':'L04','archivos':[]}
for row in rows:
 if row['lote']!='L04':continue
 p=ROOT/row['ruta'];assert p.exists(),p
 img=Image.open(p)
 assert img.size==tuple(map(int,row['resolucion'].split('x'))),(p,img.size)
 a=np.asarray(img,dtype=np.int16)
 mx=int(max(np.abs(a[:,0]-a[:,-1]).max(),np.abs(a[0]-a[-1]).max()))
 assert mx<=1,(p,mx)
 checksum=hashlib.sha256(p.read_bytes()).hexdigest()
 row['estado']='generada';row['sha256']=checksum;row['notas']='Prototipo procedimental, sin fuentes fotográficas; borde comprobado, falta prueba Blender.'
 qa['archivos'].append({'archivo':p.name,'resolucion':img.size,'max_diferencia_borde':mx,'sha256':checksum})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if item['clave_id'] not in {name for name,_,_ in items}:continue
 for v in 'abc':
  p=ROOT/item['variantes'][v]['ruta'] if 'ruta' in item['variantes'][v] else next((f for f in files if f.name==f"{item['clave_id']}_{v}.png"),None)
  assert p is not None and p.exists(),(item['clave_id'],v,p)
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='Textura procedimental provisional; escala material 1×1m, sin juntas. Revisión visual pendiente.'
catp.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n','utf-8')
(CTL/'verificacion_lote04.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False)+'\n','utf-8')
num=sum(r['estado']=='generada' for r in rows)
plan=CTL/'plan_produccion_v2.md';ls=plan.read_text('utf-8').splitlines()
for i,line in enumerate(ls):
 if line.startswith('**Progreso actual:**'):
  ls[i]=f'**Progreso actual:** 4 lotes generados como prototipos, {num}/294 PNG reales. No se ha hecho prueba definitiva en Blender ni validación histórica. L02, L03 y L04 procedimentales.'
plan.write_text('\n'.join(ls)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md';resume.write_text(f'''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado verificado\n- 98 materiales, 294 variantes PNG a/b/c.\n- L01 tejados: 15 PNG; L02 muros: 18; L03 piedra noble: 21; L04 mármoles y piedras lisas: 18.\n- **{num}/294 PNG existentes; 222 pendientes.**\n- Mosaicos 3×3, checksums y comprobación de bordes completados, pero NO existe aprobación artística ni pruebas Blender.\n- L02-L04 son prototipos procedimentales, no fotográficos. Revisar su realismo al tamaño de juego, con posibilidad de sustitución.\n\n## Próximo lote\nL05: vidrio emplomado de rulli, vidrio de cuarterones, vidriera de iglesia, esgrafiado florentino, terracota decorativa (15 PNG). Primero `vidrio_rulli_a.png` según CSV.\n\n## Recuperación\nAdjunta `paquete_continuidad_L01_L04.zip` en otra conversación y sigue desde 00_control/REANUDAR_AQUI.md y el primer estado pendiente, no desde cero.\n''','utf-8')
lot=BASE/'lote_04_comunes_marmoles_columnas.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','catalogo_resoluciones.csv','README.md','especificaciones_originales.md') or ('L04' in p.name or any(it[0] in p.name for it in items)):
   z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
full=BASE/'paquete_continuidad_L01_L04.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('generated:',num,'zip:',lot.stat().st_size,'full:',full.stat().st_size)
