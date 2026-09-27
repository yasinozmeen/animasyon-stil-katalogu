# events.json → ses.wav (48 kHz stereo) · 70'ler: TV aç/kapa bipi, harf "pop"ları, çark tıkları, sıcak akor
import json, wave, numpy as np
SR, DUR = 48000, 10.0
out = np.zeros(int(SR * DUR))
def add(sig, t, g=1.0):
    i = int(t * SR); n = min(len(sig), len(out) - i)
    if n > 0: out[i:i + n] += sig[:n] * g
def env(n, a=0.002, d=0.1):
    tt = np.arange(n) / SR; return np.minimum(1, tt / a) * np.exp(-tt / d)
def tone(f0, f1, dur, d, wave_='sine'):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = np.linspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) if wave_ == 'sine' else np.sign(np.sin(ph)) * 0.5
    return s * env(n, 0.003, d)
ev = json.load(open('events.json')); last_tick = -1
for e in sorted(ev, key=lambda e: e['t']):
    k, t = e['k'], e['t']
    if k == 'on': add(tone(180, 900, 0.18, 0.08), t, 0.35); add(tone(1200, 1200, 0.12, 0.05), t + 0.16, 0.12)
    elif k == 'off': add(tone(900, 120, 0.35, 0.12), t, 0.35)
    elif k == 'pop': f = 520 + 60 * e.get('v', 0); add(tone(f * 0.6, f * 1.4, 0.09, 0.03), t, 0.28)
    elif k == 'tick':
        if t - last_tick < 0.028: continue
        last_tick = t; n = int(0.02 * SR); tt = np.arange(n) / SR
        add(np.sin(2 * np.pi * 2300 * tt) * np.exp(-tt / 0.003) + 0.6 * np.sin(2 * np.pi * 700 * tt) * np.exp(-tt / 0.006), t, 0.3)
    elif k == 'chime':
        n = int(1.6 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for j, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
            vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * tt)
            s[int(j * 0.06 * SR):] += (np.sin(2 * np.pi * f * vib * tt) + 0.3 * np.sin(4 * np.pi * f * tt))[: n - int(j * 0.06 * SR)] * np.exp(-tt[: n - int(j * 0.06 * SR)] / 0.5)
        add(s * np.minimum(1, tt / 0.01), t, 0.16)
# eski TV hoparlörü: hafif bant geçiren (basit IIR) + yumuşak sınırlama
from math import pi
def onepole(x, fc, hp=False):
    a = np.exp(-2 * pi * fc / SR); y = np.zeros_like(x); p = 0.0
    for i in range(len(x)): p = (1 - a) * x[i] + a * p; y[i] = p
    return x - y if hp else y
out = onepole(onepole(out, 5500), 180, hp=True)
out = np.tanh(out * 1.4) * 0.8
pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
st = np.repeat(pcm[:, None], 2, axis=1)
w = wave.open('ses.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
print('ses.wav ok')
