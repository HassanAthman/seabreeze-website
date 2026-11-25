// POST /api/update-details  (Cloudflare Pages Function)
// A client (new or existing) sends the Airtel 5G line number of their router,
// their name and the phone that should get our SMS, from /update-details/.
// Saved in website_client_updates (cbriz-dashboard migrations/012) for staff
// to verify and approve in CBriz > Website Approvals. Nothing in the client
// database changes here.
// Every submission queues an SMS alert to the management phone (0782 998 842,
// renewal_monitor_settings.management_phone) through sms_outbox, which
// cbriz-sms-sender sends between 08:00 and 20:00 Kenya time.
//
// Body: { line, name, phone, alt_phone, expiry, note, lang, website (honeypot) }

const MAX_PER_CLIENT_PER_DAY = 6;
const MAX_PER_LINE_PER_DAY = 3;
const DEFAULT_ALERT_PHONE = "254782998842";

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
  else if (p.length === 13 && p.startsWith("2540")) p = "254" + p.slice(4);
  if (!/^254[17]\d{8}$/.test(p)) return null;
  return p;
}

// Same rule as CBriz (Hassan, 24 Nov 2026): a 5G line is the same with or
// without +254, 254 or the leading 0; an old account is the same with any
// zero padding or a small a. Without the A it must start with 00.
export function airtelIdentifier(value) {
  const raw = String(value ?? "").trim().toUpperCase().replace(/[\s+().-]/g, "");
  if (/^A\d+$/.test(raw)) {
    const sig = raw.slice(1).replace(/^0+/, "");
    return sig && sig.length <= 9 ? { kind: "ACCOUNT", key: "A" + sig.padStart(9, "0") } : null;
  }
  if (!/^\d+$/.test(raw)) return null;
  if (/^2540?[17]\d{8}$/.test(raw)) return { kind: "NUMERIC", key: raw.slice(-9) };
  if (/^0[17]\d{8}$/.test(raw)) return { kind: "NUMERIC", key: raw.slice(1) };
  if (/^[17]\d{8}$/.test(raw)) return { kind: "NUMERIC", key: raw };
  const sig = raw.replace(/^0+/, "");
  if (raw.startsWith("00") && raw.length <= 10 && sig && sig.length <= 9)
    return { kind: "ACCOUNT", key: "A" + sig.padStart(9, "0") };
  return null;
}

async function sha256Hex(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function updateRef() {
  const d = new Intl.DateTimeFormat("en-CA", { timeZone: "Africa/Nairobi", year: "2-digit", month: "2-digit", day: "2-digit" })
    .format(new Date()).replace(/-/g, "");
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(4));
  return `UP-${d}-${[...bytes].map((b) => alphabet[b % alphabet.length]).join("")}`;
}

const MSG = {
  en: {
    form: "Please fill in the form and try again.",
    line: "Please enter your Airtel 5G line number (the number of your router), e.g. 0712 345 678.",
    name: "Please enter your full name.",
    phone: "Please enter a valid Kenyan phone number for SMS, e.g. 0712 345 678.",
    alt: "The other phone number is not valid. Check it or leave it empty.",
    expiry: "Please pick a real date for when your plan ends, or leave it empty.",
    busy: "Sorry, this is not available right now. Please WhatsApp 0734 782 203.",
    many: "We have received several updates for this line today. Please WhatsApp 0734 782 203 instead.",
    fail: "Sorry, that did not save. Please try again or WhatsApp 0734 782 203.",
    ok: (ref) => `Thank you. We received your details (ref ${ref}). Our office will check them and update your record, usually within one working day.`
  },
  sw: {
    form: "Tafadhali jaza fomu na ujaribu tena.",
    line: "Tafadhali andika namba ya laini yako ya Airtel 5G (namba ya router yako), mfano 0712 345 678.",
    name: "Tafadhali andika jina lako kamili.",
    phone: "Tafadhali andika namba sahihi ya simu ya Kenya ya kupokea SMS, mfano 0712 345 678.",
    alt: "Namba ya simu nyingine si sahihi. Iangalie au iache wazi.",
    expiry: "Tafadhali chagua tarehe sahihi kifurushi chako kinapoisha, au iache wazi.",
    busy: "Samahani, huduma hii haipatikani sasa. Tafadhali tuma WhatsApp 0734 782 203.",
    many: "Tumepokea mabadiliko kadhaa ya laini hii leo. Tafadhali tuma WhatsApp 0734 782 203.",
    fail: "Samahani, haikuhifadhiwa. Jaribu tena au tuma WhatsApp 0734 782 203.",
    ok: (ref) => `Asante. Tumepokea taarifa zako (namba ${ref}). Ofisi yetu itazikagua na kusasisha rekodi yako, kwa kawaida ndani ya siku moja ya kazi.`
  },
  it: {
    form: "Compila il modulo e riprova.",
    line: "Inserisci il numero della tua linea Airtel 5G (il numero del router), es. 0712 345 678.",
    name: "Inserisci il tuo nome e cognome.",
    phone: "Inserisci un numero di telefono keniota valido per gli SMS, es. 0712 345 678.",
    alt: "L'altro numero di telefono non è valido. Controllalo o lascialo vuoto.",
    expiry: "Scegli una data valida di scadenza del piano, o lascia vuoto.",
    busy: "Spiacenti, il servizio non è disponibile ora. Scrivici su WhatsApp al 0734 782 203.",
    many: "Oggi abbiamo già ricevuto diversi aggiornamenti per questa linea. Scrivici su WhatsApp al 0734 782 203.",
    fail: "Spiacenti, non è stato salvato. Riprova o scrivici su WhatsApp al 0734 782 203.",
    ok: (ref) => `Grazie. Abbiamo ricevuto i tuoi dati (rif. ${ref}). Il nostro ufficio li verificherà e aggiornerà la tua scheda, di solito entro un giorno lavorativo.`
  }
};

