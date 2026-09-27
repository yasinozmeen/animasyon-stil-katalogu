# sfx.json → sfx.wav (48 kHz stereo) — terminal: tuş tıkı, bip, CRT açılış/kapanış
import json, numpy as np, wave, os
SR = 48000; DUR = 9.0
d = os.path.dirname(os.path.abspath(__file__))
ev = json.load(open(os.path.join(d, 'sfx.json')))
out = np.zeros(int(SR * DUR) + SR)
rng = np.random.default_rng(7)
def env(n, a=0.001, dec=0.02):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / dec)
def bp_noise(n, lo, hi):
    x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); X[(f < lo) | (f > hi)] = 0; y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)
def tone(n, f, harm=((1, 1),)):
    t = np.arange(n) / SR; return sum(a * np.sin(2 * np.pi * f * k * t) for k, a in harm)
def add(t, x, g):
    i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i] * g
for e in ev:
    k, t = e['k'], e['t']; v = e.get('v', 1)
    if k == 'key':
        n = int(0.05 * SR); x = bp_noise(n, 1800, 6000) * env(n, 0.0003, 0.006) + 0.6 * tone(n, 170) * env(n, 0.001, 0.012)
        add(t, x, 0.16 * v)
    elif k == 'enter':
        n = int(0.08 * SR); x = bp_noise(n, 1200, 5000) * env(n, 0.0003, 0.01) + 0.8 * tone(n, 120) * env(n, 0.001, 0.02); add(t, x, 0.22)
    elif k == 'tick':
        n = int(0.02 * SR); add(t, bp_noise(n, 2500, 7000) * env(n, 0.0002, 0.003), 0.07)
    elif k == 'flip':
        n = int(0.015 * SR); add(t, bp_noise(n, 3500, 9000) * env(n, 0.0002, 0.002), 0.06)
    elif k in ('lock', 'beep', 'beepHi'):
        f = {'lock': 1318, 'beep': 880, 'beepHi': 1760}[k]; L = {'lock': 0.09, 'beep': 0.11, 'beepHi': 0.2}[k]
        n = int(L * SR); e2 = np.minimum(1, np.arange(n) / (0.004 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.02 * SR))
        x = tone(n, f, ((1, 1), (3, 0.18), (5, 0.06))) * e2; add(t, x, 0.10)
        if k == 'lock': add(t + 0.1, x, 0.07)
    elif k == 'on':
        n = int(0.5 * SR); x = tone(n, 52) * env(n, 0.004, 0.16) + 0.25 * bp_noise(n, 300, 4000) * env(n, 0.0005, 0.03); add(t, x, 0.35)
    elif k == 'off':
        n = int(0.45 * SR); tt = np.arange(n) / SR; f = 900 * np.exp(-tt * 9) + 90
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.14) + 0.5 * tone(n, 48) * env(n, 0.003, 0.12); add(t, x, 0.18)
out = out[:int(SR * DUR)]
fade = int(0.3 * SR); out[-fade:] *= np.linspace(1, 0, fade)
peak = np.abs(out).max(); out = out / max(peak, 1e-9) * min(peak, 0.7) if peak > 0.7 else out
st = np.stack([out, out], 1); pcm = (np.clip(st, -1, 1) * 32767).astype('<i2')
w = wave.open(os.path.join(d, 'sfx.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('sfx.wav', len(ev), 'olay')
