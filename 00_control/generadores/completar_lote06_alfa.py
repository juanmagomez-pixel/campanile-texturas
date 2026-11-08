from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from scipy.ndimage import gaussian_filter
import numpy as np,csv,hashlib,json,zipfile,shutil
BASE=Path('/mnt/data');ROOT=BASE/'texturas_renacimiento_italiano';CTL=ROOT/'00_control';OUT=ROOT/'comunes/arboles_y_troncos';OUT.mkdir(parents=True,exist_ok=True)
S=512;HI=1024

def make_olive(v):
 # Crop one of the three independent photorealistic sprigs from generated transparent sheet.
 src=Image.open(BASE/'a_clean_png_style_composite_image_on_a_transparent.png').convert('RGBA')
 idx='abc'.index(v);im=src.crop((idx*724,0,(idx+1)*724,724)).resize((S,S),Image.Resampling.LANCZOS)
 arr=np.asarray(im,dtype=np.uint8).copy()
 r=arr[:,:,0].astype(int);g=arr[:,:,1].astype(int);b=arr[:,:,2].astype(int)
 # Clear color-key overspill: neon green, red, yellow artifacts are not leaf pixels.
 neon=((r>215)&(g<90)&(b<100))|((g>210)&(r<115)&(b<130))|((r>200)&(g>180)&(b<80))
 arr[:,:,3][neon]=0
 arr[:,:,3][arr[:,:,3]<42]=0
 # Remove the faint fringe without erasing thin natural twigs.
 alpha=Image.fromarray(arr[:,:,3]).filter(ImageFilter.MedianFilter(3))
 arr[:,:,3]=np.asarray(alpha)
 arr[:,:,:3][arr[:,:,3]==0]=0
 return Image.fromarray(arr,'RGBA')

def add_leaf(canvas,x,y,deg,length,width,palette,rng,old=0):
 # Real leaf-like elliptical taper with central vein, variable specularity and wear.
 radius=int(length+width+16);x0=int(x-radius);y0=int(y-radius)
 x1=int(x+radius);y1=int(y+radius);w=x1-x0;h=y1-y0
 yy,xx=np.mgrid[y0:y1,x0:x1].astype('float32')
 ang=np.deg2rad(deg);dx=xx-x;dy=yy-y
 u=(dx*np.cos(ang)+dy*np.sin(ang))/length
 vv=(-dx*np.sin(ang)+dy*np.cos(ang))
 taper=np.maximum(0, np.sin(np.clip(u,0,1)*np.pi))**.75
 serration=1+ .05*np.sin(u*18*np.pi)
 leafmask=(u>0)&(u<1)&(np.abs(vv)<width*taper*serration*.5)
 light=np.clip((vv/width),-.8,.8)*(-10)
 noisy=rng.normal(0,2.8,size=(h,w))
 base=np.array(palette,dtype='float32')
 pix=np.zeros((h,w,4),dtype=np.uint8)
 for c in range(3):pix[:,:,c]=np.uint8(np.clip(base[c]+light+noisy,0,255))
 midrib=(np.abs(vv)<1.4)&(u>.09)&(u<.88)
 pix[midrib,0]=np.minimum(255,pix[midrib,0].astype(int)+11)
 pix[midrib,1]=np.minimum(255,pix[midrib,1].astype(int)+10)
 pix[midrib,2]=np.minimum(255,pix[midrib,2].astype(int)+8)
 pix[:,:,3]=np.where(leafmask,244,0).astype(np.uint8)
 if old:
  brown=(rng.random(size=(h,w))<.02*old)&leafmask
  pix[brown,:3]=np.array([123,102,72])
 bx=max(0,x0);by=max(0,y0);ex=min(HI,x1);ey=min(HI,y1)
 if bx<ex and by<ey:
  crop=Image.fromarray(pix,'RGBA').crop((bx-x0,by-y0,ex-x0,ey-y0))
  canvas.alpha_composite(crop,(bx,by))

