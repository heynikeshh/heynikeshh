"""Render the profile banner. Requires Pillow and macOS supplemental fonts."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
W, H = 1200, 540
BG = '#080e1c'
MUTED = '#8b9ab5'
CYAN = '#65d8ed'
WHITE = '#edf4ff'
FONT = Path('/System/Library/Fonts/Supplemental')
def font(size, bold=False, mono=False):
    name = 'Courier New.ttf' if mono else ('Arial Bold.ttf' if bold else 'Arial.ttf')
    return ImageFont.truetype(str(FONT / name), size)

def text(d, xy, value, size, color=WHITE, bold=False, mono=False):
    d.text(xy, value, font=font(size, bold, mono), fill=color)

def center(d, x, y, value, size, color=WHITE, mono=False):
    f = font(size, mono=mono)
    d.text((x, y), value, font=f, fill=color, anchor='mm')

base = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(base)
for x in range(24, W, 28):
    for y in range(24, H, 28):
        d.point((x, y), fill='#1b2940')
d.rounded_rectangle((1, 1, W-2, H-2), radius=24, outline='#25314a', width=2)
text(d, (48, 32), 'N / V', 20, CYAN, mono=True)
text(d, (152, 34), 'AI ENGINEERING  /  PRODUCT  /  PLATFORMS', 15, MUTED, mono=True)
text(d, (48, 88), 'Nikeshh', 60, bold=True)
text(d, (48, 151), 'Vijayabaskaran', 60, bold=True)
text(d, (50, 236), 'Intelligence, engineered.', 26, CYAN)
text(d, (50, 280), 'Assistants. Retrieval. Agentic workflows.', 19, MUTED)
text(d, (50, 310), 'From the first interface to the last mile of production.', 17, MUTED)
# A neural circuit: connected, concentric pathways with a stable central mark.
cx, cy = 963, 195
for radius in (66, 105, 146):
    d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline='#243750', width=1)
nodes=[]
for k in range(12):
    a = 2*math.pi*k/12
    r = 146 if k%2==0 else 105
    nodes.append((cx+math.cos(a)*r, cy+math.sin(a)*r))
for k, p in enumerate(nodes):
    q=nodes[(k+4)%12]
    d.line((p,q), fill='#203650', width=1)
    d.line((p,(cx,cy)), fill='#1d3047', width=1)
    d.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4), fill='#42657f')
d.rounded_rectangle((cx-44,cy-35,cx+44,cy+35),radius=16,fill='#0e2031',outline='#38677c',width=2)
center(d,cx,cy,'AI',30,CYAN,mono=True)
# Process diagram is illustrative, not a claim of live telemetry.
d.rounded_rectangle((32, 380, 1168, 510), radius=16, fill='#0d1627', outline='#26364e')
text(d,(52,394),'HOW I THINK ABOUT SYSTEMS',13,MUTED,mono=True)
labels=['CONTEXT','RETRIEVAL','REASONING','TOOLS','EVALUATION']
xs=[150,375,600,825,1050]
for i,x in enumerate(xs):
    if i<4: d.line((x+80,458,xs[i+1]-80,458),fill='#334961',width=2)
    d.rounded_rectangle((x-80,435,x+80,481),radius=9,fill='#111f32',outline='#334961')
    center(d,x,458,labels[i],15,WHITE,mono=True)

frames=[]
for frame in range(96):
    im=base.copy(); d=ImageDraw.Draw(im)
    t=frame/96
    # Orbiting signals and quiet neural connections.
    for orbit,r in enumerate((66,105,146)):
        a=2*math.pi*(t+orbit/3)*(1 if orbit!=1 else -1)
        p=(cx+math.cos(a)*r, cy+math.sin(a)*r)
        for rad,col in ((10,'#12344b'),(6,'#27778b'),(3,CYAN)):
            d.ellipse((p[0]-rad,p[1]-rad,p[0]+rad,p[1]+rad),fill=col)
    active=int(t*12)%12
    p=nodes[active]
    d.line((p,(cx,cy)),fill='#3c9bb1',width=2)
    d.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=CYAN)
    d.rounded_rectangle((cx-44,cy-35,cx+44,cy+35),radius=16,fill='#0e2031',outline='#38677c',width=2)
    center(d,cx,cy,'AI',30,CYAN,mono=True)
    # Route packets along the system, with a subtle active-stage indicator.
    step=t*5
    idx=int(step)%5
    x=xs[idx]
    d.rounded_rectangle((x-80,435,x+80,481),radius=9,outline=CYAN,width=2)
    center(d,x,458,labels[idx],15,CYAN,mono=True)
    for j in range(4):
        q=(t*2+j/4)%1
        px=xs[j]+83+q*(xs[j+1]-xs[j]-166)
        d.ellipse((px-3,455,px+3,461),fill=CYAN)
    frames.append(im)
# Fixed palette avoids color fluctuations between frames.
palette=base.quantize(colors=96)
frames=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
frames[0].convert('RGB').save(OUT/'engineering-banner.png')
frames[0].save(OUT/'engineering-banner.gif', save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True, disposal=1)
print(f"Rendered {len(frames)} frames; GIF {(OUT/'engineering-banner.gif').stat().st_size/1024:.0f} KB")
