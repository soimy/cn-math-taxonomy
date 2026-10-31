#!/usr/bin/env node
/* Issue #21：函数的概念诊断截图——答对第 1 题后继续，连对 3 题后到结果页。 */
'use strict';
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');
const WebSocket = globalThis.WebSocket || require('undici').WebSocket;
const E = require('../diagnose/engine.js');

const ROOT = path.join(__dirname, '..');
const OUT = process.env.OUT || '/workspace/shots-21';
const PORT = parseInt(process.env.PORT || '8766', 10);
const DEBUG_PORT = parseInt(process.env.DEBUG_PORT || '9334', 10);
const BASE = 'http://127.0.0.1:' + PORT;
const SEED = 'issue21';
const TOPIC = 'cnm_h027';

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function findChrome() {
  const c = process.env.CHROME || [
    '/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/usr/bin/chromium-browser', '/usr/bin/chromium'
  ].find((p) => fs.existsSync(p));
  if (!c) throw new Error('找不到 Chrome');
  return c;
}
function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => { let b = ''; res.on('data', (c) => (b += c)); res.on('end', () => { try { resolve(JSON.parse(b)); } catch (e) { reject(e); } }); }).on('error', reject);
  });
}
function fetchOk(url) { return fetch(url).then((r) => r.ok, () => false); }
async function waitFor(fn, what, ms) {
  const end = Date.now() + (ms || 20000);
  for (;;) {
    try { const v = await fn(); if (v) return v; } catch (e) { /* retry */ }
    if (Date.now() > end) throw new Error('等待超时：' + what);
    await sleep(120);
  }
}
class CDP {
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map(); ws.addEventListener('message', (m) => this.onMessage(m.data)); }
  static async connect(url) {
    const ws = new WebSocket(url);
    await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
    return new CDP(ws);
  }
  onMessage(data) {
    const msg = JSON.parse(data);
    if (msg.id && this.pending.has(msg.id)) {
      const { resolve, reject } = this.pending.get(msg.id);
      this.pending.delete(msg.id);
      if (msg.error) reject(new Error(msg.error.message)); else resolve(msg.result);
    }
  }
  send(method, params) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params: params || {} }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const topics = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/topics.json'), 'utf8'));
  const deps = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/dependencies.json'), 'utf8'));
  const questions = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/questions.json'), 'utf8'));
  const G = E.buildGraph(topics, deps, questions);
  let sess = E.createSession(G, [TOPIC], { seed: SEED, confirm: 3, limit: 16 });
  const plan = [];
  for (let i = 0; i < 8; i++) {
    const it = E.nextItem(G, sess);
    if (!it) break;
    plan.push({ attempt: it.attempt, q: it.question });
    sess = E.applyAnswer(G, sess, it.topicId, 'correct');
  }
  if (plan.length < 3) throw new Error('预期至少连对 3 题，实际 ' + plan.length);
  console.log('plan:', plan.map((p) => p.q.id + '@' + p.attempt).join(', '));

  const chromePath = findChrome();
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'cnm-21-'));
  const server = spawn('python3', ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
  const chrome = spawn(chromePath, [
    '--headless=new', '--remote-debugging-port=' + DEBUG_PORT, '--user-data-dir=' + profile,
    '--window-size=1280,900', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage', 'about:blank'
  ], { stdio: 'ignore' });

  const cleanup = () => { try { chrome.kill(); } catch (e) {} try { server.kill(); } catch (e) {} };
  process.on('exit', cleanup);

  try {
    await waitFor(() => fetchOk(BASE + '/diagnose/engine.js'), 'http.server');
    const page = await waitFor(async () => {
      const list = await getJson('http://127.0.0.1:' + DEBUG_PORT + '/json/list');
      return list.find((t) => t.type === 'page');
    }, 'Chrome');
    const cdp = await CDP.connect(page.webSocketDebuggerUrl);
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });

    const evalJs = async (expression) => {
      const r = await cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.text || 'eval error');
      return r.result.value;
    };
    const goto = async (url) => {
      await cdp.send('Page.navigate', { url });
      await waitFor(() => evalJs('document.readyState === "complete"'), 'load');
      await sleep(200);
    };
    const exists = (sel) => evalJs('!!document.querySelector(' + JSON.stringify(sel) + ')');
    const click = async (sel) => {
      await evalJs('document.querySelector(' + JSON.stringify(sel) + ').click()');
      await sleep(150);
    };
    const shot = async (name) => {
      const r = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: 0, y: 0, width: 1280, height: 900, scale: 1 } });
      const file = path.join(OUT, name);
      fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
      console.log('  shot', file);
      return file;
    };
    const answerCurrent = async (q) => {
      if (q.type === 'choice') {
        await waitFor(() => exists('#choice-' + q.answer), '选项 ' + q.answer);
        await click('#choice-' + q.answer);
        await click('#btn-submit');
      } else {
        await waitFor(() => exists('#ans'), '输入框');
        await evalJs('(() => { const i = document.getElementById("ans"); i.value = ' + JSON.stringify(String(q.answer)) + '; i.dispatchEvent(new Event("input", { bubbles: true })); })()');
        await click('#btn-submit');
      }
      await waitFor(() => exists('#btn-next') || exists('#btn-right'), '判题后按钮');
      if (await exists('#btn-next')) await click('#btn-next');
      else if (await exists('#btn-right')) await click('#btn-right');
      await sleep(200);
    };

    await goto(BASE + '/diagnose/');
    await evalJs('localStorage.clear()');
    await evalJs('localStorage.setItem("cnmDiagnose.settings.v2", JSON.stringify({ confirm: 3, limit: 16 }))');
    await goto(BASE + '/diagnose/?target=' + TOPIC + '&seed=' + SEED);
    await waitFor(() => exists('.q-text'), '第 1 题');
    let tag = await evalJs('Array.from(document.querySelectorAll(".tag")).map(e => e.textContent).join("|")');
    console.log('  tags1', tag);
    if (!/本知识点第 1 \/ 3 题/.test(tag)) throw new Error('期望第 1/3 题，得到 ' + tag);

    // 答对第 1 题，应继续第 2 题（核心回归）
    await answerCurrent(plan[0].q);
    await waitFor(async () => (await exists('.q-text')) && !(await exists('#summary')), '答对第 1 题后继续');
    if (await exists('#summary')) throw new Error('答对第 1 题后不应进入结果页');
    tag = await evalJs('Array.from(document.querySelectorAll(".tag")).map(e => e.textContent).join("|")');
    console.log('  tags2', tag);
    if (!/本知识点第 2 \/ 3 题/.test(tag)) throw new Error('期望第 2/3 题，得到 ' + tag);
    const reason = await evalJs('document.querySelector(".reason") && document.querySelector(".reason").textContent');
    console.log('  reason2', reason);
    await shot('01-after-q1-continues.png');

    // 答对第 2、第 3 题 → 结果页
    await answerCurrent(plan[1].q);
    await waitFor(() => exists('.q-text'), '第 3 题');
    tag = await evalJs('Array.from(document.querySelectorAll(".tag")).map(e => e.textContent).join("|")');
    console.log('  tags3', tag);
    if (!/本知识点第 3 \/ 3 题/.test(tag)) throw new Error('期望第 3/3 题，得到 ' + tag);
    await shot('02-on-q3.png');
    await answerCurrent(plan[2].q);
    await waitFor(() => exists('#summary'), '结果页');
    const headline = await evalJs('document.querySelector("#summary h2") && document.querySelector("#summary h2").textContent');
    const mastered = await evalJs('document.querySelector("#mastered summary") && document.querySelector("#mastered summary").textContent');
    console.log('  headline', headline);
    console.log('  mastered', mastered);
    await shot('03-result-after-3.png');

    // 开始页设置控件
    await goto(BASE + '/diagnose/');
    await waitFor(() => exists('#confirm-select'), '确认题数选择');
    const opts = await evalJs('Array.from(document.querySelectorAll("#confirm-select option")).map(o => o.value + ":" + o.selected)');
    console.log('  confirm options', opts);
    await shot('04-start-confirm-setting.png');

    console.log('OK');
  } finally {
    cleanup();
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
