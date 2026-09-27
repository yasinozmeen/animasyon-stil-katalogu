# events.json → ses.wav · çizgi roman: panel "tık"ları, balon "boing"i, tahta blok TIK/TAK, mantar "POP", zil
import json, wave, numpy as np
SR, DUR = 48000, 10.0
N = int(SR * DUR); out = np.zeros(N)
def add(sig, t, g=1.0):
    i = int(t * SR); n = min(len(sig), N - i)
    if n > 0: out[i:i + n] += sig[:n] * g
def tt(d): return np.arange(int(d * SR)) / SR
def sweep(f0, f1, d, dec, vib=0):
    x = tt(d); f = f0 * (f1 / f0) ** (x / d) * (1 + vib * np.sin(2 * np.pi * 14 * x) * np.exp(-x * 4))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / dec) * np.minimum(1, x / 0.003)
def wood(f):
    x = tt(0.12); return (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 2.7 * x)) * np.exp(-x / 0.025)
def bell(f):
    x = tt(1.6); return sum(a * np.sin(2 * np.pi * f * m * x) * np.exp(-x * (1.5 + m)) for m, a in [(1, 1), (2.76, 0.5), (5.4, 0.25)])
for e in json.load(open('events.json')):
    k, t = e['k'], e['t']
    if k == 'paper': add(wood(1400) * 0.4, t, 0.25)
    elif k == 'boing': add(sweep(180, 520, 0.35, 0.18, vib=0.25), t, 0.3)
    elif k == 'tick': add(wood(1250), t, 0.4)
    elif k == 'tock': add(wood(820), t, 0.4)
    elif k == 'pop':
        add(sweep(900, 140, 0.12, 0.05), t, 0.5); add(wood(2200), t, 0.3); add(sweep(300, 700, 0.25, 0.1, vib=0.1), t + 0.05, 0.15)
    elif k == 'ding': add(bell(1320), t, 0.18); add(bell(1760), t + 0.12, 0.12)
out = np.tanh(out * 1.3) * 0.85
pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
w = wave.open('ses.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes()); w.close()
print('ses.wav ok')
