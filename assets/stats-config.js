/* 访问统计配置。两项都留空时，站点不加载任何统计脚本，也不发出任何统计请求。
 * 填哪一项、怎么填，见 docs/pwa.md「统计」一节。 */
window.CNM_STATS = {
  // Cloudflare Web Analytics 的 token（站点的统计信标）。填了才会加载 Cloudflare 的信标脚本。
  cloudflareToken: '',
  // 已停用：上游自建采集地址，本 fork 不再上报（留空即不发出任何统计请求）。
  endpoint: '',
  // 可选回调：每个事件都会调用一次，参数是 { event, source, path, ts, ... }。
  onEvent: null
};
