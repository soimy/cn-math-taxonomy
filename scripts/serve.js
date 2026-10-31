#!/usr/bin/env node
/* 开发用静态服务（禁缓存）：node scripts/serve.js [port] [dir]
 *
 * 为什么需要它
 * ------------
 * 本地验收长期用 `python3 -m http.server`。它不发 Cache-Control / ETag / Last-Modified
 * 之类的缓存指令，Chrome 于是按启发式规则把 diagnose/app.js 当成「可以一直用」的资源
 * 长期缓存：curl 和浏览器 fetch 都能拿到新文件，页面执行的却是几小时前的旧代码
 * （performance.getEntriesByType('resource') 里 transferSize: 0 即命中磁盘缓存）。
 * 复核者因此反复误判「功能没做」。本脚本行为等价于 http.server，但对代码与数据文件
 * 强制禁缓存，从根上消除这个假象。
 *
 * 用法
 * ----
 *   node scripts/serve.js              # 端口 8920，服务仓库根目录
 *   node scripts/serve.js 8930         # 指定端口
 *   node scripts/serve.js 8930 docs    # 只服务 docs/（相对路径按 cwd 解析）
 *
 * 同源反代：/v1/* 转发到 diagnose/llm-config.js 里的 upstream（默认本机 3000 端口），
 * 浏览器只和本服务同源通信，不再依赖网关的 CORS 头。上游连不上/超时 → 502 JSON。
 *
 * 零依赖：只 require Node 标准库（http / https / fs / path / url）。
 */
'use strict';

const http = require('http');
const https = require('https');
const fs = require('fs');
const fsp = fs.promises;
const path = require('path');
const LLMConfig = require('../diagnose/llm-config.js');

/** 需要强制禁缓存的扩展名（代码与数据：改了就必须立刻生效） */
const NO_CACHE_EXT = new Set(['.js', '.mjs', '.css', '.html', '.htm', '.json', '.map']);

/** 禁缓存响应头：no-store 是硬约束，其余为兼容老浏览器/中间层 */
const NO_CACHE_HEADERS = {
  'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
  'Pragma': 'no-cache',
  'Expires': '0',
};

/** Content-Type 表。`.js` 必须是 text/javascript，否则 ES module 会被拒绝执行 */
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.pdf': 'application/pdf',
  '.wasm': 'application/wasm',
};

function contentTypeOf(filePath) {
  return MIME[path.extname(filePath).toLowerCase()] || 'application/octet-stream';
}

/** 响应头：所有静态资源一律 no-store（开发服务不需要磁盘缓存，简单优先）。
 *  NO_CACHE_EXT 列出的代码与数据文件是硬要求，其余扩展名跟随同一策略。 */
function baseHeaders(filePath) {
  const h = {
    'Content-Type': contentTypeOf(filePath),
    'X-Content-Type-Options': 'nosniff',
  };
  Object.assign(h, NO_CACHE_HEADERS);
  return h;
}

function sendText(res, status, text, extra) {
  if (res.writableEnded) return;
  const body = Buffer.from(text, 'utf8');
  res.writeHead(status, Object.assign({
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Length': String(body.length),
  }, NO_CACHE_HEADERS, extra || {}));
  res.end(body);
}

function sendJson(res, status, obj) {
  if (res.writableEnded || res.headersSent) return;
  const body = Buffer.from(JSON.stringify(obj), 'utf8');
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': String(body.length),
  });
  res.end(body);
}

/* /v1 反代的上游超时。必须远大于 route 侧 60s：route 自己会 abort 并给出超时错误，
 * 反代若先掐断，会把「60s 的长推理正常等待」误判成 502，也拿不到上游的真实失败原因。 */
const PROXY_TIMEOUT_MS = 120000;

/**
 * 把 /v1/* 同源转发到 LLMConfig.upstream：method / 请求体 / 必要请求头原样过去，
 * 响应状态码、content-type、响应体流式回写（不缓冲整个 body）。
 * 上游连不上 / 超时 → 502 JSON；用 settled + res.headersSent 保证只回一次响应。
 */
