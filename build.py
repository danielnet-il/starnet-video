"""Build a 9:16 explainer video from a scenes JSON: voice (Piper, free/offline) + animation (engine.html).
Usage: python3 build.py scenes.json out.mp4
scenes.json: {"fps":24,"scenes":[{"head","icon","narration","foot"?}, ...]}  (timings are computed from the audio)
"""
import json, os, re, subprocess, sys, tempfile, urllib.request, tarfile, shutil
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, 'tools')
PIPER_URL = 'https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz'
VOICE_URL = 'https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz'
TD = 1.0          # must match engine.html
LEAD = 0.35       # narration starts this long after the scene starts
MIN_SCENE = 4.5
TAIL = 0.9

def sh(*a, **k): return subprocess.run(a, check=True, **k)

def ensure_tools():
    piper = os.path.join(TOOLS, 'piper', 'piper'); voice = os.path.join(TOOLS, 'voice', 'en-us-lessac-medium.onnx')
    os.makedirs(TOOLS, exist_ok=True)
    if not os.path.exists(piper):
        f = os.path.join(TOOLS, 'piper.tgz'); urllib.request.urlretrieve(PIPER_URL, f)
        tarfile.open(f).extractall(TOOLS); os.remove(f)
    if not os.path.exists(voice):
        os.makedirs(os.path.join(TOOLS, 'voice'), exist_ok=True)
        f = os.path.join(TOOLS, 'voice.tgz'); urllib.request.urlretrieve(VOICE_URL, f)
        tarfile.open(f).extractall(os.path.join(TOOLS, 'voice')); os.remove(f)
    return piper, voice

def speakable(t):
    rep = {'2FA': 'two F A', 'on-chain': 'on chain', 'USDT': 'U S D T', 'USDC': 'U S D C', 'BTC': 'bitcoin', 'ETH': 'ether', 'SAFU': 'safu'}
    for k, v in rep.items(): t = t.replace(k, v)
    return t

def duration(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).decode().strip())

def main(src, dst):
    cfg = json.load(open(src)); fps = cfg.get('fps', 24); scenes = cfg['scenes']
    edge = shutil.which('edge-tts')
    if edge: piper = voice = None
    else: piper, voice = ensure_tools()
    tmp = tempfile.mkdtemp(prefix='build_')
    # 1) voice per scene
    for i, s in enumerate(scenes):
        txt = os.path.join(tmp, f'l{i}.txt'); wav = os.path.join(tmp, f'l{i}.wav')
        open(txt, 'w').write(speakable(s['narration']))
        if edge:
            mp3 = os.path.join(tmp, f'l{i}.mp3')
            sh(edge, '--voice', os.environ.get('EDGE_VOICE', 'en-US-AndrewNeural'), '--file', txt, '--write-media', mp3, stderr=subprocess.DEVNULL)
            sh('ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ar', '44100', '-ac', '1', wav)
        else: sh(piper, '--model', voice, '--sentence_silence', '0.25', '--output_file', wav, stdin=open(txt), stderr=subprocess.DEVNULL)
        s['_voice'] = duration(wav)
    # 2) timings from the audio
    t = 0.0
    for s in scenes:
        s['start'] = round(t, 3); s['end'] = round(t + max(MIN_SCENE, s['_voice'] + LEAD + TAIL), 3); t = s['end']
    total = scenes[-1]['end']; nframes = int(total * fps)
    cfgp = os.path.join(tmp, 'scenes_timed.json'); json.dump({'fps': fps, 'scenes': scenes}, open(cfgp, 'w'))
    # 3) audio mix
    ins, fl = [], []
    for i, s in enumerate(scenes):
        ms = int((s['start'] + LEAD) * 1000); ins += ['-i', os.path.join(tmp, f'l{i}.wav')]; fl.append(f'[{i}:a]adelay={ms}|{ms}[a{i}]')
    mix = ''.join(f'[a{i}]' for i in range(len(scenes)))
    fc = ';'.join(fl) + f';{mix}amix=inputs={len(scenes)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=1[out]'
    voice_wav = os.path.join(tmp, 'voice.wav')
    sh('ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[out]', '-t', str(total), '-ar', '44100', '-ac', '1', voice_wav)
    # 4) frames in parallel
    frames = os.path.join(tmp, 'frames'); n = max(2, (os.cpu_count() or 2)); chunk = -(-nframes // n)
    jobs = [(a, min(a + chunk, nframes)) for a in range(0, nframes, chunk)]
    def run(j): sh(sys.executable, os.path.join(HERE, 'render_frames.py'), cfgp, frames, str(j[0]), str(j[1]))
    with ThreadPoolExecutor(len(jobs)) as ex: list(ex.map(run, jobs))
    # 5) encode
    sh('ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', os.path.join(frames, 'f%05d.png'), '-i', voice_wav,
       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', dst)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'built {dst} ({total:.1f}s, {nframes} frames)')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
