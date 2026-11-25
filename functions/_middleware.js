// Runs before every request on the Pages project (Cloudflare Pages Function middleware).
//
// Google should see one address per page: https://seabreezedata.co.ke/...
// The same site also answers on www.seabreezedata.co.ke and on the Pages
// address seabreeze-management.pages.dev, which Google would treat as copies.
// Send those to the main domain with a permanent (301) redirect, keeping the
// path and query. Pull request previews (<hash>.seabreeze-management.pages.dev)
// keep working but tell search engines not to index them.

const MAIN = "seabreezedata.co.ke";
const MOVE = new Set(["www.seabreezedata.co.ke", "seabreeze-management.pages.dev"]);

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const host = url.hostname.toLowerCase();

  if (MOVE.has(host)) {
    url.hostname = MAIN;
    url.protocol = "https:";
    url.port = "";
    // 308 keeps a form POST a POST; plain page visits get the classic 301.
    const status = context.request.method === "GET" || context.request.method === "HEAD" ? 301 : 308;
    return Response.redirect(url.toString(), status);
  }

  const res = await context.next();
  if (host.endsWith(".pages.dev")) {
    const out = new Response(res.body, res);
    out.headers.set("X-Robots-Tag", "noindex");
    return out;
  }
  return res;
}
