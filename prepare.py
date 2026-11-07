"""Validate the render request (from repository_dispatch client_payload or an example file) and write job.json + meta.json."""
import json, os, re, sys

ICONS = {"question", "exchange", "key", "risk", "wallet", "scales", "compare", "outro",
         "hack", "record", "laptop", "paused", "frozen", "safe", "scam", "lesson",
         "chartdown", "link", "liquidation", "outflow", "gauge", "checklist"}

def clean(s, n):
    s = re.sub(r'[\x00-\x1f]', ' ', str(s)).strip()
    return s[:n]

def main():
    raw = os.environ.get('PAYLOAD', '').strip()
    p = json.loads(raw) if raw and raw != 'null' else {}
    if not p.get('scenes'):                       # manual run: use an example file
        p = {'scenes': json.load(open(os.environ.get('EXAMPLE', 'examples/binance_hack.json')))['scenes'],
             'title': 'Test render', 'caption': 'Test', 'hashtags': '#test', 'publish': False}
    scenes = p['scenes']
    if isinstance(scenes, str): scenes = json.loads(scenes)
    if not (3 <= len(scenes) <= 14): sys.exit('scenes must be 3..14')
    out = []
    for s in scenes:
        if s.get('icon') not in ICONS: sys.exit(f"unknown icon: {s.get('icon')}")
        o = {'head': clean(s['head'], 40).upper(), 'icon': s['icon'], 'narration': clean(s['narration'], 260)}
        if s.get('foot'): o['foot'] = clean(s['foot'], 90)
        if s.get('big'): o['big'] = clean(s['big'], 14)
        if s.get('dir') in ('up', 'down'): o['dir'] = s['dir']
        if s.get('sub'): o['sub'] = clean(s['sub'], 48)
        if s.get('value') is not None: o['value'] = max(0, min(100, int(s['value'])))
        if s.get('items'): o['items'] = [clean(x, 30).upper() for x in list(s['items'])[:3]]
        out.append(o)
    json.dump({'fps': 24, 'scenes': out}, open('job.json', 'w'))
    meta = {'viral_title': clean(p.get('title', ''), 95), 'caption': clean(p.get('caption', ''), 400),
            'hashtags': clean(p.get('hashtags', ''), 120), 'publish': bool(p.get('publish', False))}
    json.dump(meta, open('meta.json', 'w'))
    print('prepared', len(out), 'scenes; publish =', meta['publish'])

main()
