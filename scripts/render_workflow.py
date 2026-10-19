"""Render the selected white-background studio journal (requires Pillow)."""
from pathlib import Path
import argparse
import math
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parents[1]/'assets'
INK='#242127'; MUTED='#68636c'; BORDER='#dfdce3'; ACCENT='#8b7898'
parser=argparse.ArgumentParser()
parser.add_argument('--body-font', default='/System/Library/Fonts/Supplemental/Arial.ttf')
parser.add_argument('--display-font', default='/System/Library/Fonts/Supplemental/Courier New.ttf')
args=parser.parse_args()

def font(size,bold=False,pixel=False):
    f=ImageFont.truetype(args.display_font if pixel else args.body_font,size)
    if bold:
        try:
            axes=f.get_variation_axes();f.set_variation_by_axes([600 if a['name']==b'Weight' else a['default'] for a in axes])
        except (OSError,AttributeError): pass
    return f


WHITE=INK; LINE='#c9c2d0'; small=font(12)

def wrap_text(draw, text, font, width):
    lines=[]
    for word in text.split():
        if not lines or draw.textlength(lines[-1]+' '+word,font=font)>width:
            lines.append(word)
        else:
            lines[-1]+=' '+word
    return lines

def iteration_scene(progress):
    # Draw one shared circle at 3x resolution: arrows and marker use its tangent.
    scale=3; size=208; center=104; radius=82
    scene=Image.new('RGBA',(size*scale,size*scale))
    draw=ImageDraw.Draw(scene)
    def point(angle):
        return ((center+radius*math.cos(angle))*scale,(center+radius*math.sin(angle))*scale)
    draw.ellipse(((center-radius)*scale,(center-radius)*scale,(center+radius)*scale,(center+radius)*scale),outline='#a294ae',width=2*scale)
    for angle in (-math.pi/5,4*math.pi/5):
        tip=point(angle)
        tangent=(-math.sin(angle),math.cos(angle))
        normal=(math.cos(angle),math.sin(angle))
        back=(tip[0]-tangent[0]*10*scale,tip[1]-tangent[1]*10*scale)
        draw.polygon([tip,(back[0]+normal[0]*4*scale,back[1]+normal[1]*4*scale),(back[0]-normal[0]*4*scale,back[1]-normal[1]*4*scale)],fill='#695176')
    for j in range(3):
        xx=center-56+j*10; yy=center-33+j*8
        draw.rounded_rectangle((xx*scale,yy*scale,(xx+90)*scale,(yy+52)*scale),radius=6*scale,fill='#ffffff',outline='#d4cedb' if j<2 else '#85728f',width=2*scale)
        if j==2:
            for offset,length in ((16,62),(28,38),(40,50)):
                draw.line(((xx+12)*scale,(yy+offset)*scale,(xx+12+length)*scale,(yy+offset)*scale),fill='#74637e' if offset==16 else LINE,width=2*scale)
    px,py=point(-math.pi/2+2*math.pi*progress)
    draw.ellipse((px-4*scale,py-4*scale,px+4*scale,py+4*scale),fill=WHITE)
    return scene.resize((size,size),Image.Resampling.LANCZOS)

def line(d, pts, fill=WHITE, width=2):
    d.line(pts,fill=fill,width=width,joint='curve')

def circle(d,x,y,r,fill,outline=None,width=1):
    d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=width)

