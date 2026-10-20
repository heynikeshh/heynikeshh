"""Render the profile banner using the website's copy, fonts, logos, and video.

Requires Pillow, fonttools[woff], imageio-ffmpeg and the site's installed Node
packages. Pass --site-dir and --display-font (the Bubbledot TTF used by the site).
The display font source is credited in assets/README.md.
"""
import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont, ImageOps
from fontTools.ttLib import TTFont
import imageio_ffmpeg

parser = argparse.ArgumentParser()
parser.add_argument('--site-dir', required=True, type=Path)
parser.add_argument('--display-font', required=True, type=Path)
args = parser.parse_args()
OUT = Path(__file__).resolve().parents[1] / 'assets'
W, H, COUNT = 1200, 600, 60

with tempfile.TemporaryDirectory() as folder:
    temp = Path(folder)
    # Read content and rasterise vector marks directly from the website checkout.
    data = json.loads(subprocess.check_output(['node', '-e', r'''
const fs = require('fs'), path = require('path'), vm = require('vm');
const site = process.argv[1], out = process.argv[2];
const ts = require(path.join(site, 'node_modules/typescript'));
const sharp = require(path.join(site, 'node_modules/sharp'));
function read(file) {
  const exports = {};
  vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(site, file), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS }
  }).outputText, { exports });
  return exports;
}
(async () => {
  const content = read('src/content/site.ts');
  for (const [index, company] of content.trustedBy.entries()) {
    if (company.logo) await sharp(path.join(site, 'public', company.logo)).resize(80, 80, { fit: 'inside' }).png().toFile(path.join(out, `trust-${index}.png`));
  }
  const icons = fs.readFileSync(path.join(site, 'src/components/social-icons.tsx'), 'utf8');
  const matches = [...icons.matchAll(/<svg[^>]*>([\s\S]*?)<\/svg>/g)];
  for (const [index, match] of matches.entries()) {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#bdb8c0">${match[1]}</svg>`;
    await sharp(Buffer.from(svg)).resize(24, 24).png().toFile(path.join(out, `social-${index}.png`));
  }
  console.log(JSON.stringify({ intro: content.homeIntro, trust: content.trustedBy,
    name: content.site.name, skills: content.skills.length,
    years: read('src/content/home-sections.ts').stats[0].value }));
})();
''', str(args.site_dir.resolve()), str(temp)], text=True))
    font = TTFont(args.site_dir / 'public/fonts/InterVariable.woff2')
    font.flavor = None
    font.save(temp / 'inter.ttf')
    display = ImageFont.truetype(str(args.display_font), 64)
    body = ImageFont.truetype(str(temp / 'inter.ttf'), 17)
    small = ImageFont.truetype(str(temp / 'inter.ttf'), 13)
    metric = ImageFont.truetype(str(args.display_font), 26)
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
        '-i', str(args.site_dir / 'public/assets/hero-bg.mp4'),
        '-vf', f'fps=10,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}',
        '-frames:v', str(COUNT), str(temp / '%03d.png'),
    ], check=True)
    backgrounds = [Image.open(p).convert('RGB') for p in sorted(temp.glob('[0-9]*.png'))]
    overlay = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(overlay)
    # Trust marks and overlapping pill match the Home panel.
    count, size, step = len(data['trust']), 42, 26
    pill_width = 224
    total = (count - 1) * step + size + pill_width - 14
    x = int((W - total) / 2)
    for i, company in enumerate(data['trust']):
        mark = Image.open(temp / f'trust-{i}.png').convert('RGBA')
        circle = Image.new('RGBA', (size, size))
        cd = ImageDraw.Draw(circle)
        cd.ellipse((0, 0, size - 1, size - 1), fill='#28282a', outline='#747474')
        inner_size = size - 8
        inner = Image.new('RGBA', (inner_size, inner_size), 'white')
        if company.get('cover'):
            cover_size = round(inner_size * 1.12)
            mark = ImageOps.fit(mark, (cover_size, cover_size), method=Image.Resampling.LANCZOS)
        else:
            if company.get('wide'):
                width = round(size * .55)
                height = max(1, round(mark.height * width / mark.width))
            else:
                height = round(size * .34)
                width = max(1, round(mark.width * height / mark.height))
            mark = mark.resize((width, height), Image.Resampling.LANCZOS)
        inner.alpha_composite(mark, ((inner_size - mark.width) // 2, (inner_size - mark.height) // 2))
        mask = Image.new('L', (inner_size, inner_size))
        ImageDraw.Draw(mask).ellipse((0, 0, inner_size - 1, inner_size - 1), fill=255)
        inner.putalpha(mask)
        circle.alpha_composite(inner, (4, 4))
        overlay.alpha_composite(circle, (x + i * step, 76))
    pill_x = x + (count - 1) * step + size - 16
    d.rounded_rectangle((pill_x, 76, pill_x + pill_width, 118), radius=21, fill='#28282a', outline='#747474')
    d.text((pill_x + pill_width / 2 + 3, 97), 'Trusted by enterprise teams', font=small, fill='#c4c2c3', anchor='mm')

    first = 'Building calm,'
    group_width = d.textlength(first, font=display) + 77
    start = (W - group_width) / 2
    avatar = Image.open(args.site_dir / 'public/assets/pixel-avatar.png').convert('RGBA')
    avatar.thumbnail((64, 88), Image.Resampling.LANCZOS)
    overlay.alpha_composite(avatar, (int(start), 125))
    d.text((start + 77, 166), first, font=display, fill='white', anchor='lm')
    d.text((W / 2, 236), 'reliable intelligence', font=display, fill='white', anchor='mm')

    # Use the live intro wording and underline the same interactive phrases.
    segments = [(data['intro']['opening'], False)]
    for item in data['intro']['highlights']:
        segments.extend([(item['label'], True), (item['suffix'], False)])
    lines, line, width = [], [], 0
    for text, underlined in segments:
        for word in text.splitlines() or ['']:
            # Break at segment boundaries to keep each callout phrase together.
            word_width = d.textlength(word, font=body)
            if width + word_width > 780 and line:
                lines.append(line)
                line, width = [], 0
            line.append((word, underlined))
            width += word_width
    if line: lines.append(line)
    for row, line in enumerate(lines):
        x = (W - sum(d.textlength(word, font=body) for word, _ in line)) / 2
        y = 314 + row * 30
        for word, underlined in line:
            width = d.textlength(word, font=body)
            d.text((x, y), word, font=body, fill='#f5f0f8' if underlined else '#d0d0d0', anchor='lm')
            if underlined: d.line((x, y + 12, x + width, y + 12), fill='#9e8ba9', width=1)
            x += width
    for i in range(3):
        icon = Image.open(temp / f'social-{i}.png').convert('RGBA')
        overlay.alpha_composite(icon, (540 + i * 48, 385))
    stats = [(data['years'], 'Years shipping'), ('5', 'Selected systems'), ('5+', 'Enterprise orgs'), (str(data['skills']), 'Core skills')]
    for i, (value, label) in enumerate(stats):
        x = 240 + i * 240
        d.text((x, 505), value, font=metric, fill='white', anchor='mm')
        d.text((x, 535), label, font=small, fill='#b7b0be', anchor='mm')

    scrim = Image.new('RGBA', (W, H))
    sd = ImageDraw.Draw(scrim)
    stops = [(0, .60), (.35, .20), (.70, .33), (1, .80)]
    for y in range(H):
        t = y / (H - 1)
        for (a, av), (b, bv) in zip(stops, stops[1:]):
            if a <= t <= b:
                opacity = av + (bv - av) * (t - a) / (b - a)
                break
        sd.line((0, y, W, y), fill=(0, 0, 0, round(opacity * 255)))
    frames = []
    for i in range(COUNT):
        index = round((1 - math.cos(2 * math.pi * i / COUNT)) / 2 * (len(backgrounds) - 1))
        image = Image.alpha_composite(backgrounds[index].convert('RGBA'), scrim)
        image = Image.alpha_composite(image, overlay).convert('RGB')
        if i == 0: image.save(OUT / 'home-banner.png')
        frames.append(image)
    sample = Image.new('RGB', (W, H * 6))
    for j in range(6): sample.paste(frames[j * COUNT // 6], (0, j * H))
    colors = sample.quantize(colors=224).getpalette()[:224 * 3]
    avatar_colors = avatar.convert('RGB').quantize(colors=16).getpalette()[:16 * 3]
    grays = [value for i in range(16) for value in (i * 17,) * 3]
    palette = Image.new('P', (1, 1))
    palette.putpalette(colors + avatar_colors + grays)
    indexed = [image.quantize(palette=palette, dither=Image.Dither.NONE) for image in frames]
    indexed[0].save(OUT / 'home-banner.gif', save_all=True, append_images=indexed[1:], duration=100, loop=0, optimize=True, disposal=1)
print(f"Rendered {COUNT} frames; {(OUT / 'home-banner.gif').stat().st_size / 1024 / 1024:.2f} MB")