def holm(v):
 idx='abc'.index(v);rng=np.random.default_rng(22000+idx*51)
 im=Image.new('RGBA',(HI,HI),(0,0,0,0));d=ImageDraw.Draw(im,'RGBA')
 # asymmetrical woody main stem with mixed secondaries
 mains=[(475,942),(504,760),(520,582),(542,404),(550,239),(561,127)]
 d.line(mains,fill=(102,84,68,255),width=9,joint='curve')
 secondary=[]
 for j in range(9):
  y=820-j*77;rootx=503+j*7
  side=-1 if j%2==0 else 1
  bx=int(rootx);by=int(y)
  ex=int(bx+side*rng.integers(190,320));ey=int(y-rng.integers(90,210))
  mid=(int((bx+ex)/2+side*rng.integers(10,35)),int((by+ey)/2-20))
  d.line([(bx,by),mid,(ex,ey)],fill=(100,83,64,255),width=int(max(3,7-j*.32)))
  secondary.append(((bx,by),mid,(ex,ey)))
 # Leaves around the branching skeleton; each one has its own angular shading and microvariation.
 for j,(root,mid,end) in enumerate(secondary):
  for k in range([11,10,8][idx]):
   t=(k+.5)/([11,10,8][idx]+.2)
   ax=(1-t)**2*root[0]+2*(1-t)*t*mid[0]+t*t*end[0]
   ay=(1-t)**2*root[1]+2*(1-t)*t*mid[1]+t*t*end[1]
   for sign in (-1,1):
    if rng.random()<.11*idx:continue
    deg=(170 if sign<0 else -30)+(j%3)*15+rng.normal(0,18)
    color=[(50,80,49),(55,84,51),(65,85,57)][idx]
    var=int(rng.normal(0,9));color=tuple(max(0,min(255,c+var)) for c in color)
    add_leaf(im,ax+rng.normal(0,10),ay+rng.normal(0,12),deg,rng.uniform(70,107),rng.uniform(28,45),color,rng,idx)
 return im.resize((S,S),Image.Resampling.LANCZOS)

def cypress(v):
 idx='abc'.index(v);rng=np.random.default_rng(23000+idx*50)
 im=Image.new('RGBA',(HI,HI),(0,0,0,0));d=ImageDraw.Draw(im,'RGBA')
 d.line([(494,968),(506,777),(510,520),(511,244),(510,70)],fill=(75,77,56,255),width=10)
 for j in range(17):
  by=920-j*47;bx=506+int(rng.normal(0,22))
  side=-1 if j%2==0 else 1
  ex=bx+side*int(rng.uniform(115,280));ey=by-int(rng.uniform(85,175))
  d.line((bx,by,ex,ey),fill=(60,81,59,245),width=int(rng.integers(3,7)))
  # scale-like cypress foliage: 150 small overlapping natural green tips per branch
  for k in range([230,210,170][idx]):
   t=rng.uniform(.07,1)
   xx=bx+t*(ex-bx);yy=by+t*(ey-by)
   spread=20*(1-t)+8
   x=xx+rng.normal(0,spread);y=yy+rng.normal(0,spread*.8)
   if not (8<x<HI-8 and 8<y<HI-8):continue
   color=[(40,67,44),(42,64,45),(47,60,46)][idx]
   dd=int(rng.normal(0,12));col=tuple(np.clip(c+dd,0,255) for c in color)
   rad=int(rng.integers(2,6))
   d.ellipse((x-rad,y-rad*2,x+rad,y+rad*2),fill=(*map(int,col),int(rng.integers(180,250))))
 return im.resize((S,S),Image.Resampling.LANCZOS)

def gaussian_noise(seed,sigma):
 rng=np.random.default_rng(seed);z=rng.normal(size=(S,S)).astype('float32');a=gaussian_filter(z,sigma=sigma,mode='nearest')
 return (a-a.mean())/max(float(a.std()),1e-5)

