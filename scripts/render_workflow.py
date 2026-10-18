"""Render the README workflow illustration (Pillow; optional local font paths)."""
from pathlib import Path
import argparse
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

parser=argparse.ArgumentParser()
parser.add_argument('--body-font', default='/System/Library/Fonts/Supplemental/Arial.ttf')
parser.add_argument('--display-font', default='/System/Library/Fonts/Supplemental/Courier New.ttf')
args=parser.parse_args()
OUT=Path(__file__).resolve().parents[1]/'assets'
W,H=960,756
WHITE='#eeeeee'; MUTED='#949494'; LINE='#434047'
body=ImageFont.truetype(args.body_font,22)
caption=ImageFont.truetype(args.body_font,16)
principle_font=ImageFont.truetype(args.body_font,18)
number=ImageFont.truetype(args.display_font,22)
small=ImageFont.truetype(args.body_font,12)
positions=[(16,16),(490,16),(16,390),(490,390)]
titles=['Define the promise','Ship a complete slice','Measure what matters','Improve with evidence']
principles=[
    ('Context before complexity.', "Start with the user's problem and the constraints of the system."),
    ('Explicit boundaries.', 'Give models and tools clear contracts, permissions, budgets, and fallbacks.'),
    ('Evidence over intuition.', 'Use evaluations and production feedback to improve quality, latency, and cost.'),
    ('Ownership after launch.', 'Build in the documentation, observability, and operational clarity a team needs.'),
]

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
    draw.ellipse(((center-radius)*scale,(center-radius)*scale,(center+radius)*scale,(center+radius)*scale),outline='#95869f',width=2*scale)
    for angle in (-math.pi/5,4*math.pi/5):
        tip=point(angle)
        tangent=(-math.sin(angle),math.cos(angle))
        normal=(math.cos(angle),math.sin(angle))
        back=(tip[0]-tangent[0]*10*scale,tip[1]-tangent[1]*10*scale)
        draw.polygon([tip,(back[0]+normal[0]*4*scale,back[1]+normal[1]*4*scale),(back[0]-normal[0]*4*scale,back[1]-normal[1]*4*scale)],fill='#d0c5d9')
    for j in range(3):
        xx=center-56+j*10; yy=center-33+j*8
        draw.rounded_rectangle((xx*scale,yy*scale,(xx+90)*scale,(yy+52)*scale),radius=6*scale,fill='#17141a',outline='#49434f' if j<2 else '#a79caf',width=2*scale)
        if j==2:
            for offset,length in ((16,62),(28,38),(40,50)):
                draw.line(((xx+12)*scale,(yy+offset)*scale,(xx+12+length)*scale,(yy+offset)*scale),fill='#aaa1b3' if offset==16 else LINE,width=2*scale)
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
        d.rounded_rectangle((x-72,y-69,x+10,y-51),radius=8,fill='#27262a',outline='#77727d')
        for j in range(3):
            yy=y-27+j*30
            d.rounded_rectangle((x-87,yy-7,x-73,yy+7),radius=3,outline='#848087')
            line(d,[(x-58,yy),(x+24-j*12,yy)],LINE)
            if not active or p>(j+1)/4:
                line(d,[(x-84,yy),(x-80,yy+3),(x-75,yy-4)],WHITE)
        for r in (28,16,5):circle(d,x+103,y+4,r,None,'#8b8292' if r!=5 else WHITE,2)
        line(d,[(x+55,y+4),(x+70,y+4)],LINE)
        if active:
            a=p*math.pi*2
            circle(d,x+103+math.cos(a)*28,y+4+math.sin(a)*28,3,WHITE)
    elif i==1:
        d.rounded_rectangle((x-139,y-63,x+139,y+65),radius=11,outline='#7b747f',width=2)
        line(d,[(x-139,y-39),(x+139,y-39)],LINE)
        for j in range(3):circle(d,x-122+j*11,y-51,2,'#827a8a')
        d.rounded_rectangle((x-48,y-56,x+48,y-47),radius=5,fill='#c8c8c8')
        d.rounded_rectangle((x-120,y-24,x-37,y+47),radius=5,outline=LINE)
        for j in range(4):line(d,[(x-105,y-10+j*13),(x-57,y-10+j*13)],'#746d7c')
        for yy in (-18,1):line(d,[(x-15,y+yy),(x+108,y+yy)],'#aba5b0',3)
        for xx in (-15,53):d.rounded_rectangle((x+xx,y+18,x+xx+55,y+46),radius=5,fill='#262329',outline=LINE)
        q=p if active else .55
        xx=x-110+q*215; yy=y+26
        d.polygon([(xx,yy),(xx,yy+20),(xx+5,yy+15),(xx+11,yy+14)],fill=WHITE)
    elif i==2:
        line(d,[(x-136,y-60),(x-136,y+62),(x+142,y+62)],LINE)
        for yy in (-30,0,30):line(d,[(x-136,y+yy),(x+141,y+yy)],'#29272d',1)
        pts=[(x-123,y+39),(x-85,y+20),(x-48,y+27),(x-9,y-13),(x+32,y-1),(x+77,y-37),(x+127,y-46)]
        line(d,pts,'#a294ae',3)
        q=p if active else .65
        k=min(int(q*(len(pts)-1)),len(pts)-2); f=q*(len(pts)-1)-k
        xx=pts[k][0]+(pts[k+1][0]-pts[k][0])*f
        yy=pts[k][1]+(pts[k+1][1]-pts[k][1])*f
        line(d,[(xx,y-58),(xx,y+62)],'#615968',1)
        circle(d,xx,yy,8,'#29232f');circle(d,xx,yy,4,WHITE)
        d.rounded_rectangle((x+63,y+39,x+139,y+57),radius=8,fill='#29262e')
        d.text((x+101,y+48),'evaluate',font=small,fill='#dad6de',anchor='mm')
    else:
        scene=iteration_scene(p if active else 0)
        im.paste(scene,(int(x-104),int(y-104)),scene)