export async function onRequestPost({ request, env }) {
  let b;
  try {
    b = await request.json();
  } catch {
    return reply(400, { error: MSG.en.form });
  }
  const lang = ["sw", "it"].includes(b.lang) ? b.lang : "en";
  const m = MSG[lang];

  // Honeypot: people never see this field; bots fill it in.
  if (b.website) return reply(200, { ok: true, ref: null, message: m.ok("-") });

  const lineInput = text(b.line, 30);
  const ident = airtelIdentifier(lineInput);
  const name = text(b.name, 120);
  const phone = normalizeKenyanPhone(b.phone);
  const altRaw = text(b.alt_phone, 20);
  const alt = altRaw ? normalizeKenyanPhone(altRaw) : null;
  const expiry = text(b.expiry, 10);
  const note = text(b.note, 300);

  if (!ident) return reply(400, { error: m.line });
  if (!name || name.length < 3) return reply(400, { error: m.name });
  if (!phone) return reply(400, { error: m.phone });
  if (altRaw && !alt) return reply(400, { error: m.alt });
  if (expiry && !(/^\d{4}-\d{2}-\d{2}$/.test(expiry) && !Number.isNaN(Date.parse(expiry + "T12:00:00Z"))
      && new Date(expiry + "T12:00:00Z").toISOString().slice(0, 10) === expiry)) return reply(400, { error: m.expiry });

  if (!env.DB) return reply(503, { error: m.busy });

  const day = new Date().toISOString().slice(0, 10);
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const clientHash = await sha256Hex(`${ip}|${day}|update-details`);

  try {
    const counts = await env.DB.prepare(`
      SELECT
        (SELECT COUNT(*) FROM website_client_updates WHERE client_hash = ?1 AND created_at >= datetime('now','-1 day')) AS per_client,
        (SELECT COUNT(*) FROM website_client_updates WHERE line_key = ?2 AND created_at >= datetime('now','-1 day')) AS per_line
    `).bind(clientHash, ident.key).first();
    if (Number(counts?.per_client) >= MAX_PER_CLIENT_PER_DAY || Number(counts?.per_line) >= MAX_PER_LINE_PER_DAY)
      return reply(429, { error: m.many });

    const ref = updateRef();
    // A newer submission for the same line replaces an older one still waiting
    // (the client corrected a typo); staff only see the latest.
    await env.DB.batch([
      env.DB.prepare(`UPDATE website_client_updates SET status = 'SUPERSEDED', review_note = ?1
        WHERE line_key = ?2 AND status = 'PENDING'`).bind(`Replaced by ${ref}`, ident.key),
      env.DB.prepare(`
        INSERT INTO website_client_updates (ref, line_input, line_kind, line_key, client_name, contact_phone,
          alt_phone, expiry_hint, client_note, language, client_hash)
        VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)
      `).bind(ref, lineInput, ident.kind, ident.key, name, phone, alt, expiry || null, note || null, lang, clientHash)
    ]);

    // Staff alert. Never block the client's request on it.
    try {
      const rows = await env.DB.prepare(`SELECT setting_key, setting_value FROM renewal_monitor_settings
        WHERE setting_key IN ('website_update_alerts_enabled', 'management_phone')`).all();
      const cfg = Object.fromEntries((rows.results || []).map((r) => [r.setting_key, r.setting_value]));
      const to = normalizeKenyanPhone(cfg.management_phone) || DEFAULT_ALERT_PHONE;
      if (cfg.website_update_alerts_enabled !== "0") {
        const line = ident.kind === "NUMERIC" ? "0" + ident.key : ident.key;
        const known = await env.DB.prepare(`SELECT id, customer_name FROM customers
          WHERE COALESCE(customer_status,'') <> 'MERGED' AND (
            substr(replace(replace(COALESCE(airtel_msisdn,''),' ',''),'+',''), -9) = ?1
            OR UPPER(TRIM(COALESCE(airtel_account,''))) = ?1) LIMIT 1`).bind(ident.key).first();
        const who = known ? `existing client #${known.id}` : "NEW line, not in CBriz";
        const message = `CBriz website update ${ref}: ${name}, line ${line} (${who}), SMS phone 0${phone.slice(3)}.` +
          ` Verify, then approve in CBriz > Website Approvals.`;
        await env.DB.prepare(`INSERT INTO sms_outbox (customer_id, phone, message, purpose, requested_by, status)
          VALUES (?1, ?2, ?3, 'STAFF_ALERT', 'website:update-details', 'QUEUED')`)
          .bind(known ? known.id : null, to, message.slice(0, 300)).run();
      }
    } catch (e) {
      console.error("Update alert not queued", String(e));
    }

    return reply(201, { ok: true, ref, message: m.ok(ref) });
  } catch (e) {
    console.error("update-details failed", String(e));
    return reply(500, { error: m.fail });
  }
}
