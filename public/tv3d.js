/* Internet TV hero: a 15-second loop drawn on canvas in light 3D.
   0-5s the home router sends signal to the TV and it switches on,
   5-10s the TV shows a generic home screen (no real channels or logos),
   10-15s a phone and a TV box join with the same picture.
   Pauses off screen, in background tabs, on the pause button and for reduced motion. */
(function(){
  var cv=document.getElementById('tv3d'); if(!cv||!cv.getContext) return;
  var ctx=cv.getContext('2d'), W=0, H=0, DPR=Math.min(window.devicePixelRatio||1,2);
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var caps=[].slice.call(document.querySelectorAll('.tvcap')), btn=document.querySelector('.tv-pause');
  var LOOP=15, visible=true, paused=reduce, clock=reduce?12.5:0, last=null, capShown=0;
  function size(){ var r=cv.getBoundingClientRect(); W=r.width; H=r.height; cv.width=Math.round(W*DPR); cv.height=Math.round(H*DPR); ctx.setTransform(DPR,0,0,DPR,0,0); }
  size(); window.addEventListener('resize', function(){ size(); draw(clock); });

  var yaw=0, pitch=.28;
  function P(x,y,z){
    var c=Math.cos(yaw), s=Math.sin(yaw), X=x*c-z*s, Z=x*s+z*c;
    var Y=y*Math.cos(pitch)+Z*Math.sin(pitch), D=Z*Math.cos(pitch)-y*Math.sin(pitch)+8.2;
    var f=Math.min(W*.92,H*1.2)/D*.9; return {x:W/2+X*f, y:H*.86-Y*f, d:D, f:f};
  }
  function path(pts){ ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y); for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y); ctx.closePath(); }
  function fill(pts,c){ path(pts); ctx.fillStyle=c; ctx.fill(); }
  function clamp(v){ return v<0?0:v>1?1:v; }
  function ease(v){ v=clamp(v); return v*v*(3-2*v); }
  function lerp(a,b,u){ return {x:a.x+(b.x-a.x)*u, y:a.y+(b.y-a.y)*u}; }
  // a point inside a projected quad (tl, tr, br, bl)
  function at(q,u,v){ return lerp(lerp(q[0],q[1],u), lerp(q[3],q[2],u), v); }
  function sub(q,u0,v0,u1,v1){ return [at(q,u0,v0),at(q,u1,v0),at(q,u1,v1),at(q,u0,v1)]; }
  function grad(q,stops){ var a=at(q,0,0), b=at(q,0,1), g=ctx.createLinearGradient(a.x,a.y,b.x,b.y); stops.forEach(function(s){ g.addColorStop(s[0],s[1]); }); return g; }

  // box centred on x,z with its base at y; colours for top, front and sides
  function box(x,y,z,w,h,d,top,front,side){
    var a=w/2, b=d/2, v=function(dx,dy,dz){ return P(x+dx,y+dy,z+dz); };
    var F=[v(-a,h,-b),v(a,h,-b),v(a,0,-b),v(-a,0,-b)], L=[v(-a,h,b),v(-a,h,-b),v(-a,0,-b),v(-a,0,b)],
        R=[v(a,h,-b),v(a,h,b),v(a,0,b),v(a,0,-b)], T=[v(-a,h,b),v(a,h,b),v(a,h,-b),v(-a,h,-b)];
    if(yaw>0) fill(R,side); else fill(L,side);
    fill(T,top); fill(F,front); return F;
  }

  // abstract "programme" tiles: colour pairs and a simple shape, nothing real
  var TILES=[['#f08a24','#7a2e5c','sun'],['#0b6e78','#06242b','wave'],['#5a4bb0','#1b1640','hill'],['#c0392b','#3a0f14','dots'],['#2f7a5c','#0d2a1f','hill'],['#d9a441','#4a2a05','sun'],['#3fb3bd','#0a3d47','wave']];
  function art(q,t,k){
    var c=TILES[k%TILES.length]; fill(q,grad(q,[[0,c[0]],[1,c[1]]]));
    ctx.save(); path(q); ctx.clip();
    if(c[2]==='sun'){ var s=at(q,.68,.42), r=Math.abs(q[1].x-q[0].x)*.13; ctx.beginPath(); ctx.arc(s.x,s.y,r,0,7); ctx.fillStyle='rgba(255,236,190,.9)'; ctx.fill(); fill(sub(q,0,.62,1,1),'rgba(10,40,60,.55)'); }
    else if(c[2]==='wave'){ ctx.strokeStyle='rgba(255,255,255,.35)'; ctx.lineWidth=Math.max(1,Math.abs(q[1].x-q[0].x)*.02);
      for(var j=0;j<3;j++){ ctx.beginPath(); for(var i=0;i<=20;i++){ var p=at(q,i/20,.45+j*.15+Math.sin(i/3+t*2+j)*.04); i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);} ctx.stroke(); } }
    else if(c[2]==='hill'){ fill([at(q,0,1),at(q,.35,.45),at(q,.7,1)],'rgba(255,255,255,.22)'); fill([at(q,.4,1),at(q,.75,.55),at(q,1.1,1)],'rgba(0,0,0,.25)'); }
    else { for(var m=0;m<6;m++){ var d=at(q,.15+m*.14,.5+Math.sin(m+t*3)*.15); ctx.beginPath(); ctx.arc(d.x,d.y,Math.abs(q[1].x-q[0].x)*.04,0,7); ctx.fillStyle='rgba(255,255,255,.55)'; ctx.fill(); } }
    ctx.restore();
  }
  function playIcon(q,u,v,s,alpha){
    var c=at(q,u,v), w=Math.abs(q[1].x-q[0].x)*s;
    ctx.beginPath(); ctx.arc(c.x,c.y,w,0,7); ctx.fillStyle='rgba(255,255,255,'+(.85*alpha)+')'; ctx.fill();
    ctx.beginPath(); ctx.moveTo(c.x-w*.32,c.y-w*.5); ctx.lineTo(c.x+w*.55,c.y); ctx.lineTo(c.x-w*.32,c.y+w*.5); ctx.closePath(); ctx.fillStyle='rgba(11,47,58,'+alpha+')'; ctx.fill();
  }
  function pill(q,u,v,txt,on){
    var c=at(q,u,v), hgt=Math.max(7,Math.abs(q[3].y-q[0].y)*.09);
    ctx.font='700 '+Math.round(hgt*.62)+'px "JetBrains Mono", ui-monospace, monospace'; var w=ctx.measureText(txt).width+hgt*.8;
    ctx.beginPath(); if(ctx.roundRect) ctx.roundRect(c.x,c.y,w,hgt,hgt/2); else ctx.rect(c.x,c.y,w,hgt);
    ctx.fillStyle=on?'#f08a24':'rgba(255,255,255,.18)'; ctx.fill();
    ctx.fillStyle=on?'#2a1500':'#eef7f7'; ctx.textAlign='left'; ctx.textBaseline='middle'; ctx.fillText(txt,c.x+hgt*.4,c.y+hgt*.54); return w;
  }
  // the home screen shown on every device; detail = 1 for the TV, less for small screens
  function screen(q,t,on,detail){
    fill(q,'#05141a');
    if(on<=0){ fill(sub(q,.05,.05,.45,.5),'rgba(255,255,255,.04)'); return; }
    if(on<1){ var m=sub(q,0,.5-.5*ease(on*1.6),1,.5+.5*ease(on*1.6)); fill(m,'rgba(220,245,248,'+(1-on)+')'); if(on<.6) return; }
    var a=ease((on-.6)/.4);
    ctx.save(); path(q); ctx.clip(); ctx.globalAlpha=a;
    fill(q,grad(q,[[0,'#0c2c36'],[1,'#061a20']]));
    var hero=sub(q,.04,.07,.96,.6), k=Math.floor(t/3.2)%TILES.length;
    art(hero,t,k);
    fill(sub(hero,0,.55,.55,1),'rgba(5,20,26,.45)');
    if(detail>.5){
      fill(sub(hero,.05,.66,.4,.74),'rgba(255,255,255,.85)'); fill(sub(hero,.05,.8,.28,.86),'rgba(255,255,255,.45)');
      ctx.beginPath(); var ld=at(hero,.05,.12); ctx.arc(ld.x,ld.y,Math.max(2,Math.abs(hero[1].x-hero[0].x)*.012),0,7); ctx.fillStyle='#ff4d4d'; ctx.fill();
      var lx=.08; ['IT','EN','+'].forEach(function(s,i){ var w=pill(hero,lx,.07,s,i===((Math.floor(t*.6))%2)); lx+=w/Math.abs(hero[1].x-hero[0].x)+.015; });
    }
    playIcon(hero,.78,.72,.06,1);
    // a row of tiles sliding slowly, the focus box moves along it
    var n=detail>.5?5:3, gap=.025, tw=(.92-gap*(n-1))/n, shift=(t*.02)%1;
    for(var i=0;i<n;i++){ var u0=.04+i*(tw+gap), tq=sub(q,u0,.66,u0+tw,.93); art(tq,t,i+k+1+Math.floor(shift*3)); }
    var f=Math.floor(t*.8)%n, fu=.04+f*(tw+gap), fq=sub(q,fu-.006,.655,fu+tw+.006,.935);
    path(fq); ctx.strokeStyle='#f08a24'; ctx.lineWidth=Math.max(1.5,Math.abs(q[1].x-q[0].x)*.008); ctx.stroke();
    ctx.restore(); ctx.globalAlpha=1;
    // soft glass reflection
    fill([at(q,0,0),at(q,.35,0),at(q,.15,1),at(q,0,1)],'rgba(255,255,255,.035)');
  }

  function draw(t){
    var beat=t<5?0:t<10?1:2;
    yaw=reduce?-.22:Math.sin(t/LOOP*Math.PI*2)*.2-.04;
    ctx.clearRect(0,0,W,H);
    // room: back wall with a window on the sea, warm floor
    var wall=[P(-4.0,4.3,3),P(4.0,4.3,3),P(4.0,0,3),P(-4.0,0,3)];
    fill(wall,grad(wall,[[0,'#0f4f5c'],[1,'#0a3640']]));
    var win=[P(-3.75,3.6,2.98),P(-2.5,3.6,2.98),P(-2.5,1.6,2.98),P(-3.75,1.6,2.98)];
    fill(win,grad(win,[[0,'#2e3263'],[.38,'#c9667a'],[.55,'#ffc07a'],[.56,'#3c6f82'],[1,'#0e4d5a']]));
    var sn=at(win,.62,.5); ctx.beginPath(); ctx.arc(sn.x,sn.y,Math.abs(win[1].x-win[0].x)*.09,Math.PI,0); ctx.fillStyle='#ffe3a6'; ctx.fill();
    path(win); ctx.strokeStyle='rgba(238,247,247,.75)'; ctx.lineWidth=3; ctx.stroke();
    var mid=[at(win,.5,0),at(win,.5,1)]; ctx.beginPath(); ctx.moveTo(mid[0].x,mid[0].y); ctx.lineTo(mid[1].x,mid[1].y); ctx.stroke();
    var floor=[P(-4.0,0,3),P(4.0,0,3),P(4.0,0,-1.6),P(-4.0,0,-1.6)];
    fill(floor,grad(floor,[[0,'#8a5e3b'],[1,'#5e3d24']]));
    var lip=[P(-4.0,0,-1.6),P(4.0,0,-1.6),P(4.0,-.18,-1.6),P(-4.0,-.18,-1.6)]; fill(lip,'#4a2f1b');
    var rug=[P(-2.4,.01,1.4),P(2.4,.01,1.4),P(2.4,.01,-1.2),P(-2.4,.01,-1.2)]; fill(rug,'rgba(240,138,36,.22)');
    // cabinet and TV
    box(0,0,2.25,5,.75,.9,'#d9c4a3','#b89b74','#8f7556');
    box(0,.75,2.35,.9,.12,.4,'#2a3a40','#1d2a2f','#142024');
    box(0,.87,2.4,.14,.2,.1,'#2a3a40','#1d2a2f','#142024');
    var on=beat===0?clamp((t-2.4)/1.4):1;
    if(!reduce && t>LOOP-.5) on=clamp((LOOP-t)/.5);
    var tvF=box(0,1.05,2.45,3.7,2.1,.12,'#1a262b','#0d1518','#0a1114');
    var scr=sub(tvF,.025,.04,.975,.96);
    if(on>.6){ var gc=at(scr,.5,.5); var g=ctx.createRadialGradient(gc.x,gc.y,0,gc.x,gc.y,gc.y*.9); g.addColorStop(0,'rgba(63,179,189,'+(.18*on)+')'); g.addColorStop(1,'rgba(63,179,189,0)'); ctx.fillStyle=g; ctx.fillRect(0,0,W,H); }
    screen(scr,t,on,1);
    // home 5G router on the cabinet: rings, light and the signal travelling to the TV
    var rx=-2.05, rtop=P(rx,1.95,2.15), pulse=reduce?.6:(Math.sin(t*4)+1)/2;
    for(var j=1;j<=3;j++){ var ph=reduce?j/4:((t*.7)+j/3)%1, rr=rtop.f*(.25+ph*.9);
      ctx.strokeStyle='rgba(240,138,36,'+(.75*(1-ph))+')'; ctx.lineWidth=2.2; ctx.beginPath(); ctx.arc(rtop.x,rtop.y,rr,-Math.PI*.85,-Math.PI*.15); ctx.stroke(); }
    var rb=box(rx,.75,2.15,.42,1.15,.42,'#ffffff','#e6eff0','#b9cdd1');
    fill(sub(rb,0,.62,1,.7),'#0b6e78');
    var led=at(rb,.5,.25); ctx.beginPath(); ctx.arc(led.x,led.y,Math.max(2,rtop.f*.04),0,7); ctx.fillStyle='rgba(240,138,36,'+(.5+.5*pulse)+')'; ctx.fill();
    ctx.fillStyle='rgba(238,247,247,.92)'; ctx.font='700 '+Math.max(11,rtop.f*.22)+'px "Bricolage Grotesque", system-ui, sans-serif'; ctx.textAlign='center'; ctx.textBaseline='alphabetic';
    ctx.fillText('5G',rtop.x,rtop.y-rtop.f*.45);
    var tvc=P(-.6,2.3,2.38), from=P(rx,1.9,2.15), flow=beat===0?clamp((t-.6)/2):1;
    for(var d=0;d<9;d++){ var u=reduce?d/9:((t*.55)+d/9)%1; if(u>flow) continue;
      var x=from.x+(tvc.x-from.x)*u, y=from.y+(tvc.y-from.y)*u-Math.sin(u*Math.PI)*from.f*.7;
      ctx.beginPath(); ctx.arc(x,y,Math.max(1.6,from.f*.035)*(1-u*.4),0,7); ctx.fillStyle='rgba(255,192,122,'+(.95-u*.5)+')'; ctx.fill(); }
    // beat 3: a TV box on the cabinet and a phone in front, same picture
    var join=reduce?1:beat===2?ease((t-10)/1.2):0;
    if(!reduce && t>LOOP-.5) join*=clamp((LOOP-t)/.5);
    if(join>0){
      var bx=box(1.6,.75,1.95,.8*join,.18*join,.55,'#4a5c63','#2b3a40','#1d2a2f');
      var bl=at(bx,.85,.5); ctx.beginPath(); ctx.arc(bl.x,bl.y,Math.max(1.5,P(1.6,.8,1.9).f*.025),0,7); ctx.fillStyle='#3fb3bd'; ctx.fill();
      var py=.15+.55*join, ph=box(2.75,py,.3,.62,1.2,.06,'#4a5c63','#0d1518','#0a1114');
      screen(sub(ph,.07,.05,.93,.95),t,join,0);
      var tb=box(-3.0,py-.1,.4,1.25,.85,.06,'#4a5c63','#0d1518','#0a1114');
      screen(sub(tb,.05,.07,.95,.93),t+1.3,join,0);
    }
    var c=beat; if(c!==capShown && caps.length===3){ caps[capShown].hidden=true; caps[c].hidden=false; capShown=c; }
  }

  function frame(now){
    if(last==null) last=now;
    var dt=Math.min(.1,(now-last)/1000); last=now;
    if(!paused){ clock=(clock+dt)%LOOP; }
    draw(clock);
    if(visible && !paused && !document.hidden) requestAnimationFrame(frame); else last=null;
  }
  function start(){ if(visible && !paused && !document.hidden){ last=null; requestAnimationFrame(frame); } }
  function label(){ if(!btn) return; btn.querySelector('.tp-pause').hidden=paused; btn.querySelector('.tp-play').hidden=!paused; }
  if(btn){
    label();
    btn.addEventListener('click', function(){ paused=!paused; label(); if(!paused) start(); });
  }
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(es){ var v=es[0].isIntersecting, was=visible; visible=v; if(v && !was) start(); }).observe(cv);
  }
  document.addEventListener('visibilitychange', start);
  draw(clock); start();
})();
