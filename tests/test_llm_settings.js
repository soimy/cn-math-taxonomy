#!/usr/bin/env node
/* 直连百炼的设置层测试：node tests/test_llm_settings.js
 *
 * 纯 Node、无浏览器、不联网：自己塞一个假 localStorage，靠删除 require.cache
 * 重新加载 diagnose/llm-config.js，覆盖「保存 → 刷新生效 / 坏配置回退 / 清除」
 * 以及设置页与请求点的静态安全约束。
 */
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');

let passed = 0;
let failed = 0;
function test(name, fn) {
  try { fn(); passed++; console.log('  ok   ' + name); }
  catch (e) { failed++; console.log('  FAIL ' + name + '\n       ' + (e && e.stack || e).split('\n').slice(0, 5).join('\n       ')); }
}

const ROOT = path.join(__dirname, '..');
const CONFIG_PATH = path.join(ROOT, 'diagnose', 'llm-config.js');
const STORE_KEY = 'cnmDiagnose.llm';
const LEGACY_KEY = 'cnmDiagnose.llmBase';

function makeStorage(initial) {
  const map = Object.assign({}, initial || {});
  return {
    getItem: function (k) {
      return Object.prototype.hasOwnProperty.call(map, k) ? map[k] : null;
    },
    setItem: function (k, v) { map[k] = String(v); },
    removeItem: function (k) { delete map[k]; },
    _map: map
  };
}

function loadFresh() {
  delete require.cache[require.resolve(CONFIG_PATH)];
  return require(CONFIG_PATH);
}

/** 每个用例独立的 localStorage；结束后恢复原样（Node 默认没有）。 */
function withStorage(fn, initial) {
  const had = Object.prototype.hasOwnProperty.call(global, 'localStorage');
  const prev = global.localStorage;
  global.localStorage = makeStorage(initial);
  try { return fn(); }
  finally {
    if (had) global.localStorage = prev;
    else delete global.localStorage;
  }
}

const PRESET = {
  label: '阿里云百炼',
  base: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  model: 'qwen3.8-flash',
  altModels: ['qwen3.8-flash', 'qwen3.8-27b']
};
const DEFAULT_MODEL = 'DeepSeek-V4.1-Flash-1017-Unlimited';

/* ================================================================
 * 1. 预设表
 * ================================================================ */

console.log('\n--- 预设表 ---');

test('PRESETS 只有百炼一个预设，字段与约定一致', () => {
  delete global.localStorage;
  const cfg = loadFresh();
  const keys = Object.keys(cfg.PRESETS);
  assert.deepStrictEqual(keys, ['dashscope']);
  const p = cfg.PRESETS.dashscope;
  assert.strictEqual(p.label, PRESET.label);
  assert.strictEqual(p.base, PRESET.base);
  assert.strictEqual(p.model, PRESET.model);
  assert.deepStrictEqual(p.altModels, PRESET.altModels);
});

test('未配置时 model 保持默认型号，resolveBase 走 Node 默认地址', () => {
  delete global.localStorage;
  const cfg = loadFresh();
  assert.strictEqual(cfg.model, DEFAULT_MODEL);
  assert.strictEqual(cfg.isConfigured(), false);
  assert.strictEqual(cfg.resolveBase(), cfg.upstream + '/v1');
  assert.deepStrictEqual(cfg.authHeaders(), {});
});

/* ================================================================
 * 2. 保存 → 刷新生效
 * ================================================================ */

console.log('\n--- 保存与刷新 ---');

test('saveConfig 只给 key 时 base/model 取预设，重新加载后 model/base 生效', () => {
  withStorage(function () {
    const cfg = loadFresh();
    assert.strictEqual(cfg.saveConfig({ key: 'sk-ws-0123456789HGpY' }), true);
    assert.strictEqual(cfg.isConfigured(), true);
    assert.deepStrictEqual(cfg.getConfig(), {
      base: PRESET.base,
      model: PRESET.model,
      key: 'sk-ws-0123456789HGpY'
    });

    const cfg2 = loadFresh();
    assert.strictEqual(cfg2.model, PRESET.model);
    assert.strictEqual(cfg2.isConfigured(), true);
    assert.strictEqual(cfg2.resolveBase(), PRESET.base);
    assert.notStrictEqual(cfg2.resolveBase().slice(-1), '/');
  });
});