def cut(v):
 idx='abc'.index(v);seed=24000+idx*70
 yy,xx=np.mgrid[:S,:S].astype('float32')
 x=xx-256;y=yy-255
 angle=np.arctan2(y,x)
 distort=gaussian_noise(seed,17)*2.3+np.sin(angle*13)*2
 rad=np.sqrt((x+5*np.sin(angle*3))**2+(y-4*np.cos(angle*5))**2)+distort
 outer=221-idx*3+np.sin(angle*19)*2.5
 alpha=np.clip((outer-rad)*70,0,255)
 interior=rad<outer-21
 bands=np.sin(rad*.49+gaussian_noise(seed+1,19)*.8)
 fine=gaussian_noise(seed+2,2)*2.9+gaussian_noise(seed+3,11)*5
 base=np.array([(205,176,120),(183,158,118),(164,142,111)][idx])
 a=base[None,None,:]+bands[:,:,None]*np.array([10,9,8])+fine[:,:,None]
 bark=np.array([(86,72,56),(80,72,61),(73,69,62)][idx])
 a=np.where(interior[:,:,None],a,bark[None,None,:]+fine[:,:,None]*.8)
 # narrow radial timber splits
 crack=np.abs(np.sin(angle*8+gaussian_noise(seed+5,23)*.15))<.026
 crack &=rad>65
 a[crack]-=np.array([29,25,19])
 rgba=np.concatenate([np.uint8(np.clip(a,0,255)),np.uint8(alpha)[:,:,None]],axis=2)
 rgba[rgba[:,:,3]<20,3]=0
 rgba[rgba[:,:,3]==0,:3]=0
 return Image.fromarray(rgba,'RGBA')

items=[('ramillete_olivo',make_olive),('ramillete_encina',holm),('ramillete_cipres',cypress),('corte_tronco',cut)]
files=[]
for name,fn in items:
 for v in 'abc':
  p=OUT/f'{name}_{v}.png'
  if not p.exists():fn(v).save(p,optimize=True)
  files.append(p)

