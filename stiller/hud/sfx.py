# sfx.json → sfx.wav — hud: temiz sinüs blip'leri, halka tıkları, tamamlanma çanı
import json, numpy as np, wave, os
SR = 48000; DUR = 9.0
d = os.path.dirname(os.path.abspath(__file__)); ev = json.load(open(os.path.join(d, 'sfx.json')))
out = np.zeros(int(SR * DUR) + SR); rng = np.random.default_rng(3)
def env(n, a=0.002, dec=0.05): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / dec)
def sine(n, f): return np.sin(2 * np.pi * f * np.arange(n) / SR)
def add(t, x, g): i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i] * g
for e in ev:
    k, t = e['k'], e['t']
    if k == 'tick': n = int(0.03 * SR); add(t, sine(n, 3200) * env(n, 0.0005, 0.004), 0.08)
    elif k == 'blip': n = int(0.2 * SR); add(t, sine(n, 2093) * env(n, 0.002, 0.035), 0.10); add(t + 0.06, sine(n, 2637) * env(n, 0.002, 0.04), 0.08)
    elif k == 'ping': n = int(1.0 * SR); add(t, (sine(n, 1396) + 0.3 * sine(n, 2793)) * env(n, 0.003, 0.28), 0.10)
    elif k == 'low': n = int(0.6 * SR); add(t, sine(n, 82) * env(n, 0.01, 0.18), 0.30)
    elif k == 'mark': n = int(0.12 * SR); add(t, sine(n, 1760) * env(n, 0.001, 0.02), 0.09)
    elif k == 'chime':
        for j, f in enumerate([1318.5, 1975.5, 2637]): n = int(1.2 * SR); add(t + j * 0.07, sine(n, f) * env(n, 0.003, 0.35), 0.07)
out = out[:int(SR * DUR)]; fade = int(0.3 * SR); out[-fade:] *= np.linspace(1, 0, fade)
pk = np.abs(out).max(); out = out * (0.7 / pk) if pk > 0.7 else out
pcm = (np.clip(np.stack([out, out], 1), -1, 1) * 32767).astype('<i2')
w = wave.open(os.path.join(d, 'sfx.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('sfx.wav', len(ev), 'olay')
