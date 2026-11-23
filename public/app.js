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
    ],
    it: [
      ["Apri M-Pesa","Scegli Lipa na M-Pesa, poi Pay Bill."],
      ["Numero aziendale: 4129691","Scrivilo esattamente così. È il paybill di Seabreeze."],
      ["Numero di conto","Il numero della tua linea Airtel 5G, ad esempio 0101234567."],
      ["Importo e PIN","Inserisci il prezzo del pacchetto, poi il tuo PIN. Fatto."]
    ]
  };
  var pageLang = (document.documentElement.lang||'en').slice(0,2);
  if(!steps[pageLang]) pageLang = 'en';
  var say = {
    en: {need:'Please add your name, a phone number we can call and your town.', open:'Opening WhatsApp. If it does not open, message 0734 782 203 directly.'},
    sw: {need:'Tafadhali weka jina lako, namba ya simu tunayoweza kupiga na mji wako.', open:'Tunafungua WhatsApp. Isipofunguka, tuma ujumbe kwa 0734 782 203 moja kwa moja.'},
    it: {need:'Inserisci il tuo nome, un numero di telefono a cui chiamarti e la tua città.', open:'Stiamo aprendo WhatsApp. Se non si apre, scrivi direttamente allo 0734 782 203.'}
  }[pageLang];
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
    Object.keys(steps).forEach(function(k){ var b=document.getElementById('lang-'+k); if(b) b.setAttribute('aria-pressed', lang===k); });
  }
  Object.keys(steps).forEach(function(k){ var b=document.getElementById('lang-'+k); if(b) b.onclick = function(){ renderSteps(k); }; });
  renderSteps(pageLang);
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
      m.hidden=false; m.textContent = say.need; return;
    }
    var msg = 'Hi Seabreeze, I have an enquiry.\nName: '+g('f-name')+'\nPhone: '+g('f-phone')+'\nTown: '+g('f-town')+(g('f-landmark')?'\nLandmark: '+g('f-landmark'):'')+'\nNeed: '+g('f-need')+'\nHeard about you via: '+g('f-src');
    m.hidden=false; m.textContent = say.open;
    window.location.href = 'https://wa.me/254734782203?text=' + encodeURIComponent(msg);
  });
})();