function proxyV1(req, res, pathname, search) {
  let target;
  try {
    target = new URL(LLMConfig.upstream + pathname + search);
  } catch (e) {
    sendJson(res, 502, {
      error: 'upstream unreachable',
      upstream: LLMConfig.upstream,
      reason: (e && e.message) || String(e),
    });
    return;
  }

  let settled = false;
  function fail(reason) {
    if (settled) return;
    settled = true;
    if (res.headersSent || res.writableEnded) {
      try { res.destroy(); } catch (e) { /* ignore */ }
      return;
    }
    sendJson(res, 502, {
      error: 'upstream unreachable',
      upstream: LLMConfig.upstream,
      reason: String(reason == null ? 'unknown' : reason),
    });
  }

  const headers = {};
  if (req.headers['content-type']) headers['content-type'] = req.headers['content-type'];
  if (req.headers['authorization']) headers['authorization'] = req.headers['authorization'];
  if (req.headers['content-length']) headers['content-length'] = req.headers['content-length'];

  const mod = target.protocol === 'https:' ? https : http;
  let proxyReq;
  try {
    proxyReq = mod.request({
      protocol: target.protocol,
      hostname: target.hostname,
      port: target.port || (target.protocol === 'https:' ? 443 : 80),
      method: req.method,
      path: target.pathname + target.search,
      headers: headers,
    }, function (upRes) {
      if (settled || res.headersSent) {
        upRes.resume();
        return;
      }
      settled = true;
      res.writeHead(upRes.statusCode || 502, {
        'Content-Type': upRes.headers['content-type'] || 'application/octet-stream',
      });
      upRes.on('error', function () {
        try { res.destroy(); } catch (e) { /* ignore */ }
      });
      upRes.pipe(res);
    });
  } catch (e) {
    fail((e && e.code) || (e && e.message) || e);
    return;
  }

  proxyReq.setTimeout(PROXY_TIMEOUT_MS, function () {
    fail('ETIMEDOUT');
    try { proxyReq.destroy(); } catch (e) { /* ignore */ }
  });
  proxyReq.on('error', function (err) {
    fail((err && err.code) || (err && err.message) || err);
  });
  req.on('error', function (err) {
    fail((err && err.code) || (err && err.message) || err);
  });
  req.pipe(proxyReq);
}

/**
 * 把 URL 里的 pathname 映射成磁盘绝对路径，并做越界检查。
 * 返回 { ok: true, filePath, isDir } 或 { ok: false, status, message }。
 *
 * 安全要点：先 decodeURIComponent 再 normalize/resolve，否则 %2e%2e 能绕过 `../` 检查；
 * resolve 之后必须落在 root 之内（等于 root 或 root + sep 开头）。
 */
function resolveRequestPath(root, rawPathname) {
  let pathname;
  try {
    pathname = decodeURIComponent(rawPathname);
  } catch (e) {
    return { ok: false, status: 400, message: '400 Bad Request（URL 编码非法）' };
  }
  if (pathname.indexOf('\0') !== -1) {
    return { ok: false, status: 400, message: '400 Bad Request' };
  }
  // 去掉开头的斜杠，统一按相对路径交给 path.resolve（绝对路径前缀一律剥掉，不允许指向 root 之外）
  const rel = pathname.replace(/^\/+/, '');
  const target = path.resolve(root, rel);
  if (target !== root && !target.startsWith(root + path.sep)) {
    return { ok: false, status: 403, message: '403 Forbidden（路径越界）' };
  }
  return { ok: true, filePath: target };
}