test('saveConfig 写入的 base 末尾斜杠会被去掉', () => {
  withStorage(function () {
    const cfg = loadFresh();
    cfg.saveConfig({ base: 'https://example.test/v1///', model: 'm1', key: 'k' });
    assert.strictEqual(cfg.getConfig().base, 'https://example.test/v1');
    assert.strictEqual(cfg.resolveBase(), 'https://example.test/v1');
  });
});

test('?llm= 查询参数优先于已保存配置', () => {
  withStorage(function () {
    const cfg = loadFresh();
    cfg.saveConfig({ base: 'https://saved.test/v1', model: 'm', key: 'k' });
    const hadLoc = Object.prototype.hasOwnProperty.call(global, 'location');
    const prevLoc = global.location;
    global.location = { search: '?llm=' + encodeURIComponent('https://query.test/v1/') };
    try {
      assert.strictEqual(cfg.resolveBase(), 'https://query.test/v1');
    } finally {
      if (hadLoc) global.location = prevLoc;
      else delete global.location;
    }
  });
});

/* ================================================================
 * 3. 鉴权头
 * ================================================================ */

console.log('\n--- authHeaders ---');

test('有 key 返回 Bearer，无 key 返回 {}', () => {
  withStorage(function () {
    const cfg = loadFresh();
    assert.deepStrictEqual(cfg.authHeaders(), {});
    cfg.saveConfig({ key: 'sk-abc' });
    assert.deepStrictEqual(cfg.authHeaders(), { Authorization: 'Bearer sk-abc' });
  });
});

test('没有 localStorage（Node / 隐私模式）时 authHeaders 返回 {} 且不抛', () => {
  delete global.localStorage;
  const cfg = loadFresh();
  assert.deepStrictEqual(cfg.authHeaders(), {});
  assert.strictEqual(cfg.isConfigured(), false);
});

/* ================================================================
 * 4. 脱敏
 * ================================================================ */

console.log('\n--- maskKey ---');

test('maskKey 只露前 5 后 4，中间段不出现', () => {
  delete global.localStorage;
  const cfg = loadFresh();
  const out = cfg.maskKey('sk-ws-0123456789HGpY');
  assert.strictEqual(out, 'sk-ws...HGpY');
  assert.ok(out.indexOf('HGpY') !== -1);
  assert.ok(out.indexOf('0123456789') === -1);
});

test('maskKey 对空串与过短 key 返回空串', () => {
  delete global.localStorage;
  const cfg = loadFresh();
  assert.strictEqual(cfg.maskKey(''), '');
  assert.strictEqual(cfg.maskKey(null), '');
  assert.strictEqual(cfg.maskKey('sk-short'), '');
  assert.strictEqual(cfg.maskKey('12345678901'), '');
});

/* ================================================================
 * 5. 坏配置回退
 * ================================================================ */

console.log('\n--- 坏配置回退 ---');

test('非法 JSON 当作未配置，resolveBase 回退到旧键 cnmDiagnose.llmBase', () => {
  withStorage(function () {
    const cfg = loadFresh();
    localStorage.setItem(STORE_KEY, '{not json');
    localStorage.setItem(LEGACY_KEY, 'https://legacy.test/v1/');
    assert.strictEqual(cfg.getConfig(), null);
    assert.strictEqual(cfg.isConfigured(), false);
    assert.strictEqual(cfg.resolveBase(), 'https://legacy.test/v1');
    assert.strictEqual(cfg.model, DEFAULT_MODEL);
  });
});

test('只有 base 的残缺配置当作未配置，回退旧键，再删旧键回默认', () => {
  withStorage(function () {
    localStorage.setItem(STORE_KEY, JSON.stringify({ base: 'https://partial.test/v1' }));
    localStorage.setItem(LEGACY_KEY, 'https://legacy.test/v1');
    const cfg = loadFresh();
    assert.strictEqual(cfg.isConfigured(), false);
    assert.strictEqual(cfg.resolveBase(), 'https://legacy.test/v1');

    localStorage.removeItem(LEGACY_KEY);
    assert.strictEqual(cfg.resolveBase(), cfg.upstream + '/v1');
  });
});

