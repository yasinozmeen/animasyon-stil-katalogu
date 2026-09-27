# sfx.json → sfx.wav — kinetik: tahta tık / tok vuruşlar; duvar kısmında hece benzeri hızlanan pıtırtı
import json, numpy as np, wave, os
SR = 48000; DUR = 9.0
d = os.path.dirname(os.path.abspath(__file__)); ev = json.load(open(os.path.join(d, 'sfx.json')))
out = np.zeros(int(SR * DUR) + SR); rng = np.random.default_rng(11)
def env(n, a=0.001, dec=0.03): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / dec)
def sine(n, f): return np.sin(2 * np.pi * f * np.arange(n) / SR)
def hsh(v): s = np.sin(v * 127.1 + 311.7) * 43758.5453; return s - np.floor(s)
def wood(f, dec=0.025):   # tahta blok: iki kısmi + kısa gürültü
    n = int(0.25 * SR); return (sine(n, f) + 0.45 * sine(n, f * 2.76) * env(n, 0.0005, dec * 0.4)) * env(n, 0.0008, dec) + 0.15 * rng.standard_normal(n) * env(n, 0.0002, 0.002)
def add(t, x, g): i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i] * g
for e in ev:
    k, t, v = e['k'], e['t'], e.get('v', 0)
    if k == 'tick': add(t, wood(1250), 0.14 * (v or 1))
    elif k == 'soft': add(t, wood(1900, 0.015), 0.05)
    elif k == 'knock': add(t, wood(330, 0.06), 0.30); add(t, sine(int(0.4 * SR), 70) * env(int(0.4 * SR), 0.004, 0.12), 0.22)
    elif k == 'wood': add(t, wood([620, 740, 880, 1050][int(v)], 0.035), 0.16 + 0.04 * v)
    elif k == 'patter': add(t, wood(900 + 700 * hsh(v), 0.012), 0.06 + 0.03 * hsh(v + 3))
    elif k == 'tink': n = int(0.8 * SR); add(t, (sine(n, 2349) + 0.2 * sine(n, 4698)) * env(n, 0.002, 0.2), 0.06)
out = out[:int(SR * DUR)]; fade = int(0.25 * SR); out[-fade:] *= np.linspace(1, 0, fade)
pk = np.abs(out).max(); out = out * (0.7 / pk) if pk > 0.7 else out
pcm = (np.clip(np.stack([out, out], 1), -1, 1) * 32767).astype('<i2')
w = wave.open(os.path.join(d, 'sfx.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('sfx.wav', len(ev), 'olay')
