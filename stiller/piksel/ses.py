# events.json → ses.wav · çiptun: kare dalga zıplama/para/kafa/ezme, başlık seçimi, zafer arpeji
import json, wave, numpy as np
SR, DUR = 48000, 10.0
out = np.zeros(int(SR * DUR))
def add(sig, t, g=1.0):
    i = int(t * SR); n = min(len(sig), len(out) - i)
    if n > 0: out[i:i + n] += sig[:n] * g
def sq(freqs, durs, duty=0.5, dec=None):
    parts = []
    for f, d in zip(freqs, durs):
        n = int(d * SR); tt = np.arange(n) / SR
        f = np.full(n, f) if np.isscalar(f) else np.linspace(f[0], f[1], n)
        ph = np.cumsum(f) / SR % 1.0
        s = np.where(ph < duty, 1.0, -1.0)
        if dec: s *= np.exp(-tt / dec)
        parts.append(s)
    s = np.concatenate(parts); s *= np.minimum(1, np.arange(len(s)) / 60) * np.minimum(1, (len(s) - np.arange(len(s))) / 200)
    return s
def tri(f, d):
    n = int(d * SR); ph = np.arange(n) * f / SR % 1.0; return (4 * np.abs(ph - 0.5) - 1) * np.exp(-np.arange(n) / SR / (d * 0.6))
for e in json.load(open('events.json')):
    k, t = e['k'], e['t']
    if k == 'jump': add(sq([(260, 780)], [0.14], 0.25), t, 0.18)
    elif k == 'hop': add(sq([(330, 900)], [0.09], 0.25), t, 0.16)
    elif k == 'coin': add(sq([988, 1319], [0.07, 0.28], 0.5, 0.12), t, 0.16)
    elif k == 'bump': add(tri(110, 0.12), t, 0.5); add(sq([(220, 110)], [0.08], 0.5), t, 0.1)
    elif k == 'stomp': add(sq([(600, 150)], [0.12], 0.125), t, 0.18)
    elif k == 'select': add(sq([1047, 1568, 2093], [0.06, 0.06, 0.2], 0.5, 0.15), t, 0.14)
    elif k == 'fanfare':
        notes = [523, 659, 784, 1047, 784, 1047]; ds = [0.1, 0.1, 0.1, 0.22, 0.1, 0.5]
        add(sq(notes, ds, 0.25), t, 0.13); add(sq([n / 2 for n in notes], ds, 0.5), t, 0.07)
    elif k == 'iris': add(sq([(880, 220)], [0.5], 0.5, 0.3), t, 0.1)
out = np.tanh(out * 1.2) * 0.85
pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
w = wave.open('ses.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes()); w.close()
print('ses.wav ok')
