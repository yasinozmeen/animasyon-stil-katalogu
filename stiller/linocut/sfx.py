# kısa sentez sesler (hışırtı/whoosh yok): python3 sfx.py events.json out.wav dur
import json, sys, numpy as np, wave
SR = 48000
ev, outp, dur = json.load(open(sys.argv[1])), sys.argv[2], float(sys.argv[3])
buf = np.zeros(int(SR * dur) + SR)
def env(n, a=0.002, d=0.08):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def sweep(f0, f1, ms, d, harm=0.0):
    n = int(SR * ms / 1000); t = np.arange(n) / SR; f = f0 * (f1 / f0) ** (t / (ms / 1000))
    ph = 2 * np.pi * np.cumsum(f) / SR; x = np.sin(ph) + harm * np.sin(2 * ph); return x * env(n, 0.002, d)
def mix(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o
S = {
 'tap':   lambda g, f: mix(0.9 * sweep(f or 140, 70, 90, 0.035), 0.15 * sweep(1800, 1500, 8, 0.002)),
 'pop':   lambda g, f: sweep(f or 320, (f or 320) * 2.2, 60, 0.03, 0.2),
 'tick':  lambda g, f: sweep(f or 2600, (f or 2600) * .9, 14, 0.004),
 'bip':   lambda g, f: sweep(f or 880, f or 880, 110, 0.06, 0.1),
 'thump': lambda g, f: mix(sweep(f or 95, 45, 220, 0.08, 0.3), 0.2 * sweep(700, 300, 25, 0.006)),
 'plop':  lambda g, f: sweep(f or 520, (f or 520) * .32, 110, 0.045, 0.15),
 'squish':lambda g, f: sweep(f or 200, (f or 200) * 1.6, 140, 0.06, 0.35),
 'chime': lambda g, f: mix(*[sweep((f or 660) * k, (f or 660) * k, 900, 0.35 / k) / k for k in (1, 2, 3)]),
}
for e in ev:
    x = S[e['type']](e.get('gain', 1), e.get('f')) * e.get('gain', 1)
    i = int(e['t'] * SR); buf[i:i + len(x)] += x[:len(buf) - i]
# hafif oda yankısı (sıcaklık)
out = buf.copy()
for dl, g in ((0.043, .18), (0.071, .12), (0.113, .07)): k = int(dl * SR); out[k:] += buf[:-k] * g
out = out[:int(SR * dur)]; m = np.max(np.abs(out)) or 1; out = out / m * 0.5
st = np.stack([out, out], 1); d = (st * 32767).astype(np.int16)
w = wave.open(outp, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes()); w.close()
print('ok', outp)
