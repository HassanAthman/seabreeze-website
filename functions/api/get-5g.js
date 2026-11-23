// POST /api/get-5g  (Cloudflare Pages Function)
// A client asks for a new Airtel 5G connection on /get-airtel-5g/.
// Saves the request as a lead in the CBriz "New 5G Leads" tracker
// (table new_5g_leads, cbriz-dashboard migrations/009_new_5g_leads.sql), so
// staff see it in CBriz and keep the client's details for renewals.
// Also queues a short alert SMS to staff through sms_outbox (sent by
// cbriz-sms-sender between 08:00 and 20:00 Kenya time).
//
// Body: { first_name, last_name, phone, email, no_email, county, town,
//         landmark, speed, plan_days, heard_from, marketing, website (honeypot) }

const MAX_PER_CLIENT_PER_DAY = 5;
// Staff phone(s) that get the "new website lead" SMS. Override with the Pages
// variable LEAD_ALERT_PHONES (comma separated). Only Airtel numbers are used.
const DEFAULT_ALERT_PHONES = "254734782203,254782998842";
const HEARD_FROM = ["Facebook", "TikTok", "Instagram", "WhatsApp", "Google", "A friend", "An agent or installer", "SMS", "Other"];

function reply(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" }
  });
}
const text = (v, max) => (typeof v === "string" ? v.trim().replace(/\s+/g, " ").slice(0, max) : "");

// 07XXXXXXXX / 01XXXXXXXX / 2547XXXXXXXX / +2541XXXXXXXX / 7XXXXXXXX -> 2547XXXXXXXX
export function normalizeKenyanPhone(value) {
  let p = String(value || "").replace(/[^\d]/g, "");
  if (p.length === 10 && p.startsWith("0")) p = "254" + p.slice(1);
  else if (p.length === 9) p = "254" + p;
  if (!/^254[17]\d{8}$/.test(p)) return null;
  return p;
}

async function sha256Hex(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function leadRef() {
  const d = new Intl.DateTimeFormat("en-CA", { timeZone: "Africa/Nairobi", year: "2-digit", month: "2-digit", day: "2-digit" })
    .format(new Date()).replace(/-/g, "");
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(4));
  return `SB-${d}-${[...bytes].map((b) => alphabet[b % alphabet.length]).join("")}`;
}

export async function onRequestPost({ request, env }) {
  let b;
  try {
    b = await request.json();
  } catch {
    return reply(400, { error: "Please fill in the form and try again." });
  }

  // Honeypot: people never see this field; bots fill it in.
  if (b.website) return reply(200, { ok: true, ref: null });

  const first = text(b.first_name, 60), last = text(b.last_name, 60);
  const phone = normalizeKenyanPhone(b.phone);
  const noEmail = b.no_email === true;
  const email = noEmail ? "" : text(b.email, 254).toLowerCase();
  const county = text(b.county, 80), town = text(b.town, 120), landmark = text(b.landmark, 200);
  const speed = Number(b.speed), days = Number(b.plan_days);
  const heard = HEARD_FROM.includes(b.heard_from) ? b.heard_from : "Other";

  if (!first || !last) return reply(400, { error: "Please enter your first and last name, as on your ID." });
  if (!phone) return reply(400, { error: "Please enter a valid Kenyan phone number, e.g. 0712 345 678." });
  if (!noEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email))
    return reply(400, { error: "Please enter your email address, or tick \"I don't have an email\"." });
  if (!county || !town) return reply(400, { error: "Please enter your county and town or estate." });
  if (![15, 30].includes(speed)) return reply(400, { error: "Please choose 15 Mbps or 30 Mbps." });
  if (![30, 90, 180].includes(days)) return reply(400, { error: "Please choose 30, 90 or 180 days." });

  if (!env.DB) return reply(503, { error: "Sorry, this is not available right now. Please WhatsApp 0734 782 203." });

  const day = new Date().toISOString().slice(0, 10);
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const clientHash = await sha256Hex(`${ip}|${day}|get-5g`);

  try {
    const open = await env.DB.prepare(
      "SELECT lead_ref FROM new_5g_leads WHERE contact_phone = ?1 AND status NOT IN ('INSTALLED','CANCELLED') LIMIT 1"
    ).bind(phone).first();
    if (open) {
      return reply(200, { ok: true, ref: open.lead_ref, existing: true,
        message: `We already have your request (${open.lead_ref}). We will call you on 0${phone.slice(3)}. To speed things up, WhatsApp 0734 782 203.` });
    }

    const recent = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM new_5g_leads WHERE client_hash = ?1 AND created_at >= datetime('now','-1 day')"
    ).bind(clientHash).first();
    if (Number(recent?.n) >= MAX_PER_CLIENT_PER_DAY)
      return reply(429, { error: "We have received several requests from this connection today. Please WhatsApp 0734 782 203 instead." });

    const ref = leadRef();
    const notes = `Website sign-up. Heard about us via: ${heard}.`;
    const res = await env.DB.prepare(`
      INSERT INTO new_5g_leads (lead_ref, first_name, last_name, contact_phone, email, email_is_seabreeze,
        location_county, location_town, location_landmark, package_speed, plan_days, source,
        marketing_consent, notes, client_hash)
      VALUES (?1, ?2, ?3, ?4, ?5, 0, ?6, ?7, ?8, ?9, ?10, 'WEBSITE', ?11, ?12, ?13)
    `).bind(ref, first, last, phone, email || null, county, town, landmark || null, speed, days,
      b.marketing === true ? 1 : 0, notes, clientHash).run();
    const leadId = res.meta.last_row_id;

    await env.DB.prepare(
      "INSERT INTO new_5g_lead_events (lead_id, event_type, detail, event_source) VALUES (?1, 'CAPTURED', ?2, 'WEBSITE')"
    ).bind(leadId, notes + (noEmail ? " No email: use a Seabreeze address." : "")).run();

    // Staff alert. Never block the client's request on it.
    const alertText = `New 5G request ${ref}: ${first} ${last}, 0${phone.slice(3)}, ${town}, ${county}. ` +
      `${speed}Mbps ${days} days.${noEmail ? " No email." : ""} Open CBriz > New 5G Leads.`;
    const phones = String(env.LEAD_ALERT_PHONES || DEFAULT_ALERT_PHONES).split(",")
      .map((p) => normalizeKenyanPhone(p)).filter(Boolean);
    for (const p of phones) {
      try {
        await env.DB.prepare(
          "INSERT INTO sms_outbox (phone, message, purpose, requested_by) VALUES (?1, ?2, 'STAFF_ALERT', 'website:get-5g')"
        ).bind(p, alertText.slice(0, 300)).run();
      } catch (e) {
        console.error("Lead alert not queued", String(e));
      }
    }

    return reply(201, { ok: true, ref });
  } catch (e) {
    console.error("get-5g failed", String(e));
    return reply(500, { error: "Sorry, that did not save. Please try again or WhatsApp 0734 782 203." });
  }
}
