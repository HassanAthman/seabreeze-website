// POST /api/sms-preferences  (Cloudflare Pages Function)
// Saves a client's SMS choices into the CBriz D1 database (tables from
// cbriz-dashboard migrations/007_sms_preferences.sql). The cbriz-sms-sender
// worker reads sms_preferences before every reminder or marketing SMS.
//
// Body: { phone, reminders: 0|1|null, marketing: 0|1|null, website: "" }
// null means "leave as it is". Payment receipts are never affected.

const MAX_PER_PHONE_PER_DAY = 5;
const MAX_PER_CLIENT_PER_DAY = 20;

function reply(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" }
  });
}

// 07XXXXXXXX / 01XXXXXXXX / 2547XXXXXXXX / +2541XXXXXXXX / 7XXXXXXXX -> 2547XXXXXXXX
export function normalizeKenyanPhone(value) {
  let p = String(value || "").replace(/[^\d]/g, "");
  if (p.length === 10 && p.startsWith("0")) p = "254" + p.slice(1);
  else if (p.length === 9) p = "254" + p;
  if (!/^254[17]\d{8}$/.test(p)) return null;
  return p;
}

function choice(v) {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return n === 0 || n === 1 ? n : undefined;
}

async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return reply(400, { error: "Please fill in the form and try again." });
  }

  // Honeypot: people never see this field; bots fill it in.
  if (body.website) return reply(200, { message: "Saved. Thank you." });

  const phone = normalizeKenyanPhone(body.phone);
  if (!phone) return reply(400, { error: "Please enter a valid Kenyan phone number, e.g. 0712 345 678." });

  const reminders = choice(body.reminders);
  const marketing = choice(body.marketing);
  if (reminders === undefined || marketing === undefined) return reply(400, { error: "Please choose Yes or No." });
  if (reminders === null && marketing === null) return reply(400, { error: "Please choose for reminders, offers, or both." });

  if (!env.DB) return reply(503, { error: "Sorry, this is not available right now. Please WhatsApp 0720 499 691." });

  const day = new Date().toISOString().slice(0, 10);
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const clientHash = await sha256Hex(`${ip}|${day}`);

  try {
    const counts = await env.DB.prepare(`
      SELECT
        (SELECT COUNT(*) FROM sms_preference_requests WHERE phone = ?1 AND created_at >= datetime('now','-1 day')) AS per_phone,
        (SELECT COUNT(*) FROM sms_preference_requests WHERE client_hash = ?2 AND created_at >= datetime('now','-1 day')) AS per_client
    `).bind(phone, clientHash).first();
    if (Number(counts?.per_phone) >= MAX_PER_PHONE_PER_DAY || Number(counts?.per_client) >= MAX_PER_CLIENT_PER_DAY) {
      return reply(429, { error: "Too many changes today. Please try again tomorrow or WhatsApp 0720 499 691." });
    }

    await env.DB.batch([
      env.DB.prepare(`
        INSERT INTO sms_preference_requests (phone, reminders, marketing, source, client_hash)
        VALUES (?1, ?2, ?3, 'WEBSITE', ?4)
      `).bind(phone, reminders, marketing, clientHash),
      env.DB.prepare(`
        INSERT INTO sms_preferences (phone, reminders, marketing, source, updated_at)
        VALUES (?1, COALESCE(?2, 1), COALESCE(?3, 1), 'WEBSITE', CURRENT_TIMESTAMP)
        ON CONFLICT(phone) DO UPDATE SET
          reminders = COALESCE(?2, sms_preferences.reminders),
          marketing = COALESCE(?3, sms_preferences.marketing),
          source = 'WEBSITE',
          updated_at = CURRENT_TIMESTAMP
      `).bind(phone, reminders, marketing)
    ]);
  } catch (error) {
    console.error("sms-preferences save failed:", String(error));
    return reply(500, { error: "Sorry, that did not save. Please try again or WhatsApp 0720 499 691." });
  }

  const parts = [];
  if (reminders !== null) parts.push(reminders ? "you will get renewal reminders" : "renewal reminders are stopped");
  if (marketing !== null) parts.push(marketing ? "you will get offers" : "offers are stopped");
  return reply(200, { message: `Saved for 0${phone.slice(3)}: ${parts.join(" and ")}. Payment receipts still come after every payment.` });
}

export function onRequest() {
  return reply(405, { error: "Method not allowed" });
}