frames=[]
for frame in range(120):
    im=Image.new('RGB',(W,H),'#060606')
    glow=Image.new('RGB',(W,H),'#000000');gd=ImageDraw.Draw(glow)
    gd.ellipse((100,120,860,640),fill='#211727')
    glow=glow.filter(ImageFilter.GaussianBlur(100))
    im=Image.blend(im,glow,.55)
    d=ImageDraw.Draw(im)
    t=frame/120*4; active=int(t); p=t-active
    for i,(x,y) in enumerate(positions):
        d.rounded_rectangle((x,y,x+454,y+350),radius=18,fill='#101012',outline='#66606c' if active==i else '#2e2b32',width=1)
        d.text((x+24,y+24),f'0{i+1}',font=number,fill='#c0b5c9')
        d.text((x+72,y+25),titles[i],font=body,fill=WHITE)
        if i==active:
            circle(d,x+426,y+35,3,WHITE)
            line(d,[(x+24,y+333),(x+24+406*p,y+333)],'#bfb2cb',2)
        icon(im,d,i,x+227,y+140,p,active==i)
        heading,description=principles[i]
        d.text((x+24,y+239),heading,font=principle_font,fill=WHITE,anchor='lt')
        for row,text in enumerate(wrap_text(d,description,caption,406)):
            d.text((x+24,y+269+row*21),text,font=caption,fill='#b2aeb5',anchor='lt')
    frames.append(im)
frames[0].save(OUT/'workflow.png')
# Constant palette keeps line art steady while the illustrations animate.
sample=Image.new('RGB',(W,H*4))
for i in range(4):sample.paste(frames[i*30],(0,H*i))
palette=sample.quantize(colors=96)
indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
indexed[0].save(OUT/'workflow.gif',save_all=True,append_images=indexed[1:],duration=80,loop=0,optimize=True,disposal=1)
print(f"Workflow animation: {(OUT/'workflow.gif').stat().st_size/1024:.0f} KB")
