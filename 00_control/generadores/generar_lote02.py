from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, csv, json, hashlib, zipfile
from scipy.ndimage import gaussian_filter

BASE=Path('/mnt/data'); WORK=BASE/'texturas_renacimiento_italiano'; CTL=WORK/'00_control';OUT=WORK/'comunes'/'muros'
OUT.mkdir(parents=True,exist_ok=True)
S=512
Y,X=np.mgrid[0:S,0:S]

def noise(seed, sigma=12):
 r=np.random.default_rng(seed).normal(size=(S,S)).astype('float32')
 a=gaussian_filter(r,sigma=sigma,mode='wrap')
 return (a-a.mean()) / max(float(a.std()),1e-5)

def surface(seed):
 return 1.0*noise(seed,2.5)+0.48*noise(seed+111,9)+0.29*noise(seed+222,31)+0.16*noise(seed+333,65)

def clip(a):return np.uint8(np.clip(a,0,255))

def seamless(ar,border=16):
 a=ar.astype('float32').copy()
 for j in range(border):
  t=(1+np.cos(np.pi*j/border))/2
  m=(a[:,j].copy()+a[:,S-1-j].copy())/2
  a[:,j]=a[:,j]*(1-t)+m*t
  a[:,S-1-j]=a[:,S-1-j]*(1-t)+m*t
 for j in range(border):
  t=(1+np.cos(np.pi*j/border))/2
  m=(a[j].copy()+a[S-1-j].copy())/2
  a[j]=a[j]*(1-t)+m*t
  a[S-1-j]=a[S-1-j]*(1-t)+m*t
 out=clip(a)
 assert np.abs(out[:,0].astype(int)-out[:,-1].astype(int)).max()<=1
 assert np.abs(out[0].astype(int)-out[-1].astype(int)).max()<=1
 return out

def add_grains(color, base_noise, micro=2.5):
 return np.stack([color[c]+base_noise*micro for c in range(3)],axis=2).astype('float32')

def plaster(v, very_old=False):
 idx='abc'.index(v); seed=905+idx*100+(500 if very_old else 0)
 shades=[(232,225,205),(219,208,188),(208,193,167)] if very_old else [(236,231,218),(228,221,207),(219,211,196)]
 n=surface(seed)
 arr=add_grains(shades[idx],n,3.0 if idx==0 else 4.3)
 dark=(noise(seed+30,38)*0.68+noise(seed+56,76)*0.48)
 dirt=({0:1.9,1:5.5,2:10.0}[idx])*(np.clip(dark,0,2)/2)
 arr-=dirt[:,:,None]*np.array([1,1.03,1.08])[None,None,:]
 spots=noise(seed+21,2.0)>({0:2.85,1:2.45,2:2.15}[idx])
 arr[spots]*=0.87
 if very_old:
  # Irregular plaster loss: the underlying brick is a distinct real material layer,
  # not cartoon-drawn cracks or figurative painting.
  under=brick(v,'toscano',seed_shift=233)*.90
  patch=noise(602+idx,25)*.62+noise(620+idx,48)*.34+noise(637+idx,8)*.28+noise(639+idx,2)*.12
  mask=patch>np.quantile(patch,[.955,.90,.82][idx])
  edge=gaussian_filter(mask.astype('float32'),1.7,mode='wrap')
  # thin soot line around exposed plaster edge
  rim=np.clip(gaussian_filter(mask.astype('float32'),4,mode='wrap')-edge,0,1)
  arr-=rim[:,:,None]*14
  arr=arr*(1-edge[:,:,None])+under*edge[:,:,None]
 return arr

