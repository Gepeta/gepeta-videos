import sys
from PIL import Image
ts=sys.argv[1].split(','); cols=int(sys.argv[2]) if len(sys.argv)>2 else 6; w=int(sys.argv[3]) if len(sys.argv)>3 else 300
h=w*16//9; rows=(len(ts)+cols-1)//cols
s=Image.new('RGB',(w*cols,h*rows))
for i,t in enumerate(ts): s.paste(Image.open(f'prev_{t}.jpg').resize((w,h)),((i%cols)*w,(i//cols)*h))
s.save('sheet.jpg',quality=86)
