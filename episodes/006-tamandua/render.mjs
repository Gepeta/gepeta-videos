// uso: node render.mjs preview t1,t2,...   |   node render.mjs video out.mp4 [frameIni frameFim]
import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import fs from 'fs';
const [mode, arg, f0, f1] = process.argv.slice(2);
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new',
  args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files'] });
const p = await b.newPage();
p.on('console', m => console.log('PAGE', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
await p.setViewport({ width: 1080, height: 1920 });
await p.goto('file:///home/claude/tamandua/index.html' + (process.env.Q || ''));
await p.waitForFunction('document.title==="ready"', { timeout: 120000 });
const total = await p.evaluate('window.TOTAL');
console.log('total', total, JSON.stringify(await p.evaluate('window.SHOTS')));
if (mode === 'preview') {
  for (const t of arg.split(',').map(Number)) {
    const d = await p.evaluate(t => window.renderAt(t), t);
    fs.writeFileSync(`prev_${t}.jpg`, Buffer.from(d.split(',')[1], 'base64'));
  }
} else {
  const N = Math.round(total * 30); const a = f0 ? +f0 : 0, z = f1 ? Math.min(+f1, N) : N;
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', '30', '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', arg + '.tmp.mp4']);
  const t0 = Date.now();
  for (let f = a; f < z; f++) {
    const d = await p.evaluate(t => window.renderAt(t), f / 30);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log('frame', f, '/', z, ((Date.now() - t0) / (f - a + 1)).toFixed(0), 'ms/f');
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); fs.renameSync(arg + '.tmp.mp4', arg); console.log('done', arg);
}
await b.close();
