# Profile visuals

`home-banner.gif` and its static reduced-motion alternative, `home-banner.png`,
are rendered from the nikeshh.com website checkout. The renderer reads the current
Home intro, trust marks, social icons, experience value, and skill count from that
checkout. It uses the original background video and avatar, the site's Inter font,
and its Bubbledot display typeface.

Render with Pillow, fonttools[woff], imageio-ffmpeg, and the website's installed
Node dependencies available:

```sh
python3 scripts/render_profile.py --site-dir /path/to/Nikeshh.com --display-font /path/to/BubbledotICG-FinePos.ttf
```

BubbledotICG-FinePos is the display font loaded by the website from
[OnlineWebFonts](https://www.onlinewebfonts.com/fonts), whose
[font stylesheet](https://db.onlinewebfonts.com/c/8cb707a9b8a73f8a7403336b861c3074?family=BubbledotICG-FinePos)
identifies its license as CC BY 4.0. The font binary is not redistributed here.
Inter is licensed under the SIL Open Font License in the website checkout.
Brand marks belong to their respective owners.

The banner omits website navigation and the CTA. Its logo rings use the same
white interiors and image sizing as the website. The surrounding README link
opens the website.
