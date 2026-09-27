# events.json → ses.wav · projektör tıkırtısı (24/sn, çok hafif), 1 kHz "2-pop", sessiz film piyanosu motifleri, kare kayması takırtısı
import json, wave, numpy as np
SR, DUR = 48000, 10.0
N = int(SR * DUR); out = np.zeros(N)
def add(sig, t, g=1.0):
    i = int(t * SR); n = min(len(sig), N - i)
    if n > 0: out[i:i + n] += sig[:n] * g
def click(g=1.0, f=1800, d=0.004):
    n = int(0.02 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) + 0.5 * np.sin(2 * np.pi * 180 * tt) * np.exp(-tt / 0.008)) * g
def piano(freq, dur=2.2):
    n = int(dur * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for h, a in enumerate([1, 0.5, 0.28, 0.16, 0.1, 0.06], 1):
        s += a * np.sin(2 * np.pi * freq * h * (1 + 0.0004 * h * h) * tt) * np.exp(-tt * (1.3 + h * 0.7))
    return s * np.minimum(1, tt / 0.004)
nt = lambda m: 440 * 2 ** ((m - 69) / 12)
rs = np.random.default_rng(3)
t = 0.12
while t < 9.9:  # projektör: düzensiz aralıklı, kısık tık
    add(click(0.05 + 0.02 * rs.random(), 1500 + 400 * rs.random()), t); t += 1 / 24 + rs.normal(0, 0.0015)
for e in json.load(open('events.json')):
    k, t = e['k'], e['t']
    if k == 'pop': n = int(SR / 30); add(np.sin(2 * np.pi * 1000 * np.arange(n) / SR), t, 0.35)
    elif k == 'motif':
        for i, (m, dt) in enumerate([(69, 0), (72, 0.42), (76, 0.84), (74, 1.3)]): add(piano(nt(m)), t + dt, 0.2)
        add(piano(nt(45), 3), t, 0.16)
    elif k == 'slip':
        for i in range(7): add(click(0.25, 900, 0.006), t + i * 0.032)
    elif k == 'chord':
        for i, m in enumerate([60, 64, 67, 71]): add(piano(nt(m), 2.5), t + i * 0.05, 0.15)
        add(piano(nt(36), 3), t, 0.18)
    elif k == 'low':
        for i, m in enumerate([57, 60, 64, 69]): add(piano(nt(m), 1.2), t + i * 0.09, 0.14)
        add(piano(nt(33), 1.1), t, 0.2)
# eski optik ses: bant sınırlı
def onepole(x, fc, hp=False):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); p = 0.0
    for i in range(len(x)): p = (1 - a) * x[i] + a * p; y[i] = p
    return x - y if hp else y
out = onepole(onepole(out, 4200), 120, hp=True)
fade = np.ones(N); fade[-int(0.25 * SR):] = np.linspace(1, 0, int(0.25 * SR)); out *= fade
out = np.tanh(out * 1.3) * 0.85
pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
w = wave.open('ses.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes()); w.close()
print('ses.wav ok')
