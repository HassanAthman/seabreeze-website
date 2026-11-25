// Official payment receipt: https://seabreezedata.co.ke/r/<token>
// Receipts are made by staff on the CBriz desk (Receipts tab) or for new
// clients when their paybill payment is linked (cbriz-dashboard,
// functions/_lib/new-client-core.js). The token is the secret part of the
// link: 16 random characters, so receipts cannot be guessed or listed.
// Not an ETR / eTIMS tax invoice; the page says so.

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const kes = v => Number(v || 0).toLocaleString("en-KE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const prettyDay = d => /^\d{4}-\d{2}-\d{2}$/.test(d || "")
  ? new Date(d + "T12:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }) : "";
const prettyTime = t => {
  const m = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/.exec(t || "");
  return m ? `${prettyDay(`${m[1]}-${m[2]}-${m[3]}`)}, ${m[4]}:${m[5]}` : esc(t);
};
const ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
const TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];
function words(n) {
  n = Math.floor(n);
  if (n < 20) return ONES[n];
  if (n < 100) return TENS[Math.floor(n / 10)] + (n % 10 ? "-" + ONES[n % 10] : "");
  if (n < 1000) return ONES[Math.floor(n / 100)] + " hundred" + (n % 100 ? " and " + words(n % 100) : "");
  if (n < 1e6) return words(Math.floor(n / 1000)) + " thousand" + (n % 1000 ? (n % 1000 < 100 ? " and " : " ") + words(n % 1000) : "");
  return String(n);
}
const amountWords = v => { const n = Math.round(Number(v) || 0); const w = words(n); return n ? "Kenya Shillings " + w.charAt(0).toUpperCase() + w.slice(1) + " only" : ""; };

function page(status, title, body) {
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>${esc(title)}</title><link rel="icon" href="/favicon.svg">
<style>
:root{--ink:#0d2a33;--muted:#4d6870;--line:#d5e2e3;--sea:#0b6e78;--sun:#f08a24;--bg:#f3f7f7;--paper:#fff}
@media (prefers-color-scheme:dark){:root{--ink:#e4f0f1;--muted:#9db6bb;--line:#1f4048;--sea:#3fb3bd;--bg:#081c21;--paper:#0f2a31}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Segoe UI",system-ui,-apple-system,Arial,sans-serif}
.wrap{max-width:760px;margin:24px auto;padding:0 16px}
.rc{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:28px;position:relative;overflow:hidden}
.rc:before{content:"";position:absolute;left:0;right:0;top:0;height:6px;background:linear-gradient(90deg,var(--sea),var(--sun))}
.top{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:flex-start}
.co img{height:44px;display:block;margin-bottom:8px}.co b{font-size:17px}.co div{color:var(--muted);font-size:13px}
.no{text-align:right}.no h1{margin:0;font-size:20px;letter-spacing:.06em;text-transform:uppercase;color:var(--sea)}.no div{font-size:14px}
table{width:100%;border-collapse:collapse;margin:22px 0 8px}th,td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{width:38%;color:var(--muted);font-weight:600;font-size:13px}
.total{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;background:color-mix(in srgb,var(--sea) 10%,transparent);border-radius:10px;padding:14px 16px;margin-top:14px}
.total b{font-size:24px}.words{color:var(--muted);font-size:13px;margin-top:6px}
.stamp{display:inline-block;border:2px solid var(--sea);color:var(--sea);border-radius:8px;padding:4px 12px;font-weight:700;letter-spacing:.08em;transform:rotate(-4deg);margin-top:18px}
.void{border-color:#b42318;color:#b42318}
.note{color:var(--muted);font-size:12.5px;margin-top:18px;border-top:1px dashed var(--line);padding-top:12px}
.actions{margin:16px 0;display:flex;gap:8px;flex-wrap:wrap}.actions button,.actions a{font:inherit;font-weight:600;border:0;border-radius:10px;padding:10px 16px;background:var(--sea);color:#fff;cursor:pointer;text-decoration:none}
.actions a{background:transparent;color:var(--sea);border:1px solid var(--line)}
@media print{body{background:#fff;color:#000}.actions{display:none}.wrap{margin:0;max-width:none}.rc{border:0;padding:0}:root{--ink:#000;--muted:#444;--line:#bbb;--paper:#fff}}
@media (max-width:520px){.rc{padding:20px}.no{text-align:left}th{width:42%}}
</style></head><body><div class="wrap">${body}</div></body></html>`, {
    status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "private, no-store", "x-robots-tag": "noindex, nofollow", "referrer-policy": "no-referrer" }
  });
}

export async function onRequestGet({ params, env }) {
  const token = String(params.token || "");
  const notFound = () => page(404, "Receipt not found", `<div class="rc"><h1>Receipt not found</h1><p>Please check the link, or WhatsApp us on 0734 782 203 and we will send it again.</p></div>`);
  if (!/^[A-Za-z0-9]{16}$/.test(token) || !env.DB) return notFound();
  const r = await env.DB.prepare("SELECT * FROM receipts WHERE token = ?").bind(token).first().catch(() => null);
  if (!r) return notFound();
  env.DB.prepare("UPDATE receipts SET views = views + 1 WHERE id = ?").bind(r.id).run().catch(() => {});
  let co = {};
  try { co = JSON.parse(r.company_json || "{}"); } catch { co = {}; }
  const voided = r.status === "VOID";
  const issued = r.created_at ? prettyTime(new Date(new Date(r.created_at.replace(" ", "T") + "Z").getTime() + 3 * 3600000).toISOString().slice(0, 16).replace("T", " ")) : "";
  let period = "";
  if (r.period_from && r.period_to) {
    period = `${prettyDay(r.period_from)} to ${prettyDay(r.period_to)} (ends 23:59)`;
    if (r.is_advance) period += `<div class="words">Paid in advance: starts when the current plan ends.</div>`;
  } else if (r.lead_id) period = "30 days from the day the router is connected";
  const rows = [
    ["Received from", esc(r.received_from)],
    ["For", esc(r.service)],
    period ? ["Service period", period] : null,
    ["Paid by", `M-Pesa to Paybill ${esc(co.paybill || "4129691")}`],
    ["M-Pesa code", `<b>${esc(r.mpesa_code)}</b>`],
    ["Paid on", prettyTime(r.paid_at)],
    r.account_ref ? ["Account entered", esc(r.account_ref)] : null
  ].filter(Boolean);
  const body = `
<div class="actions"><button onclick="window.print()">Print or save as PDF</button><a href="https://seabreezedata.co.ke/">seabreezedata.co.ke</a></div>
<article class="rc">
  <div class="top">
    <div class="co"><img src="/brand/logo.svg" alt="Seabreeze"><b>${esc(co.name || "Seabreeze Data Ventures Ltd")}</b>
      <div>Authorised Airtel Kenya Enterprise Solution Partner</div>
      <div>${esc(co.address || "")}${co.postal ? " · " + esc(co.postal) : ""}</div>
      <div>${esc(co.phone || "")}${co.email ? " · " + esc(co.email) : ""}</div>
      <div>KRA PIN: <b>${esc(co.kra_pin || "")}</b></div></div>
    <div class="no"><h1>Official receipt</h1><div>No. <b>${esc(r.receipt_no)}</b></div><div>Issued ${issued}</div></div>
  </div>
  <table>${rows.map(([k, v]) => `<tr><th>${k}</th><td>${v}</td></tr>`).join("")}</table>
  <div class="total"><span>Amount received</span><b>KES ${kes(r.amount)}</b></div>
  <div class="words">${esc(amountWords(r.amount))}</div>
  ${voided ? `<div class="stamp void">VOID</div><div class="words">${esc(r.void_reason || "")}</div>` : `<div class="stamp">PAID</div>`}
  <p class="note">This receipt confirms a payment received by ${esc(co.name || "Seabreeze Data Ventures Ltd")}. It is not an ETR or eTIMS tax invoice. Questions: WhatsApp 0734 782 203. Thank you for choosing Seabreeze Data Ventures.</p>
</article>`;
  return page(200, `Receipt ${r.receipt_no}`, body);
}