test('getItem 抛错（隐私模式）时不抛，按未配置处理', () => {
  const had = Object.prototype.hasOwnProperty.call(global, 'localStorage');
  const prev = global.localStorage;
  global.localStorage = {
    getItem: function () { throw new Error('SecurityError'); },
    setItem: function () { throw new Error('SecurityError'); },
    removeItem: function () { throw new Error('SecurityError'); }
  };
  try {
    const cfg = loadFresh();
    assert.strictEqual(cfg.getConfig(), null);
    assert.strictEqual(cfg.isConfigured(), false);
    assert.deepStrictEqual(cfg.authHeaders(), {});
    assert.strictEqual(cfg.model, DEFAULT_MODEL);
    assert.strictEqual(cfg.resolveBase(), cfg.upstream + '/v1');
  } finally {
    if (had) global.localStorage = prev;
    else delete global.localStorage;
  }
});

/* ================================================================
 * 6. 清除
 * ================================================================ */

console.log('\n--- clearConfig ---');

test('clearConfig 后回到默认（未配置 / 默认基址 / 空鉴权头）', () => {
  withStorage(function () {
    const cfg = loadFresh();
    cfg.saveConfig({ key: 'sk-ws-0123456789HGpY' });
    assert.strictEqual(cfg.isConfigured(), true);
    assert.strictEqual(cfg.clearConfig(), true);
    assert.strictEqual(cfg.isConfigured(), false);
    assert.strictEqual(cfg.getConfig(), null);
    assert.strictEqual(cfg.resolveBase(), cfg.upstream + '/v1');
    assert.deepStrictEqual(cfg.authHeaders(), {});

    const cfg2 = loadFresh();
    assert.strictEqual(cfg2.model, DEFAULT_MODEL);
  });
});

/* ================================================================
 * 7. 写入失败
 * ================================================================ */

console.log('\n--- 写入失败 ---');

test('setItem 抛错（配额/隐私模式）时 saveConfig 返回 false', () => {
  const had = Object.prototype.hasOwnProperty.call(global, 'localStorage');
  const prev = global.localStorage;
  global.localStorage = {
    getItem: function () { return null; },
    setItem: function () { throw new Error('QuotaExceededError'); },
    removeItem: function () {}
  };
  try {
    const cfg = loadFresh();
    assert.strictEqual(cfg.saveConfig({ key: 'k' }), false);
    assert.strictEqual(cfg.isConfigured(), false);
  } finally {
    if (had) global.localStorage = prev;
    else delete global.localStorage;
  }
});

/* ================================================================
 * 8. 静态安全扫描
 * ================================================================ */

console.log('\n--- 静态扫描 ---');

function jsFiles(dir) {
  return fs.readdirSync(path.join(ROOT, dir))
    .filter(function (n) { return n.endsWith('.js'); })
    .map(function (n) { return path.join(ROOT, dir, n); });
}

test('diagnose/*.js（除 llm-config.js）与 scripts/*.js 不含百炼地址/型号字面量', () => {
  const files = jsFiles('diagnose').filter(function (p) {
    return path.basename(p) !== 'llm-config.js';
  }).concat(jsFiles('scripts'));
  const bad = [];
  const literals = ['dashscope.aliyuncs.com', 'qwen3.8'];
  for (const file of files) {
    const text = fs.readFileSync(file, 'utf8');
    for (const lit of literals) {
      if (text.indexOf(lit) !== -1) bad.push(path.relative(ROOT, file) + ' 含「' + lit + '」');
    }
  }
  assert.deepStrictEqual(bad, []);
});

test('diagnose/*.html 也不含百炼地址/型号字面量（设置页只从 PRESETS 读）', () => {
  const files = fs.readdirSync(path.join(ROOT, 'diagnose'))
    .filter(function (n) { return n.endsWith('.html'); })
    .map(function (n) { return path.join(ROOT, 'diagnose', n); });
  const bad = [];
  const literals = ['dashscope.aliyuncs.com', 'qwen3.8'];
  for (const file of files) {
    const text = fs.readFileSync(file, 'utf8');
    for (const lit of literals) {
      if (text.indexOf(lit) !== -1) bad.push(path.relative(ROOT, file) + ' 含「' + lit + '」');
    }
  }
  assert.deepStrictEqual(bad, []);
});

/* ================================================================
 * 收尾
 * ================================================================ */

console.log('\n' + (failed === 0 ? '全部通过' : '存在失败') + '：' + passed + ' passed, ' + failed + ' failed');
process.exit(failed === 0 ? 0 : 1);