def icon(im,d,i,x,y,p,active):
    # Each scene is drawn explicitly, using the site's restrained line style.
    if i==0:
        d.rounded_rectangle((x-110,y-61,x+48,y+65),radius=10,outline=LINE,width=2)
        d.rounded_rectangle((x-72,y-69,x+10,y-51),radius=8,fill='#efedf2',outline='#a49aab')
        for j in range(3):
            yy=y-27+j*30
            d.rounded_rectangle((x-87,yy-7,x-73,yy+7),radius=3,outline='#a59bab')
            line(d,[(x-58,yy),(x+24-j*12,yy)],LINE)
            if not active or p>(j+1)/4:
                line(d,[(x-84,yy),(x-80,yy+3),(x-75,yy-4)],WHITE)
        for r in (28,16,5):circle(d,x+103,y+4,r,None,'#a295ad' if r!=5 else WHITE,2)
        line(d,[(x+55,y+4),(x+70,y+4)],LINE)
        if active:
            a=p*math.pi*2
            circle(d,x+103+math.cos(a)*28,y+4+math.sin(a)*28,3,WHITE)
    elif i==1:
        d.rounded_rectangle((x-139,y-63,x+139,y+65),radius=11,outline='#8c7b98',width=2)
        line(d,[(x-139,y-39),(x+139,y-39)],LINE)
        for j in range(3):circle(d,x-122+j*11,y-51,2,'#a496ae')
        d.rounded_rectangle((x-48,y-56,x+48,y-47),radius=5,fill='#c8c8c8')
        d.rounded_rectangle((x-120,y-24,x-37,y+47),radius=5,outline=LINE)
        for j in range(4):line(d,[(x-105,y-10+j*13),(x-57,y-10+j*13)],'#a69aae')
        for yy in (-18,1):line(d,[(x-15,y+yy),(x+108,y+yy)],'#9c8ca7',3)
        for xx in (-15,53):d.rounded_rectangle((x+xx,y+18,x+xx+55,y+46),radius=5,fill='#f0ecf4',outline=LINE)
        q=p if active else .55
        xx=x-110+q*215; yy=y+26
        d.polygon([(xx,yy),(xx,yy+20),(xx+5,yy+15),(xx+11,yy+14)],fill=WHITE)
    elif i==2:
        line(d,[(x-136,y-60),(x-136,y+62),(x+142,y+62)],LINE)
        for yy in (-30,0,30):line(d,[(x-136,y+yy),(x+141,y+yy)],'#eeebf1',1)
        pts=[(x-123,y+39),(x-85,y+20),(x-48,y+27),(x-9,y-13),(x+32,y-1),(x+77,y-37),(x+127,y-46)]
        line(d,pts,'#9b82ae',3)
        q=p if active else .65
        k=min(int(q*(len(pts)-1)),len(pts)-2); f=q*(len(pts)-1)-k
        xx=pts[k][0]+(pts[k+1][0]-pts[k][0])*f
        yy=pts[k][1]+(pts[k+1][1]-pts[k][1])*f
        line(d,[(xx,y-58),(xx,y+62)],'#cec4d6',1)
        circle(d,xx,yy,8,'#ede5f3');circle(d,xx,yy,4,WHITE)
        d.rounded_rectangle((x+63,y+39,x+139,y+57),radius=8,fill='#eae3ef')
        d.text((x+101,y+48),'evaluate',font=small,fill='#5e486f',anchor='mm')
    else:
        scene=iteration_scene(p if active else 0)
        im.paste(scene,(int(x-104),int(y-104)),scene)

ns={'icon':icon,'wrap_text':wrap_text}
TITLES=['Define the promise','Ship a complete slice','Measure what matters','Improve with evidence']
PRINCIPLES=[
 ('Context before complexity.',"Start with the user's problem and the constraints of the system."),
 ('Explicit boundaries.','Give models and tools clear contracts, permissions, budgets, and fallbacks.'),
 ('Evidence over intuition.','Use evaluations and production feedback to improve quality, latency, and cost.'),
 ('Ownership after launch.','Build in the documentation, observability, and operational clarity a team needs.'),
]

def txt(d,xy,s,size,color=INK,bold=False,pixel=False,anchor='lt'):
    d.text(xy,s,font=font(size,bold,pixel),fill=color,anchor=anchor)

def paragraph(d,x,y,s,width,size=16,color=MUTED,leading=None):
    rows=ns['wrap_text'](d,s,font(size),width)
    for j,row in enumerate(rows):txt(d,(x,y+j*(leading or size+6)),row,size,color)
    return len(rows)*(leading or size+6)

def art(im,i,cx,cy,progress,active,scale=1):
    layer=Image.new('RGB',(340,208),'white')
    ns['icon'](layer,ImageDraw.Draw(layer),i,170,104,progress,active)
    if scale!=1:layer=layer.resize((round(340*scale),round(208*scale)),Image.Resampling.LANCZOS)
    im.paste(layer,(round(cx-layer.width/2),round(cy-layer.height/2)))

def journal(frame):
    im=Image.new('RGB',(960,800),'white');d=ImageDraw.Draw(im)
    active=int(frame/96*4);p=(frame/96*4)%1
    d.line((51,58,51,657),fill=BORDER,width=2)
    for i in range(4):
        y=12+i*196
        if i:d.line((98,y-4,936,y-4),fill='#e8e4ec',width=1)
        d.ellipse((31,y+22,71,y+62),fill=INK if active==i else '#f2eff5')
        txt(d,(51,y+42),f'0{i+1}',18,'#ffffff' if active==i else ACCENT,pixel=True,anchor='mm')
        txt(d,(104,y+21),TITLES[i],25,bold=True)
        txt(d,(104,y+67),PRINCIPLES[i][0],18,bold=True)
        paragraph(d,104,y+98,PRINCIPLES[i][1],473,16,MUTED,24)
        art(im,i,770,y+91,p,active==i,.8)
        if i==active:
            yy=y+68+p*108
            d.ellipse((48,yy-3,54,yy+3),fill=ACCENT)
            d.line((104,y+172,104+470*p,y+172),fill='#b7a7c2',width=2)
    return im

for name,renderer in [('workflow',journal)]:
    frames=[renderer(i) for i in range(96)]
    frames[0].save(OUT/f'{name}.png')
    w,h=frames[0].size
    sample=Image.new('RGB',(w,h*4))
    for j in range(4):sample.paste(frames[j*24],(0,h*j))
    palette=sample.quantize(colors=96)
    indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
    indexed[0].save(OUT/f'{name}.gif',save_all=True,append_images=indexed[1:],duration=90,loop=0,optimize=True,disposal=1)
    print(name,round((OUT/f'{name}.gif').stat().st_size/1024),'KB')
