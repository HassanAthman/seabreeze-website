/* Help centre: old #links, search and "Was this helpful?" */
(function(){
  var base = location.pathname.replace(/support\/.*$/, 'support/');
  // Old links such as /support/#change-wifi-password now have their own page.
  if (window.HC_OLD && location.hash) {
    var to = HC_OLD[location.hash.slice(1)];
    if (to) { location.replace(base + to + '/'); return; }
  }

  // ---- search ----
  var q = document.getElementById('hcq'), res = document.getElementById('hcres'), none = document.getElementById('hcnone');
  if (q && res) {
    // extra words people type, in English, Kiswahili and Italian
    var WORDS = {
      'renew-paybill': 'pay renew paybill mpesa m-pesa 4129691 lipa kulipa malipo pagare rinnovo rinnovare',
      'paid-no-internet': 'paid payment not reflect no internet nimelipa sina mtandao pagato non funziona',
      'change-wifi-password': 'wifi password name change 192.168.1.1 admin jina nenosiri badilisha nome cambiare',
      'check-expiry': 'expiry expire end date when plan ends mwisho kuisha tarehe scadenza scade',
      'slow-internet': 'slow speed buffering polepole kasi lenta lento velocita',
      'restart-router': 'restart reboot unplug off on zima washa riavvia spegni',
      'no-internet': 'no internet offline down not working lights hakuna mtandao taa non funziona luci',
      'forgot-wifi-password': 'forgot password lost label nimesahau nenosiri dimenticato',
      'router-placement': 'place position window signal weak weka dirisha posizione finestra segnale',
      'router-guide': 'router 3d parts lights reset ports sehemu taa parti',
      'lipa-mdogo-mdogo': 'small amounts installments mdogo kidogo kidogo rate a rate',
      'payment-questions': 'prices price cost package wrong account someone else early bei kifurushi prezzi prezzo costo',
      'sms-reminders': 'sms reminder stop messages ujumbe kumbusho promemoria',
      'stay-safe': 'fraud scam safe pin cash wizi ulaghai truffa sicurezza',
      'sms-answers': 'sms text message instant answer expiry paid price agent new mpya ujumbe jibu messaggio risposta'
    };
    var items = [], seen = {};
    [].forEach.call(document.querySelectorAll('.topics2 a, .pops a'), function(a){
      var href = a.getAttribute('href'); if (seen[href]) { var it = seen[href]; it.text += ' ' + a.textContent.toLowerCase(); return; }
      var slug = (href.match(/support\/([^\/]+)\//) || [])[1] || '';
      var title = (a.querySelector('b') || a.querySelector('span:not(.pop-ic)') || a).textContent.trim();
      var o = { href: href, title: title, text: (a.textContent + ' ' + (WORDS[slug] || '')).toLowerCase() };
      seen[href] = o; items.push(o);
    });
    var sel = -1;
    function render(){
      var v = q.value.trim().toLowerCase(), words = v.split(/\s+/).filter(Boolean);
      if (!words.length) { res.hidden = true; none.hidden = true; return; }
      var hits = items.map(function(it){
        var s = 0; words.forEach(function(w){ if (it.text.indexOf(w) > -1) s += (it.title.toLowerCase().indexOf(w) > -1 ? 2 : 1); });
        return { it: it, s: s };
      }).filter(function(h){ return h.s > 0; }).sort(function(a, b){ return b.s - a.s; }).slice(0, 6);
      res.innerHTML = '';
      hits.forEach(function(h, i){
        var a = document.createElement('a'); a.href = h.it.href; a.textContent = h.it.title; a.setAttribute('role', 'option'); a.id = 'hco' + i;
        res.appendChild(a);
      });
      sel = -1; res.hidden = !hits.length; none.hidden = !!hits.length;
    }
    q.addEventListener('input', render);
    q.addEventListener('focus', render);
    q.addEventListener('keydown', function(e){
      var opts = res.querySelectorAll('a'); if (!opts.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + opts.length) % opts.length;
        [].forEach.call(opts, function(o, i){ o.classList.toggle('on', i === sel); });
        q.setAttribute('aria-activedescendant', opts[sel].id);
      } else if (e.key === 'Enter') { e.preventDefault(); location.href = opts[sel < 0 ? 0 : sel].href; }
      else if (e.key === 'Escape') { res.hidden = true; }
    });
    document.addEventListener('click', function(e){ if (!e.target.closest('.hc-search')) res.hidden = true; });
  }

  // ---- was this helpful? ----
  [].forEach.call(document.querySelectorAll('.helpful'), function(box){
    var key = 'hc-' + box.getAttribute('data-guide');
    function show(v){
      box.querySelector('.hf-btns').hidden = true;
      box.querySelector(v === 'yes' ? '.hf-yes' : '.hf-no').hidden = false;
    }
    try { var old = localStorage.getItem(key); if (old) show(old); } catch (_) {}
    [].forEach.call(box.querySelectorAll('button[data-v]'), function(b){
      b.addEventListener('click', function(){
        var v = b.getAttribute('data-v'); show(v);
        try { localStorage.setItem(key, v); } catch (_) {}
      });
    });
  });
})();
