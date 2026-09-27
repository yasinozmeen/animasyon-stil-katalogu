# python3 synth.py events.json out.wav dur  — kısa sentez sesler (pop/blip/bloop/thud/tick/chime/boing/clack)
import json, sys, numpy as np, wave
ev, out, dur = json.load(open(sys.argv[1])), sys.argv[2], float(sys.argv[3])
SR = 48000; buf = np.zeros(int(SR * (dur + 0.5)))
def env(n, dec): t = np.arange(n) / SR; a = np.minimum(1, t / 0.004); return a * np.exp(-t / dec)
def sweep(f0, f1, d, dec, shape=np.sin):
    n = int(SR * d); t = np.arange(n) / SR; f = f0 * (f1 / f0) ** (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    return shape(ph) * env(n, dec)
def gen(kind, p):
    if kind == 'pop': return sweep(p.get('f', 900), p.get('f', 900) * 0.45, 0.09, 0.03)
    if kind == 'blip': return sweep(p.get('f', 1200), p.get('f', 1200), 0.12, 0.035)
    if kind == 'bloop': return sweep(p.get('f', 300), p.get('f', 300) * 2.4, 0.16, 0.06)
    if kind == 'bloopdn': return sweep(p.get('f', 700), p.get('f', 700) * 0.4, 0.2, 0.07)
    if kind == 'thud': return sweep(p.get('f', 110), p.get('f', 110) * 0.6, 0.3, 0.09)
    if kind == 'tick': return sweep(p.get('f', 2400), p.get('f', 2400), 0.03, 0.006)
    if kind == 'clack': return sweep(p.get('f', 1600), p.get('f', 1600) * 0.7, 0.05, 0.012, lambda x: np.sign(np.sin(x)) * 0.5)
    if kind == 'chime':
        n = int(SR * 0.9); t = np.arange(n) / SR; f = p.get('f', 880)
        return (np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*f*1.5*t) + 0.25*np.sin(2*np.pi*f*2.01*t)) / 1.75 * env(n, 0.28)
    if kind == 'boing':
        n = int(SR * 0.35); t = np.arange(n) / SR; f0 = p.get('f', 260)
        f = f0 * (1 + 0.6 * np.exp(-t * 9) * np.sin(2 * np.pi * 14 * t)); ph = 2 * np.pi * np.cumsum(f) / SR
        return np.sin(ph) * env(n, 0.12)
    raise ValueError(kind)
for e in ev:
    s = gen(e['k'], e) * e.get('v', 0.5); i = int(e['t'] * SR); j = min(len(buf), i + len(s)); buf[i:j] += s[:j - i]
buf = buf[:int(SR * dur)]
# gentle tail fade + soft limiter
fl = int(SR * 0.3); buf[-fl:] *= np.linspace(1, 0, fl)
buf = np.tanh(buf * 1.1) * 0.8
st = np.stack([buf, buf], 1); pcm = (st * 32767).astype('<i2')
w = wave.open(out, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('wrote', out, len(ev), 'events')
