from PIL import Image, ImageDraw, ImageFilter
import numpy as np, sys
SP='/tmp/claude-0/-home-user-dunaeva-bureau-site/a21c98c5-6b86-5b58-a723-768b8d381088/scratchpad/'
src=Image.open('source/04-stripe-chair.jpg').convert('RGB')
c=np.asarray(src,np.float32)
m=np.load(SP+'bgmask.npy')
fg=Image.fromarray(((~m)*255).astype(np.uint8)).convert('RGB')
ImageDraw.floodfill(fg,(600,700),(255,0,0))
keep=(np.asarray(fg)==[255,0,0]).all(2)
_l=c@np.array([0.3,0.59,0.11],np.float32); _s=c.max(2)-c.min(2)
yy=np.arange(c.shape[0])[:,None]
keep&=~((yy>1330)&(_l>150)&(_s<25)); keep[1300:, :230]=False
print('kept',keep.mean())
alpha=Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
bb=alpha.getbbox(); print(bb)
rgba=src.copy(); rgba.putalpha(alpha); rgba.crop(bb).save('cutouts/chair-stripe-original.png')
lum=c@np.array([0.3,0.59,0.11],np.float32)
x=np.clip((lum-40)/(225-40),0,1); x=x*x*(3-2*x); v=8+x*239
bw=np.stack([v,v,v],2)
out=Image.fromarray(np.clip(bw,0,255).astype(np.uint8)); out.putalpha(alpha); out.crop(bb).save('cutouts/chair-stripe-bw.png')
r,b=c[...,0],c[...,2]; sat=c.max(2)-c.min(2)
frame=(lum>40)&(lum<125)&(r>=b+12)&(sat<70)
fm=np.asarray(Image.fromarray((frame*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1)),np.float32)[...,None]/255
o2=Image.fromarray(np.clip(bw*(1-fm)+c*fm,0,255).astype(np.uint8)); o2.putalpha(alpha); o2.crop(bb).save('cutouts/chair-stripe-bw-brass.png')
W,H=bb[2]-bb[0],bb[3]-bb[1]
sheet=Image.new('RGB',(W*3+80,H+40),'white')
for i,f in enumerate(['chair-stripe-original','chair-stripe-bw','chair-stripe-bw-brass']):
    p=Image.open(f'cutouts/{f}.png'); sheet.paste(p,(20+i*(W+20),20),p)
sheet.thumbnail((1800,1000)); sheet.save('cutouts/chair-stripe-compare.jpg',quality=88)
