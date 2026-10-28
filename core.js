// Executor keychain emulator core: mask-ROM sound chip (tone divider + 5-bit LFSR, 1-bit bridged output)
// driving a lumped electro-mechanical speaker model. Pure DSP, no browser APIs.
class ExecutorCore {
  constructor(sampleRate, opts = {}) {
    this.sr = sampleRate;
    this.OS = 4;                       // oversampling factor for the speaker ODE
    this.fs = sampleRate * this.OS;
    this.dt = 1 / this.fs;
    this.p = Object.assign({
      K: 32335,        // chip tick rate (Hz) = Fosc/4, measured from the recording
      sagAmt: 0.09,    // oscillator speed-up right after a press (battery recovered)
      sagTau: 0.10,    // s, battery polarisation under load
      recTau: 1.5,     // s, battery recovery in silence
      vbat: 3.0,       // V (2x LR44 / 3V)
      rint: 6.0,       // ohm, internal resistance of tired button cells
      fsSpk: 720,      // Hz cone resonance
      qms: 1.8,
      fh: 2450,        // Hz front-cavity (grille) Helmholtz resonance
      qh: 4.0,
      portMix: 0.3,
      leak: 0.2,      // rear-leak cancellation strength (notch ~3.5 kHz)
      leakMs: 0.286,
      gain: 1.0,
      trim: 1.0,       // oscillator resistor trim (pitch AND tempo, as on the real chip)
      breakF: 4800, breakDb: 7, panelF: 1000, panelDb: -7,
      lfsrBits: 15,
    }, opts);
    this.buildPrograms();
    this.reset();
  }
  reset() {
    this.prog = -1; this.seg = 0; this.segT = 0; this.mode = 0; this.N = 32;
    this.tc = 0; this.nc = 0; this.lfsr = 0x1; this.bit = 0; this.tickPhase = 0;
    this.sag = 1; this.held = false;
    this.i = 0; this.x = 0; this.v = 0; this.q = 0; this.qv = 0;
    this.dl = new Float32Array(256); this.dlw = 0;
    this.lp1 = [0,0,0,0]; this.lp2 = [0,0,0,0]; this.hpx = 0; this.hpy = 0;
    this.osAcc = 0; this.osN = 0;
    this.lastBit = 0; this.lastV = 0;
    this.designLP();
  }
  ms(t) { return Math.max(1, Math.round(t * this.p.K / 1000)); }
  buildPrograms() {
    const S = [], ms = (t) => this.ms(t);
    const T = (N, d) => [1, N, ms(d)], Nz = (N, d) => [2, N, ms(d)], Z = (d) => [0, 0, ms(d)];
    const tri = (a, b, st) => { const o = []; for (let n = a; n < b; n++) o.push(T(n, st)); for (let n = b; n > a; n--) o.push(T(n, st)); return o; };
    // 1  fast warble: divider swept as a triangle 28..45, one count per 3.2 ms
    // 1  fast warble: frequency swept linearly 1290<->557 Hz (divider 25..58), 120 ms per cycle
    { const K = this.p.K, a = 25, b = 58, rate = (K / a - K / b) / 0.060, o = [];
      const d = (n) => 1000 * (K / (n - 0.5) - K / (n + 0.5)) / rate;
      for (let n = a; n < b; n++) o.push(T(n, d(n))); for (let n = b; n > a; n--) o.push(T(n, d(n)));
      S.push({ name: 'Warble', loop: true, segs: o }); }
    // 2  bomb: falling whistle (N 28->54 by 1, ->66 by 2, 115.6 ms/step), then LFSR explosion
    { const o = []; for (let n = 28; n <= 54; n++) o.push(T(n, 115.6)); for (let n = 56; n <= 66; n += 2) o.push(T(n, 115.6)); o.push(Nz(4, 3860)); S.push({ name: 'Bomb', loop: false, segs: o }); }
    // 3  two-tone: N 64 / 85 (a fourth apart), 150 ms each
    S.push({ name: 'Two-tone', loop: true, segs: [T(64, 150), T(85, 150)] });
    // 4  cannon: LFSR clock divider 5, then slowed 6..16 (rumble dies away)
    { const o = [Nz(4, 100)]; for (let n = 5; n <= 16; n++) o.push(Nz(n, 60)); S.push({ name: 'Cannon', loop: true, segs: o }); }
    // 5  machine gun: LFSR bursts 90 ms on / 13 ms off
    S.push({ name: 'Machine gun', loop: true, segs: [Nz(5, 90), Z(13)] });
    // 6  stepped laser: N 31,32,33,34 at 250 ms
    S.push({ name: 'Step laser', loop: true, segs: [T(31, 250), T(32, 250), T(33, 250), T(34, 250)] });
    // 7  slow siren: triangle 66..111, 3.17 ms per count
    S.push({ name: 'Siren', loop: true, segs: tri(66, 111, 3.17) });
    // 8  space gun: hiss (LFSR /2) then chirp N 24->44 by 1, ->66 by 2, 16.6 ms/step
    { const o = [Nz(2, 270)]; for (let n = 24; n <= 44; n++) o.push(T(n, 16.6)); for (let n = 46; n <= 66; n += 2) o.push(T(n, 16.6)); S.push({ name: 'Space gun', loop: true, segs: o }); }
    this.programs = S;
  }
  press(k) { this.prog = k; this.seg = 0; this.segT = 0; this.held = true; this.loadSeg(); }
  // finish=false: stop looping sounds now (level-hold). finish=true: let the current pass end (one-shot).
  release(k, finish = false) { if (k === undefined || k === this.prog) { this.held = false; if (!finish && this.programs[this.prog] && this.programs[this.prog].loop) this.stop(); } }
  stop() { this.prog = -1; this.mode = 0; }
  loadSeg() { const s = this.programs[this.prog].segs[this.seg]; this.mode = s[0]; this.N = s[1]; this.segT = s[2]; }
  tick() {
    if (this.prog < 0) { this.bit = 0; return 0; }
    if (--this.segT <= 0) {
      const P = this.programs[this.prog];
      this.seg++;
      if (this.seg >= P.segs.length) { if (P.loop && this.held) this.seg = 0; else { this.stop(); return 0; } }
      this.loadSeg();
    }
    if (this.mode === 1) {           // tone: down counter reloaded with N, 1/3 duty
      if (--this.tc <= 0) this.tc = this.N;
      return this.tc > this.N - Math.round(this.N / 3) ? 1 : -1;
    } else if (this.mode === 2) {    // noise: LFSR clocked every N ticks
      if (--this.nc <= 0) { this.nc = this.N; this.clockLfsr(); }
      return (this.lfsr & 1) ? 1 : -1;
    }
    return 0;
  }
  clockLfsr() {          // Fibonacci LFSR, maximal taps for 5/7/15/17 bits
    const n = this.p.lfsrBits, t = { 5: [5, 3], 7: [7, 6], 15: [15, 14], 17: [17, 14] }[n] || [15, 14];
    const b = ((this.lfsr >> (t[0] - 1)) ^ (this.lfsr >> (t[1] - 1))) & 1;
    this.lfsr = ((this.lfsr << 1) | b) & ((1 << n) - 1);
  }
  designLP() {           // two biquads, Butterworth-ish at 0.42*sr, for decimation
    const fc = 0.42 * this.sr, w = 2 * Math.PI * fc / this.fs, c = Math.cos(w), s = Math.sin(w);
    const mk = (Q) => { const a = s / (2 * Q), b0 = (1 - c) / 2, a0 = 1 + a; return [b0 / a0, (1 - c) / a0, b0 / a0, -2 * c / a0, (1 - a) / a0]; };
    this.c1 = mk(0.5412); this.c2 = mk(1.3066);
    // peaking sections: cone break-up mode and case-panel absorption
    const pk = (f0, Q, dB) => { const A = Math.pow(10, dB / 40), w0 = 2 * Math.PI * f0 / this.fs, al = Math.sin(w0) / (2 * Q), cw = Math.cos(w0), a0 = 1 + al / A;
      return [(1 + al * A) / a0, -2 * cw / a0, (1 - al * A) / a0, -2 * cw / a0, (1 - al / A) / a0]; };
    this.cb = pk(this.p.breakF, 1.2, this.p.breakDb); this.cp = pk(this.p.panelF, 1.5, this.p.panelDb);
    this.zb = [0, 0]; this.zp = [0, 0];
  }
  bq(c, z, x) { const y = c[0] * x + z[0]; z[0] = c[1] * x - c[3] * y + z[1]; z[1] = c[2] * x - c[4] * y; return y; }
  // render n output samples into out (Float32Array), also fills scope arrays if given
  render(out, n, scopeBit, scopeP) {
    const p = this.p, OS = this.OS, dt = this.dt;
    const R = 8, L = 0.1e-3, Bl = 0.6, m = 0.15e-3;
    const ws = 2 * Math.PI * p.fsSpk, k = m * ws * ws, Rm = ws * m / p.qms;
    const wh = 2 * Math.PI * p.fh, eRL = Math.exp(-R * dt / L);
    const dly = Math.min(255, Math.round(p.leakMs * 1e-3 * this.fs));
    const g = p.gain * 1.5e-8;
    const hpA = Math.exp(-2 * Math.PI * 100 / this.sr);
    for (let j = 0; j < n; j++) {
      let acc = 0;
      for (let o = 0; o < OS; o++) {
        // battery / oscillator state
        const sounding = this.prog >= 0;
        if (sounding) this.sag -= this.sag * dt / p.sagTau; else this.sag += (1 - this.sag) * dt / p.recTau;
        const vdd = p.vbat - (sounding ? p.rint * Math.abs(this.i) * 0.5 : 0) - 0.15 * (1 - this.sag);
        // advance chip ticks, box-filter the 1-bit value over this oversample
        const rate = p.K * p.trim * (1 + 0.04 * (vdd - 3)) * (1 + p.sagAmt * this.sag) * dt;
        let ph = this.tickPhase, val = 0, left = 1;
        while (ph + left * rate >= 1) { const f = (1 - ph) / rate; val += this.lastBit * f; left -= f; ph = 0; this.lastBit = this.tick(); }
        ph += left * rate; val += this.lastBit * left; this.tickPhase = ph;
        const V = val * vdd;
        // voice coil (exact RL step), cone mass-spring-damper with stiffening suspension
        const iinf = (V - Bl * this.v) / R; this.i = iinf + (this.i - iinf) * eRL;
        const xx = this.x / 0.4e-3;
        const a = (Bl * this.i - Rm * this.v - k * this.x * (1 + 0.6 * xx * xx)) / m;
        this.v += a * dt; this.x += this.v * dt;
        // front cavity: Helmholtz resonator driven by cone velocity
        const qa = wh * wh * (this.v - this.q) - (wh / p.qh) * this.qv;
        this.qv += qa * dt; this.q += this.qv * dt;
        let pr = (1 - p.portMix) * a + p.portMix * qa;
        // rear leak through case seams: delayed, inverted copy
        this.dl[this.dlw] = pr; const rd = this.dl[(this.dlw - dly + 256) & 255]; this.dlw = (this.dlw + 1) & 255;
        pr = pr - p.leak * rd;
        pr = this.bq(this.cp, this.zp, this.bq(this.cb, this.zb, pr));
        acc = this.bq(this.c2, this.lp2, this.bq(this.c1, this.lp1, pr));
        if (scopeBit && o === 0) { scopeBit[j] = val; }
      }
      let y = acc * g;
      const hy = hpA * (this.hpy + y - this.hpx); this.hpx = y; this.hpy = hy;
      out[j] = hy; if (scopeP) scopeP[j] = hy;
    }
  }
}
if (typeof module !== 'undefined') module.exports = ExecutorCore;
