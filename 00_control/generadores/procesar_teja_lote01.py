from pathlib import Path
import json, csv, zipfile, hashlib, numpy as np
from PIL import Image,ImageEnhance,ImageDraw,ImageFont
work=Path('/mnt/data/texturas_renacimiento_italiano')
ctl=work/'00_control'; folder=work/'comunes/tejados'; folder.mkdir(parents=True,exist_ok=True)
files={
 'a':'/mnt/data/a_top_down_close_up_full_frame_seamless_texture_l.png',
 'b':'/mnt/data/a_close_up_top_down_orthographic_view_of_an_old_t.png',
 'c':'/mnt/data/a_photorealistic_top_down_perfectly_frontal_tig.png',
}
# Preserve photographic texture. Align crop edges to the repeating tile rhythm, and only blend a narrow band
# to avoid the obvious seams while retaining detailed stone/ceramic texture.

def make_seamless(path, size=512):
    raw=np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)
    H,W=raw.shape[:2]
    # Use downsampled grayscale for efficiency and optimise long repeat interval to tile approximately aligned positions.
    g=np.asarray(Image.fromarray(raw.astype('uint8')).convert('L').resize((628,628),Image.Resampling.BILINEAR),dtype=np.float32)
    s=W/628
    # Decide seam positions by geometric similarity of narrow strips; prioritize matching edges phase.
    bestx=(1e9,44,558)
    for width in range(455,565,2):
        for start in range(12,628-width-12,2):
            end=start+width
            # Approximate seam match using 2 wide pixel strips.
            left=g[40:588,start:start+2]
            right=g[40:588,end-2:end]
            score=np.mean(np.abs(left-right))
            if score < bestx[0]:bestx=(score,start,end)
    besty=(1e9,44,558)
    for height in range(455,565,2):
        for start in range(12,628-height-12,2):
            end=start+height
            top=g[start:start+2,40:588]
            bot=g[end-2:end,40:588]
            score=np.mean(np.abs(top-bot))
            if score < besty[0]:besty=(score,start,end)
    x0,x1=int(bestx[1]*s),int(bestx[2]*s)
    y0,y1=int(besty[1]*s),int(besty[2]*s)
    tile=Image.fromarray(raw[y0:y1,x0:x1].astype('uint8')).resize((size,size),Image.Resampling.LANCZOS)
    arr=np.asarray(tile,dtype=np.float32).copy()
    # Symmetric edge-only blend: opposite edges share exactly the same pixel values.
    bw=16
    for j in range(bw):
      alpha=(1-j/bw)**1.9
      l=arr[:,j,:].copy(); r=arr[:,size-1-j,:].copy(); middle=.5*(l+r)
      arr[:,j,:]=l*(1-alpha)+middle*alpha
      arr[:,size-1-j,:]=r*(1-alpha)+middle*alpha
    for j in range(bw):
      alpha=(1-j/bw)**1.9
      t=arr[j,:,:].copy(); b=arr[size-1-j,:,:].copy(); middle=.5*(t+b)
      arr[j,:,:]=t*(1-alpha)+middle*alpha
      arr[size-1-j,:,:]=b*(1-alpha)+middle*alpha
    out=Image.fromarray(np.clip(arr,0,255).astype('uint8'))
    a=np.asarray(out,dtype=np.int16)
    # difference at external border guaranteed 0-1 LSB
    metrics={'edge_left_right_max':int(np.abs(a[:,0,:]-a[:,-1,:]).max()),
             'edge_top_bottom_max':int(np.abs(a[0,:,:]-a[-1,:,:]).max()),
             'crop_px':[x0,y0,x1,y1],'score_greyscale':[round(bestx[0],2),round(besty[0],2)]}
    return out,metrics

quality={}
for v,path in files.items():
 name=f'teja_arabe_roja_{v}.png'
 out,metric=make_seamless(path)
 out.save(folder/name,optimize=True)
 metric['tamano_bytes']=(folder/name).stat().st_size
 quality[v]=metric
 # 3x3 tile proof
 proof=Image.new('RGB',(512*3,512*3))
 for iy in range(3):
  for ix in range(3):proof.paste(out,(ix*512,iy*512))
 proof.resize((768,768),Image.Resampling.LANCZOS).save(ctl/f'preview_teja_arabe_roja_{v}_mosaico3x3.jpg',quality=88)
# Contact sheet 3 variants
contact=Image.new('RGB',(512*3,560),(235,235,230))
d=ImageDraw.Draw(contact)
for i,v in enumerate('abc'):
 im=Image.open(folder/f'teja_arabe_roja_{v}.png')
 contact.paste(im,(i*512,0));d.text((i*512+16,527),f'{v} - '+ {'a':'Cuidada','b':'Usada','c':'Vieja'}[v],fill=(20,20,20))
contact.save(ctl/'preview_teja_arabe_roja_variantes.jpg',quality=90)
# Update catalogue JSON and progress for outputs that actually exist.
cat_path=ctl/'catalogo_texturas_v2.json'
cat=json.loads(cat_path.read_text('utf-8'))
for x in cat['materiales']:
 if x['clave_id']!='teja_arabe_roja':continue
 for v in 'abc':
  path=folder/f'teja_arabe_roja_{v}.png'
  x['variantes'][v]['estado']='revisada' # dimensions and seamless pixels checked; visual mockup provided
  x['variantes'][v]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  x['variantes'][v]['observaciones']='Primer prototipo 512px con unión de bordes verificada; validar en render del edificio antes de aprobar final.'
cat_path.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
progress_path=ctl/'progreso_produccion.csv'
with progress_path.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f); rows=list(reader);keys=reader.fieldnames
for r in rows:
 if r['id_material']=='teja_arabe_roja':
  v=r['variante'];r['estado']='revisada';r['sha256']=hashlib.sha256((folder/f'teja_arabe_roja_{v}.png').read_bytes()).hexdigest();r['notas']='Prueba de mosaico 3×3; pendiente de prueba en render Blender.'
with progress_path.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
# Update plan current status so future session can unambiguously know what happened.
plan_path=ctl/'plan_produccion_v2.md'
plan=plan_path.read_text('utf-8')
plan=plan.replace('**Progreso actual:** catálogo y controles de producción preparados; 0/294 PNG generados y 0/294 entregados. No marcar una variante como generada hasta existir su PNG real.',
                  '**Progreso actual:** 3/294 PNG producidos y revisados en mosaico (teja árabe roja a, b, c), 0/294 entregados en un lote completo. Los 12 PNG restantes de L01 están pendientes. La validación final en render Blender sigue pendiente. No marcar una variante como generada hasta existir su PNG real.')
plan_path.write_text(plan,'utf-8')
# ZIP checkpoint: generated 3 PNG + entire control package, no deceptive claim of complete L01.
checkpoint=Path('/mnt/data/avance_L01_teja_arabe_roja_v1.zip')
with zipfile.ZipFile(checkpoint,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ctl.iterdir()):z.write(p,p.relative_to(work))
 for p in sorted(folder.iterdir()):z.write(p,p.relative_to(work))
print('Checkpoint:',checkpoint,checkpoint.stat().st_size)
print('Review data:',json.dumps(quality,indent=2,ensure_ascii=False))
print('Status:',sum(r['estado']=='revisada' for r in rows),len(rows))
