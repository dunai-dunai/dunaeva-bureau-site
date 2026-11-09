from PIL import Image, ImageDraw, ImageFilter
import numpy as np, sys
SP=''  # folder with bgmask.npy (flood fill of the white backdrop)
src=Image.open('source/04-stripe-chair.jpg').convert('RGB')
c=np.asarray(src,np.float32)
m=np.load(SP+'bgmask.npy')
fg=Image.fromarray(((~m)*255).astype(np.uint8)).convert('RGB')
ImageDraw.floodfill(fg,(600,700),(255,0,0))
keep=(np.asarray(fg)==[255,0,0]).all(2)
_l=c@np.array([0.3,0.59,0.11],np.float32); _s=c.max(2)-c.min(2)
yy=np.arange(c.shape[0])[:,None]
keep&=~((yy>1330)&(_l>150)&(_s<25)); keep[1300:, :230]=False
keep&=~((_l>232)&(_s<10))
keep&=~((yy>1240)&(_l>140)&(_s<22))
print('kept',keep.mean())
alpha=Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(0.7))
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
# black + milk, bronze frame
milk=np.array([239,230,214],np.float32); ink=np.array([22,21,20],np.float32)
t=x[...,None]
mk=ink+(milk-ink)*t
o3=Image.fromarray(np.clip(mk*(1-fm)+c*fm,0,255).astype(np.uint8)); o3.putalpha(alpha); o3.crop(bb).save('cutouts/chair-stripe-milk-brass.png')
sheet=Image.new('RGB',(W*2+60,H+40),'white')
for i,f in enumerate(['chair-stripe-bw-brass','chair-stripe-milk-brass']):
    p=Image.open(f'cutouts/{f}.png'); sheet.paste(p,(20+i*(W+20),20),p)
sheet.thumbnail((1400,1000)); sheet.save('cutouts/chair-stripe-milk-compare.jpg',quality=88)