def brick(v,kind,seed_shift=0):
 idx='abc'.index(v); lomb=kind=='lombardo'; n=surface(220+idx*88+(1200 if lomb else 0)+seed_shift)
 # Five long bricks across 1.5 m ~= 0.30 m, 24 courses ~= 0.0625 m.
 # Alternating running bond with periodic, consistent width.
 bw=S/5.0; bh=S/24.0
 row=(Y//bh).astype('int32')
 offset=(row%2)*(bw/2)
 xx=np.mod(X+offset,bw)
 yy=np.mod(Y,bh)
 col=np.floor((X+offset)/bw).astype('int32')%5
 rng=np.random.default_rng(218 if not lomb else 283)
 varied=rng.normal(size=(24,5)); varied=(varied-varied.mean())/max(float(varied.std()),1e-3)
 bv=varied[row%24,col]
 base=np.array([(178,95,67),(163,78,54),(144,69,52)][idx] if not lomb else [(160,69,56),(143,56,46),(128,52,44)][idx],dtype='float32')
 base_var = bv[:,:,None]*np.array([10.3,9.3,8.1])[None,None,:]
 a=base[None,None,:]+base_var+ n[:,:,None]*np.array([5.7,4.9,4.2])[None,None,:]
 # Mortar under thin bricks, muted pale lime joints; edges organic, not thick black outlines.
 rough=noise(1593+idx*200+seed_shift,1.0)
 mx=np.minimum(xx,bw-xx)
 my=np.minimum(yy,bh-yy)
 mortar=(mx < (2.2 if not lomb else 1.4)+rough*.33) | (my < (1.5 if not lomb else 1.0)+rough*.2)
 mortar_color=np.array((155,145,129) if not lomb else (144,132,124),dtype='float32')
 mor=mortar_color[None,None,:]+n[:,:,None]*3.0
 a=np.where(mortar[:,:,None],mor,a)
 # Very subtle worn surface depressions, blotching, and small erosion marks.
 dirt=noise(700+seed_shift+idx*4,18)
 a-=np.clip(dirt,0,2)[:,:,None]*(2+idx*4)
 return a

def adobe(v):
 idx='abc'.index(v);n=surface(340+idx*58)
 base=np.array([(187,150,104),(177,136,95),(158,121,88)][idx],dtype='float32')
 a=base[None,None,:]+ n[:,:,None]*[7,6,5]
 # Blocks 40 ×20 cm under the mud coat, 5 columns ×10 courses per 2 m.
 bw=S/5;bh=S/10;row=np.floor(Y/bh).astype(int)
 xx=np.mod(X+(row%2)*(bw/2),bw)
 yy=np.mod(Y,bh)
 joints=np.minimum(np.minimum(xx,bw-xx)/4.0,np.minimum(yy,bh-yy)/3.0)
 # Faint seams, never hard drawn outlines.
 a-=np.clip(1.0-joints,0,1)[:,:,None]*np.array([10,9,8])[None,None,:]
 # Natural straw fibers—tiny brown-yellow flecks, not stylized linear decorations.
 straw=noise(1390+idx*11,.65)>2.15
 a[straw] +=np.array([8,7,-2])
 erosion=np.clip(noise(893+idx*5,26),0,2)/2
 a-=erosion[:,:,None]*(4+idx*5)
 return a

def masonry(v):
 idx='abc'.index(v);rng=np.random.default_rng(5000)
 # Toroidally periodic warped Voronoi polygon field, 20-50 cm stones across a 2×2 m area.
 centers=[]
 for ry in range(6):
  for rx in range(6):
   centers.append(((rx+.52+rng.uniform(-.23,.23))*S/6,(ry+.49+rng.uniform(-.22,.22))*S/6))
 centers=np.array(centers,dtype='float32')
 # irregularize boundaries with multi-scale smoothly varied displacement
 xx=np.mod(X+noise(303,13)*3+noise(307,37)*4,S).astype('float32')
 yy=np.mod(Y+noise(313,15)*3+noise(317,43)*3,S).astype('float32')
 dist=[]
 for cx,cy in centers:
  dx=np.minimum(np.abs(xx-cx),S-np.abs(xx-cx))
  dy=np.minimum(np.abs(yy-cy),S-np.abs(yy-cy))
  dist.append(dx*dx+dy*dy)
 dstack=np.stack(dist,axis=0)
 ids=np.argmin(dstack,axis=0)
 ds=np.partition(dstack,1,axis=0)
 edge=np.sqrt(ds[1])-np.sqrt(ds[0])
 rng=np.random.default_rng(5333)
 shade=rng.normal(0,1,size=len(centers)).astype('float32')*10
 tint=rng.normal(0,1,size=len(centers)).astype('float32')*2
 cols=shade[:,None]*np.array([1,0.99,0.95])[None,:]+tint[:,None]*np.array([1,0.10,-0.40])[None,:]
 base=np.array([(123,119,111),(114,110,104),(105,100,94)][idx],dtype='float32')
 n=surface(930+idx*30)
 a=base[None,None,:]+cols[ids]+n[:,:,None]*[7,7,6]
 # Pale, rough lime mortar in irregular joints; stone edges are not black ink outlines.
 mortar=(edge<(4.0+idx*.35)).astype('float32')
 soft=gaussian_filter(mortar,.85,mode='wrap')
 mort=np.array((114,110,104),dtype='float32')[None,None,:]+n[:,:,None]*3
 a=a*(1-soft[:,:,None])+mort*soft[:,:,None]
 # Water-stain weathering and dispersed mineral blooms.
 dirt=noise(1993+idx*15,23)
 a-=np.maximum(dirt,0)[:,:,None]*(3+idx*4)
 return a

TYPES=[('enlucido_claro',lambda v:plaster(v,False)),
       ('enlucido_desconchado',lambda v:plaster(v,True)),
       ('adobe',adobe),
       ('ladrillo_toscano',lambda v:brick(v,'toscano')),
       ('ladrillo_lombardo',lambda v:brick(v,'lombardo')),
       ('mamposteria_zocalo',masonry)]

produced=[]
for typ,fn in TYPES:
 for v in 'abc':
  img=seamless(fn(v))
  name=f'{typ}_{v}.png';path=OUT/name
  Image.fromarray(img,'RGB').save(path,optimize=True)
  produced.append(path)

# Mosaic previews: material sheets (6 columns, 3 states), all 18 distinct images.
thumb=209;gap=7;left=12;top=60;row_h=252
sheet=Image.new('RGB',(left*2+6*thumb+5*gap,top+3*row_h+12),(239,238,234))
d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
sub=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
d.text((left,10),'L02 · Muros renacentistas · prototipos procedurales realistas',font=font,fill=(35,36,37))
for col,(typ,_) in enumerate(TYPES):
 for row,v in enumerate('abc'):
  im=Image.open(OUT/f'{typ}_{v}.png').resize((thumb,thumb),Image.Resampling.LANCZOS)
  x=left+col*(thumb+gap);y=top+row*row_h
  sheet.paste(im,(x,y));d.text((x,y+thumb+4),typ[:21]+f' · {v}',font=sub,fill=(46,47,45))
sheet.save(CTL/'preview_L02_18_texturas.jpg',quality=90)
for p in produced:
 im=Image.open(p)
 mosaic=Image.new('RGB',(1536,1536))
 for y in range(3):
  for x in range(3):mosaic.paste(im,(x*512,y*512))
 mosaic.resize((768,768),Image.Resampling.LANCZOS).save(CTL/f'preview_{p.stem}_mosaico3x3.jpg',quality=85)

manifest=CTL/'progreso_produccion.csv'
with manifest.open(encoding='utf-8-sig',newline='') as f:
 dr=csv.DictReader(f);rows=list(dr);fields=dr.fieldnames
assert sum(r['lote']=='L02' for r in rows)==18
for r in rows:
 if r['lote']!='L02':continue
 f=WORK/r['ruta']
 assert f.exists(),f
 r['estado']='generada'
 r['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
 r['notas']='Prototipo procedural de base; verificación de bordes y mosaico 3×3. No certificado fotográfico; requiere contraste visual y prueba Blender.'
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
 cw=csv.DictWriter(f,fieldnames=fields);cw.writeheader();cw.writerows(rows)
cat=CTL/'catalogo_texturas_v2.json'
data=json.loads(cat.read_text('utf-8'))
for item in data['materiales']:
 for v in 'abc':
  fn=f"{item['clave_id']}_{v}.png"
  if (OUT/fn) not in produced:continue
  var=item['variantes'][v];var['estado']='generada';var['sha256']=hashlib.sha256((OUT/fn).read_bytes()).hexdigest()
  var['observaciones']='Prototipo procedimental (no fuente fotográfica). Material con escala arquitectónica y bordes emparejados. Pendiente prueba visual Blender.'
cat.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print('manifest total generated',sum(r['estado']=='generada' for r in rows))
# quality record
qa={'lote':'L02','tipo':'prototipos procedimentales','imagenes':[]}
for p in produced:
 a=np.asarray(Image.open(p),dtype='int16')
 mx=int(max(np.abs(a[:,0]-a[:,-1]).max(),np.abs(a[0]-a[-1]).max()))
 assert mx<=1,(p,mx)
 qa['imagenes'].append({'archivo':p.name,'resolucion':'512x512','diferencia_borde_max':mx,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(CTL/'verificacion_lote02.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
resume=CTL/'REANUDAR_AQUI.md'
resume.write_text('''# Reanudar aquí — control de producción\n\nCorte: 2026-11-07.\n\n## Estado verificado\n- 98 familias; 294 PNG previstos (a/b/c).\n- **L01 completo como prototipos:** 15 PNG en `comunes/tejados`. Teja roja y oscura: fuente de imagen individual; pizarra, paja y plomo: fuente recortada de atlas (menor detalle real).\n- **L02 completo como prototipos:** 18 PNG en `comunes/muros`, generados por procedimiento, no por fotografía; deben validarse por realismo a escala del juego.\n- **33/294 PNG físicamente creados**, todos 512x512, pruebas 3x3 y comprobación del borde repetible; 261 PNG pendientes.\n- Todos **pendientes de validación final** en modelos y render Blender (especialmente escala de piezas y repetición visible).\n\n## Próxima tarea concreta\n- Inspeccionar en juego L01 + L02; sustituir cualquier textura cuyo aspecto sea demasiado procedural, fuente de atlas de baja nitidez o estructura de piezas a escala incorrecta.\n- Continuar L03, comunes/piedra_noble (21 PNG), empezando `piedra_serena_sillares_a`.\n- Actualizar progreso y archivo ZIP tras cada lote.\n\n## Continuación en otro chat\nAdjunta `paquete_continuidad_L01_L02.zip`, abre `00_control/REANUDAR_AQUI.md` y sigue desde L03, sin rehacer L01 ni L02 salvo ajustes de calidad solicitados.\n''','utf-8')
plan=CTL/'plan_produccion_v2.md'
lines=plan.read_text('utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('**Progreso actual:**'):
  lines[i]='**Progreso actual:** L01: 15 PNG, L02: 18 PNG (prototipos). Total 33/294, 261 pendientes. Se han hecho pruebas 3×3 y se han verificado bordes, pero no existe validación Blender ni histórica final; L02 es procedimental.'
plan.write_text('\n'.join(lines)+'\n','utf-8')
zipname=BASE/'lote_02_comunes_muros.zip'
with zipfile.ZipFile(zipname,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.glob('*.png')):z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
 for p in sorted(CTL.iterdir()):
  if 'L01' in p.name or any(mat in p.name for mat in ['teja_arabe_roja','teja_oscura_vieja','pizarra_liguria','paja_techumbre','plomo_cupula']):continue
  z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
full=BASE/'paquete_continuidad_L01_L02.zip'
with zipfile.ZipFile(full,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(WORK.rglob('*')):
  if p.is_file():z.write(p,Path('texturas_renacimiento_italiano')/p.relative_to(WORK))
print('L02 zip',zipname,zipname.stat().st_size,'continuity',full,full.stat().st_size)
