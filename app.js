(function(){
  var steps = {
    en: [
      ["Open M-Pesa","Select Lipa na M-Pesa, then Pay Bill."],
      ["Business number: 4129691","Type it exactly. This is Seabreeze's paybill."],
      ["Account number","Your Airtel 5G line number, e.g. 0101234567."],
      ["Amount and PIN","Enter your package price, then your PIN. Done."]
    ],
    sw: [
      ["Fungua M-Pesa","Chagua Lipa na M-Pesa, kisha Pay Bill."],
      ["Nambari ya biashara: 4129691","Andika kama ilivyo. Hii ni paybill ya Seabreeze."],
      ["Nambari ya akaunti","Nambari ya laini yako ya Airtel 5G, mfano 0101234567."],
      ["Kiasi na PIN","Weka bei ya kifurushi chako, kisha PIN yako. Umemaliza."]
    ]
  };
  var list = document.getElementById('steps');
  if(list){
  function renderSteps(lang){
    list.innerHTML = '';
    steps[lang].forEach(function(s){
      var li = document.createElement('li');
      var d = document.createElement('div');
      var b = document.createElement('b'); b.textContent = s[0];
      var sm = document.createElement('small'); sm.textContent = s[1];
      d.appendChild(b); d.appendChild(sm); li.appendChild(d); list.appendChild(li);
    });
    document.getElementById('lang-en').setAttribute('aria-pressed', lang==='en');
    document.getElementById('lang-sw').setAttribute('aria-pressed', lang==='sw');
  }
  document.getElementById('lang-en').onclick = function(){ renderSteps('en'); };
  document.getElementById('lang-sw').onclick = function(){ renderSteps('sw'); };
  renderSteps('en');
  }

  // Basic phone walkthrough
  var screens = [
    {t:"M-PESA", lines:["1 Send Money","2 Withdraw Cash","3 Buy Airtime","4 Lipa na M-PESA"], sel:3, soft:["Select","Back"]},
    {t:"Lipa na M-PESA", lines:["1 Pay Bill","2 Buy Goods"], sel:0, soft:["Select","Back"]},
    {t:"Enter business no.", input:"4129691", soft:["OK","Back"]},
    {t:"Enter account no.", input:"0101234567", soft:["OK","Back"]},
    {t:"Enter amount", input:"1999", soft:["OK","Back"]},
    {t:"Pay KES 1,999 to", lines:["SEABREEZE","Acc 0101234567","Enter PIN"], input:"****", soft:["OK","Back"]}
  ];
  var scr = document.getElementById('screen'), dots = document.getElementById('phoneSteps'), cur = 0, timer;
  if(scr){
  function draw(i){
    cur = i; var s = screens[i];
    var html = '<div class="bar"><span>Safaricom</span><span>12:40</span></div><div class="ttl">'+s.t+'</div>';
    (s.lines||[]).forEach(function(l,k){ html += '<div'+(k===s.sel?' style="background:rgba(31,42,20,.85);color:var(--screen);padding:0 4px"':'')+'>'+l+'</div>'; });
    if(s.input) html += '<div class="input">'+s.input+'</div>';
    html += '<div class="soft"><span>'+s.soft[0]+'</span><span>'+s.soft[1]+'</span></div>';
    scr.innerHTML = html;
    Array.prototype.forEach.call(dots.children, function(d,k){ d.setAttribute('aria-current', k===i); });
  }
  screens.forEach(function(_,k){
    var b = document.createElement('button'); b.type='button'; b.setAttribute('aria-label','Step '+(k+1));
    b.onclick = function(){ clearInterval(timer); draw(k); }; dots.appendChild(b);
  });
  draw(0);
  if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    timer = setInterval(function(){ draw((cur+1)%screens.length); }, 2600);
  }
  }

  // Copy paybill
  var cb=document.getElementById('copyBtn'); if(cb) cb.onclick = function(){
    var done = function(){ var c=document.getElementById('copied'); c.hidden=false; setTimeout(function(){c.hidden=true;},2000); };
    try{
      navigator.clipboard.writeText('4129691').then(done, function(){ selectNum(); });
    }catch(e){ selectNum(); }
  };
  function selectNum(){ var r=document.createRange(); r.selectNodeContents(document.getElementById('paybill')); var s=getSelection(); s.removeAllRanges(); s.addRange(r); }

  // Lead form: opens WhatsApp with the details filled in
  var lf = document.getElementById('leadForm');
  if(lf) lf.addEventListener('submit', function(e){
    e.preventDefault();
    var g = function(id){ return (document.getElementById(id).value||'').trim(); };
    var m = document.getElementById('formMsg');
    if(g('f-phone').replace(/\D/g,'').length < 9 || !g('f-name') || !g('f-town')){
      m.hidden=false; m.textContent = 'Please add your name, a phone number we can call and your town.'; return;
    }
    var msg = 'Hi Seabreeze, I have an enquiry.\nName: '+g('f-name')+'\nPhone: '+g('f-phone')+'\nTown: '+g('f-town')+(g('f-landmark')?'\nLandmark: '+g('f-landmark'):'')+'\nNeed: '+g('f-need')+'\nHeard about you via: '+g('f-src');
    m.hidden=false; m.textContent = 'Opening WhatsApp. If it does not open, message 0720 499 691 directly.';
    window.location.href = 'https://wa.me/254720499691?text=' + encodeURIComponent(msg);
  });
})();