/* ---- 3D hero: a 5G outdoor unit on a pole sends signal rings to homes ---- */
(function(){
  var cv = document.getElementById('scene3d'); if(!cv || !cv.getContext) return;
  var ctx = cv.getContext('2d'), W=0, H=0, DPR=Math.min(window.devicePixelRatio||1, 2);
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var running = true, t0 = performance.now();
  function size(){ var r=cv.getBoundingClientRect(); W=r.width; H=r.height; cv.width=W*DPR; cv.height=H*DPR; ctx.setTransform(DPR,0,0,DPR,0,0); }
  size(); window.addEventListener('resize', size);
  // homes around the unit (x,z on the ground, h = height)
  var homes=[], n=9;
  for(var i=0;i<n;i++){ var a=i/n*Math.PI*2+0.3, r=3.2+((i*37)%10)/6; homes.push({x:Math.cos(a)*r, z:Math.sin(a)*r, w:.55+((i*13)%5)/10, h:.5+((i*7)%4)/6, lit:0}); }
  function proj(x,y,z,yaw){
    var c=Math.cos(yaw), s=Math.sin(yaw), X=x*c-z*s, Z=x*s+z*c;
    var tilt=.3, Y=y*Math.cos(tilt)-Z*Math.sin(tilt), D=Z*Math.cos(tilt)+y*Math.sin(tilt)+11;
    var f=Math.min(W,H)*.8/D; return {x:W/2+X*f, y:H*.74-Y*f, d:D, f:f};
  }
  function poly(pts,fill){ ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y); for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y); ctx.closePath(); ctx.fillStyle=fill; ctx.fill(); }
  function box(b,yaw,glow){
    var x=b.x,z=b.z,w=b.w/2,h=b.h, P=function(dx,dy,dz){return proj(x+dx,dy,z+dz,yaw);};
    var top=[P(-w,h,-w),P(w,h,-w),P(w,h,w),P(-w,h,w)];
    var faces=[[P(-w,0,-w),P(w,0,-w),P(w,h,-w),P(-w,h,-w)],[P(w,0,-w),P(w,0,w),P(w,h,w),P(w,h,-w)],[P(w,0,w),P(-w,0,w),P(-w,h,w),P(w,h,w)],[P(-w,0,w),P(-w,0,-w),P(-w,h,-w),P(-w,h,w)]];
    faces.sort(function(a,b){return (b[0].d+b[2].d)-(a[0].d+a[2].d);});
    faces.forEach(function(f,i){ poly(f, i>1 ? 'rgba(214,233,235,'+(.92)+')' : 'rgba(170,200,205,.95)'); });
    // roof
    var ridge=[P(0,h+.35,-w),P(0,h+.35,w)];
    poly([top[0],top[1],ridge[0]],'#0b6e78'); poly([top[3],top[2],ridge[1]],'#0b6e78');
    poly([top[1],top[2],ridge[1],ridge[0]],'#0e8591'); poly([top[0],top[3],ridge[1],ridge[0]],'#0a5d66');
    // window glow when signal arrives
    var wp=P(0,h*.5,0); ctx.beginPath(); ctx.arc(wp.x,wp.y,Math.max(2,wp.f*.09),0,Math.PI*2);
    ctx.fillStyle='rgba(240,138,36,'+(.25+glow*.75)+')'; ctx.fill();
    if(glow>.05){ ctx.beginPath(); ctx.arc(wp.x,wp.y,wp.f*.35*glow,0,Math.PI*2); ctx.fillStyle='rgba(240,138,36,'+(.18*glow)+')'; ctx.fill(); }
  }
  // a small island for the homes, floating on the page's own ocean background
  function backdrop(t, yaw){
    var hy=H*.27;
    // shallow water and a slow ripple around the island
    for(var r=0;r<2;r++){ var rr=6.2+r*.7+(reduce?0:Math.sin(t*.8+r)*.15); ctx.beginPath();
      for(var q0=0;q0<=72;q0++){ var a0=q0/72*Math.PI*2, p0=proj(Math.cos(a0)*rr,0,Math.sin(a0)*rr,yaw); q0?ctx.lineTo(p0.x,p0.y):ctx.moveTo(p0.x,p0.y); }
      ctx.fillStyle=r?'rgba(120,200,205,.07)':'rgba(120,200,205,.14)'; ctx.fill(); }
    // island
    ctx.beginPath();
    for(var q=0;q<=72;q++){ var qa=q/72*Math.PI*2, qp=proj(Math.cos(qa)*5.8,0,Math.sin(qa)*5.8,yaw); q?ctx.lineTo(qp.x,qp.y):ctx.moveTo(qp.x,qp.y); }
    ctx.fillStyle='rgba(240,214,170,.9)'; ctx.fill();
    ctx.beginPath();
    for(var q2=0;q2<=72;q2++){ var qb=q2/72*Math.PI*2, qr=proj(Math.cos(qb)*5.4,0,Math.sin(qb)*5.4,yaw); q2?ctx.lineTo(qr.x,qr.y):ctx.moveTo(qr.x,qr.y); }
    var land=ctx.createLinearGradient(0,hy,0,H); land.addColorStop(0,'#2f7a5c'); land.addColorStop(1,'#1d5a45');
    ctx.fillStyle=land; ctx.fill();
  }
  function frame(now){
    var t=(now-t0)/1000, yaw=reduce?0.6:t*.12+0.6;
    ctx.clearRect(0,0,W,H);
    backdrop(t, yaw);
    ctx.save(); ctx.beginPath();
    for(var q=0;q<=72;q++){ var qa=q/72*Math.PI*2, qp=proj(Math.cos(qa)*5.4,0,Math.sin(qa)*5.4,yaw); q?ctx.lineTo(qp.x,qp.y):ctx.moveTo(qp.x,qp.y); }
    ctx.clip();
    // ground grid
    ctx.lineWidth=1; ctx.strokeStyle='rgba(159,195,200,.13)';
    for(var g=-6; g<=6; g++){ var a=proj(g,0,-6,yaw), b=proj(g,0,6,yaw); ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
      a=proj(-6,0,g,yaw); b=proj(6,0,g,yaw); ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke(); }
    // signal rings on the ground
    var period=3.2, rings=3;
    for(var k=0;k<rings;k++){
      var ph=reduce ? (k+1)/(rings+1) : ((t/period)+k/rings)%1, R=ph*6.5;
      ctx.beginPath();
      for(var s=0;s<=64;s++){ var an=s/64*Math.PI*2, q=proj(Math.cos(an)*R,0.02,Math.sin(an)*R,yaw); s?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y); }
      ctx.strokeStyle='rgba(240,138,36,'+(0.75*(1-ph))+')'; ctx.lineWidth=2.2; ctx.stroke();
      homes.forEach(function(hm){ var d=Math.hypot(hm.x,hm.z); if(Math.abs(d-R)<.35) hm.lit=1; });
    }
    ctx.restore();
    homes.forEach(function(hm){ hm.lit = reduce ? .8 : Math.max(0, hm.lit-0.012); });
    // draw homes far-to-near, unit inserted by depth
    var items=homes.map(function(h){ return {d:proj(h.x,0,h.z,yaw).d, h:h}; }); items.push({d:proj(0,0,0,yaw).d, unit:true});
    items.sort(function(a,b){return b.d-a.d;});
    items.forEach(function(it){
      if(!it.unit){ box(it.h,yaw,it.h.lit); return; }
      var base=proj(0,0,0,yaw), top=proj(0,2.3,0,yaw), u0=proj(0,2.2,0,yaw), u1=proj(0,3.4,0,yaw), f=base.f;
      ctx.strokeStyle='#9db6bb'; ctx.lineWidth=Math.max(2,f*.07); ctx.beginPath(); ctx.moveTo(base.x,base.y); ctx.lineTo(top.x,top.y); ctx.stroke();
      var uw=f*.42, uh=u0.y-u1.y; // outdoor unit body
      var gr=ctx.createLinearGradient(u0.x-uw/2,0,u0.x+uw/2,0); gr.addColorStop(0,'#cfdfe1'); gr.addColorStop(.45,'#ffffff'); gr.addColorStop(1,'#a9c2c6');
      ctx.fillStyle=gr; ctx.beginPath(); if(ctx.roundRect) ctx.roundRect(u1.x-uw/2,u1.y,uw,uh,uw*.35); else ctx.rect(u1.x-uw/2,u1.y,uw,uh); ctx.fill();
      ctx.fillStyle='#0b6e78'; ctx.fillRect(u1.x-uw/2,u1.y+uh*.62,uw,uh*.1);
      var pulse=reduce?.6:(Math.sin(t*4)+1)/2; ctx.beginPath(); ctx.arc(u1.x,u1.y+uh*.25,Math.max(2,uw*.08),0,Math.PI*2); ctx.fillStyle='rgba(240,138,36,'+(.5+.5*pulse)+')'; ctx.fill();
      // airborne signal arcs
      for(var j=1;j<=3;j++){ var ph2=reduce?j/4:((t*.9)+j/3)%1, rr=uw*(.7+ph2*2.2);
        ctx.strokeStyle='rgba(240,138,36,'+(.8*(1-ph2))+')'; ctx.lineWidth=2.5;
        ctx.beginPath(); ctx.arc(u1.x,u1.y+uh*.3,rr,-Math.PI*.85,-Math.PI*.15); ctx.stroke(); }
      ctx.fillStyle='rgba(238,247,247,.9)'; ctx.font='700 '+Math.max(11,f*.2)+'px "Bricolage Grotesque", system-ui, sans-serif'; ctx.textAlign='center';
      ctx.fillText('5G', u1.x, u1.y-uw*1.15);
    });
    if(running && !reduce) requestAnimationFrame(frame);
  }
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(es){ var v=es[0].isIntersecting; if(v && !running){ running=true; requestAnimationFrame(frame);} running=v; }).observe(cv);
  }
  document.addEventListener('visibilitychange', function(){ if(document.hidden) running=false; else if(!running){ running=true; requestAnimationFrame(frame);} });
  requestAnimationFrame(frame);
  if(reduce) window.addEventListener('resize', function(){ requestAnimationFrame(frame); });
})();

/* ---- gentle reveal: content is visible at rest; it only slides up a little as it enters ---- */
(function(){
  if(!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var els=[].slice.call(document.querySelectorAll('.reveal'));
  els.forEach(function(el){ var r=el.getBoundingClientRect(); if(r.top>window.innerHeight) el.classList.add('pre'); });
  var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.remove('pre'); io.unobserve(e.target);} }); },{rootMargin:'0px 0px -40px 0px'});
  els.forEach(function(el){ io.observe(el); });
})();
