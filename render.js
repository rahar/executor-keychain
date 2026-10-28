const C = require('./core.js'); const fs = require('fs');
function wav(fn, data, sr) {
  const b = Buffer.alloc(44 + data.length * 2); b.write('RIFF', 0); b.writeUInt32LE(36 + data.length * 2, 4); b.write('WAVEfmt ', 8);
  b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22); b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34);
  b.write('data', 36); b.writeUInt32LE(data.length * 2, 40);
  for (let i = 0; i < data.length; i++) b.writeInt16LE(Math.max(-32767, Math.min(32767, Math.round(data[i] * 32767))), 44 + i * 2);
  fs.writeFileSync(fn, b);
}
const sr = 44100; fs.mkdirSync('out', { recursive: true });
const lens = [0.38, 7.70, 0.63, 1.66, 0.77, 2.04, 1.24, 2.47]; // same hold times as the recording
const pre = [0.05, 0.03, 0.04, 0.02, 0.02, 0.02, 0.03, 0.0];
let peak = 0;
const all = [];
for (let k = 0; k < 8; k++) {
  const c = new C(sr); const n = Math.round((lens[k] + 0.1) * sr); const out = new Float32Array(n);
  const a = Math.round(pre[k] * sr), b = Math.round((pre[k] + lens[k]) * sr);
  c.render(out.subarray(0, a), a); c.press(k); c.render(out.subarray(a, b), b - a); c.release(k); c.render(out.subarray(b), n - b);
  for (const v of out) peak = Math.max(peak, Math.abs(v));
  all.push(out);
}
console.log('peak', peak);
all.forEach((o, k) => { for (let i = 0; i < o.length; i++) o[i] *= 1; wav('out/s' + (k + 1) + '.wav', o, sr); });
