/* Interactive 3D router for the help centre.
   Drawn on a 2D canvas with a tiny projector (no library), so it stays light on phones.
   Drag to turn it, tap a numbered part, or play the restart guide. Words come from the page HTML,
   so every language version shows its own text. */
(function(){
  var cv=document.getElementById('router3d'); if(!cv||!cv.getContext) return;
  var ctx=cv.getContext('2d'), W=0, H=0, DPR=Math.min(window.devicePixelRatio||1,2);
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var dark=window.matchMedia('(prefers-color-scheme: dark)');
  function isDark(){ var t=document.documentElement.getAttribute('data-theme'); return t?t==='dark':dark.matches; }

  // ---- model: a rounded tower router on a small stand ----
  var A=.62, B=.5, N=72, Y0=.16, Y1=2.45, PW=4;
  function se(t,a,b){ var c=Math.cos(t), s=Math.sin(t);
    return [a*Math.sign(c)*Math.pow(Math.abs(c),2/PW), b*Math.sign(s)*Math.pow(Math.abs(s),2/PW)]; }
  function ring(a,b){ var r=[]; for(var i=0;i<N;i++){ var p=se(i/N*Math.PI*2,a,b); r.push(p); } return r; }
  var body=ring(A,B), stand=ring(A*.86,B*.86);
  function prism(r,y0,y1,col){
    var f=[];
    for(var i=0;i<r.length;i++){ var a=r[i], b=r[(i+1)%r.length];
      var nx=(b[1]-a[1]), nz=-(b[0]-a[0]), l=Math.hypot(nx,nz); nx/=l; nz/=l;
      f.push({p:[[a[0],y0,a[1]],[b[0],y0,b[1]],[b[0],y1,b[1]],[a[0],y1,a[1]]], n:[nx,0,nz], c:col}); }
    f.push({p:r.map(function(q){return [q[0],y1,q[1]];}).reverse(), n:[0,1,0], c:col, top:true});
    return f;
  }
  // outward normal check: our ring goes counter-clockwise in (x,z) seen from above, normals as computed point outward
  var faces=prism(stand,0,Y0,[60,72,78]).concat(prism(body,Y0,Y1,[236,242,243]));
  // decals on the flat front (+z) and back (-z)
  var FZ=B+.004, BZ=-B-.004;
  var parts={
    lights:{p:[0,1.85,FZ], n:[0,0,1], yaw:0},
    label:{p:[0,1.55,BZ], n:[0,0,-1], yaw:Math.PI},
    power:{p:[.26,.74,BZ], n:[0,0,-1], yaw:Math.PI},
    lan:{p:[-.2,.74,BZ], n:[0,0,-1], yaw:Math.PI},
    reset:{p:[.46,.3,BZ], n:[0,0,-1], yaw:Math.PI-.25}
  };
  // LEDs: power, signal, WiFi
  var leds=[{y:2.05,c:[56,200,120]},{y:1.85,c:[64,170,240]},{y:1.65,c:[56,200,120]}], ledOn=[1,1,1];

  // ---- camera ----
  var yaw=-.55, pitch=.32, tYaw=null, dist=7.2;
  function rot(x,y,z){
    var c=Math.cos(yaw), s=Math.sin(yaw), X=x*c+z*s, Z=-x*s+z*c;
    var cp=Math.cos(pitch), sp=Math.sin(pitch), Y=y*cp-Z*sp, Z2=y*sp+Z*cp;
    return [X,Y,Z2];
  }
  function proj(x,y,z){
    var r=rot(x,y-1.25,z), d=dist-r[2], f=Math.min(W,H)*1.9/d;
    return {x:W/2+r[0]*f, y:H*.5-r[1]*f, d:d, f:f, v:r};
  }
  function facing(p,n){ // visible from the camera?
    var v=rot(p[0],p[1]-1.25,p[2]), m=rot(n[0],n[1],n[2]);
    return (-v[0])*m[0]+(-v[1])*m[1]+(dist-v[2])*m[2] > 0;
  }
  var L=[-.45,.65,.62]; (function(){ var l=Math.hypot(L[0],L[1],L[2]); L=L.map(function(v){return v/l;}); })();

  function size(){ var r=cv.getBoundingClientRect(); W=r.width; H=r.height; cv.width=Math.round(W*DPR); cv.height=Math.round(H*DPR); ctx.setTransform(DPR,0,0,DPR,0,0); draw(); }

  function poly(pts,fill,stroke){ ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y); for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i].x,pts[i].y); ctx.closePath(); ctx.fillStyle=fill; ctx.fill(); if(stroke){ ctx.strokeStyle=stroke; ctx.stroke(); } }
  function shade(c,n){ var m=rot(n[0],n[1],n[2]), k=.7+.3*Math.max(0,m[0]*L[0]+m[1]*L[1]+m[2]*L[2]);
    return 'rgb('+Math.round(c[0]*k)+','+Math.round(c[1]*k)+','+Math.round(c[2]*k)+')'; }
  // a flat shape on the front/back face, given in face coordinates (u across, y up)
  function decal(z,sign,pts,fill,stroke){ poly(pts.map(function(q){ return proj(q[0]*sign,q[1],z); }),fill,stroke); }
  function circle(z,sign,cx,cy,r,fill,stroke){ var pts=[]; for(var i=0;i<20;i++){ var a=i/20*Math.PI*2; pts.push([cx+Math.cos(a)*r, cy+Math.sin(a)*r]); } decal(z,sign,pts,fill,stroke); }
  function rect(z,sign,x,y,w,h,fill,stroke){ decal(z,sign,[[x,y],[x+w,y],[x+w,y+h],[x,y+h]],fill,stroke); }

  var plugOut=0, now=0;
  function drawPlug(){
    // power plug sitting in the back socket; plugOut 0 = in, 1 = pulled out
    var px=-.26, py=.5-plugOut*.12, z0=-B-.02-plugOut*.9, z1=z0-.32, s=.075;
    var pts=[[px-s,py-s],[px+s,py-s],[px+s,py+s],[px-s,py+s]];
    var a=pts.map(function(q){return proj(q[0],q[1],z0);}), b=pts.map(function(q){return proj(q[0],q[1],z1);});
    for(var i=0;i<4;i++){ var j=(i+1)%4; poly([a[i],a[j],b[j],b[i]],'#2a3236'); }
    poly(b,'#394349');
    // cable: down to the floor and away
    var c0=proj(px,py,z1), c1=proj(px,py-.2,z1-.35), c2=proj(px-.2,0,z1-.8), c3=proj(px-.6,0,z1-1.6);
    ctx.strokeStyle='#2a3236'; ctx.lineWidth=Math.max(2,c0.f*.035); ctx.lineCap='round';
    ctx.beginPath(); ctx.moveTo(c0.x,c0.y); ctx.bezierCurveTo(c1.x,c1.y,c2.x,c2.y,c3.x,c3.y); ctx.stroke();
  }

  function draw(){
    if(!W) return;
    ctx.clearRect(0,0,W,H);
    var dk=isDark();
    // floor shadow
    var g0=proj(0,0,0); ctx.save(); ctx.translate(g0.x,g0.y); ctx.scale(1,.32);
    var sh=ctx.createRadialGradient(0,0,0,0,0,g0.f*1.1); sh.addColorStop(0,'rgba(0,0,0,'+(dk?.45:.22)+')'); sh.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sh; ctx.beginPath(); ctx.arc(0,0,g0.f*1.1,0,Math.PI*2); ctx.fill(); ctx.restore();

    var backVis=facing([0,1,-B],[0,0,-1]), frontVis=facing([0,1,B],[0,0,1]);
    if(!backVis) drawPlug();
    // body faces, back to front (convex, so culling is enough; sort keeps the stand right)
    var list=[];
    faces.forEach(function(fc){
      var c=fc.p.reduce(function(s,q){return [s[0]+q[0],s[1]+q[1],s[2]+q[2]];},[0,0,0]).map(function(v){return v/fc.p.length;});
      if(!facing(c,fc.n)) return;
      list.push({fc:fc, d:proj(c[0],c[1],c[2]).d});
    });
    list.sort(function(a,b){return b.d-a.d;});
    list.forEach(function(it){ var col=shade(it.fc.c,it.fc.n); poly(it.fc.p.map(function(q){return proj(q[0],q[1],q[2]);}),col,col); });

    // top vents
    if(facing([0,Y1,0],[0,1,0])) for(var v=-3;v<=3;v++){ var a=proj(v*.11,Y1+.002,-.25), b=proj(v*.11,Y1+.002,.25);
      ctx.strokeStyle='rgba(60,72,78,.45)'; ctx.lineWidth=Math.max(1.5,a.f*.022); ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke(); }

    if(frontVis){
      // brand stripe and the three lights
      rect(FZ,1,-.42,.82,.84,.05,'#f08a24');
      rect(FZ,1,-.1,1.52,.2,.66,'rgba(20,32,36,.85)');
      leds.forEach(function(l,i){
        var on=ledOn[i], blink=(i===1 && on===.5) ? ((Math.sin(now/140)>0)?1:0) : on;
        var c=l.c, col=blink?'rgb('+c+')':'#55646a';
        circle(FZ,1,0,l.y,.045,col);
        if(blink){ var p=proj(0,l.y,FZ), gr=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.f*.2);
          gr.addColorStop(0,'rgba('+c+',.55)'); gr.addColorStop(1,'rgba('+c+',0)'); ctx.fillStyle=gr; ctx.beginPath(); ctx.arc(p.x,p.y,p.f*.2,0,Math.PI*2); ctx.fill(); }
      });
      // "5G" mark made of simple strokes
      var m0=proj(-.12,1.25,FZ), m1=proj(.12,1.25,FZ);
      ctx.fillStyle='#0b6e78'; ctx.font='800 '+Math.max(9,m0.f*.2)+'px "Bricolage Grotesque", system-ui, sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
      ctx.save(); var mc=proj(0,1.25,FZ); ctx.translate(mc.x,mc.y); ctx.scale(Math.max(.05,Math.abs(m1.x-m0.x)/(m0.f*.24)),1); ctx.fillText('5G',0,0); ctx.restore();
    }
    if(backVis){
      var S=-1; // back face: u is mirrored so the layout reads left-to-right from behind
      // label with lines and a small code block
      rect(BZ,S,-.32,1.3,.64,.5,'#ffffff','rgba(60,72,78,.5)');
      for(var k=0;k<4;k++) rect(BZ,S,-.27,1.68-k*.09,.34-(k%2)*.1,.03,'rgba(40,52,58,.65)');
      for(var qx=0;qx<4;qx++) for(var qy=0;qy<4;qy++) if((qx*7+qy*3)%3) rect(BZ,S,.12+qx*.04,1.38+qy*.04,.035,.035,'#28343a');
      // ports
      rect(BZ,S,-.3,.43,.15,.13,'#20282c'); rect(BZ,S,-.11,.43,.15,.13,'#20282c');
      rect(BZ,S,-.28,.45,.11,.06,'#5b6b72'); rect(BZ,S,-.09,.45,.11,.06,'#5b6b72');
      circle(BZ,S,.26,.5,.075,'#20282c'); circle(BZ,S,.26,.5,.03,'#6d7d84');
      circle(BZ,S,.42,.5,.03,'#6d7d84'); circle(BZ,S,.42,.5,.014,'#20282c');
      drawPlug();
    }
    placeHotspots();
  }

  // ---- hotspots (HTML buttons, so they are translatable and keyboard friendly) ----
  var hsWrap=document.getElementById('r3hs'), hs=[].slice.call(hsWrap.querySelectorAll('button'));
  var info=document.getElementById('r3Info'), cards=[].slice.call(info.querySelectorAll('[data-info]'));
  function placeHotspots(){
    hs.forEach(function(b){
      var pt=parts[b.getAttribute('data-part')], p=pt.p, sgn=pt.n[2]<0?-1:1;
      // decals on the back are mirrored in drawing, so mirror the hotspot x as well
      var pr=proj(p[0]*(sgn<0?-1:1),p[1],p[2]);
      b.style.transform='translate('+pr.x.toFixed(1)+'px,'+pr.y.toFixed(1)+'px)';
      b.classList.toggle('back',!facing(p,pt.n));
    });
  }
  function showInfo(key){
    cards.forEach(function(c){ c.hidden=c.getAttribute('data-info')!==key; });
    hs.forEach(function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-part')===key); });
  }
  function turnTo(target){ var d=((target-yaw)%(Math.PI*2)+Math.PI*3)%(Math.PI*2)-Math.PI; tYaw=yaw+d; kick(); }
  hs.forEach(function(b){ b.addEventListener('click',function(){ stopRestart(); userTurned=true; var k=b.getAttribute('data-part'); showInfo(k); turnTo(parts[k].yaw); }); });

  // ---- dragging ----
  var drag=null, userTurned=false;
  cv.addEventListener('pointerdown',function(e){ drag={x:e.clientX,y:e.clientY,yaw:yaw,pitch:pitch,moved:false}; userTurned=true; tYaw=null; try{cv.setPointerCapture(e.pointerId);}catch(_){} });
  cv.addEventListener('pointermove',function(e){ if(!drag) return; var dx=e.clientX-drag.x, dy=e.clientY-drag.y;
    if(Math.abs(dx)+Math.abs(dy)>3) drag.moved=true;
    yaw=drag.yaw+dx*.012; pitch=Math.max(-.05,Math.min(.75,drag.pitch+dy*.006)); kick(); });
  function end(){ drag=null; }
  cv.addEventListener('pointerup',end); cv.addEventListener('pointercancel',end);
  cv.addEventListener('keydown',function(e){ if(e.key==='ArrowLeft'){yaw-=.2;kick();} if(e.key==='ArrowRight'){yaw+=.2;kick();} });
  cv.tabIndex=0;

  // ---- restart guide ----
  var tabExplore=document.getElementById('r3Explore'), tabRestart=document.getElementById('r3Restart');
  var steps=document.getElementById('r3Steps'), items=[].slice.call(steps.querySelectorAll('li'));
  var restart=null; // {t0}
  var STEP_T=[0,2.6,5.4,7.4,11.5]; // step start times (s); last = end
  function setTab(r){ tabExplore.setAttribute('aria-pressed',!r); tabRestart.setAttribute('aria-pressed',r); steps.hidden=!r; info.hidden=r; hsWrap.hidden=r; }
  function startRestart(){ setTab(true); restart={t0:performance.now()}; userTurned=true; turnTo(Math.PI-.35); kick(); }
  function stopRestart(){ if(!restart && steps.hidden) return; restart=null; plugOut=0; ledOn=[1,1,1]; setTab(false); items.forEach(function(li){li.className='';}); kick(); }
  tabRestart.addEventListener('click',function(){ startRestart(); });
  tabExplore.addEventListener('click',function(){ stopRestart(); showInfo('intro'); });
  document.querySelectorAll('[data-play="restart"]').forEach(function(a){ a.addEventListener('click',function(){ setTimeout(startRestart,400); }); });
  function runRestart(){
    var t=(performance.now()-restart.t0)/1000, step=0;
    if(reduce) t=STEP_T[4];
    for(var i=0;i<4;i++) if(t>=STEP_T[i]) step=i;
    items.forEach(function(li,i){ li.className = i<step||t>=STEP_T[4] ? 'done' : (i===step?'cur':''); });
    if(t<STEP_T[1]){ plugOut=Math.min(1,t/1.2); ledOn = t>1.2?[0,0,0]:[1,1,1]; }
    else if(t<STEP_T[2]){ plugOut=1; ledOn=[0,0,0]; }
    else if(t<STEP_T[3]){ plugOut=1-Math.min(1,(t-STEP_T[2])/1.2); ledOn=[0,0,0]; if(t-STEP_T[2]>.8) turnTo(-.5); }
    else { plugOut=0; var u=t-STEP_T[3]; ledOn=[1, u>1?(u>3?1:.5):0, u>3.2?1:0]; }
    if(reduce){ restart=null; return; }
    if(t>=STEP_T[4]+2.5){ restart.t0=performance.now(); turnTo(Math.PI-.35); }
  }

  // ---- loop: runs only while visible and something is moving ----
  var visible=true, raf=0;
  function kick(){ if(!raf) raf=requestAnimationFrame(loop); }
  var last=performance.now();
  function loop(ts){
    raf=0; var dt=Math.min(.05,(ts-last)/1000); last=ts; now=ts;
    var moving=false;
    if(tYaw!==null){ var d=tYaw-yaw; if(Math.abs(d)<.005||reduce){ yaw=tYaw; tYaw=null; } else { yaw+=d*Math.min(1,dt*5); moving=true; } }
    else if(!userTurned && !reduce){ yaw+=dt*.35; moving=true; }
    if(restart){ runRestart(); moving=true; }
    if(ledOn[1]===.5) moving=true;
    draw();
    if(visible && (moving || drag)) raf=requestAnimationFrame(loop);
  }
  if('IntersectionObserver' in window) new IntersectionObserver(function(es){ visible=es[0].isIntersecting; if(visible) kick(); }).observe(cv);
  document.addEventListener('visibilitychange',function(){ visible=!document.hidden; if(visible) kick(); });
  if(dark.addEventListener) dark.addEventListener('change',draw);
  window.addEventListener('resize',size);
  size(); kick();
})();