/** 建服务实例（测试里直接调用，不依赖进程参数） */
function createServer(options) {
  const opts = options || {};
  const root = path.resolve(opts.dir || path.resolve(__dirname, '..'));
  const quiet = !!opts.quiet;
  const log = quiet ? function () {} : function (line) { console.log(line); };

  const server = http.createServer(function (req, res) {
    let pathname = '/';
    let search = '';
    try {
      // 用完整 URL 拼一个假 origin，避免 req.url 是绝对形式时解析失败
      const u = new URL(req.url, 'http://localhost');
      pathname = u.pathname;
      search = u.search;
    } catch (e) {
      sendText(res, 400, '400 Bad Request');
      return;
    }

    /* /v1/* 同源反代必须在方法白名单之前：POST /v1/chat/completions 不能被 405 挡住 */
    if (pathname.indexOf('/v1/') === 0) {
      proxyV1(req, res, pathname, search);
      return;
    }

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      sendText(res, 405, '405 Method Not Allowed', { Allow: 'GET, HEAD' });
      return;
    }

    const resolved = resolveRequestPath(root, pathname);
    if (!resolved.ok) {
      sendText(res, resolved.status, resolved.message);
      return;
    }
    let filePath = resolved.filePath;

    fsp.stat(filePath).then(function (st) {
      if (st.isDirectory()) {
        if (!pathname.endsWith('/')) {
          // 目录不带斜杠：重定向到带斜杠，保证相对路径解析正确
          res.writeHead(301, Object.assign({ Location: pathname + '/' }, NO_CACHE_HEADERS));
          res.end();
          return null;
        }
        filePath = path.join(filePath, 'index.html');
        return fsp.stat(filePath);
      }
      return st;
    }).then(function (st) {
      if (st === null) return null; // 已重定向
      if (!st.isFile()) {
        sendText(res, 404, '404 Not Found: ' + pathname);
        return null;
      }
      return fsp.readFile(filePath).then(function (body) {
        // baseHeaders 已含 no-store；Content-Length 一起下发，HEAD 与 GET 头一致
        const headers = Object.assign({ 'Content-Length': String(body.length) }, baseHeaders(filePath));
        res.writeHead(200, headers);
        if (req.method === 'HEAD') res.end(); else res.end(body);
        return null;
      });
    }).catch(function (err) {
      const code = err && err.code;
      if (code === 'ENOENT' || code === 'ENOTDIR' || code === 'EISDIR') {
        sendText(res, 404, '404 Not Found: ' + pathname);
      } else {
        log('  读失败 ' + pathname + ' → ' + (code || err));
        sendText(res, 500, '500 Internal Server Error');
      }
    });
  });

  server.root = root;
  return server;
}

function main(argv) {
  const port = Number(argv[0] === undefined ? 8920 : argv[0]);
  if (!Number.isInteger(port) || port < 0 || port > 65535) {
    console.error('错误：端口必须是 0–65535 的整数，收到 ' + JSON.stringify(argv[0]));
    process.exit(2);
  }
  const dir = path.resolve(argv[1] || path.resolve(__dirname, '..'));
  let stat;
  try {
    stat = fs.statSync(dir);
  } catch (e) {
    console.error('错误：目录不存在 ' + dir);
    process.exit(2);
  }
  if (!stat.isDirectory()) {
    console.error('错误：不是目录 ' + dir);
    process.exit(2);
  }

  const server = createServer({ dir: dir });

  /* 端口占用检测要显式指定监听地址：
   * Node 在 host 省略时走 getaddrinfo 顺序（本机 localhost 先解析到 ::1），双栈 listen 请求
   * err,address 时会异步重试另一个地址，导致「绑上了但永远不回 listen 回调」的静默挂起——
   * 明明端口被占，进程却不报错也不退出。这里固定 127.0.0.1（浏览器访问 localhost 会命中），
   * 一次绑定、一次成败，EADDRINUSE 立刻可见。 */
  const host = '127.0.0.1';

  server.on('error', function (err) {
    let msg;
    if (err && err.code === 'EADDRINUSE') {
      msg = '错误：端口 ' + port + ' 已被占用（EADDRINUSE），换一个端口，例如 node scripts/serve.js ' + (port + 1);
    } else if (err && err.code === 'EACCES') {
      msg = '错误：没有权限监听端口 ' + port + '（EACCES）';
    } else {
      msg = '错误：服务启动失败 ' + (err && err.code ? err.code + ' ' : '') + (err && err.message);
    }
    // 先 close 再退出：让 close 回调里的写盘/管道 flush 完成，输出不会被 process.exit 截断
    server.close(function () {
      console.error(msg);
      process.exit(1);
    });
  });

  server.listen(port, host, function () {
    const actual = server.address().port;
    console.log('静态服务已启动：http://' + host + ':' + actual + '/diagnose/');
    console.log('（只监听 IPv4：浏览器若把 localhost 解析成 ::1 会连不上，用 127.0.0.1 访问）');
    console.log('已禁缓存：.js/.css/.html/.json 等返回 Cache-Control: no-store（改完代码刷新即生效）');
    console.log('根目录：' + dir + '（监听 ' + host + ':' + actual + '）');
  });

  const stop = function () { server.close(function () { process.exit(0); }); };
  process.on('SIGINT', stop);
  process.on('SIGTERM', stop);
  return server;
}

module.exports = { createServer: createServer, resolveRequestPath: resolveRequestPath, MIME: MIME };

if (require.main === module) main(process.argv.slice(2));
