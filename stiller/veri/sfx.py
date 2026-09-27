# sfx.json → sfx.wav — veri: veri noktası başına yükselen yumuşak tık (kalem/klavye değil, marimba benzeri), not için "tok"
import json, numpy as np, wave, os
SR = 48000; DUR = 9.0
d = os.path.dirname(os.path.abspath(__file__)); ev = json.load(open(os.path.join(d, 'sfx.json')))
out = np.zeros(int(SR * DUR) + SR)
def env(n, a=0.002, dec=0.05): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / dec)
def sine(n, f): return np.sin(2 * np.pi * f * np.arange(n) / SR)
def add(t, x, g): i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i] * g
for e in ev:
    k, t = e['k'], e['t']
    if k == 'dot':   # veri azaldıkça perde iner
        f = 880 * 2 ** (-(e['v']) / 14); n = int(0.35 * SR); add(t, (sine(n, f) + 0.25 * sine(n, 4 * f)) * env(n, 0.002, 0.06), 0.07)
    elif k == 'tick': n = int(0.2 * SR); add(t, (sine(n, 660) + 0.2 * sine(n, 2640)) * env(n, 0.002, 0.05), 0.07)
    elif k == 'tock': n = int(0.5 * SR); add(t, (sine(n, 392) + 0.3 * sine(n, 1176)) * env(n, 0.003, 0.12), 0.12)
    elif k == 'soft':
        for j, f in enumerate([523.25, 783.99]): n = int(1.0 * SR); add(t + j * 0.09, sine(n, f) * env(n, 0.004, 0.3), 0.07)
out *= 2.6
out = out[:int(SR * DUR)]; fade = int(0.3 * SR); out[-fade:] *= np.linspace(1, 0, fade)
pk = np.abs(out).max(); out = out * (0.7 / pk) if pk > 0.7 else out
pcm = (np.clip(np.stack([out, out], 1), -1, 1) * 32767).astype('<i2')
w = wave.open(os.path.join(d, 'sfx.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('sfx.wav', len(ev), 'olay')
