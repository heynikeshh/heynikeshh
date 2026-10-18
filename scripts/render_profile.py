"""Render a README banner from the portfolio's actual visual assets.

Requires Pillow, fonttools[woff], and imageio-ffmpeg. Run with --site-dir pointing
at the nikeshh.com checkout; --inter-font can point at a local Inter TTF.
"""
import argparse
from pathlib import Path
import math
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fontTools.ttLib import TTFont
import imageio_ffmpeg

parser = argparse.ArgumentParser()
parser.add_argument('--site-dir', required=True, type=Path)
parser.add_argument('--inter-font', type=Path, default=Path('/System/Library/Fonts/Supplemental/Arial.ttf'))
args = parser.parse_args()
OUT = Path(__file__).resolve().parents[1] / 'assets'
W, H = 1200, 600

with tempfile.TemporaryDirectory() as folder:
    temp = Path(folder)
    font = TTFont(args.site_dir / 'public/fonts/GeistPixel-Circle.woff2')
    font.flavor = None
    font.save(temp / 'display.ttf')
    display = ImageFont.truetype(str(temp / 'display.ttf'), 64)
    brand = ImageFont.truetype(str(temp / 'display.ttf'), 26)
    body = ImageFont.truetype(str(args.inter_font), 22)
    small = ImageFont.truetype(str(args.inter_font), 17)
    label = ImageFont.truetype(str(args.inter_font), 18)
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
        '-i', str(args.site_dir / 'public/assets/hero-bg.mp4'),
        '-vf', 'fps=12,scale=1200:675,crop=1200:600',
        '-frames:v', '96', str(temp / '%03d.png'),
    ], check=True)
    backgrounds = [Image.open(p).convert('RGB').filter(ImageFilter.GaussianBlur(1.2)) for p in sorted(temp.glob('*.png'))]
    overlay = Image.new('RGBA', (W,H))
    d = ImageDraw.Draw(overlay)
    # Stable typography over the moving website backdrop.
    d.text((40,30), 'Nikeshh', font=brand, fill='#ffffff')
    d.text((1160,37), 'AI engineer / Product builder', font=small, fill='#c8c8c8', anchor='ra')
    d.rounded_rectangle((493,108,707,148), radius=20, fill='#28282a', outline='#686868')
    d.ellipse((512,125,518,131),fill='#d8d8d8')
    d.text((609,127),'Intelligent systems',font=small,fill='#dedede',anchor='mm')
    first = 'Building calm,'
    text_width = d.textlength(first,font=display)
    group_width = text_width + 76
    start = (W-group_width)/2
    avatar = Image.open(args.site_dir/'public/assets/pixel-avatar.png').convert('RGBA')
    avatar.thumbnail((64,88),Image.Resampling.LANCZOS)
    overlay.alpha_composite(avatar,(int(start),178))
    d.text((start+76,190),first,font=display,fill='#ffffff',anchor='lt')
    d.text((W/2,292),'reliable intelligence',font=display,fill='#ffffff',anchor='mm')
    d.text((W/2,365),'Assistants, retrieval, and agentic workflows.',font=body,fill='#d4d4d4',anchor='mm')
    d.text((W/2,399),'Designed for people. Engineered for production.',font=body,fill='#bcbcbc',anchor='mm')
    # Match the site's monochrome CTA, with a soft and stable halo.
    halo=Image.new('RGBA',(W,H))
    hd=ImageDraw.Draw(halo)
    hd.rounded_rectangle((494,443,706,496),radius=27,fill=(255,255,255,52))
    halo=halo.filter(ImageFilter.GaussianBlur(18))
    overlay=Image.alpha_composite(halo,overlay)
    d=ImageDraw.Draw(overlay)
    d.rounded_rectangle((493,442,707,497),radius=28,fill='#141414',outline='#747474',width=1)
    d.text((588,469),'Explore nikeshh.com',font=label,fill='#eeeeee',anchor='mm')
    d.line((682,474,690,466),fill='#eeeeee',width=1)
    d.line((682,466,690,466,690,474),fill='#eeeeee',width=1)
    d.text((W/2,560),'Nikeshh Vijayabaskaran',font=small,fill='#969696',anchor='mm')
    scrim=Image.new('RGBA',(W,H))
    sd=ImageDraw.Draw(scrim)
    for y in range(H):
        opacity = int(255*(0.28+0.36*abs(y-H/2)/(H/2)))
        sd.line((0,y,W,y),fill=(0,0,0,opacity))
    frames=[]
    for i in range(96):
        # Cosine timing makes the ambient forward/backward loop seamless.
        index=round((1-math.cos(2*math.pi*i/96))/2*(len(backgrounds)-1))
        im=backgrounds[index].convert('RGBA')
        im=Image.alpha_composite(im,scrim)
        im=Image.alpha_composite(im,overlay).convert('RGB')
        if i==0: im.save(OUT/'engineering-banner.png')
        frames.append(im.resize((840,420),Image.Resampling.LANCZOS))
    # Shared palette keeps the background and text consistent between frames.
    sample=Image.new('RGB',(840,420*8))
    for j in range(8):sample.paste(frames[j*12],(0,j*420))
    background_palette=sample.quantize(colors=224).getpalette()[:224*3]
    avatar_palette=avatar.convert('RGB').quantize(colors=16).getpalette()[:16*3]
    grays=[value for i in range(16) for value in (i*17,)*3]
    palette=Image.new('P',(1,1))
    palette.putpalette(background_palette+avatar_palette+grays)
    indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
    indexed[0].save(OUT/'engineering-banner.gif',save_all=True,append_images=indexed[1:],duration=80,loop=0,optimize=True,disposal=1)
print(f"Rendered 96 frames; {(OUT/'engineering-banner.gif').stat().st_size/1024/1024:.2f} MB")
