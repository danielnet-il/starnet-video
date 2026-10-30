"""Render a range of frames of engine.html. Usage: render_frames.py SCENES_JSON OUT_DIR START END"""
import json, sys, os
from playwright.sync_api import sync_playwright

here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; a, z = int(sys.argv[3]), int(sys.argv[4])
fps = cfg.get('fps', 24); os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 540, 'height': 960}, device_scale_factor=2)
    pg.goto('file://' + os.path.join(here, 'engine.html'))
    pg.evaluate('s => window.SCENES = s', cfg['scenes'])
    pg.wait_for_timeout(300)
    for i in range(a, z):
        pg.evaluate(f'draw({i / fps})')
        pg.screenshot(path=os.path.join(out, f'f{i:05d}.png'))
    b.close()