# Preview checkerboard behind each alpha cutout only in the diagnostic image.
sz=239;left=13;head=50;rh=268;gap=10
sheet=Image.new('RGB',(2*left+4*sz+3*gap,head+3*rh+10),(240,238,235))
d=ImageDraw.Draw(sheet);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
d.text((left,10),'L06 · Recursos botánicos RGBA · 12 variantes (prototipos)',font=f,fill=(36,36,36))
for c,(name,_) in enumerate(items):
 for row,v in enumerate('abc'):
  p=OUT/f'{name}_{v}.png';im=Image.open(p).convert('RGBA')
  cb=Image.new('RGBA',im.size,(220,220,216,255));dc=ImageDraw.Draw(cb)
  for yy in range(0,S,32):
   for xx in range(0,S,32):
    if (xx//32+yy//32)%2==0:dc.rectangle((xx,yy,xx+31,yy+31),fill=(188,188,184,255))
  composed=Image.alpha_composite(cb,im).convert('RGB').resize((sz,sz),Image.Resampling.LANCZOS)
  x=left+c*(sz+gap);y=head+row*rh
  sheet.paste(composed,(x,y));d.text((x,y+sz+3),f'{name} · {v}',font=f,fill=(44,43,42))
sheet.save(CTL/'preview_L06_botanica_12_alfa.jpg',quality=91)
# QA
manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.DictReader(f);rows=list(rd);fields=rd.fieldnames
assert sum(r['id_material'] in {x[0] for x in items} for r in rows)==12
qa={'lote':'L06_alfa','imagenes':[]}
for r in rows:
 if r['id_material'] not in {x[0] for x in items}:continue
 p=ROOT/r['ruta'];assert p.exists(),p
 im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512),(p,im.mode,im.size)
 arr=np.asarray(im,dtype=np.uint8);assert arr[0,0,3]==0 and np.any(arr[:,:,3]==0) and np.any(arr[:,:,3]>=245),(p,'invalid alpha')
 sha=hashlib.sha256(p.read_bytes()).hexdigest();r['estado']='generada';r['sha256']=sha
 r['notas']='RGBA no repetible. Olivo fuente imagen generada con limpieza de halo; encina/ciprés/tronco prototipos procedimentales. Revisar realismo y alpha en Godot.'
 qa['imagenes'].append({'archivo':p.name,'sha256':sha,'resolucion':im.size,'mode':im.mode,'alpha_zero':float((arr[:,:,3]==0).mean())})
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
catp=CTL/'catalogo_texturas_v2.json';cat=json.loads(catp.read_text('utf-8'))
for item in cat['materiales']:
 if item['clave_id'] not in {x[0] for x in items}:continue
 for v in 'abc':
  p=next(p for p in files if p.name==f"{item['clave_id']}_{v}.png")
  item['variantes'][v]['estado']='generada';item['variantes'][v]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  item['variantes'][v]['observaciones']='RGBA, no repetible. Prototipo botánico; validar detalle natural y halos a escala del juego.'
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n','utf-8')
(CTL/'verificacion_lote06_alfa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
count=sum(r['estado']=='generada' for r in rows)
assert count==294,count
plan=CTL/'plan_produccion_v2.md';lines=plan.read_text('utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[i]=f'**Progreso actual:** {count}/294 PNG generados como prototipos. Catálogo completo en cantidad. Pendiente validación artística, histórica y Blender: las fuentes L02-L16 en su mayoría procedimentales.'
plan.write_text('\n'.join(lines)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md';resume.write_text('''# Reanudar aquí — catálogo completo en número de archivos

Corte: 2026-11-07.

## Estado verificado
- 98 familias × tres variantes a/b/c: **294 PNG reales generados**.
- Todos los lotes L01–L16 tienen sus PNG, pero **todos siguen en estado `generada`, no `revisada` ni `entregada`**.
- Bordes y tamaño se verificaron en texturas que se repiten, alpha en recortes. Cada archivo tiene hash SHA-256.
- L06 incluye fotos generadas para olivo y prototipos procedimentales para encina, ciprés y corte tronco.

## Próximo objetivo de calidad (imprescindible)
1. Crear una escena real de Blender con planos, muros, cubiertas, árboles, UV físicas y cámara isométrica para evaluar nitidez y repetición.
2. Revisar si los materiales procedimentales L02–L16 cumplen el estilo fotorrealista solicitado; sustituir los demasiado gráficos o sintéticos.
3. Revisar L01 pizarra/paja/plomo que proceden de recortes de atlas de baja resolución efectiva.
4. Corregir posibles anacronismos y escala: teja florentina coppi/embrici, estampados decorativos locales, ladrillos y baldosas.
5. Inspeccionar recortes alfa sobre fondos claros y oscuros para quitar halos, especialmente ramilletes de olivo.

## Continuación
Adjuntar `paquete_completo_texturas_renacimiento_italiano.zip` en otro chat, leer `00_control/README.md` y `00_control/progreso_produccion.csv`, y comenzar validación técnica/visual. No asumir que 294 generados equivale a material final aprobado.
''',encoding='utf-8')
# Save olive source for reproducibility and generator script copy.
source=CTL/'fuentes_lote06';source.mkdir(exist_ok=True)
shutil.copy2(BASE/'a_clean_png_style_composite_image_on_a_transparent.png',source/'olivo_variantes_3x1_fuente.png')
lot=BASE/'lote_06_completo_madera_follaje.zip'
with zipfile.ZipFile(lot,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted((ROOT/'comunes/madera').iterdir()):
  if p.suffix=='.png' and ('vigas' in p.stem or 'tablas' in p.stem):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(OUT.glob('*.png')):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
 for p in sorted(CTL.iterdir()):
  if p.is_file() and (p.name in ('REANUDAR_AQUI.md','plan_produccion_v2.md','catalogo_texturas_v2.json','progreso_produccion.csv','README.md','especificaciones_originales.md') or 'L06' in p.name or 'botanica' in p.name):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(ROOT))
print('L06 complete, files',len(files),'produced',count,'lotzip',lot.stat().st_size)
