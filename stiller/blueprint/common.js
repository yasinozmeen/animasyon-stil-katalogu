// ---- ortak yardımcılar ----
const W = 1920, H = 1080;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const eio2 = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
const eout = t => 1 - Math.pow(1 - t, 3);
const ein = t => t * t * t;
const eback = (t, s = 1.70158) => { t = clamp(t); return 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2); };
function rng(seed) { let s = (seed >>> 0) || 1; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
function mk(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
const UR_LATIN = 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';
const UR_EXT = 'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF';
function loadFont(fam, file, weight, style = 'normal') {
  return Promise.all([['latin', UR_LATIN], ['latin-ext', UR_EXT]].map(([sub, ur]) => {
    const f = new FontFace(fam, `url(fonts/${file}-${sub}.woff2)`, { weight: String(weight), style, unicodeRange: ur });
    document.fonts.add(f); return f.load();
  }));
}
// Polyline yolu: noktalar + kümülatif uzunluk
class Path {
  constructor() { this.p = []; }
  M(x, y) { this.p.push([x, y]); return this; }
  L(x, y, n) { const [a, b] = this.p[this.p.length - 1]; n = n || Math.max(2, Math.ceil(Math.hypot(x - a, y - b) / 4)); for (let i = 1; i <= n; i++) this.p.push([lerp(a, x, i / n), lerp(b, y, i / n)]); return this; }
  C(x1, y1, x2, y2, x, y, n = 40) { const [a, b] = this.p[this.p.length - 1]; for (let i = 1; i <= n; i++) { const t = i / n, u = 1 - t; this.p.push([u*u*u*a + 3*u*u*t*x1 + 3*u*t*t*x2 + t*t*t*x, u*u*u*b + 3*u*u*t*y1 + 3*u*t*t*y2 + t*t*t*y]); } return this; }
  Q(x1, y1, x, y, n = 30) { const [a, b] = this.p[this.p.length - 1]; for (let i = 1; i <= n; i++) { const t = i / n, u = 1 - t; this.p.push([u*u*a + 2*u*t*x1 + t*t*x, u*u*b + 2*u*t*y1 + t*t*y]); } return this; }
  A(cx, cy, rx, ry, a0, a1, n) { n = n || Math.max(8, Math.ceil(Math.abs(a1 - a0) * Math.max(rx, ry) / 4)); for (let i = 0; i <= n; i++) { const a = lerp(a0, a1, i / n); const q = [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]; if (i === 0 && this.p.length) this.L(q[0], q[1]); else this.p.push(q); } return this; }
  // Catmull-Rom (centripetal) noktalardan geçen eğri
  S(pts, n = 16) { const P = this.p.length ? [this.p[this.p.length - 1], ...pts] : pts; if (!this.p.length) this.p.push(P[0]);
    for (let i = 0; i < P.length - 1; i++) { const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
      const d = (a, b) => Math.pow(Math.hypot(b[0] - a[0], b[1] - a[1]) || 1e-3, 0.5);
      const t0 = 0, t1 = t0 + d(p0, p1), t2 = t1 + d(p1, p2), t3 = t2 + d(p2, p3);
      for (let k = 1; k <= n; k++) { const t = lerp(t1, t2, k / n);
        const A1 = p0.map((v, j) => (t1 - t) / (t1 - t0) * v + (t - t0) / (t1 - t0) * p1[j]);
        const A2 = p1.map((v, j) => (t2 - t) / (t2 - t1) * v + (t - t1) / (t2 - t1) * p2[j]);
        const A3 = p2.map((v, j) => (t3 - t) / (t3 - t2) * v + (t - t2) / (t3 - t2) * p3[j]);
        const B1 = A1.map((v, j) => (t2 - t) / (t2 - t0) * v + (t - t0) / (t2 - t0) * A2[j]);
        const B2 = A2.map((v, j) => (t3 - t) / (t3 - t1) * v + (t - t1) / (t3 - t1) * A3[j]);
        this.p.push(B1.map((v, j) => (t2 - t) / (t2 - t1) * v + (t - t1) / (t2 - t1) * B2[j])); } }
    return this; }
  jitter(amp, seed, freq = 0.012) { const r = rng(seed); const ph = [r() * 9, r() * 9, r() * 9, r() * 9]; this.done();
    this.p = this.p.map(([x, y], i) => { const s = this.cum[i]; return [x + amp * (Math.sin(s * freq + ph[0]) * .7 + Math.sin(s * freq * 2.3 + ph[1]) * .3), y + amp * (Math.sin(s * freq * 1.1 + ph[2]) * .7 + Math.sin(s * freq * 2.7 + ph[3]) * .3)]; });
    return this.done(); }
  done() { this.cum = [0]; for (let i = 1; i < this.p.length; i++) this.cum.push(this.cum[i - 1] + Math.hypot(this.p[i][0] - this.p[i - 1][0], this.p[i][1] - this.p[i - 1][1])); this.len = this.cum[this.cum.length - 1]; return this; }
  at(s) { s = clamp(s, 0, this.len); let lo = 0, hi = this.cum.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (this.cum[m] < s) lo = m; else hi = m; }
    const f = (s - this.cum[lo]) / ((this.cum[hi] - this.cum[lo]) || 1); const a = this.p[lo], b = this.p[hi];
    return { x: lerp(a[0], b[0], f), y: lerp(a[1], b[1], f), ang: Math.atan2(b[1] - a[1], b[0] - a[0]), i: lo }; }
  // [s0,s1] aralığını ctx yoluna ekler
  trace(c, s0, s1) { if (s1 <= s0) return null; const A = this.at(s0), B = this.at(s1); c.moveTo(A.x, A.y);
    for (let i = A.i + 1; i <= B.i; i++) c.lineTo(this.p[i][0], this.p[i][1]); c.lineTo(B.x, B.y); return B; }
  resample(N) { this.done(); const q = []; for (let i = 0; i < N; i++) { const a = this.at(this.len * i / (N - 1)); q.push([a.x, a.y]); } const o = new Path(); o.p = q; return o.done(); }
}
const P = () => new Path();
